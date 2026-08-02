"""
Lightweight ML ranking layer (scikit-learn) on top of raw Google Places results.

Approach (content-based filtering):
  1. Build a text "profile" for each place from its Google `types` list.
  2. Vectorize place profiles + the user's stated preferences with TF-IDF.
  3. Rank places by cosine similarity to the user preference vector,
     blended with their normalized Google rating (so a great match with
     a 2-star rating doesn't beat a strong match with a 4.7-star rating).

This keeps things fast/local (no external ML calls) while still being a
genuine learned-similarity ranking rather than a hand-written if/else.
"""
from typing import List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

# Rating weight vs preference-match weight in the final score
RATING_WEIGHT = 0.4
PREFERENCE_WEIGHT = 0.6

# Maps our user-facing preference tags to related Google Place "types"
PREFERENCE_SYNONYMS = {
    "nature": "park natural_feature campground zoo hiking outdoors",
    "food": "restaurant cafe bakery food meal_takeaway",
    "culture": "museum art_gallery church temple mosque historical landmark",
    "nightlife": "bar night_club casino",
    "adventure": "amusement_park zoo aquarium tourist_attraction",
    "shopping": "shopping_mall store market",
    "relaxation": "spa lodging beach",
}


def _place_profile(place: Dict) -> str:
    return " ".join(place.get("types", [])) or place.get("name", "")


def rank_places(places: List[Dict], preferences: List[str]) -> List[Dict]:
    """Returns the same places list, sorted best-match-first, each with a `score` field (0-1)."""
    if not places:
        return []

    profiles = [_place_profile(p) for p in places]

    # Expand user preference tags into Google-types-like text for a fair comparison
    pref_text = " ".join(PREFERENCE_SYNONYMS.get(p.lower(), p) for p in preferences) or "tourist_attraction"

    corpus = profiles + [pref_text]
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Empty vocabulary edge case (e.g. all places have no types) -> no preference signal
        for p in places:
            p["score"] = round(float(p.get("rating") or 0) / 5, 3)
        return sorted(places, key=lambda x: x["score"], reverse=True)

    place_vectors = tfidf_matrix[:-1]
    pref_vector = tfidf_matrix[-1]
    similarity_scores = cosine_similarity(place_vectors, pref_vector).flatten()

    ratings = np.array([[p.get("rating") or 0] for p in places], dtype=float)
    if ratings.max() > 0:
        normalized_ratings = MinMaxScaler().fit_transform(ratings).flatten()
    else:
        normalized_ratings = ratings.flatten()

    final_scores = PREFERENCE_WEIGHT * similarity_scores + RATING_WEIGHT * normalized_ratings

    for place, score in zip(places, final_scores):
        place["score"] = round(float(score), 3)

    return sorted(places, key=lambda x: x["score"], reverse=True)
