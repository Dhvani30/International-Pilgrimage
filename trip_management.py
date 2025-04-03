from flask import Blueprint, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import TripPlan, Booking, Notification, User
from extensions import db
from datetime import datetime
import uuid

trip_bp = Blueprint('trip', __name__)

@trip_bp.route('/trip/delete/<int:trip_id>', methods=['POST'])
@login_required
def delete_trip(trip_id):
    """Delete a trip plan"""
    trip = TripPlan.query.get_or_404(trip_id)
    
    # Ensure the trip belongs to the current user
    if trip.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Only allow deletion of unpaid trips
    if trip.payment_status == 'paid':
        return jsonify({'success': False, 'error': 'Cannot delete a paid trip. Please request a refund instead.'}), 400
    
    try:
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            title='Trip Deleted',
            message=f'Your trip to {trip.pilgrimage.name} has been deleted.',
            link=url_for('main.pilgrimages')
        )
        db.session.add(notification)
        
        # Delete the trip
        db.session.delete(trip)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@trip_bp.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            title='Booking Cancelled',
            message=f'Your booking for {booking.pilgrimage.name} has been cancelled.',
            link=url_for('main.pilgrimages')
        )
        db.session.add(notification)
        
        # Delete the booking
        db.session.delete(booking)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@trip_bp.route('/payment/refund_request/<int:trip_id>', methods=['POST'])
@login_required
def refund_request(trip_id):
    """Request a refund for a paid trip"""
    trip = TripPlan.query.get_or_404(trip_id)
    
    # Ensure the trip belongs to the current user
    if trip.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Only allow refund requests for paid trips
    if trip.payment_status != 'paid':
        return jsonify({'success': False, 'error': 'This trip has not been paid for yet.'}), 400
    
    # Get refund reason and details from request
    data = request.json
    reason = data.get('reason')
    details = data.get('details', '')
    
    if not reason:
        return jsonify({'success': False, 'error': 'Please provide a reason for the refund.'}), 400
    
    try:
        # Update trip status
        trip.payment_status = 'refund_pending'
        trip.refund_reason = reason
        trip.refund_details = details
        trip.refund_requested_at = datetime.utcnow()
        
        # Create notification for user
        user_notification = Notification(
            user_id=current_user.id,
            title='Refund Request Submitted',
            message=f'Your refund request for the trip to {trip.pilgrimage.name} has been submitted and is being processed.',
            link=url_for('main.trip_details', trip_id=trip.id)
        )
        db.session.add(user_notification)
        
        # Create notification for admin (assuming admin has user_id=1)
        admin = User.query.filter_by(id=1).first()
        if admin:
            admin_notification = Notification(
                user_id=admin.id,
                title='New Refund Request',
                message=f'User {current_user.username} has requested a refund for their trip to {trip.pilgrimage.name}.',
                link=url_for('main.trip_details', trip_id=trip.id)
            )
            db.session.add(admin_notification)
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

