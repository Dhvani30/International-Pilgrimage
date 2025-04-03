from flask import Flask
import os
from config import Config
from extensions import db, migrate, login_manager, mail, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload folder exists
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Configure CSRF to exempt certain routes if needed
    csrf.exempt("payment.process_payment")

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    with app.app_context():
        # Import models after db is initialized to avoid circular imports
        from models import User, DailyPlanAttraction  # Ensure DailyPlanAttraction is imported

        # Create database tables
        db.create_all()

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Context processor to inject models into templates
        @app.context_processor
        def inject_models():
            return dict(DailyPlanAttraction=DailyPlanAttraction)

        # Register blueprints
        from routes import main
        from auth import auth
        from payment import payment_bp
        from trip_management import trip_bp
        from trip_planner import trip_planner_bp

        app.register_blueprint(main)
        app.register_blueprint(auth)
        app.register_blueprint(payment_bp)
        app.register_blueprint(trip_bp)
        app.register_blueprint(trip_planner_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
