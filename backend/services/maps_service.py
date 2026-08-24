import os
import requests

API_KEY = os.getenv("GEOAPIFY_API_KEY")

GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"
PLACES_URL = "https://api.geoapify.com/v2/places"

HEADERS = {
    "User-Agent": "AI-Travel-Planner/1.0"
}


def geocode_location(destination):
    if not API_KEY:
        print("⚠️ Warning: GEOAPIFY_API_KEY is not set!")
        return None
    try:
        params = {
            "text": destination,
            "limit": 1,
            "apiKey": API_KEY
        }
        response = requests.get(GEOCODING_URL, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()

        features = data.get("features", [])
        if not features:
            return None

        props = features[0].get("properties", {})
        return {
            "lat": props.get("lat"),
            "lng": props.get("lon")
        }
    except Exception as e:
        print("Geoapify Geocoding Error:", e)
        return None


def _format_address(props):
    parts = [
        props.get("street"),
        props.get("suburb"),
        props.get("city"),
        props.get("state"),
        props.get("country"),
    ]
    return ", ".join([p for p in parts if p])


def _osm_url(lat, lng):
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map=18/{lat}/{lng}"


def _fetch_places(lat, lng, categories, limit=15):
    if not API_KEY:
        return []
    try:
        params = {
            "categories": categories,
            "filter": f"circle:{lng},{lat},15000",
            "bias": f"proximity:{lng},{lat}",
            "limit": limit,
            "apiKey": API_KEY
        }
        response = requests.get(PLACES_URL, params=params, headers=HEADERS, timeout=20)
        response.raise_for_status()
        features = response.json().get("features", [])

        places = []
        for feature in features:
            props = feature.get("properties", {})
            name = props.get("name")
            if not name:
                continue

            place_lat = props.get("lat")
            place_lng = props.get("lon")

            places.append({
                "name": name,
                "address": _format_address(props),
                "rating": props.get("rank", {}).get("popularity", 4.0),
                "user_ratings_total": None,
                "types": props.get("categories", []),
                "maps_url": _osm_url(place_lat, place_lng) if place_lat and place_lng else None,
                "photo_url": None,
                "lat": place_lat,
                "lng": place_lng
            })
        return places
    except Exception as e:
        print(f"Geoapify Places Error for categories '{categories}':", e)
        return []


def get_attractions(destination):
    location = geocode_location(destination)
    if not location:
        return []
    return _fetch_places(
        location["lat"], location["lng"],
        categories="tourism.sights,tourism.attraction,entertainment.museum,heritage"
    )


def get_hotels(destination):
    location = geocode_location(destination)
    if not location:
        return []
    return _fetch_places(
        location["lat"], location["lng"],
        categories="accommodation.hotel,accommodation.guest_house,accommodation.motel"
    )


def get_restaurants(destination):
    location = geocode_location(destination)
    if not location:
        return []
    return _fetch_places(
        location["lat"], location["lng"],
        categories="catering.restaurant,catering.cafe"
    )