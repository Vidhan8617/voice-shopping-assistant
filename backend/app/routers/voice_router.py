"""
Voice command endpoint — the heart of the app.

Flow: transcript in -> NLU parses intent -> intent mutates the list (or
triggers a search) -> response includes a human-readable confirmation +
any relevant substitute suggestions, so the frontend can just display
`message` directly without re-deriving it.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import HistoryEntry, ShoppingItem
from app.schemas.schemas import ShoppingItemOut, VoiceCommandIn, VoiceCommandResult
from app.services.category_service import categorize
from app.services.nlu_service import parse_voice_command
from app.services.suggestion_service import get_substitutes

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/command", response_model=VoiceCommandResult)
def handle_voice_command(payload: VoiceCommandIn, db: Session = Depends(get_db)):
    intent = parse_voice_command(payload.transcript, payload.language)

    if intent.action == "unknown" or not intent.item:
        return VoiceCommandResult(
            intent=intent,
            message="Sorry, I didn't catch that. Try something like 'add milk' or 'remove bread'.",
        )

    if intent.action == "add":
        category = categorize(intent.item)
        item = ShoppingItem(
            name=intent.item, quantity=intent.quantity or 1,
            unit=intent.unit, category=category,
        )
        db.add(item)
        db.add(HistoryEntry(item_name=item.name, added_at=datetime.now(timezone.utc)))
        db.commit()
        db.refresh(item)

        qty_str = f"{item.quantity} " if item.quantity != 1 else ""
        unit_str = f"{item.unit} of " if item.unit else ""
        message = f"Added {qty_str}{unit_str}{item.name} to your list."

        subs = get_substitutes(intent.item)
        return VoiceCommandResult(
            intent=intent,
            item=ShoppingItemOut.model_validate(item),
            message=message,
            suggestions=[s.item_name for s in subs],
        )

    if intent.action == "remove":
        existing = (
            db.query(ShoppingItem)
            .filter(ShoppingItem.name == intent.item)
            .order_by(ShoppingItem.created_at.desc())
            .first()
        )
        if existing is None:
            return VoiceCommandResult(
                intent=intent, message=f"'{intent.item}' isn't on your list.",
            )
        db.delete(existing)
        db.commit()
        return VoiceCommandResult(intent=intent, message=f"Removed {intent.item} from your list.")

    if intent.action == "search":
        return VoiceCommandResult(
            intent=intent,
            message=f"Searching for '{intent.item}'. Check the search results below.",
        )

    return VoiceCommandResult(intent=intent, message="Something unexpected happened.")
