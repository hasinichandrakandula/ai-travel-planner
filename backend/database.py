import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Fetch DATABASE_URL from Render environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")

# 2. Convert standard mysql URI to pymysql dialect
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# 3. Clean SSL parameters for PyMySQL compatibility
connect_args = {}
if "ssl-mode=REQUIRED" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?ssl-mode=REQUIRED", "").replace("&ssl-mode=REQUIRED", "")
    connect_args["ssl"] = {"ssl_mode": "REQUIRED"}

# 4. Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()