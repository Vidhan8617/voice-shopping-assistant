"""
Voice-activated product search, with optional price ceiling and brand filter.

Parses simple price phrases out of the raw query (e.g. "toothpaste under $5")
so the frontend can send the transcript straight through without needing its
own parsing logic — this keeps all NLU concerns on the backend.
"""
import re

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Product
from app.schemas.schemas import ProductOut

router = APIRouter(prefix="/api/search", tags=["search"])

_UNDER_PRICE = re.compile(r"under\s+\$?(\d+(?:\.\d+)?)", re.IGNORECASE)
_BRAND_PATTERN = re.compile(r"\bby\s+(\w+)", re.IGNORECASE)


@router.get("", response_model=list[ProductOut])
def search_products(
    q: str = Query(..., min_length=1, description="Raw search text, e.g. 'organic apples under $5'"),
    db: Session = Depends(get_db),
):
    max_price = None
    price_match = _UNDER_PRICE.search(q)
    if price_match:
        max_price = float(price_match.group(1))
        q = _UNDER_PRICE.sub("", q)

    brand = None
    brand_match = _BRAND_PATTERN.search(q)
    if brand_match:
        brand = brand_match.group(1)
        q = _BRAND_PATTERN.sub("", q)

    q = re.sub(r"\b(organic|find|search|for|me)\b", "", q, flags=re.IGNORECASE).strip()

    query = db.query(Product)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    return query.limit(20).all()
