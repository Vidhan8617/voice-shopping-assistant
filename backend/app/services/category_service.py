"""
Auto-categorization service.

Same pattern as NLU: cheap dictionary lookup first, LLM fallback for items
we don't recognize. Most shopping items are common enough that the static
map covers them instantly; the fallback exists so the app doesn't just dump
everything into "Other" the moment a user asks for something unusual.
"""
import json
import re

from app.core.config import get_settings
from app.core.constants import CATEGORY_MAP, DEFAULT_CATEGORY

settings = get_settings()

try:
    from groq import Groq
    _groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
except Exception:
    _groq_client = None

_VALID_CATEGORIES = [
    "Dairy", "Produce", "Bakery", "Snacks", "Beverages",
    "Meat & Seafood", "Pantry", "Personal Care", "Other",
]


def categorize(item_name: str) -> str:
    key = item_name.strip().lower()
    if key in CATEGORY_MAP:
        return CATEGORY_MAP[key]

    if _groq_client is not None:
        try:
            response = _groq_client.chat.completions.create(
                model=settings.groq_model,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Classify the grocery item '{item_name}' into exactly one of "
                        f"these categories: {', '.join(_VALID_CATEGORIES)}. "
                        f"Respond with only the category name, nothing else."
                    ),
                }],
                temperature=0,
                max_tokens=10,
            )
            guess = re.sub(r"[^\w\s&]", "", response.choices[0].message.content.strip())
            for cat in _VALID_CATEGORIES:
                if cat.lower() == guess.lower():
                    return cat
        except Exception:
            pass  # fall through to default — categorization is non-critical

    return DEFAULT_CATEGORY
