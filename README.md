# 🧳 AI Travel Planner

Sign in → tell it where you're travelling → get AI-ranked places to visit,
hotels to stay, and must-try restaurants.

**Stack:** Streamlit (frontend) · FastAPI (backend) · MySQL (users/history) ·
scikit-learn (ranking) · Gemini (AI trip summary) · Google Maps Places API (data)

```
ai-travel-planner/
├── backend/
│   ├── main.py              FastAPI app (signup, login, recommend, history)
│   ├── database.py          MySQL/SQLAlchemy connection
│   ├── models.py             users, search_history tables
│   ├── schemas.py            Pydantic request/response models
│   ├── auth.py               password hashing + JWT
│   ├── recommender.py        scikit-learn TF-IDF/cosine ranking of places
│   ├── schema.sql            raw SQL if you prefer creating tables manually
│   ├── services/
│   │   ├── maps_service.py   Google Geocoding + Places API calls
│   │   ├── llm_service.py    Gemini-generated trip summary (with fallback)
│   │   └── mock_data.py      sample data used if no Maps API key is set yet
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── app.py                 Streamlit UI: sign in -> destination -> results
    ├── requirements.txt
    └── .env.example
```

## 1. MySQL

Create the database (SQLAlchemy will also auto-create tables on first run,
but you can run this manually too):

```bash
mysql -u root -p < backend/schema.sql
```

## 2. Backend setup

```bash
cd backend
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then fill in DB credentials + API keys
uvicorn main:app --reload --port 8000
```

Backend docs (Swagger UI) will be at **http://localhost:8000/docs**.

## 3. Frontend setup

In a second terminal:

```bash
cd frontend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # BACKEND_URL defaults to http://localhost:8000
streamlit run app.py
```

Open **http://localhost:8501** — you'll land on the sign-in screen first.

## API keys you need

| Key | Where to get it | Required? |
|---|---|---|
| `GOOGLE_MAPS_API_KEY` | Google Cloud Console → enable **Places API** + **Geocoding API** | Optional — app runs on mock data without it |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) | Optional — falls back to a template summary without it |

The app is fully runnable and demoable **without any API keys** (using
`services/mock_data.py`), so you can wire up the UI/DB/auth first and drop
in real keys later.

## How the recommendation ranking works

`recommender.py` uses scikit-learn's `TfidfVectorizer` + cosine similarity to
match each place's Google `types` (e.g. `museum`, `park`, `restaurant`)
against the user's selected interests (nature, food, culture, etc.), blended
with the place's normalized Google rating. This is a genuine content-based
filtering model, not a hardcoded sort — swap in a collaborative-filtering
model later using the `search_history` table once you have real usage data.

## Notes / next steps

- Passwords are hashed with bcrypt; sessions use JWT bearer tokens.
- `search_history` table logs every search, ready to power a smarter
  personalized recommender down the line.
- For production: move secrets out of `.env`, add HTTPS, rate-limit the
  `/recommend` endpoint, and consider caching Google Places results per
  destination to save on API costs.
