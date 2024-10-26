from flask import Blueprint, request, jsonify
import requests
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
from math import radians, sin, cos, sqrt, atan2

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

gym_finder_bp = Blueprint('gym_finder', __name__)

# RapidAPI credentials
RAPIDAPI_KEY = "0e97da0af5msh8e4e1038279ed59p1c8354jsn4372da16c67d"
RAPIDAPI_HOST = "google-map-places.p.rapidapi.com"

def get_nearby_gyms_with_details(latitude, longitude, radius=1000):
    url = f"https://{RAPIDAPI_HOST}/maps/api/place/nearbysearch/json"
    
    querystring = {
        "location": f"{latitude},{longitude}",
        "radius": str(radius),
        "type": "gym",
        "language": "en"
    }
    
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    nearby_gyms = response.json()
    
    gyms_with_details = []
    
    for gym in nearby_gyms.get('results', []):
        place_id = gym['place_id']
        details_url = f"https://{RAPIDAPI_HOST}/maps/api/place/details/json"
        details_querystring = {
            "place_id": place_id,
            "language": "en"
        }
        
        details_response = requests.get(details_url, headers=headers, params=details_querystring)
        gym_details = details_response.json()
        
        gyms_with_details.append({**gym, **gym_details.get('result', {})})
    
    return gyms_with_details

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance

def filter_and_sort_gyms(gyms, current_latitude, current_longitude):
    gym_list = []
    for gym in gyms:
        gym_lat = gym['geometry']['location']['lat']
        gym_lng = gym['geometry']['location']['lng']
        distance = calculate_distance(current_latitude, current_longitude, gym_lat, gym_lng)
        
        gym_list.append({
            'name': gym['name'],
            'vicinity': gym['vicinity'],
            'rating': gym.get('rating', 'N/A'),
            'distance': distance,
            'reviews': gym.get('reviews', []),
            'opening_hours': gym.get('opening_hours', {}).get('weekday_text', []),
            'place_id': gym['place_id']
        })
    
    return sorted(gym_list, key=lambda x: x['distance'])

def analyze_comments(reviews):
    stop_words = set(stopwords.words('english'))
    all_words = []

    for review in reviews:
        words = word_tokenize(review['text'].lower())
        all_words.extend([word for word in words if word.isalnum() and word not in stop_words])

    word_freq = Counter(all_words)
    return word_freq.most_common(10)

@gym_finder_bp.route('/nearby_gyms', methods=['GET'])
def get_nearby_gyms():
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        
        gyms_with_details = get_nearby_gyms_with_details(latitude, longitude)
        filtered_gyms = filter_and_sort_gyms(gyms_with_details, latitude, longitude)
        
        result = []
        for gym in filtered_gyms[:5]:
            gym_data = {
                "name": gym['name'],
                "address": gym['vicinity'],
                "rating": gym['rating'],
                "distance": f"{gym['distance']:.2f} kilometers",
                "opening_hours": gym['opening_hours'],
            }
            
            reviews = gym['reviews']
            if reviews:
                keywords = analyze_comments(reviews)
                gym_data["top_keywords"] = [{"word": word, "frequency": freq} for word, freq in keywords]
            else:
                gym_data["top_keywords"] = []
            
            result.append(gym_data)
        
        return jsonify({
            "current_location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "current_time": datetime.now().isoformat(),
            "gyms": result
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500