from app import create_app
from extensions import db
from models import Pilgrimage, Attraction
import random

def seed_attractions():
    """Seed attractions for all pilgrimages"""
    app = create_app()
    
    with app.app_context():
        # Get all pilgrimages
        pilgrimages = Pilgrimage.query.all()
        
        for pilgrimage in pilgrimages:
            print(f"Adding attractions for {pilgrimage.name}...")
            
            # Check if attractions already exist
            existing_attractions = Attraction.query.filter_by(pilgrimage_id=pilgrimage.id).count()
            if existing_attractions > 0:
                print(f"  Attractions already exist for {pilgrimage.name}, skipping.")
                continue
            
            # Create attractions based on pilgrimage type/location
            create_attractions_for_pilgrimage(pilgrimage)
            
        db.session.commit()
        print("Attractions seeding completed!")

def create_attractions_for_pilgrimage(pilgrimage):
    """Create appropriate attractions for a specific pilgrimage"""
    # Base attractions that most pilgrimages would have
    base_attractions = [
        {
            'name': f"Main {pilgrimage.name} Site",
            'description': f"The primary sacred site of {pilgrimage.name}.",
            'category': 'religious',
            'visit_duration': 120,
            'popularity': 10,
            'entrance_fee': random.choice([0, 50, 100, 200]),
            'opening_hours': "08:00 - 18:00"
        },
        {
            'name': f"Historical Museum of {pilgrimage.location}",
            'description': f"Learn about the rich history of {pilgrimage.location} and its significance.",
            'category': 'historical',
            'visit_duration': 90,
            'popularity': 8,
            'entrance_fee': random.choice([50, 100, 150]),
            'opening_hours': "09:00 - 17:00"
        },
        {
            'name': f"Local Market in {pilgrimage.location}",
            'description': f"Experience the local culture and buy souvenirs at this vibrant market.",
            'category': 'cultural',
            'visit_duration': 60,
            'popularity': 7,
            'entrance_fee': 0,
            'opening_hours': "10:00 - 20:00"
        },
        {
            'name': f"Meditation Garden",
            'description': f"A peaceful garden perfect for meditation and spiritual reflection.",
            'category': 'spiritual',
            'visit_duration': 60,
            'popularity': 5,
            'entrance_fee': random.choice([0, 50]),
            'opening_hours': "Sunrise to Sunset"
        }
    ]
    
    # Location-specific attractions
    location_specific = []
    
    # Add location-specific attractions based on pilgrimage name or location
    if "Vatican" in pilgrimage.name:
        location_specific = [
            {
                'name': "St. Peter's Basilica",
                'description': "One of the largest churches in the world and a masterpiece of Renaissance architecture.",
                'category': 'religious',
                'visit_duration': 120,
                'popularity': 10,
                'entrance_fee': 0,
                'opening_hours': "07:00 - 18:30"
            },
            {
                'name': "Vatican Museums",
                'description': "Home to one of the world's greatest art collections, including the Sistine Chapel.",
                'category': 'cultural',
                'visit_duration': 180,
                'popularity': 9,
                'entrance_fee': 170,
                'opening_hours': "09:00 - 16:00"
            },
            {
                'name': "Sistine Chapel",
                'description': "Famous for its ceiling painted by Michelangelo, one of the most renowned artworks in the world.",
                'category': 'religious',
                'visit_duration': 60,
                'popularity': 10,
                'entrance_fee': 0,  # Included in Vatican Museums
                'opening_hours': "09:00 - 16:00"
            }
        ]
    elif "Jerusalem" in pilgrimage.name or "Jerusalem" in pilgrimage.location:
        location_specific = [
            {
                'name': "Western Wall",
                'description': "The holiest place where Jews are permitted to pray, also known as the Wailing Wall.",
                'category': 'religious',
                'visit_duration': 60,
                'popularity': 10,
                'entrance_fee': 0,
                'opening_hours': "24 hours"
            },
            {
                'name': "Church of the Holy Sepulchre",
                'description': "The site where Jesus was crucified and resurrected according to Christian tradition.",
                'category': 'religious',
                'visit_duration': 90,
                'popularity': 10,
                'entrance_fee': 0,
                'opening_hours': "05:00 - 21:00"
            },
            {
                'name': "Dome of the Rock",
                'description': "An Islamic shrine located on the Temple Mount in the Old City of Jerusalem.",
                'category': 'religious',
                'visit_duration': 60,
                'popularity': 9,
                'entrance_fee': 0,
                'opening_hours': "Limited hours for non-Muslims"
            }
        ]
    elif "Mecca" in pilgrimage.name or "Mecca" in pilgrimage.location:
        location_specific = [
            {
                'name': "Masjid al-Haram",
                'description': "The largest mosque in the world and surrounds the Kaaba, the holiest site in Islam.",
                'category': 'religious',
                'visit_duration': 180,
                'popularity': 10,
                'entrance_fee': 0,
                'opening_hours': "24 hours"
            },
            {
                'name': "Mount Arafat",
                'description': "A granite hill east of Mecca, an important site during the Hajj pilgrimage.",
                'category': 'religious',
                'visit_duration': 120,
                'popularity': 9,
                'entrance_fee': 0,
                'opening_hours': "24 hours"
            }
        ]
    elif "Varanasi" in pilgrimage.name or "Varanasi" in pilgrimage.location:
        location_specific = [
            {
                'name': "Dashashwamedh Ghat",
                'description': "The main and probably the oldest ghat of Varanasi located on the Ganges River.",
                'category': 'religious',
                'visit_duration': 90,
                'popularity': 10,
                'entrance_fee': 0,
                'opening_hours': "24 hours"
            },
            {
                'name': "Kashi Vishwanath Temple",
                'description': "One of the most famous Hindu temples dedicated to Lord Shiva.",
                'category': 'religious',
                'visit_duration': 60,
                'popularity': 10,
                'entrance_fee': 0,
                'opening_hours': "03:00 - 23:00"
            },
            {
                'name': "Evening Ganga Aarti",
                'description': "A spiritual ritual performed every evening on the banks of the river Ganges.",
                'category': 'cultural',
                'visit_duration': 60,
                'popularity': 10,
                'entrance_fee': 0,
                'opening_hours': "18:00 - 19:30"
            }
        ]
    
    # Combine base and location-specific attractions
    all_attractions = base_attractions + location_specific
    
    # Add some generic attractions if we don't have enough
    if len(all_attractions) < 6:
        generic_attractions = [
            {
                'name': f"Scenic Viewpoint of {pilgrimage.location}",
                'description': f"Enjoy breathtaking views of {pilgrimage.location} and its surroundings.",
                'category': 'natural',
                'visit_duration': 45,
                'popularity': 6,
                'entrance_fee': random.choice([0, 50]),
                'opening_hours': "Sunrise to Sunset"
            },
            {
                'name': f"Traditional Restaurant",
                'description': f"Taste authentic local cuisine in a traditional setting.",
                'category': 'cultural',
                'visit_duration': 90,
                'popularity': 7,
                'entrance_fee': 0,
                'opening_hours': "12:00 - 22:00"
            },
            {
                'name': f"Ancient Temple Ruins",
                'description': f"Explore the ancient ruins that date back centuries.",
                'category': 'historical',
                'visit_duration': 75,
                'popularity': 8,
                'entrance_fee': random.choice([0, 75, 100]),
                'opening_hours': "09:00 - 17:00"
            },
            {
                'name': f"Sacred River Walk",
                'description': f"Take a peaceful walk along the sacred river that flows through {pilgrimage.location}.",
                'category': 'natural',
                'visit_duration': 60,
                'popularity': 6,
                'entrance_fee': 0,
                'opening_hours': "Sunrise to Sunset"
            },
            {
                'name': f"Artisan Workshop",
                'description': f"Visit local artisans and learn about traditional crafts of {pilgrimage.location}.",
                'category': 'cultural',
                'visit_duration': 60,
                'popularity': 5,
                'entrance_fee': random.choice([0, 50]),
                'opening_hours': "10:00 - 16:00"
            }
        ]
        
        # Add enough generic attractions to have at least 6 total
        needed = max(0, 6 - len(all_attractions))
        all_attractions.extend(generic_attractions[:needed])
    
    # Create and add attractions to database
    for attraction_data in all_attractions:
        attraction = Attraction(
            pilgrimage_id=pilgrimage.id,
            image_url=pilgrimage.image_url,  # Use the pilgrimage image as a placeholder
            latitude=pilgrimage.latitude + (random.random() - 0.5) * 0.01 if pilgrimage.latitude else None,
            longitude=pilgrimage.longitude + (random.random() - 0.5) * 0.01 if pilgrimage.longitude else None,
            **attraction_data
        )
        db.session.add(attraction)
    
    print(f"  Added {len(all_attractions)} attractions for {pilgrimage.name}")

if __name__ == "__main__":
    seed_attractions()

