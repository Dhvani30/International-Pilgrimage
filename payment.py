from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, make_response, abort
from flask_login import login_required, current_user
from models import TripPlan, User, Notification, Booking, RefundRequest
from extensions import db, mail, csrf
from flask_mail import Message
import uuid
from datetime import datetime, timedelta
from fpdf import FPDF
import os

payment_bp = Blueprint('payment', __name__)

# Dummy account for testing payments
DUMMY_ACCOUNTS = {
    "test@example.com": {
        "card_number": "4111111111111111",
        "expiry": "12/25",
        "cvv": "123",
        "name": "Test User",
        "balance": 50000.00
    },
    "demo@example.com": {
        "card_number": "5555555555554444",
        "expiry": "10/26",
        "cvv": "321",
        "name": "Demo User",
        "balance": 100000.00
    }
}

@payment_bp.route('/checkout/<int:trip_id>', methods=['GET'])
@login_required
def checkout(trip_id):
    trip = TripPlan.query.get_or_404(trip_id)
    
    if trip.user_id != current_user.id:
        flash('You do not have permission to access this trip.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if trip.payment_status == 'paid':
        flash('This trip has already been paid for.', 'info')
        return redirect(url_for('payment.receipt', trip_id=trip.id))
    
    if not trip.base_price:
        pilgrimage = trip.pilgrimage
        price_breakdown = calculate_trip_price(
            pilgrimage,
            trip.num_travelers,
            trip.accommodation_type,
            trip.transportation,
            trip.guide_required
        )
        trip.base_price = price_breakdown['base_price']
        trip.accommodation_fee = price_breakdown['accommodation_fee']
        trip.transportation_fee = price_breakdown['transportation_fee']
        trip.guide_fee = price_breakdown['guide_fee']
        trip.tax_amount = price_breakdown['tax_amount']
        trip.discount_amount = price_breakdown['discount_amount']
        trip.total_price = price_breakdown['total']
        db.session.commit()
    
    dummy_accounts = list(DUMMY_ACCOUNTS.keys())
    
    return render_template('payment/checkout.html', 
                         trip=trip,
                         dummy_accounts=dummy_accounts,
                         stripe_public_key=current_app.config.get('STRIPE_PUBLIC_KEY', 'pk_test_sample'))

@csrf.exempt
@payment_bp.route('/process-payment/<int:trip_id>', methods=['POST'])
@login_required
def process_payment(trip_id):
    trip = TripPlan.query.get_or_404(trip_id)

    if trip.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        trip.payment_status = 'paid'
        trip.payment_id = f"PAYMENT-{uuid.uuid4().hex[:10].upper()}"
        trip.payment_method = 'card'
        trip.payment_date = datetime.utcnow()
        
        if not trip.confirmation_code:
            trip.confirmation_code = f"SJ-{uuid.uuid4().hex[:8].upper()}"
        
        booking = Booking(
            user_id=current_user.id,
            pilgrimage_id=trip.pilgrimage_id,
            travel_date=trip.start_date,
            special_requirements=trip.additional_notes
        )
        db.session.add(booking)
        
        notification = Notification(
            user_id=current_user.id,
            title='Payment Successful',
            message=f'Your payment for the trip to {trip.pilgrimage.name} was successful.',
            link=url_for('payment.receipt', trip_id=trip.id)
        )
        db.session.add(notification)
        
        db.session.commit()
        send_receipt_email(trip)
        
        return jsonify({
            'success': True,
            'redirect': url_for('payment.receipt', trip_id=trip.id)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Payment error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/receipt/<int:trip_id>')
@login_required
def receipt(trip_id):
    trip = TripPlan.query.get_or_404(trip_id)
    
    if trip.user_id != current_user.id:
        flash('You do not have permission to access this receipt.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('payment/receipt.html', trip=trip)

@payment_bp.route('/receipt/<int:trip_id>/pdf')
@login_required
def receipt_pdf(trip_id):
    trip = TripPlan.query.get_or_404(trip_id)
    
    if trip.user_id != current_user.id:
        abort(403)
    
    pdf = FPDF()
    pdf.add_page()
    
    # Try to use DejaVu font for Unicode support
    try:
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
        use_unicode = True
    except:
        pdf.set_font('helvetica', '', 12)
        use_unicode = False
    
    # Header
    pdf.set_font('DejaVu', 'B', 16) if use_unicode else pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, 'Sacred Journeys - Payment Receipt', 0, 1, 'C')
    pdf.ln(10)
    
    # Trip details
    pdf.set_font('DejaVu', '', 12) if use_unicode else pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 10, f'Confirmation Code: {trip.confirmation_code}', 0, 1)
    pdf.cell(0, 10, f'Payment Date: {trip.payment_date.strftime("%b %d, %Y %I:%M %p")}', 0, 1)
    pdf.ln(10)
    
    # Price breakdown
    pdf.set_font('DejaVu', 'B', 12) if use_unicode else pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, 'Payment Details', 0, 1)
    pdf.set_font('DejaVu', '', 12) if use_unicode else pdf.set_font('helvetica', '', 12)
    
    def format_currency(amount):
        return f"₹{amount:.2f}" if use_unicode else f"Rs.{amount:.2f}"
    
    pdf.cell(100, 10, 'Base Price:', 0, 0)
    pdf.cell(0, 10, format_currency(trip.base_price), 0, 1, 'R')
    
    pdf.cell(100, 10, 'Accommodation Fee:', 0, 0)
    pdf.cell(0, 10, format_currency(trip.accommodation_fee), 0, 1, 'R')
    
    pdf.cell(100, 10, 'Transportation Fee:', 0, 0)
    pdf.cell(0, 10, format_currency(trip.transportation_fee), 0, 1, 'R')
    
    pdf.cell(100, 10, 'Guide Fee:', 0, 0)
    pdf.cell(0, 10, format_currency(trip.guide_fee), 0, 1, 'R')
    
    pdf.cell(100, 10, 'Tax (8.5%):', 0, 0)
    pdf.cell(0, 10, format_currency(trip.tax_amount), 0, 1, 'R')
    
    if trip.discount_amount > 0:
        pdf.cell(100, 10, 'Discount:', 0, 0)
        pdf.cell(0, 10, format_currency(-trip.discount_amount), 0, 1, 'R')
    
    pdf.set_font('DejaVu', 'B', 14) if use_unicode else pdf.set_font('helvetica', 'B', 14)
    pdf.cell(100, 10, 'Total:', 0, 0)
    pdf.cell(0, 10, format_currency(trip.total_price), 0, 1, 'R')
    pdf.ln(15)
    
    # Footer
    pdf.set_font('DejaVu', 'I', 10) if use_unicode else pdf.set_font('helvetica', 'I', 10)
    pdf.cell(0, 10, 'Thank you for choosing Sacred Journeys!', 0, 1, 'C')
    
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers.set('Content-Disposition', 'attachment', filename=f'receipt_{trip.confirmation_code}.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response

@payment_bp.route('/cancel-trip/<int:trip_id>', methods=['POST'])
@login_required
def cancel_trip(trip_id):
    trip = TripPlan.query.get_or_404(trip_id)
    
    if trip.user_id != current_user.id:
        flash('You do not have permission to cancel this trip.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if trip.payment_status != 'paid':
        flash('Only paid trips can be cancelled.', 'danger')
        return redirect(url_for('main.trip_details', trip_id=trip.id))
    
    if trip.start_date < datetime.utcnow().date():
        flash('Cannot cancel trips that have already started.', 'danger')
        return redirect(url_for('main.trip_details', trip_id=trip.id))
    
    try:
        refund_amount = calculate_refund_amount(trip.total_price, (trip.start_date - datetime.utcnow().date()).days)
        
        refund_request = RefundRequest(
            trip_id=trip.id,
            user_id=current_user.id,
            amount=refund_amount,
            status='pending',
            request_date=datetime.utcnow(),
            reason='Trip cancellation'
        )
        db.session.add(refund_request)
        
        trip.payment_status = 'cancelled'
        trip.cancellation_date = datetime.utcnow()
        
        notification = Notification(
            user_id=current_user.id,
            title='Trip Cancelled',
            message=f'Your trip to {trip.pilgrimage.name} has been cancelled. Refund pending.',
            link=url_for('payment.refund_status', trip_id=trip.id)
        )
        db.session.add(notification)
        
        db.session.commit()
        send_cancellation_email(trip, refund_request)
        
        flash('Trip cancelled successfully. Refund request submitted.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cancelling trip: {str(e)}")
        flash('Error cancelling trip. Please try again.', 'danger')
    
    return redirect(url_for('main.trip_details', trip_id=trip.id))

@payment_bp.route('/request-refund/<int:trip_id>', methods=['POST'])
@login_required
def request_refund(trip_id):
    trip = TripPlan.query.get_or_404(trip_id)
    
    if trip.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if trip.payment_status != 'paid':
        return jsonify({'error': 'Only paid trips can be refunded'}), 400
    
    if trip.start_date < datetime.utcnow().date():
        return jsonify({'error': 'Cannot refund trips that have already started'}), 400
    
    try:
        days_until_trip = (trip.start_date - datetime.utcnow().date()).days
        refund_amount = calculate_refund_amount(trip.total_price, days_until_trip)
        
        refund_request = RefundRequest(
            trip_id=trip.id,
            user_id=current_user.id,
            amount=refund_amount,
            status='pending',
            request_date=datetime.utcnow(),
            reason=request.form.get('reason', 'Not specified')
        )
        db.session.add(refund_request)
        
        trip.payment_status = 'refund_pending'
        
        notification = Notification(
            user_id=current_user.id,
            title='Refund Requested',
            message=f'Refund requested for trip to {trip.pilgrimage.name}. Amount: ₹{refund_amount:.2f}',
            link=url_for('payment.refund_status', trip_id=trip.id)
        )
        db.session.add(notification)
        
        db.session.commit()
        send_refund_request_email(trip, refund_request)
        
        return jsonify({
            'success': True,
            'message': 'Refund request submitted successfully',
            'refund_amount': refund_amount,
            'status': 'pending'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing refund request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/refund-status/<int:trip_id>')
@login_required
def refund_status(trip_id):
    trip = TripPlan.query.get_or_404(trip_id)
    
    if trip.user_id != current_user.id:
        flash('You do not have permission to view this refund status.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    refund_request = RefundRequest.query.filter_by(trip_id=trip.id).first()
    
    return render_template('payment/refund_status.html', 
                         trip=trip,
                         refund_request=refund_request)

def calculate_refund_amount(total_amount, days_until_trip):
    """Calculate refund amount based on cancellation policy"""
    if days_until_trip > 30:
        return total_amount  # Full refund
    elif days_until_trip > 14:
        return total_amount * 0.7  # 70% refund
    elif days_until_trip > 2:
        return total_amount * 0.5  # 50% refund
    else:
        return 0  # No refund for last-minute cancellations

def send_receipt_email(trip):
    """Send receipt email to the user"""
    try:
        user = User.query.get(trip.user_id)
        if not user or not user.email:
            current_app.logger.error("Cannot send email: User not found or no email address")
            return False
        
        subject = f"Sacred Journeys - Payment Receipt #{trip.confirmation_code}"
        
        html_body = render_template(
            'payment/email_receipt.html',
            trip=trip,
            user=user
        )
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@sacredjourneys.com')
        )
        
        mail.send(msg)
        current_app.logger.info(f"Receipt email sent to {user.email}")
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending receipt email: {str(e)}")
        return False

def send_cancellation_email(trip, refund_request):
    """Send cancellation confirmation email"""
    try:
        user = User.query.get(trip.user_id)
        if not user or not user.email:
            current_app.logger.error("Cannot send email: User not found or no email address")
            return False
        
        days_until_trip = (trip.start_date - datetime.utcnow().date()).days
        refund_amount = calculate_refund_amount(trip.total_price, days_until_trip)
        
        subject = f"Sacred Journeys - Trip Cancellation #{trip.confirmation_code}"
        
        html_body = render_template(
            'payment/email_cancellation.html',
            trip=trip,
            user=user,
            refund_request=refund_request,
            refund_amount=refund_amount,
            expected_refund_date=datetime.utcnow() + timedelta(days=7)
        )
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@sacredjourneys.com')
        )
        
        mail.send(msg)
        current_app.logger.info(f"Cancellation email sent to {user.email}")
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending cancellation email: {str(e)}")
        return False

def send_refund_request_email(trip, refund_request):
    """Send refund request confirmation email"""
    try:
        user = User.query.get(trip.user_id)
        if not user or not user.email:
            current_app.logger.error("Cannot send email: User not found or no email address")
            return False
        
        subject = f"Sacred Journeys - Refund Request #{refund_request.id}"
        
        html_body = render_template(
            'payment/email_refund_request.html',
            trip=trip,
            user=user,
            refund_request=refund_request,
            expected_refund_date=datetime.utcnow() + timedelta(days=7)
        )
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@sacredjourneys.com')
        )
        
        mail.send(msg)
        current_app.logger.info(f"Refund request email sent to {user.email}")
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending refund request email: {str(e)}")
        return False

def calculate_trip_price(pilgrimage, num_travelers, accommodation_type, transportation, guide_required):
    """Calculate the total price of a trip based on various factors and return price breakdown"""
    base_price = pilgrimage.price or 100.0
    
    accommodation_multipliers = {
        'budget': 1.0,
        'standard': 1.5,
        'luxury': 2.5
    }
    
    transportation_multipliers = {
        'public': 1.0,
        'private': 1.8,
        'guided_tour': 2.2
    }
    
    base_total = base_price * num_travelers
    accommodation_fee = base_total * (accommodation_multipliers.get(accommodation_type, 1.0) - 1.0)
    transportation_fee = base_total * (transportation_multipliers.get(transportation, 1.0) - 1.0)
    guide_fee = 50.0 if guide_required else 0.0
    
    subtotal = base_total + accommodation_fee + transportation_fee + guide_fee
    tax_amount = round(subtotal * 0.085, 2)
    
    discount_amount = 0
    if num_travelers > 3:
        discount_amount = round(subtotal * 0.05, 2)
    
    total = subtotal + tax_amount - discount_amount
    
    return {
        'base_price': base_price,
        'base_total': base_total,
        'accommodation_fee': accommodation_fee,
        'transportation_fee': transportation_fee,
        'guide_fee': guide_fee,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'discount_amount': discount_amount,
        'total': round(total, 2)
    }