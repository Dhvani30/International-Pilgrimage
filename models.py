from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from datetime import datetime
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(100))
    country = db.Column(db.String(50))
    profile_picture = db.Column(db.String(200))
    bio = db.Column(db.Text)
    preferences = db.Column(db.String(50), default='all')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy='dynamic')
    trip_plans = db.relationship('TripPlan', backref='user', lazy='dynamic')
    reviews = db.relationship('Review', backref='author', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    refund_requests = db.relationship('RefundRequest', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_unread_notifications_count(self):
        return Notification.query.filter_by(user_id=self.id, read=False).count()

class Pilgrimage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(50))
    best_time = db.Column(db.String(100))
    image_url = db.Column(db.String(200))
    gallery = db.Column(db.Text)  # JSON string of image URLs
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    price = db.Column(db.Float, default=0.0)
    difficulty_level = db.Column(db.String(20), default='moderate')
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='pilgrimage', lazy='dynamic')
    trip_plans = db.relationship('TripPlan', backref='pilgrimage', lazy='dynamic')
    reviews = db.relationship('Review', backref='pilgrimage', lazy='dynamic')
    attractions = db.relationship('Attraction', backref='pilgrimage', lazy='dynamic')
    deals = db.relationship('Deal', backref='pilgrimage', lazy='dynamic')
    
    @property
    def average_rating(self):
        reviews = Review.query.filter_by(pilgrimage_id=self.id).all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)
    
    @property
    def gallery_images(self):
        if not self.gallery:
            return []
        try:
            return json.loads(self.gallery)
        except:
            return []

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pilgrimage_id = db.Column(db.Integer, db.ForeignKey('pilgrimage.id'), nullable=False)
    travel_date = db.Column(db.Date, nullable=False)
    special_requirements = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TripPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pilgrimage_id = db.Column(db.Integer, db.ForeignKey('pilgrimage.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    num_travelers = db.Column(db.Integer, nullable=False)
    accommodation_type = db.Column(db.String(20), nullable=False)
    transportation = db.Column(db.String(20), nullable=False)
    meal_preference = db.Column(db.String(20), default='no_preference')
    guide_required = db.Column(db.Boolean, default=False)
    additional_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmation_code = db.Column(db.String(20), unique=True)
    total_price = db.Column(db.Float)
    payment_status = db.Column(db.String(20), default='pending')
    payment_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='planned')  # planned, ongoing, completed, cancelled
    itinerary = db.Column(db.Text)  # JSON string of daily activities
    
    # Payment fields
    payment_method = db.Column(db.String(50))
    payment_date = db.Column(db.DateTime)
    refund_reason = db.Column(db.String(100))
    refund_details = db.Column(db.Text)
    refund_requested_at = db.Column(db.DateTime)
    
    # Price breakdown fields
    base_price = db.Column(db.Float)
    accommodation_fee = db.Column(db.Float)
    transportation_fee = db.Column(db.Float)
    guide_fee = db.Column(db.Float)
    tax_amount = db.Column(db.Float)
    discount_amount = db.Column(db.Float)
    
    # Relationships
    daily_plans = db.relationship('DailyPlan', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    refund_requests = db.relationship('RefundRequest', backref='trip', lazy='dynamic')
    
    @property
    def itinerary_days(self):
        if not self.itinerary:
            return []
        try:
            return json.loads(self.itinerary)
        except:
            return []

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pilgrimage_id = db.Column(db.Integer, db.ForeignKey('pilgrimage.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text)  # JSON string of image URLs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    helpful_votes = db.Column(db.Integer, default=0)
    
    @property
    def review_images(self):
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except:
            return []

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200))
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Attraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pilgrimage_id = db.Column(db.Integer, db.ForeignKey('pilgrimage.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # religious, historical, cultural, natural, etc.
    image_url = db.Column(db.String(200))
    address = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    opening_hours = db.Column(db.String(200))
    entrance_fee = db.Column(db.Float, default=0.0)
    visit_duration = db.Column(db.Integer, default=60)  # in minutes
    popularity = db.Column(db.Integer, default=1)  # 1-10 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    daily_plans = db.relationship('DailyPlanAttraction', backref='attraction', lazy='dynamic')

class DailyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip_plan.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    accommodation = db.Column(db.String(200))
    transportation = db.Column(db.String(100))
    meal_plan = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attractions = db.relationship('DailyPlanAttraction', backref='daily_plan', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def total_duration(self):
        """Calculate total duration of all attractions in minutes"""
        return sum(pa.attraction.visit_duration for pa in self.attractions)
    
    @property
    def start_time(self):
        """Get the start time of the first attraction"""
        first_attraction = self.attractions.order_by(DailyPlanAttraction.start_time).first()
        return first_attraction.start_time if first_attraction else "09:00"
    
    @property
    def end_time(self):
        """Get the end time of the last attraction"""
        last_attraction = self.attractions.order_by(DailyPlanAttraction.start_time.desc()).first()
        if last_attraction:
            return last_attraction.start_time
        return "17:00"

class DailyPlanAttraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    daily_plan_id = db.Column(db.Integer, db.ForeignKey('daily_plan.id'), nullable=False)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attraction.id'), nullable=False)
    start_time = db.Column(db.String(5), default="09:00")  # Format: "HH:MM"
    notes = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)  # Order in the day's schedule
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False)
    valid_from = db.Column(db.Date, nullable=False)
    valid_to = db.Column(db.Date, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    image_url = db.Column(db.String(200))
    pilgrimage_id = db.Column(db.Integer, db.ForeignKey('pilgrimage.id'))  # Optional - can be for specific pilgrimage
    min_travelers = db.Column(db.Integer, default=1)
    min_days = db.Column(db.Integer, default=1)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RefundRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip_plan.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, processed
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_date = db.Column(db.DateTime)
    reason = db.Column(db.Text)
    admin_notes = db.Column(db.Text)


print("All models have been properly defined!")