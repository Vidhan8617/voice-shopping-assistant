"""
NLU (Natural Language Understanding) service.

Design: two-layer parsing.

  1. Rule-based parser tries first. It's instant, free, and handles the
     large majority of realistic phrasing ("add milk", "remove bananas",
     "I need 2 bottles of water"). Regex over raw ML for this is a
     deliberate choice: predictable, debuggable, zero latency, zero cost.

  2. If rules can't confidently extract an action+item, we fall back to an
     LLM call (Groq, free tier) that returns strict JSON. This is what
     gives us genuine flexibility for phrasing rules didn't anticipate,
     and multilingual support (the LLM handles translation implicitly).

  If the LLM call fails (no API key, network issue, quota hit) we degrade
  gracefully to an "unknown" intent rather than crashing the request —
  this is the "basic error handling" the assignment asks for, applied to
  the riskiest external dependency in the system.
"""
import json
import re

from app.core.config import get_settings
from app.schemas.schemas import ParsedIntent

settings = get_settings()

try:
    from groq import Groq
    _groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
except Exception:
    _groq_client = None

# Number words -> digits, so "add two apples" works as well as "add 2 apples"
_WORD_NUMBERS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

_ADD_PATTERNS = [
    r"^add\s+(?:(\d+|\w+)\s+)?(.+)$",
    r"^i\s+(?:want|need)\s+(?:to\s+buy\s+)?(?:(\d+|\w+)\s+)?(.+)$",
    r"^(?:buy|get|put)\s+(?:(\d+|\w+)\s+)?(.+?)(?:\s+on\s+my\s+list|\s+to\s+my\s+list)?$",
]
_REMOVE_PATTERNS = [
    r"^remove\s+(.+?)(?:\s+from\s+my\s+list)?$",
    r"^delete\s+(.+?)(?:\s+from\s+my\s+list)?$",
    r"^take\s+off\s+(.+)$",
]
_SEARCH_PATTERNS = [
    r"^find\s+(?:me\s+)?(.+)$",
    r"^search\s+(?:for\s+)?(.+)$",
]

# Trailing unit words we strip off the item name once quantity is captured,
# e.g. "2 bottles of water" -> qty=2, unit="bottles", item="water"
_UNIT_PATTERN = re.compile(
    r"^(bottles?|cans?|kg|kilograms?|grams?|g|packs?|packets?|boxes?|dozens?)\s+of\s+(.+)$",
    re.IGNORECASE,
)


def _extract_quantity(raw: str | None) -> int:
    if raw is None:
        return 1
    if raw.isdigit():
        return int(raw)
    return _WORD_NUMBERS.get(raw.lower(), 1)


def _split_quantity_unit_item(qty_raw: str | None, rest: str) -> tuple[int, str | None, str]:
    quantity = _extract_quantity(qty_raw)
    rest = rest.strip()
    unit_match = _UNIT_PATTERN.match(rest)
    if unit_match:
        return quantity, unit_match.group(1), unit_match.group(2).strip()
    return quantity, None, rest


def parse_with_rules(transcript: str) -> ParsedIntent | None:
    """Try fast rule-based matching. Returns None if nothing matched confidently."""
    text = transcript.strip().lower()
    text = re.sub(r"[.!?]+$", "", text)  # strip trailing punctuation

    for pattern in _ADD_PATTERNS:
        m = re.match(pattern, text)
        if m:
            qty_raw, rest = m.group(1), m.group(2)
            quantity, unit, item = _split_quantity_unit_item(qty_raw, rest)
            if item:
                return ParsedIntent(
                    action="add", item=item, quantity=quantity, unit=unit,
                    confidence=0.9, source="rules",
                )

    for pattern in _REMOVE_PATTERNS:
        m = re.match(pattern, text)
        if m:
            item = m.group(1).strip()
            if item:
                return ParsedIntent(action="remove", item=item, confidence=0.9, source="rules")

    for pattern in _SEARCH_PATTERNS:
        m = re.match(pattern, text)
        if m:
            item = m.group(1).strip()
            if item:
                return ParsedIntent(action="search", item=item, confidence=0.85, source="rules")

    return None


_LLM_SYSTEM_PROMPT = """You are an intent parser for a voice shopping assistant.
Given a user's spoken command (which may be in any language), extract the shopping intent.

Respond with ONLY valid JSON, no markdown, no explanation, in this exact shape:
{"action": "add" | "remove" | "search" | "unknown", "item": "<item name in English, singular, lowercase, or null>", "quantity": <integer, default 1>, "unit": "<unit like 'bottles', 'kg', or null>"}

Rules:
- Translate the item name to English.
- If the command doesn't clearly map to add/remove/search a shopping item, use action "unknown".
- quantity is always an integer, default 1 if not specified.
"""


def parse_with_llm(transcript: str, language: str) -> ParsedIntent:
    """
    LLM fallback for phrasing the rule-based parser can't handle, and for
    non-English input. Degrades to an 'unknown' intent on any failure so a
    flaky external API never crashes the request.
    """
    if _groq_client is None:
        return ParsedIntent(action="unknown", confidence=0.0, source="llm")

    try:
        response = _groq_client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": _LLM_SYSTEM_PROMPT},
                {"role": "user", "content": f"Language: {language}\nCommand: {transcript}"},
            ],
            temperature=0,
            max_tokens=150,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*|\s*```$", "", raw.strip())
        data = json.loads(raw)

        action = data.get("action", "unknown")
        if action not in ("add", "remove", "search", "unknown"):
            action = "unknown"

        return ParsedIntent(
            action=action,
            item=data.get("item"),
            quantity=int(data.get("quantity") or 1),
            unit=data.get("unit"),
            confidence=0.75 if action != "unknown" else 0.0,
            source="llm",
        )
    except Exception:
        # Any failure (network, bad JSON, quota) -> safe fallback, never raise
        return ParsedIntent(action="unknown", confidence=0.0, source="llm")


def parse_voice_command(transcript: str, language: str = "en") -> ParsedIntent:
    """
    Public entrypoint: rules first, LLM fallback second.
    Non-English input skips straight to the LLM since our regex rules are
    English-only by design (documented trade-off, see README).
    """
    if language.lower().startswith("en"):
        rule_result = parse_with_rules(transcript)
        if rule_result is not None:
            return rule_result

    return parse_with_llm(transcript, language)
