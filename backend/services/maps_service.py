import requests

import os
import requests

API_KEY = os.getenv("GEOAPIFY_API_KEY")

GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"
PLACES_URL = "https://api.geoapify.com/v2/places"

HEADERS = {
    "User-Agent": "AI-Travel-Planner/1.0"
}


def geocode_location(destination):
    """
    Convert a location name into latitude and longitude using Geoapify.
    """
    try:
        params = {
            "text": destination,
            "limit": 1,
            "apiKey": API_KEY
        }

        response = requests.get(
            GEOCODING_URL,
            params=params,
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()

        data = response.json()

        features = data.get("features", [])
        if not features:
            return None

        feature = features[0]
        props = feature.get("properties", {})

        return {
            "lat": props.get("lat"),
            "lng": props.get("lon")
        }

    except Exception as e:
        print("Geoapify Geocoding Error:", e)
        return None


def _format_address(props):
    parts = [
        props.get("housenumber"),
        props.get("street"),
        props.get("suburb"),
        props.get("city"),
        props.get("state"),
        props.get("postcode"),
        props.get("country"),
    ]

    parts = [p for p in parts if p]
    return ", ".join(parts)


def _osm_url(lat, lng):
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map=18/{lat}/{lng}"


def _fetch_places(lat, lng, categories, limit=20):
    """
    Fetch places from Geoapify Places API.
    """
    try:
        params = {
            "categories": categories,
            "filter": f"circle:{lng},{lat},10000",
            "bias": f"proximity:{lng},{lat}",
            "limit": limit,
            "apiKey": API_KEY
        }

        response = requests.get(
            PLACES_URL,
            params=params,
            headers=HEADERS,
            timeout=20
        )
        response.raise_for_status()

        data = response.json()
        features = data.get("features", [])

        places = []

        for feature in features:
            props = feature.get("properties", {})
            if not props.get("name"):
               continue

            place_lat = props.get("lat")
            place_lng = props.get("lon")

            places.append({
                "name": props.get("name", "Unknown"),
                "address": _format_address(props),
                "rating": None,
                "user_ratings_total": None,
                "types": props.get("categories", []),
                "maps_url": _osm_url(place_lat, place_lng)
                if place_lat and place_lng else None,
                "photo_url": None,
                "lat": place_lat,
                "lng": place_lng
            })

        return places

    except Exception as e:
        print("Geoapify Places Error:", e)
        return []


def get_attractions(destination):
    """
    Fetch tourist attractions.
    """
    location = geocode_location(destination)

    if not location:
        return []

    return _fetch_places(
        location["lat"],
        location["lng"],
        categories="tourism.attraction"
    )


def get_hotels(destination):
    """
    Fetch hotels.
    """
    location = geocode_location(destination)

    if not location:
        return []

    return _fetch_places(
        location["lat"],
        location["lng"],
        categories="accommodation.hotel"
    )


def get_restaurants(destination):
    """
    Fetch restaurants.
    """
    location = geocode_location(destination)

    if not location:
        return []

    return _fetch_places(
        location["lat"],
        location["lng"],
        categories="catering.restaurant"
    )