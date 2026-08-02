"""
AI Travel Planner - FastAPI backend.

Endpoints:
  POST /signup     - create a new user
  POST /login       - authenticate, returns JWT
  POST /recommend   - (auth required) get AI-ranked attractions, hotels, restaurants for a destination
  GET  /history      - (auth required) list the logged-in user's past searches

Run:
    uvicorn main:app --reload --port 8000
"""
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES,
)
from services import maps_service, llm_service, mock_data
from recommender import rank_places

# Creates tables on startup if they don't exist yet (simple approach; use
# Alembic migrations instead for a production system).
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Travel Planner API")

# Allow the Streamlit frontend (any localhost port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "AI Travel Planner API"}


# ---------------------------------------------------------------- AUTH -----
@app.post("/signup", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(
        {"sub": new_user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return schemas.Token(access_token=token, username=new_user.username)


@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(
        {"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return schemas.Token(access_token=token, username=user.username)
# --------------------------------------------------------- RECOMMEND -----
@app.post("/recommend", response_model=schemas.RecommendResponse)
def recommend(
    req: schemas.RecommendRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    destination = req.destination.strip()

    if not destination:
        raise HTTPException(
            status_code=400,
            detail="Destination is required"
        )

    # ---------------- Fetch Attractions ----------------
    try:
        attractions = maps_service.get_attractions(destination)
    except Exception as e:
        print("Attraction error:", e)
        attractions = []

    # ---------------- Fetch Hotels ----------------
    try:
        hotels = maps_service.get_hotels(destination)
    except Exception as e:
        print("Hotel error:", e)
        hotels = []

    # ---------------- Fetch Restaurants ----------------
    try:
        restaurants = maps_service.get_restaurants(destination)
    except Exception as e:
        print("Restaurant error:", e)
        restaurants = []

    # ---------------- Ranking ----------------
    attractions = rank_places(attractions, req.preferences)
    hotels = rank_places(hotels, req.preferences)
    restaurants = rank_places(restaurants, req.preferences)

    # ---------------- AI Summary ----------------
    ai_summary = llm_service.generate_trip_summary(
        destination,
        req.days,
        req.preferences,
        attractions,
        hotels,
        restaurants
    )

    # ---------------- Save History ----------------
    db.add(
        models.SearchHistory(
            user_id=current_user.id,
            destination=destination,
            preferences=",".join(req.preferences),
            days=req.days,
            llm_summary=ai_summary,
        )
    )

    db.commit()

    # ---------------- Response ----------------
    return schemas.RecommendResponse(
        destination=destination,
        attractions=[schemas.Place(**a) for a in attractions],
        hotels=[schemas.Place(**h) for h in hotels],
        restaurants=[schemas.Place(**r) for r in restaurants],
        ai_summary=ai_summary
    )