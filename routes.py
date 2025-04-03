from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from models import Pilgrimage, Review, TripPlan, Booking, Notification
from forms import BookingForm, TripPlanningForm, ReviewForm, ProfileForm
from extensions import db
from datetime import datetime
import uuid
import json
import os

# Create the main blueprint
main = Blueprint('main', __name__)

def generate_confirmation_code():
    """Generate a unique confirmation code for bookings"""
    return f"SJ-{uuid.uuid4().hex[:8].upper()}"

# Calculate trip price function
def calculate_trip_price(pilgrimage, num_travelers, accommodation_type, transportation, guide_required):
    """Calculate the total price of a trip based on various factors and return price breakdown"""
    # Base price from pilgrimage
    base_price = pilgrimage.price or 100.0  # Default to 100 if no price set
    
    # Accommodation multiplier
    accommodation_multipliers = {
        'budget': 1.0,
        'standard': 1.5,
        'luxury': 2.5
    }
    
    # Transportation multiplier
    transportation_multipliers = {
        'public': 1.0,
        'private': 1.8,
        'guided_tour': 2.2
    }
    
    # Calculate individual components
    base_total = base_price * num_travelers
    accommodation_fee = base_total * (accommodation_multipliers.get(accommodation_type, 1.0) - 1.0)
    transportation_fee = base_total * (transportation_multipliers.get(transportation, 1.0) - 1.0)
    guide_fee = 50.0 if guide_required else 0.0
    
    # Calculate tax (8.5%)
    subtotal = base_total + accommodation_fee + transportation_fee + guide_fee
    tax_amount = round(subtotal * 0.085, 2)
    
    # Apply discount (if any) - for example, 5% for trips with more than 3 travelers
    discount_amount = 0
    if num_travelers > 3:
        discount_amount = round(subtotal * 0.05, 2)
    
    # Calculate total
    total = subtotal + tax_amount - discount_amount
    
    # Return price breakdown
    price_breakdown = {
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
    
    return price_breakdown

@main.route('/')
def index():
    # Get featured pilgrimages
    featured_pilgrimages = Pilgrimage.query.filter_by(featured=True).limit(6).all()
    
    # If no featured pilgrimages, get the ones with highest ratings
    if not featured_pilgrimages:
        # This is a simple approach - in a real app, you might want to calculate this differently
        featured_pilgrimages = Pilgrimage.query.limit(6).all()
    
    return render_template('index.html', featured_pilgrimages=featured_pilgrimages)

@main.route('/pilgrimages')
def pilgrimages():
    page = request.args.get('page', 1, type=int)
    pilgrimages = Pilgrimage.query.paginate(page=page, per_page=9)
    return render_template('pilgrimages.html', pilgrimages=pilgrimages)

@main.route('/pilgrimage/<int:id>', methods=['GET', 'POST'])
def pilgrimage(id):
    pilgrimage = Pilgrimage.query.get_or_404(id)
    form = BookingForm()
    review_form = ReviewForm()
    
    if review_form.validate_on_submit() and current_user.is_authenticated:
        # Check if user has already reviewed this pilgrimage
        existing_review = Review.query.filter_by(
            user_id=current_user.id,
            pilgrimage_id=pilgrimage.id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this pilgrimage.', 'warning')
        else:
            review = Review(
                user_id=current_user.id,
                pilgrimage_id=pilgrimage.id,
                rating=int(review_form.rating.data),
                comment=review_form.comment.data
            )
            db.session.add(review)
            db.session.commit()
            flash('Your review has been submitted!', 'success')
        
        return redirect(url_for('main.pilgrimage', id=pilgrimage.id))
    
    # Get reviews for this pilgrimage
    reviews = Review.query.filter_by(pilgrimage_id=pilgrimage.id).order_by(Review.created_at.desc()).all()
    
    return render_template('pilgrimage.html', 
                          pilgrimage=pilgrimage, 
                          form=form, 
                          review_form=review_form,
                          reviews=reviews)

@main.route('/book_pilgrimage/<int:pilgrimage_id>', methods=['POST'])
@login_required
def book_pilgrimage(pilgrimage_id):
    pilgrimage = Pilgrimage.query.get_or_404(pilgrimage_id)
    form = BookingForm()
    
    if form.validate_on_submit():
        booking = Booking(
            user_id=current_user.id,
            pilgrimage_id=pilgrimage_id,
            travel_date=form.travel_date.data,
            special_requirements=form.special_requirements.data
        )
        db.session.add(booking)
        db.session.commit()
        
        flash('Your booking has been confirmed!', 'success')
        return redirect(url_for('main.dashboard'))
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")
    
    return redirect(url_for('main.pilgrimage', id=pilgrimage_id))

@main.route('/plan_trip', methods=['GET', 'POST'])
@login_required
def plan_trip():
    form = TripPlanningForm()
    
    # Get all pilgrimages for the dropdown
    pilgrimages = Pilgrimage.query.all()
    form.pilgrimage.choices = [(str(p.id), p.name) for p in pilgrimages]
    
    # Pre-select pilgrimage if provided in URL
    pilgrimage_id = request.args.get('pilgrimage_id')
    if pilgrimage_id and request.method == 'GET':
        form.pilgrimage.data = pilgrimage_id
    
    if form.validate_on_submit():
        # Get the selected pilgrimage
        pilgrimage = Pilgrimage.query.get(int(form.pilgrimage.data))
        
        # Generate confirmation code
        confirmation_code = generate_confirmation_code()
        
        # Calculate price breakdown
        price_breakdown = calculate_trip_price(
            pilgrimage,
            form.num_travelers.data,
            form.accommodation_type.data,
            form.transportation.data,
            form.guide_required.data
        )
        
        # Create trip plan
        trip_plan = TripPlan(
            user_id=current_user.id,
            pilgrimage_id=int(form.pilgrimage.data),
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            num_travelers=form.num_travelers.data,
            accommodation_type=form.accommodation_type.data,
            transportation=form.transportation.data,
            meal_preference=form.meal_preference.data,
            guide_required=form.guide_required.data,
            additional_notes=form.additional_notes.data,
            confirmation_code=confirmation_code,
            total_price=price_breakdown['total'],
            payment_status='pending',
            base_price=price_breakdown['base_price'],
            accommodation_fee=price_breakdown['accommodation_fee'],
            transportation_fee=price_breakdown['transportation_fee'],
            guide_fee=price_breakdown['guide_fee'],
            tax_amount=price_breakdown['tax_amount'],
            discount_amount=price_breakdown['discount_amount']
        )
        
        db.session.add(trip_plan)
        db.session.commit()
        
        flash('Your trip has been planned successfully! Proceed to payment to confirm your booking.', 'success')
        return redirect(url_for('main.trip_details', trip_id=trip_plan.id))
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")
    
    return render_template('plan_trip.html', form=form)

@main.route('/trip_details/<int:trip_id>')
@login_required
def trip_details(trip_id):
    trip = TripPlan.query.get_or_404(trip_id)
    
    # Ensure the trip belongs to the current user
    if trip.user_id != current_user.id:
        flash('You do not have permission to view this trip.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('trip_details.html', trip=trip)

@main.route('/dashboard')
@login_required
def dashboard():
    # Get user's bookings and trip plans
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    trip_plans = TripPlan.query.filter_by(user_id=current_user.id).all()
    
    # Get current date for comparing with travel dates
    now = datetime.now().date()
    
    return render_template('dashboard.html', 
                          bookings=bookings, 
                          trip_plans=trip_plans,
                          now=now)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        current_user.preferences = form.preferences.data
        
        # Handle profile picture upload
        if form.profile_picture.data:
            filename = form.profile_picture.data.filename
            # Create a unique filename
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            # Save the file
            file_path = os.path.join(current_app.root_path, 'static', 'uploads', unique_filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            form.profile_picture.data.save(file_path)
            # Update the user's profile picture
            current_user.profile_picture = f"/static/uploads/{unique_filename}"
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
        form.preferences.data = current_user.preferences
    
    # Get user's reviews
    reviews = Review.query.filter_by(user_id=current_user.id).all()
    
    return render_template('profile.html', form=form, reviews=reviews)

@main.route('/review_pilgrimage/<int:pilgrimage_id>', methods=['POST'])
@login_required
def review_pilgrimage(pilgrimage_id):
    pilgrimage = Pilgrimage.query.get_or_404(pilgrimage_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        # Check if user has already reviewed this pilgrimage
        existing_review = Review.query.filter_by(
            user_id=current_user.id,
            pilgrimage_id=pilgrimage_id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this pilgrimage.', 'warning')
        else:
            review = Review(
                user_id=current_user.id,
                pilgrimage_id=pilgrimage_id,
                rating=int(form.rating.data),
                comment=form.comment.data
            )
            db.session.add(review)
            db.session.commit()
            flash('Your review has been submitted!', 'success')
    
    return redirect(url_for('main.pilgrimage', id=pilgrimage_id))

@main.route('/api/search')
def search_pilgrimages():
    query = request.args.get('q', '')
    
    if not query or len(query) < 3:
        return jsonify([])
    
    # Search for pilgrimages matching the query
    pilgrimages = Pilgrimage.query.filter(
        Pilgrimage.name.ilike(f'%{query}%') | 
        Pilgrimage.location.ilike(f'%{query}%') |
        Pilgrimage.description.ilike(f'%{query}%')
    ).all()
    
    # Format results
    results = [{
        'id': p.id,
        'name': p.name,
        'location': p.location,
        'image_url': p.image_url,
        'price': p.price,
        'average_rating': p.average_rating
    } for p in pilgrimages]
    
    return jsonify(results)

