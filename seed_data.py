from app import create_app
from extensions import db
from models import Pilgrimage
import os
import shutil
import requests
from urllib.parse import urlparse
from flask import current_app
import random

# def download_image(url, destination):
#     """Download an image from URL to the static folder"""
#     try:
#         # Create directory if it doesn't exist
#         os.makedirs(os.path.dirname(destination), exist_ok=True)
        
#         # Download the image
#         response = requests.get(url, stream=True)
#         if response.status_code == 200:
#             with open(destination, 'wb') as f:
#                 response.raw.decode_content = True
#                 shutil.copyfileobj(response.raw, f)
#             return True
#         return False
#     except Exception as e:
#         print(f"Error downloading image from {url}: {e}")
#         return False

# def create_hero_background():
#     """Create a hero background image for the homepage"""
#     hero_url = "https://images.unsplash.com/photo-1519677584237-752f8853252e"
#     hero_path = os.path.join(current_app.root_path, 'static', 'images', 'hero-background.jpg')
#     download_image(hero_url, hero_path)
#     print("Hero background image created.")

def seed_pilgrimages():
    # Clear existing pilgrimages
    db.session.query(Pilgrimage).delete()
    
    # Create static/images directory if it doesn't exist
    static_dir = os.path.join(current_app.root_path, 'static', 'images')
    os.makedirs(static_dir, exist_ok=True)
    
    # Create hero background
    #create_hero_background()
    
    pilgrimages = [
       
    {
        'name': 'Santiago de Compostela',
        'location': 'Galicia, Spain',
        'description': 'The endpoint of the Camino de Santiago, a famous Christian pilgrimage route to the shrine of St. James. This ancient pilgrimage has been traveled by millions of people over centuries, offering a profound spiritual journey through beautiful landscapes and historic towns.',
        'duration': '1-4 weeks (depending on the route)',
        'best_time': 'Spring or Fall',
        'image_url': 'https://media.istockphoto.com/id/1153284137/photo/cathedral-of-santiago-de-compostela.jpg?s=612x612&w=0&k=20&c=_2pHcdmkOUPNpR_FZC4eGbGpOa9fMYEFJvQdvZKmyYE=',
        'latitude': 42.8805,
        'longitude': -8.5455,
        'price': 1200.00
    },
    {
        'name': 'Vatican City',
        'location': 'Rome, Italy',
        'description': 'The heart of the Catholic Church and home to St. Peter\'s Basilica. Vatican City is the smallest independent state in the world and houses some of the most significant religious and cultural treasures, including the Sistine Chapel with Michelangelo\'s famous ceiling.',
        'duration': '3-5 days',
        'best_time': 'Spring or Fall',
        'image_url': 'https://images.unsplash.com/photo-1531572753322-ad063cecc140',
        'latitude': 41.9029,
        'longitude': 12.4534,
        'price': 850.00
    },
    {
        'name': 'Mecca',
        'location': 'Mecca, Saudi Arabia',
        'description': 'The holiest city in Islam and the birthplace of Prophet Muhammad. Every year, millions of Muslims perform the Hajj pilgrimage to Mecca, one of the Five Pillars of Islam. The city is home to the Masjid al-Haram, which houses the Kaaba, the most sacred site in Islam.',
        'duration': '5-7 days',
        'best_time': 'Non-Hajj season',
        'image_url': 'https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa',
        'latitude': 21.4225,
        'longitude': 39.8262,
        'price': 1500.00
    },
    {
        'name': 'Jerusalem',
        'location': 'Jerusalem, Israel',
        'description': 'A holy city for Judaism, Christianity, and Islam. Jerusalem\'s Old City is home to numerous sites of religious significance, including the Western Wall, the Church of the Holy Sepulchre, and the Dome of the Rock. Walking through its ancient streets is a profound spiritual experience.',
        'duration': '4-6 days',
        'best_time': 'Spring or Fall',
        'image_url': 'https://images.unsplash.com/photo-1544734037-e4ec2e0c3e6a',
        'latitude': 31.7683,
        'longitude': 35.2137,
        'price': 1100.00
    },
    {
        'name': 'Bodh Gaya',
        'location': 'Bihar, India',
        'description': 'The place where Gautama Buddha is said to have attained enlightenment. Bodh Gaya is one of the four main pilgrimage sites for Buddhists, centered around the Mahabodhi Temple Complex, which includes the famous Bodhi Tree under which Buddha meditated.',
        'duration': '2-3 days',
        'best_time': 'November to February',
        'image_url':  'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTjZuBEb0S9UeyqHCWcRSeBkm5e2-m1h-OCeg&s',
        'latitude': 24.6975,
        'longitude': 84.9922,
        'price': 700.00
    },
    {
        'name': 'Lourdes',
        'location': 'Lourdes, France',
        'description': 'Famous for the Marian apparitions of Our Lady of Lourdes. Since 1858, when Bernadette Soubirous reported visions of the Virgin Mary, Lourdes has become a major Catholic pilgrimage site. Many visitors come seeking healing from the waters of the Grotto.',
        'duration': '2-4 days',
        'best_time': 'April to October',
        'image_url': 'https://media.istockphoto.com/id/602326164/photo/rosary-basilica-in-the-evening-in-lourdes.jpg?s=612x612&w=0&k=20&c=EbiRi7PQtb8te__k-bZ1Q52qVv_QUAEvfWewomnhu1w=',
        'latitude': 43.0983,
        'longitude': -0.0508,
        'price': 900.00
    },
    {
        'name': 'Varanasi',
        'location': 'Uttar Pradesh, India',
        'description': 'One of the oldest continuously inhabited cities in the world and a holy city for Hindus. Situated on the banks of the sacred Ganges River, Varanasi is believed to be the abode of Lord Shiva. Pilgrims come to bathe in the Ganges and perform funeral rites.',
        'duration': '3-5 days',
        'best_time': 'October to March',
        'image_url': 'https://images.unsplash.com/photo-1561361058-c24cecae35ca',
        'latitude': 25.3176,
        'longitude': 83.0130,
        'price': 750.00
    },
    {
        'name': 'Mount Kailash',
        'location': 'Tibet, China',
        'description': 'A sacred peak in the Himalayas revered by Hindus, Buddhists, Jains, and Bon practitioners. Pilgrims perform a circumambulation (kora) around the mountain, believed to bring good fortune and wash away sins. The journey is challenging but spiritually rewarding.',
        'duration': '10-15 days',
        'best_time': 'May to September',
        'image_url': ''
    }
    ]
from extensions import db
from models import Pilgrimage
import os
import shutil
import requests
from urllib.parse import urlparse
from flask import current_app
import random

def download_image(url, destination):
    """Download an image from URL to the static folder"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Download the image
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(destination, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            return True
        return False
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return False

def create_hero_background():
    """Create a hero background image for the homepage"""
    hero_url = "https://images.unsplash.com/photo-1519677584237-752f8853252e"
    hero_path = os.path.join(current_app.root_path, 'static', 'images', 'hero-background.jpg')
    download_image(hero_url, hero_path)
    print("Hero background image created.")

def seed_pilgrimages():
    # Clear existing pilgrimages
    db.session.query(Pilgrimage).delete()
    
    # Create static/images directory if it doesn't exist
    static_dir = os.path.join(current_app.root_path, 'static', 'images')
    os.makedirs(static_dir, exist_ok=True)
    
    # Create hero background
    create_hero_background()
    
    pilgrimages = [
        {
            'name': 'Santiago de Compostela',
            'location': 'Galicia, Spain',
            'description': 'The endpoint of the Camino de Santiago, a famous Christian pilgrimage route to the shrine of St. James. This ancient pilgrimage has been traveled by millions of people over centuries, offering a profound spiritual journey through beautiful landscapes and historic towns.',
            'duration': '1-4 weeks (depending on the route)',
            'best_time': 'Spring or Fall',
            'image_url': 'https://media.istockphoto.com/id/1153284137/photo/cathedral-of-santiago-de-compostela.jpg?s=612x612&w=0&k=20&c=_2pHcdmkOUPNpR_FZC4eGbGpOa9fMYEFJvQdvZKmyYE=',
            'latitude': 42.8805,
            'longitude': -8.5455,
            'price': 1200.00
        },
        {
            'name': 'Vatican City',
            'location': 'Rome, Italy',
            'description': 'The heart of the Catholic Church and home to St. Peter\'s Basilica. Vatican City is the smallest independent state in the world and houses some of the most significant religious and cultural treasures, including the Sistine Chapel with Michelangelo\'s famous ceiling.',
            'duration': '3-5 days',
            'best_time': 'Spring or Fall',
            'image_url': 'https://images.unsplash.com/photo-1531572753322-ad063cecc140',
            'latitude': 41.9029,
            'longitude': 12.4534,
            'price': 850.00
        },
        {
            'name': 'Mecca',
            'location': 'Mecca, Saudi Arabia',
            'description': 'The holiest city in Islam and the birthplace of Prophet Muhammad. Every year, millions of Muslims perform the Hajj pilgrimage to Mecca, one of the Five Pillars of Islam. The city is home to the Masjid al-Haram, which houses the Kaaba, the most sacred site in Islam.',
            'duration': '5-7 days',
            'best_time': 'Non-Hajj season',
            'image_url': 'https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa',
            'latitude': 21.4225,
            'longitude': 39.8262,
            'price': 1500.00
        },
        {
            'name': 'Jerusalem',
            'location': 'Jerusalem, Israel',
            'description': 'A holy city for Judaism, Christianity, and Islam. Jerusalem\'s Old City is home to numerous sites of religious significance, including the Western Wall, the Church of the Holy Sepulchre, and the Dome of the Rock. Walking through its ancient streets is a profound spiritual experience.',
            'duration': '4-6 days',
            'best_time': 'Spring or Fall',
            'image_url': 'https://images.unsplash.com/photo-1544734037-e4ec2e0c3e6a',
            'latitude': 31.7683,
            'longitude': 35.2137,
            'price': 1100.00
        },
        {
            'name': 'Bodh Gaya',
            'location': 'Bihar, India',
            'description': 'The place where Gautama Buddha is said to have attained enlightenment. Bodh Gaya is one of the four main pilgrimage sites for Buddhists, centered around the Mahabodhi Temple Complex, which includes the famous Bodhi Tree under which Buddha meditated.',
            'duration': '2-3 days',
            'best_time': 'November to February',
            'image_url':  'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTjZuBEb0S9UeyqHCWcRSeBkm5e2-m1h-OCeg&s',
            'latitude': 24.6975,
            'longitude': 84.9922,
            'price': 700.00
        },
        {
            'name': 'Lourdes',
            'location': 'Lourdes, France',
            'description': 'Famous for the Marian apparitions of Our Lady of Lourdes. Since 1858, when Bernadette Soubirous reported visions of the Virgin Mary, Lourdes has become a major Catholic pilgrimage site. Many visitors come seeking healing from the waters of the Grotto.',
            'duration': '2-4 days',
            'best_time': 'April to October',
            'image_url': 'https://media.istockphoto.com/id/602326164/photo/rosary-basilica-in-the-evening-in-lourdes.jpg?s=612x612&w=0&k=20&c=EbiRi7PQtb8te__k-bZ1Q52qVv_QUAEvfWewomnhu1w=',
            'latitude': 43.0983,
            'longitude': -0.0508,
            'price': 900.00
        },
        {
            'name': 'Varanasi',
            'location': 'Uttar Pradesh, India',
            'description': 'One of the oldest continuously inhabited cities in the world and a holy city for Hindus. Situated on the banks of the sacred Ganges River, Varanasi is believed to be the abode of Lord Shiva. Pilgrims come to bathe in the Ganges and perform funeral rites.',
            'duration': '3-5 days',
            'best_time': 'October to March',
            'image_url': 'https://images.unsplash.com/photo-1561361058-c24cecae35ca',
            'latitude': 25.3176,
            'longitude': 83.0130,
            'price': 750.00
        },
        {
            'name': 'Mount Kailash',
            'location': 'Tibet, China',
            'description': 'A sacred peak in the Himalayas revered by Hindus, Buddhists, Jains, and Bon practitioners. Pilgrims perform a circumambulation (kora) around the mountain, believed to bring good fortune and wash away sins. The journey is challenging but spiritually rewarding.',
            'duration': '10-15 days',
            'best_time': 'May to September',
            'image_url': 'data:image/jpeg;base64,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',
        'latitude': 31.0672,
        'longitude': 81.3112,
        'price': 2200.00
    },
    {
        'name': 'Iona',
        'location': 'Scotland, UK',
        'description': 'A small island off the west coast of Scotland with a significant role in the spread of Christianity. St. Columba established a monastery here in 563 CE, making it a center of Celtic Christianity. Today, the restored abbey and peaceful surroundings attract spiritual seekers.',
        'duration': '2-3 days',
        'best_time': 'May to September',
        'image_url': 'https://images.unsplash.com/photo-1506783323968-e8dad28ae1de',
        'latitude': 56.3352,
        'longitude': -6.4175,
        'price': 850.00
    },
    {
        'name': 'Golden Temple',
        'location': 'Amritsar, India',
        'description': 'The holiest site in Sikhism, also known as Harmandir Sahib, famous for its gold-plated structure. This magnificent temple sits in the center of a sacred pool and attracts millions of pilgrims annually. It embodies the principles of equality and openness, welcoming visitors of all faiths with its four entrances symbolizing accessibility from all directions.',
        'duration': '1-2 days',
        'best_time': 'November to March',
        'image_url': 'https://plus.unsplash.com/premium_photo-1697730324062-c012bc98eb13?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8Z29sZGVuJTIwdGVtcGxlJTIwYW1yaXRzYXJ8ZW58MHx8MHx8fDA%3D',
        'latitude': 31.6200,
        'longitude': 74.8765,
        'price': 600.00
    },
    {
        'name': 'Western Wall',
        'location': 'Jerusalem, Israel',
        'description': 'A sacred site for Jewish prayer, believed to be the last remnant of the Second Temple. This ancient limestone wall has become the most significant site in Jewish religious and cultural tradition, where visitors place written prayers in the cracks between stones. The plaza before the wall serves as an open-air synagogue where worshippers pray day and night.',
        'duration': '1-2 days',
        'best_time': 'Year-round',
        'image_url': 'https://media.istockphoto.com/id/852178720/photo/jerusalem-wailing-wall-sunset.jpg?s=612x612&w=0&k=20&c=GqpDHsOIHFIZb7tPgrxjWJgcTB8zIDaV2H4LEPBRVEg=',
        'latitude': 31.7767,
        'longitude': 35.2345,
        'price': 850.00
    },
    {
        'name': 'Medina',
        'location': 'Saudi Arabia',
        'description': 'The city of the Prophet Muhammad and home to Al-Masjid an-Nabawi, his burial place. The second holiest site in Islam after Mecca, Medina was the capital of early Islamic civilization and contains many important historical mosques. The green dome above the Prophet\'s tomb is an iconic symbol, and the surrounding mosque has undergone numerous expansions to accommodate the millions of visitors it receives annually.',
        'duration': '2-3 days',
        'best_time': 'Year-round (except during peak Hajj season)',
        'image_url': 'https://media.istockphoto.com/id/688494594/photo/al-masjid-al-nabawi.jpg?s=612x612&w=0&k=20&c=wTrVBpUP3yB_TY1OZowiVKynWqfdol0MoIY9ZcItYoo=',
        'latitude': 24.4672,
        'longitude': 39.6112,
        'price': 1350.00
    },
    {
        'name': 'Rameswaram',
        'location': 'Tamil Nadu, India',
        'description': 'A sacred Hindu site associated with Lord Rama and the Ramanathaswamy Temple. According to Hindu mythology, this is where Rama built a bridge across the sea to Lanka to rescue his wife Sita. The temple is famous for its magnificent corridors and 22 sacred water tanks, each believed to absolve different sins. Pilgrims traditionally visit Rameswaram after their journey to Varanasi to complete the holy circuit.',
        'duration': '2-4 days',
        'best_time': 'October to April',
        'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTf5EmImNe-LQEgNsllajvhI4hflOhWApwcNw&s',
        'latitude': 9.2876,
        'longitude': 79.3129,
        'price': 650.00
    },
    {
        'name': 'Shikoku Pilgrimage',
        'location': 'Shikoku Island, Japan',
        'description': 'A Buddhist pilgrimage that spans 88 temples dedicated to Kobo Daishi. This ancient 1,200-kilometer circuit encircles the island of Shikoku and traditionally takes 30-60 days to complete on foot. Each temple represents one of the 88 human afflictions in Buddhist tradition. Modern pilgrims, known as henro, can often be identified by their white clothing, conical hats, and walking sticks, though many now complete parts of the route by bus or car.',
        'duration': '1-2 months (full circuit)',
        'best_time': 'Spring or Fall',
        'image_url': 'https://i.natgeofe.com/n/a0fa2967-ab95-453d-9afd-56a5a7f46182/STOCK_MF4105_2405_GettyImages-1300064416.jpg',
        'latitude': 33.8372,
        'longitude': 133.5354,
        'price': 1800.00
    },
    {
        'name': 'Karbala',
        'location': 'Iraq',
        'description': 'A holy city for Shia Muslims, home to the shrine of Imam Hussein. This site commemorates the martyrdom of Hussein ibn Ali, the grandson of Prophet Muhammad, during the Battle of Karbala in 680 CE. The golden-domed shrine is one of the oldest mosques in Islam and becomes the center of Ashura and Arbaeen observations, when millions of pilgrims gather to honor Imam Hussein\'s sacrifice and message of social justice.',
        'duration': '2-3 days',
        'best_time': 'During Arbaeen (40 days after Ashura)',
        'image_url': 'https://www.reviewofreligions.org/wp-content/uploads/2022/08/Karbala-small-shutterstock_1540235519.jpeg',
        'latitude': 32.6167,
        'longitude': 44.0333,
        'price': 950.00
    },
    {
        'name': 'Chartres Cathedral',
        'location': 'Chartres, France',
        'description': 'A UNESCO World Heritage Site and an important Marian pilgrimage destination. This masterpiece of French Gothic architecture is renowned for its stunning stained glass windows, which date from the 12th and 13th centuries and cover over 2,500 square meters. The cathedral houses the Sancta Camisa, believed to be the tunic worn by the Virgin Mary at the birth of Christ, which has drawn pilgrims for centuries.',
        'duration': '1-2 days',
        'best_time': 'April to October',
        'image_url': 'https://media.istockphoto.com/id/954059700/photo/south-side-of-chartres-cathedral.jpg?s=612x612&w=0&k=20&c=sgF7b5ByN8hq75QGs5KLGebKcS862-RhFORj0H9pU04=',
        'latitude': 48.4477,
        'longitude': 1.4875,
        'price': 750.00
    },
    {
        'name': 'Fatima',
        'location': 'Portugal',
        'description': 'A Marian pilgrimage site where apparitions of the Virgin Mary were reported in 1917. Three shepherd children claimed to have seen apparitions of Our Lady of Fatima, who entrusted them with three secrets. The Sanctuary of Fatima now includes the Basilica of Our Lady of the Rosary, which houses the tombs of two of the shepherd children, and a large open plaza where major ceremonies are held. May 13th and October 13th see especially large gatherings of devotees.',
        'duration': '2-3 days',
        'best_time': 'May to October',
        'image_url': 'https://joewalshtours.ie/app/uploads/2021/07/Our-Lady-of-Fatima-sanctuary-pilgrimage-Portugal-Joe-Walsh-Tours-Pilgrimages-travel-1024x683.jpg',
        'latitude': 39.6316,
        'longitude': -8.6753,
        'price': 800.00
    },
    {
        'name': 'Tirupati',
        'location': 'Andhra Pradesh, India',
        'description': 'Home to the Tirumala Venkateswara Temple, one of the wealthiest and most visited Hindu temples. Situated on the seven peaks of Tirumala Hills, this temple dedicated to Lord Venkateswara (a form of Vishnu) attracts tens of thousands of devotees daily. Many pilgrims offer their hair as sacrifice, and the traditional laddu prasadam (sweet offering) is famous throughout India. The temple\'s riches come from centuries of donations by devotees seeking blessings.',
        'duration': '1-3 days',
        'best_time': 'September to February',
        'image_url': 'https://tirupatibalajitravels.co.in/wp-content/uploads/2024/02/special-entry-darshan-1.webp',
        'latitude': 13.6288,
        'longitude': 79.4192,
        'price': 750.00
    },
    {
        'name': 'Mount Sinai',
        'location': 'Egypt',
        'description': 'Believed to be the biblical mountain where Moses received the Ten Commandments. This rugged peak in the Sinai Peninsula rises 2,285 meters above sea level and features prominently in the Abrahamic religions. Many pilgrims begin their ascent at night to reach the summit for sunrise, a profoundly moving experience. At the mountain\'s base sits the ancient St. Catherine\'s Monastery, which houses religious artifacts including what some believe to be the Burning Bush.',
        'duration': '1-2 days',
        'best_time': 'March to May or September to November',
        'image_url': 'https://thewanderingafro.com/wp-content/uploads/2023/09/Mount_Moses-scaled.jpg',
        'latitude': 28.5397,
        'longitude': 33.9733,
        'price': 1000.00
    },
    {
        'name': 'Ise Grand Shrine',
        'location': 'Mie Prefecture, Japan',
        'description': 'The most sacred Shinto shrine, dedicated to the sun goddess Amaterasu. Consisting of two main shrines and about 125 auxiliary shrines, Ise is considered the spiritual home of the Japanese people. Following ancient Shinto tradition, the shrine buildings are completely rebuilt every 20 years in an elaborate ceremony called Shikinen Sengu, preserving ancient construction techniques. The shrine is set within a primeval forest and connected by pilgrimage routes to other sacred sites.',
        'duration': '1-2 days',
        'best_time': 'Spring or Fall',
        'image_url': 'https://www.geoex.com/app/uploads/2019/07/japan-temple-historic-geoex.jpg',
        'latitude': 34.4546,
        'longitude': 136.7256,
        'price': 850.00
    },
    {
        'name': 'Canterbury Cathedral',
        'location': 'Canterbury, England',
        'description': 'A significant Christian pilgrimage site, associated with St. Thomas Becket. This magnificent cathedral became the center of pilgrimage after the archbishop Thomas Becket was murdered there in 1170. Geoffrey Chaucer\'s "Canterbury Tales" immortalized the medieval pilgrim experience. The cathedral showcases various architectural styles from Romanesque to Gothic and houses impressive stained glass windows, some dating back to the 12th century.',
        'duration': '1-2 days',
        'best_time': 'April to September',
        'image_url': 'https://world4.eu/wp-content/uploads/2023/04/canterbury-gateway.webp',
        'latitude': 51.2798,
        'longitude': 1.0829,
        'price': 900.00
    },
    {
        'name': 'Ajmer Sharif Dargah',
        'location': 'Ajmer, India',
        'description': 'The shrine of Sufi saint Moinuddin Chishti, a major pilgrimage for Muslims and people of all faiths. This marble shrine houses the tomb of the revered 12th-century Sufi saint who brought the Chishti order to India. Known as Gharib Nawaz (Benefactor of the Poor), his teachings emphasized tolerance and inclusivity. The dargah is particularly crowded during the annual Urs festival commemorating his death anniversary, with devotees believing that prayers made at the shrine are especially powerful.',
        'duration': '1-2 days',
        'best_time': 'October to March',
        'image_url': 'https://resources.thomascook.in/images/holidays/sightSeeing/ajmerdargha.jpg',
        'latitude': 26.4564,
        'longitude': 74.6283,
        'price': 500.00
    },
    {
        'name': 'Adam`s Peak (Sri Pada)',
        'location': 'Sri Lanka',
        'description': 'A sacred site for Buddhists, Hindus, Muslims, and Christians, known for the footprint-shaped mark at its summit. Rising 2,243 meters above Sri Lanka\'s central highlands, this conical mountain is a pilgrimage site for multiple faiths. Buddhists believe the footprint belongs to Buddha, Hindus attribute it to Shiva, Muslims to Adam, and Christians to St. Thomas. The challenging climb typically begins at night, with the reward of a spectacular sunrise and the mountain\'s perfect triangular shadow cast across the landscape.',
        'duration': '1-2 days',
        'best_time': 'December to May',
        'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTI3d9deqDnuX3awaT3XKIhmR7OcYtl69fF9A&s',
        'latitude': 6.8096,
        'longitude': 80.4994,
        'price': 750.00
    },
    {
        'name': 'Kumano Kodo',
        'location': 'Wakayama, Japan',
        'description': 'A network of ancient pilgrimage routes leading to the Kumano Sanzan shrines. This UNESCO World Heritage site consists of well-preserved medieval pilgrimage trails through the forested mountains of the Kii Peninsula. For over 1,000 years, these paths have led pilgrims to three grand shrines: Kumano Hongu Taisha, Kumano Hayatama Taisha, and Kumano Nachi Taisha. The network includes numerous oji (smaller shrines), sacred waterfalls, and hot springs that have spiritual significance in Shinto and Buddhist traditions.',
        'duration': '3-7 days',
        'best_time': 'Spring or Fall',
        'image_url': 'https://d2exd72xrrp1s7.cloudfront.net/www/collection/475/1R2aLT?width=768&height=576&crop=true',
        'latitude': 33.8894,
        'longitude': 135.7730,
        'price': 1600.00
    },
    {
        'name': 'Pashupatinath Temple',
        'location': 'Kathmandu, Nepal',
        'description': 'A sacred Hindu temple dedicated to Lord Shiva, located along the Bagmati River. This UNESCO World Heritage site is the largest temple complex in Nepal and one of the most significant Shiva temples on the subcontinent. The main pagoda-style temple features a distinctive gilded roof and four silver-plated doors. The temple grounds include cremation ghats along the Bagmati River, where Hindu funeral rites are performed openly, offering a profound glimpse into the Hindu understanding of life and death.',
        'duration': '1-2 days',
        'best_time': 'October to March',
        'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSoJXVVQdO2JBsB0Wh1nY_kVcxtkdGE27r9xA&s',
        'latitude': 27.7109,
        'longitude': 85.3485,
        'price': 600.00
    },
    {
        'name': 'Mount Athos',
        'location': 'Greece',
        'description': 'An Orthodox Christian monastic state, accessible only to male pilgrims. This autonomous monastic republic occupies a peninsula in northeastern Greece and has maintained its spiritual traditions since Byzantine times. Home to 20 monasteries and numerous hermitages, Mount Athos follows the Julian calendar and Byzantine hours. Access is strictly limited, requiring advance permits, and women have been forbidden from entering for over a thousand years. The dramatic mountain landscape and medieval architecture create an otherworldly atmosphere of spiritual contemplation.',
        'duration': '3-5 days',
        'best_time': 'April to October',
        'image_url': 'https://cdn.shopify.com/s/files/1/0254/1685/9682/t/5/assets/pf-029be620--holymountain.jpg?v=1601971240',
        'latitude': 40.1572,
        'longitude': 24.3289,
        'price': 1200.00
    },
    {
        'name': 'Saint Catherine`s Monastery',
        'location': 'Sinai, Egypt',
        'description': 'A UNESCO World Heritage Site at the base of Mount Sinai, linked to Moses and the Burning Bush. One of the oldest continuously functioning Christian monasteries in the world, it was built in the 6th century under Byzantine Emperor Justinian I. The monastery houses an extraordinary collection of early Christian manuscripts and icons, second only to the Vatican Library. Its remote location in the Sinai desert has helped preserve its treasures through centuries of conquests and changing empires.',
        'duration': '1-2 days',
        'best_time': 'March to May or September to November',
        'image_url': 'https://cdn.britannica.com/51/126951-050-19056A6C/St-Catherines-Monastery-Mount-Sinai-Egypt.jpg',
        'latitude': 28.5563,
        'longitude': 33.9756,
        'price': 950.00
    },
    {
        'name': 'Vaishno Devi',
        'location': 'Jammu and Kashmir, India',
        'description': 'A Hindu pilgrimage site dedicated to Goddess Vaishno Devi, nestled in the Trikuta Mountains. Located at an altitude of 5,200 feet, this cave shrine requires pilgrims to trek approximately 12 kilometers from the base camp at Katra. The main shrine contains natural rock formations believed to represent three manifestations of the goddess: Maha Kali, Maha Lakshmi, and Maha Saraswati. With over 8 million visitors annually, it is one of the most visited Hindu shrines and is managed by a dedicated board established by the government.',
        'duration': '2-3 days',
        'best_time': 'March to October',
        'image_url': 'https://www.amritara.co.in/blog/admin/assets/img/post/image_2024-11-29-10-36-16_6749992066923.jpg',
        'latitude': 33.0297,
        'longitude': 74.9490,
        'price': 800.00
    },
    {
        'name': 'Chichen Itza',
        'location': 'Yucatán, Mexico',
        'description': 'An ancient Mayan pilgrimage center with the iconic Temple of Kukulcán. This UNESCO World Heritage site and one of the New Seven Wonders of the World was one of the largest Maya cities and a powerful regional capital around 600-900 CE. The site features numerous well-preserved structures, including the famous pyramid known as El Castillo, which demonstrates the Maya\'s advanced astronomical knowledge—during equinoxes, sunlight creates the illusion of a serpent descending the pyramid\'s staircase, representing the feathered serpent deity Kukulcán.',
        'duration': '1-2 days',
        'best_time': 'November to March',
        'image_url': 'https://media.istockphoto.com/id/481272289/photo/el-castillo-of-chichen-itza-at-sunset-mexico.jpg?s=612x612&w=0&k=20&c=vp5jlz0SdiCl4ow_xRUPDgZ-09TdRdWuzE4NW7v130c=',
        'latitude': 20.6843,
        'longitude': -88.5677,
        'price': 1100.00
    }
]
        

    
    
   
    for pilgrimage_data in pilgrimages:
        pilgrimage = Pilgrimage(**pilgrimage_data)
        db.session.add(pilgrimage)
    
    db.session.commit()
    print("Database has been refreshed with pilgrimage data.")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_pilgrimages()
