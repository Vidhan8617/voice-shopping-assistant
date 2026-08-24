"""
Database tables.

Three tables:
- ShoppingItem: the user's current live list
- HistoryEntry: every add ever made (even after removal) — this is what
  powers "smart suggestions", since we need past behavior to predict future needs
- Product: a small mock catalog so voice search ("find toothpaste under $5")
  has something real to query
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.core.database import Base


class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit = Column(String, nullable=True)  # e.g. "bottles", "kg" — optional
    category = Column(String, nullable=False, default="Other")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class HistoryEntry(Base):
    __tablename__ = "history_entries"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, index=True, nullable=False)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    brand = Column(String, nullable=True)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
