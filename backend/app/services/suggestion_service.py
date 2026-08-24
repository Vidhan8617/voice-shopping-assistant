"""
Smart suggestions service.

Three suggestion types, deliberately kept as transparent heuristics rather
than a trained model — with 8-hour-to-a-few-day scope, a trained
recommender has no real training data behind it anyway (a "real" ML model
fit on a handful of synthetic rows is theater, not ML). Heuristics that
are honest about being heuristics, with a schema that could later host a
real model's output, is the more defensible engineering choice — and it's
explained as such in the README.
"""
from collections import Counter
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.constants import SEASONAL_ITEMS, SUBSTITUTES
from app.models.models import HistoryEntry, ShoppingItem
from app.schemas.schemas import SuggestionOut

REORDER_WINDOW_DAYS = 7  # if an item is typically bought within this window and hasn't been, suggest it


def get_reorder_suggestions(db: Session, limit: int = 5) -> list[SuggestionOut]:
    """
    Frequency heuristic: items the user has added multiple times before,
    that are not currently on their live list, get suggested as a likely
    reorder ("it looks like you're running low on bread").
    """
    history = db.query(HistoryEntry).all()
    if not history:
        return []

    counts = Counter(h.item_name for h in history)
    current_items = {i.name.lower() for i in db.query(ShoppingItem).all()}

    suggestions = []
    for item_name, count in counts.most_common():
        if count >= 2 and item_name not in current_items:
            suggestions.append(SuggestionOut(
                item_name=item_name,
                reason=f"You've bought this {count} times before — might be time to restock.",
                type="reorder",
            ))
        if len(suggestions) >= limit:
            break
    return suggestions


def get_seasonal_suggestions(limit: int = 3) -> list[SuggestionOut]:
    month = datetime.now(timezone.utc).month
    items = SEASONAL_ITEMS.get(month, [])
    return [
        SuggestionOut(item_name=item, reason="In season this month.", type="seasonal")
        for item in items[:limit]
    ]


def get_substitutes(item_name: str) -> list[SuggestionOut]:
    key = item_name.strip().lower()
    alternatives = SUBSTITUTES.get(key, [])
    return [
        SuggestionOut(
            item_name=alt,
            reason=f"Alternative to {key}.",
            type="substitute",
        )
        for alt in alternatives
    ]
