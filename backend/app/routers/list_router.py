"""
Shopping list CRUD endpoints. Kept thin — no business logic lives here,
only request/response wiring and DB session handling.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import HistoryEntry, ShoppingItem
from app.schemas.schemas import ShoppingItemCreate, ShoppingItemOut
from app.services.category_service import categorize

router = APIRouter(prefix="/api/list", tags=["shopping-list"])


@router.get("", response_model=list[ShoppingItemOut])
def get_list(db: Session = Depends(get_db)):
    return db.query(ShoppingItem).order_by(ShoppingItem.category, ShoppingItem.name).all()


@router.post("", response_model=ShoppingItemOut, status_code=201)
def add_item(payload: ShoppingItemCreate, db: Session = Depends(get_db)):
    category = categorize(payload.name)
    item = ShoppingItem(
        name=payload.name.strip().lower(),
        quantity=payload.quantity,
        unit=payload.unit,
        category=category,
    )
    db.add(item)
    # Every add is logged to history — this is what powers reorder suggestions later
    db.add(HistoryEntry(item_name=item.name, added_at=datetime.now(timezone.utc)))
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def remove_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ShoppingItem).filter(ShoppingItem.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    db.delete(item)
    db.commit()
    return None


@router.delete("/by-name/{item_name}", status_code=204)
def remove_item_by_name(item_name: str, db: Session = Depends(get_db)):
    """
    Voice removal is name-driven ("remove milk"), not ID-driven — the user
    doesn't know the DB id. This endpoint removes the most recently added
    match for that name.
    """
    item = (
        db.query(ShoppingItem)
        .filter(ShoppingItem.name == item_name.strip().lower())
        .order_by(ShoppingItem.created_at.desc())
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail=f"'{item_name}' is not on your list")
    db.delete(item)
    db.commit()
    return None
