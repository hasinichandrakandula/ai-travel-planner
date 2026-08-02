"""
Pydantic schemas used for request validation and response serialization.
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


# ---------- Recommendation ----------
class RecommendRequest(BaseModel):
    destination: str
    days: int = 3
    preferences: List[str] = []   # e.g. ["nature", "food", "culture", "nightlife", "adventure", "shopping"]
    budget: Optional[str] = "any"  # "low" | "medium" | "high" | "any"


class Place(BaseModel):
    name: str
    address: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    types: List[str] = []
    maps_url: Optional[str] = None
    photo_url: Optional[str] = None
    score: Optional[float] = None


class RecommendResponse(BaseModel):
    destination: str
    attractions: List[Place]
    hotels: List[Place]
    restaurants: List[Place]
    ai_summary: str
