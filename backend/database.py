import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


# Load .env file from the backend folder
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)


# Get DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")


# Convert standard MySQL URI to PyMySQL dialect
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "mysql://",
        "mysql+pymysql://",
        1
    )


# Clean SSL parameters for PyMySQL compatibility
connect_args = {}

if "ssl-mode=REQUIRED" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace(
        "?ssl-mode=REQUIRED",
        ""
    ).replace(
        "&ssl-mode=REQUIRED",
        ""
    )

    connect_args["ssl"] = {
        "ssl_mode": "REQUIRED"
    }


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300
)


# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()