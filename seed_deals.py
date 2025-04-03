from app import create_app
from extensions import db
from models import Deal, Pilgrimage
from datetime import datetime, timedelta
import random
import string

def generate_code(length=8):
    """Generate a random code for deals"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def seed_deals():
    """Seed deals for pilgrimages"""
    app = create_app()
    
    with app.app_context():
        # Clear existing deals
        db.session.query(Deal).delete()
        
        # Get all pilgrimages
        pilgrimages = Pilgrimage.query.all()
        
        # Create general deals
        general_deals = [
            {
                'title': "Early Bird Special",
                'description': "Book your pilgrimage at least 60 days in advance and save on your spiritual journey.",
                'discount_percentage': 15,
                'valid_from': datetime.now(),
                'valid_to': datetime.now() + timedelta(days=90),
                'code': "EARLYBIRD",
                'min_travelers': 1,
                'min_days': 3,
                'active': True
            },
            {
                'title': "Group Pilgrimage Discount",
                'description': "Travel with 5 or more people and enjoy special group rates on all pilgrimages.",
                'discount_percentage': 20,
                'valid_from': datetime.now(),
                'valid_to': datetime.now() + timedelta(days=180),
                'code': "GROUP20",
                'min_travelers': 5,
                'min_days': 1,
                'active': True
            },
            {
                'title': "Extended Stay Offer",
                'description': "Stay longer and save more. Valid for trips of 7 days or more.",
                'discount_percentage': 12,
                'valid_from': datetime.now(),
                'valid_to': datetime.now() + timedelta(days=120),
                'code': "LONGSTAY",
                'min_travelers': 1,
                'min_days': 7,
                'active': True
            }
        ]
        
        for deal_data in general_deals:
            deal = Deal(**deal_data)
            db.session.add(deal)
        
        # Create pilgrimage-specific deals for some pilgrimages
        for pilgrimage in random.sample(pilgrimages, min(3, len(pilgrimages))):
            deal = Deal(
                title=f"Special {pilgrimage.name} Offer",
                description=f"Exclusive discount for pilgrimages to {pilgrimage.name}. Experience this sacred journey for less.",
                discount_percentage=random.choice([10, 15, 18, 25]),
                valid_from=datetime.now(),
                valid_to=datetime.now() + timedelta(days=random.randint(30, 120)),
                code=generate_code(),
                pilgrimage_id=pilgrimage.id,
                min_travelers=random.choice([1, 2]),
                min_days=random.choice([1, 2, 3]),
                active=True
            )
            db.session.add(deal)
        
        # Create a seasonal deal
        seasons = ["Summer", "Winter", "Spring", "Monsoon"]
        season = random.choice(seasons)
        deal = Deal(
            title=f"{season} Pilgrimage Special",
            description=f"Take advantage of our {season.lower()} special offer and embark on a transformative journey.",
            discount_percentage=random.choice([10, 12, 15]),
            valid_from=datetime.now(),
            valid_to=datetime.now() + timedelta(days=90),
            code=f"{season.upper()}SPECIAL",
            min_travelers=1,
            min_days=2,
            active=True
        )
        db.session.add(deal)
        
        db.session.commit()
        print("Deals seeding completed!")

if __name__ == "__main__":
    seed_deals()

