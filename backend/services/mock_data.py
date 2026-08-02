"""
Fallback sample data so the app is runnable/demoable end-to-end even before
a GOOGLE_MAPS_API_KEY is configured. Once a real key is added, maps_service
will return live results and this file is never used.
"""
from typing import List, Dict


def mock_attractions(destination: str) -> List[Dict]:
    return [
        {"name": f"{destination} Old Town", "address": destination, "rating": 4.6,
         "user_ratings_total": 1200, "types": ["tourist_attraction", "historical_landmark"],
         "maps_url": None, "photo_url": None},
        {"name": f"{destination} National Park", "address": destination, "rating": 4.7,
         "user_ratings_total": 900, "types": ["park", "natural_feature"],
         "maps_url": None, "photo_url": None},
        {"name": f"{destination} City Museum", "address": destination, "rating": 4.4,
         "user_ratings_total": 500, "types": ["museum", "art_gallery"],
         "maps_url": None, "photo_url": None},
    ]


def mock_hotels(destination: str) -> List[Dict]:
    return [
        {"name": f"Grand {destination} Hotel", "address": destination, "rating": 4.5,
         "user_ratings_total": 800, "types": ["lodging"], "maps_url": None, "photo_url": None},
        {"name": f"{destination} Boutique Stay", "address": destination, "rating": 4.3,
         "user_ratings_total": 300, "types": ["lodging"], "maps_url": None, "photo_url": None},
    ]


def mock_restaurants(destination: str) -> List[Dict]:
    return [
        {"name": f"{destination} Local Kitchen", "address": destination, "rating": 4.6,
         "user_ratings_total": 650, "types": ["restaurant"], "maps_url": None, "photo_url": None},
        {"name": f"Cafe {destination}", "address": destination, "rating": 4.4,
         "user_ratings_total": 400, "types": ["cafe", "restaurant"], "maps_url": None, "photo_url": None},
    ]
