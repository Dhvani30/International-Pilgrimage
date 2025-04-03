from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from models import TripPlan, DailyPlan, DailyPlanAttraction, Attraction, Pilgrimage, Deal, Notification
from extensions import db
from datetime import datetime, timedelta
import json
import random

trip_planner_bp = Blueprint('trip_planner', __name__)

@trip_planner_bp.route('/trip/<int:trip_id>/planner')
@login_required
def planner(trip_id):
    """Main trip planner page"""
    trip = TripPlan.query.get_or_404(trip_id)
    
    # Ensure the trip belongs to the current user
    if trip.user_id != current_user.id:
        flash('You do not have permission to access this trip.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get or create daily plans
    daily_plans = DailyPlan.query.filter_by(trip_id=trip.id).order_by(DailyPlan.day_number).all()
    
    # If no daily plans exist, create them
    if not daily_plans:
        daily_plans = create_initial_daily_plans(trip)
    
    # Get available attractions for this pilgrimage
    attractions = Attraction.query.filter_by(pilgrimage_id=trip.pilgrimage_id).all()
    
    # Get available deals
    deals = get_applicable_deals(trip)
    
    # Pass DailyPlanAttraction to the template context
    return render_template('trip_planner/planner.html', 
                          trip=trip, 
                          daily_plans=daily_plans,
                          attractions=attractions,
                          deals=deals,
                          DailyPlanAttraction=DailyPlanAttraction)  # Add this line

@trip_planner_bp.route('/trip/<int:trip_id>/generate-itinerary', methods=['POST'])
@login_required
def generate_itinerary(trip_id):
    """Generate a complete itinerary for the trip"""
    trip = TripPlan.query.get_or_404(trip_id)
    
    # Ensure the trip belongs to the current user
    if trip.user_id != current_user.id:
        flash('You do not have permission to access this trip.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Delete existing daily plans if any
    DailyPlan.query.filter_by(trip_id=trip.id).delete()
    db.session.commit()
    
    # Create new daily plans
    daily_plans = create_initial_daily_plans(trip)
    
    # Get attractions for this pilgrimage
    attractions = Attraction.query.filter_by(pilgrimage_id=trip.pilgrimage_id).all()
    
    # If no attractions, add some dummy ones for testing
    if not attractions:
        create_dummy_attractions(trip.pilgrimage_id)
        attractions = Attraction.query.filter_by(pilgrimage_id=trip.pilgrimage_id).all()
    
    # Distribute attractions across days
    distribute_attractions(daily_plans, attractions)
    
    flash('Itinerary has been generated successfully!', 'success')
    return redirect(url_for('trip_planner.planner', trip_id=trip.id))

@trip_planner_bp.route('/trip/<int:trip_id>/daily-plan/<int:day_id>', methods=['GET', 'POST'])
@login_required
def edit_daily_plan(trip_id, day_id):
    """Edit a specific day's plan"""
    trip = TripPlan.query.get_or_404(trip_id)
    daily_plan = DailyPlan.query.get_or_404(day_id)
    
    # Ensure the trip belongs to the current user and the daily plan belongs to the trip
    if trip.user_id != current_user.id or daily_plan.trip_id != trip.id:
        flash('You do not have permission to access this plan.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Update daily plan details
        daily_plan.title = request.form.get('title')
        daily_plan.description = request.form.get('description')
        daily_plan.accommodation = request.form.get('accommodation')
        daily_plan.transportation = request.form.get('transportation')
        daily_plan.meal_plan = request.form.get('meal_plan')
        
        # Handle attractions
        # First, remove all existing attractions
        DailyPlanAttraction.query.filter_by(daily_plan_id=daily_plan.id).delete()
        
        # Add new attractions from form
        attraction_ids = request.form.getlist('attractions[]')
        start_times = request.form.getlist('start_times[]')
        notes = request.form.getlist('notes[]')
        
        for i, attraction_id in enumerate(attraction_ids):
            if attraction_id:
                attraction = Attraction.query.get(attraction_id)
                if attraction:
                    plan_attraction = DailyPlanAttraction(
                        daily_plan_id=daily_plan.id,
                        attraction_id=attraction_id,
                        start_time=start_times[i] if i < len(start_times) else "09:00",
                        notes=notes[i] if i < len(notes) else "",
                        order=i
                    )
                    db.session.add(plan_attraction)
        
        db.session.commit()
        flash('Day plan updated successfully!', 'success')
        return redirect(url_for('trip_planner.planner', trip_id=trip.id))
    
    # Get available attractions for this pilgrimage
    attractions = Attraction.query.filter_by(pilgrimage_id=trip.pilgrimage_id).all()
    
    return render_template('trip_planner/edit_day.html', 
                          trip=trip, 
                          daily_plan=daily_plan,
                          attractions=attractions)

@trip_planner_bp.route('/trip/<int:trip_id>/apply-deal', methods=['POST'])
@login_required
def apply_deal(trip_id):
    """Apply a deal to the trip"""
    trip = TripPlan.query.get_or_404(trip_id)
    
    # Ensure the trip belongs to the current user
    if trip.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    deal_code = request.form.get('deal_code')
    if not deal_code:
        return jsonify({'success': False, 'error': 'No deal code provided'}), 400
    
    # Find the deal
    deal = Deal.query.filter_by(code=deal_code, active=True).first()
    if not deal:
        return jsonify({'success': False, 'error': 'Invalid or expired deal code'}), 400
    
    # Check if deal is applicable to this trip
    if deal.pilgrimage_id and deal.pilgrimage_id != trip.pilgrimage_id:
        return jsonify({'success': False, 'error': 'This deal is not applicable to your selected pilgrimage'}), 400
    
    if deal.min_travelers > trip.num_travelers:
        return jsonify({'success': False, 'error': f'This deal requires at least {deal.min_travelers} travelers'}), 400
    
    trip_duration = (trip.end_date - trip.start_date).days
    if deal.min_days > trip_duration:
        return jsonify({'success': False, 'error': f'This deal requires at least {deal.min_days} days'}), 400
    
    today = datetime.now().date()
    if today < deal.valid_from or today > deal.valid_to:
        return jsonify({'success': False, 'error': 'This deal is not currently valid'}), 400
    
    # Apply the discount
    original_price = trip.total_price
    discount_amount = original_price * (deal.discount_percentage / 100)
    trip.discount_amount = discount_amount
    trip.total_price = original_price - discount_amount
    
    # Save the applied deal info
    trip_deals = json.loads(trip.itinerary or '{}')
    trip_deals['applied_deal'] = {
        'code': deal.code,
        'title': deal.title,
        'discount_percentage': deal.discount_percentage,
        'discount_amount': discount_amount
    }
    trip.itinerary = json.dumps(trip_deals)
    
    db.session.commit()
    
    # Create notification
    notification = Notification(
        user_id=current_user.id,
        title='Deal Applied',
        message=f'The deal "{deal.title}" has been applied to your trip to {trip.pilgrimage.name}, saving you ₹{discount_amount:.2f}!',
        link=url_for('trip_planner.planner', trip_id=trip.id)
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'Deal applied successfully! You saved ₹{discount_amount:.2f}',
        'new_price': trip.total_price,
        'discount_amount': discount_amount
    })

@trip_planner_bp.route('/trip/<int:trip_id>/save-itinerary', methods=['POST'])
@login_required
def save_itinerary(trip_id):
    """Save the complete itinerary"""
    trip = TripPlan.query.get_or_404(trip_id)
    
    # Ensure the trip belongs to the current user
    if trip.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Get all daily plans
    daily_plans = DailyPlan.query.filter_by(trip_id=trip.id).order_by(DailyPlan.day_number).all()
    
    # Format the itinerary
    itinerary = []
    for plan in daily_plans:
        day_attractions = []
        for pa in plan.attractions.order_by(DailyPlanAttraction.order).all():
            attraction = Attraction.query.get(pa.attraction_id)
            day_attractions.append({
                'id': attraction.id,
                'name': attraction.name,
                'start_time': pa.start_time,
                'duration': attraction.visit_duration,
                'notes': pa.notes
            })
        
        itinerary.append({
            'day_number': plan.day_number,
            'date': plan.date.strftime('%Y-%m-%d'),
            'title': plan.title,
            'description': plan.description,
            'accommodation': plan.accommodation,
            'transportation': plan.transportation,
            'meal_plan': plan.meal_plan,
            'attractions': day_attractions
        })
    
    # Save to trip
    trip.itinerary = json.dumps(itinerary)
    db.session.commit()
    
    # Create notification
    notification = Notification(
        user_id=current_user.id,
        title='Itinerary Saved',
        message=f'Your itinerary for {trip.pilgrimage.name} has been saved successfully.',
        link=url_for('trip_planner.planner', trip_id=trip.id)
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Itinerary saved successfully!'})

@trip_planner_bp.route('/trip/<int:trip_id>/print-itinerary')
@login_required
def print_itinerary(trip_id):
    """Print-friendly view of the itinerary"""
    trip = TripPlan.query.get_or_404(trip_id)
    
    # Ensure the trip belongs to the current user
    if trip.user_id != current_user.id:
        flash('You do not have permission to access this trip.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get daily plans
    daily_plans = DailyPlan.query.filter_by(trip_id=trip.id).order_by(DailyPlan.day_number).all()
    
    return render_template('trip_planner/print_itinerary.html', 
                          trip=trip, 
                          daily_plans=daily_plans)

@trip_planner_bp.route('/deals')
def deals():
    """View all available deals"""
    today = datetime.now().date()
    active_deals = Deal.query.filter(
        Deal.active == True,
        Deal.valid_from <= today,
        Deal.valid_to >= today
    ).all()
    
    return render_template('trip_planner/deals.html', deals=active_deals)

# Helper functions
def create_initial_daily_plans(trip):
    """Create initial daily plans for each day of the trip"""
    daily_plans = []
    trip_duration = (trip.end_date - trip.start_date).days + 1
    
    for day in range(1, trip_duration + 1):
        date = trip.start_date + timedelta(days=day-1)
        
        # Create a title based on the day number
        if day == 1:
            title = "Arrival & Orientation"
        elif day == trip_duration:
            title = "Farewell & Departure"
        else:
            title = f"Day {day} Exploration"
        
        daily_plan = DailyPlan(
            trip_id=trip.id,
            day_number=day,
            date=date,
            title=title,
            description=f"Explore the wonders of {trip.pilgrimage.name} on day {day} of your journey.",
            accommodation=trip.accommodation_type.capitalize(),
            transportation=trip.transportation.replace('_', ' ').capitalize(),
            meal_plan="Breakfast, Lunch, Dinner"
        )
        
        db.session.add(daily_plan)
        daily_plans.append(daily_plan)
    
    db.session.commit()
    return daily_plans

def distribute_attractions(daily_plans, attractions):
    """Distribute attractions across days in a logical manner"""
    if not attractions:
        return
    
    # Sort attractions by popularity
    sorted_attractions = sorted(attractions, key=lambda x: x.popularity, reverse=True)
    
    # Calculate attractions per day, ensuring top attractions are distributed first
    attractions_per_day = max(1, min(4, len(sorted_attractions) // len(daily_plans)))
    
    # Distribute attractions
    attraction_index = 0
    for plan in daily_plans:
        # Skip some attractions on first and last day
        max_attractions = attractions_per_day
        if plan.day_number == 1 or plan.day_number == len(daily_plans):
            max_attractions = max(1, attractions_per_day - 1)
        
        # Add attractions to this day
        for i in range(min(max_attractions, len(sorted_attractions) - attraction_index)):
            if attraction_index >= len(sorted_attractions):
                break
                
            attraction = sorted_attractions[attraction_index]
            
            # Calculate a reasonable start time between 9 AM and 4 PM
            hour = 9 + (i * 2) % 7  # Spread between 9 AM and 4 PM
            minute = (i * 15) % 60  # Vary the minutes
            start_time = f"{hour:02d}:{minute:02d}"
            
            plan_attraction = DailyPlanAttraction(
                daily_plan_id=plan.id,
                attraction_id=attraction.id,
                start_time=start_time,
                order=i
            )
            
            db.session.add(plan_attraction)
            attraction_index += 1
    
    db.session.commit()

def create_dummy_attractions(pilgrimage_id):
    """Create dummy attractions for testing"""
    pilgrimage = Pilgrimage.query.get(pilgrimage_id)
    if not pilgrimage:
        return
    
    # Create some dummy attractions based on the pilgrimage location
    attractions = [
        {
            'name': f"Main {pilgrimage.name} Site",
            'description': f"The primary sacred site of {pilgrimage.name}.",
            'category': 'religious',
            'visit_duration': 120,
            'popularity': 10
        },
        {
            'name': f"Historical Museum of {pilgrimage.location}",
            'description': f"Learn about the rich history of {pilgrimage.location} and its significance.",
            'category': 'historical',
            'visit_duration': 90,
            'popularity': 8
        },
        {
            'name': f"Local Market in {pilgrimage.location}",
            'description': f"Experience the local culture and buy souvenirs at this vibrant market.",
            'category': 'cultural',
            'visit_duration': 60,
            'popularity': 7
        },
        {
            'name': f"Scenic Viewpoint",
            'description': f"Enjoy breathtaking views of the surrounding landscape.",
            'category': 'natural',
            'visit_duration': 45,
            'popularity': 6
        },
        {
            'name': f"Traditional Restaurant",
            'description': f"Taste authentic local cuisine in a traditional setting.",
            'category': 'cultural',
            'visit_duration': 90,
            'popularity': 7
        },
        {
            'name': f"Meditation Garden",
            'description': f"A peaceful garden perfect for  7"
        },
        {
            'name': f"Meditation Garden",
            'description': f"A peaceful garden perfect for meditation and spiritual reflection.",
            'category': 'spiritual',
            'visit_duration': 60,
            'popularity': 5
        },
        {
            'name': f"Ancient Temple Ruins",
            'description': f"Explore the ancient ruins that date back centuries.",
            'category': 'historical',
            'visit_duration': 75,
            'popularity': 9
        }
    ]
    
    for attraction_data in attractions:
        attraction = Attraction(
            pilgrimage_id=pilgrimage_id,
            image_url=pilgrimage.image_url,  # Use the pilgrimage image as a placeholder
            latitude=pilgrimage.latitude + (random.random() - 0.5) * 0.01 if pilgrimage.latitude else None,
            longitude=pilgrimage.longitude + (random.random() - 0.5) * 0.01 if pilgrimage.longitude else None,
            **attraction_data
        )
        db.session.add(attraction)
    
    db.session.commit()

def get_applicable_deals(trip):
    """Get deals applicable to this trip"""
    today = datetime.now().date()
    trip_duration = (trip.end_date - trip.start_date).days
    
    # Find active deals that match the criteria
    deals = Deal.query.filter(
        Deal.active == True,
        Deal.valid_from <= today,
        Deal.valid_to >= today,
        Deal.min_travelers <= trip.num_travelers,
        Deal.min_days <= trip_duration
    ).all()
    
    # Filter for pilgrimage-specific deals or general deals
    applicable_deals = [
        deal for deal in deals 
        if deal.pilgrimage_id is None or deal.pilgrimage_id == trip.pilgrimage_id
    ]
    
    return applicable_deals

