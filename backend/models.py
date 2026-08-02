"""
SQLAlchemy ORM models -> MySQL tables.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    searches = relationship("SearchHistory", back_populates="user")


class SearchHistory(Base):
    """Keeps a log of every trip search a user makes; also lets the
    recommender learn a very simple notion of the user's preferences over time."""
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination = Column(String(150), nullable=False)
    preferences = Column(String(255))   # comma separated tags e.g. "food,nature,culture"
    days = Column(Integer, default=1)
    llm_summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="searches")
