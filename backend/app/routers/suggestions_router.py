from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.schemas import SuggestionOut
from app.services.suggestion_service import (
    get_reorder_suggestions,
    get_seasonal_suggestions,
    get_substitutes,
)

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


@router.get("", response_model=list[SuggestionOut])
def get_all_suggestions(db: Session = Depends(get_db)):
    """Combined feed: reorder predictions + seasonal picks, for the suggestions panel."""
    return get_reorder_suggestions(db) + get_seasonal_suggestions()


@router.get("/substitutes/{item_name}", response_model=list[SuggestionOut])
def get_item_substitutes(item_name: str):
    return get_substitutes(item_name)
