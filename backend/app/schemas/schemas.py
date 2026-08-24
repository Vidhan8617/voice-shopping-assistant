"""
Pydantic schemas — the request/response contracts for the API.

Kept separate from SQLAlchemy models on purpose: DB models describe storage,
schemas describe the wire format. They often look similar but shouldn't be
the same class — that coupling bites you the moment they need to diverge
(e.g. hiding an internal field from the API response).
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---- Shopping list items ----

class ShoppingItemOut(BaseModel):
    id: int
    name: str
    quantity: int
    unit: Optional[str] = None
    category: str
    created_at: datetime

    class Config:
        from_attributes = True  # allows Pydantic to read directly from SQLAlchemy objects


class ShoppingItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    quantity: int = Field(default=1, ge=1)
    unit: Optional[str] = None


# ---- Voice command processing ----

class VoiceCommandIn(BaseModel):
    transcript: str = Field(..., min_length=1, description="Raw text from speech recognition")
    language: str = Field(default="en", description="ISO language code, e.g. 'en', 'hi', 'es'")


class ParsedIntent(BaseModel):
    action: Literal["add", "remove", "search", "unknown"]
    item: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    source: Literal["rules", "llm"]  # which parser resolved this — useful for debugging/demo


class VoiceCommandResult(BaseModel):
    intent: ParsedIntent
    item: Optional[ShoppingItemOut] = None  # populated if the action mutated the list
    message: str  # human-readable confirmation, e.g. "Added 2 bottles of water"
    suggestions: list[str] = []  # e.g. substitute suggestions triggered by this action


# ---- Suggestions ----

class SuggestionOut(BaseModel):
    item_name: str
    reason: str
    type: Literal["reorder", "seasonal", "substitute"]


# ---- Search ----

class ProductOut(BaseModel):
    id: int
    name: str
    brand: Optional[str]
    category: str
    price: float

    class Config:
        from_attributes = True
