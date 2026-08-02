"""
Generates a short, friendly AI trip summary/itinerary blurb using Gemini.
Falls back to a simple template if no GEMINI_API_KEY is configured, so the
app still works end-to-end without an LLM key.
"""
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

_model = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        _model = None


def _names(places: List[Dict], n: int = 5) -> str:
    return ", ".join(p["name"] for p in places[:n] if p.get("name"))


def generate_trip_summary(destination: str, days: int, preferences: List[str],
                           attractions: List[Dict], hotels: List[Dict],
                           restaurants: List[Dict]) -> str:
    prefs_text = ", ".join(preferences) if preferences else "a bit of everything"

    if _model is not None:
        prompt = (
            f"You are a friendly travel planner. A user is visiting {destination} "
            f"for {days} days and is interested in: {prefs_text}.\n"
            f"Top attractions found: {_names(attractions)}.\n"
            f"Top hotels found: {_names(hotels)}.\n"
            f"Top restaurants found: {_names(restaurants)}.\n\n"
            "Write a warm, upbeat 4-6 sentence trip overview that ties these "
            "together into a mini itinerary suggestion. Keep it concise, no headers, no bullet points."
        )
        try:
            response = _model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return _fallback_summary(destination, days, prefs_text, attractions, hotels, restaurants)

    return _fallback_summary(destination, days, prefs_text, attractions, hotels, restaurants)


def _fallback_summary(destination, days, prefs_text, attractions, hotels, restaurants) -> str:
    """Used when no LLM API key is configured."""
    return (
        f"Here's a quick {days}-day plan for {destination}, tailored around {prefs_text}. "
        f"Start your days exploring spots like {_names(attractions, 3) or 'the top local attractions'}, "
        f"stay somewhere comfortable such as {_names(hotels, 2) or 'one of the highly-rated hotels below'}, "
        f"and don't miss eating at {_names(restaurants, 3) or 'the top-rated local restaurants'}. "
        "Mix sightseeing with relaxed downtime so you actually enjoy the trip instead of rushing through it!"
    )
