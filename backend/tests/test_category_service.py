from app.services.category_service import categorize


def test_known_dairy_item():
    assert categorize("milk") == "Dairy"


def test_known_produce_item():
    assert categorize("apple") == "Produce"


def test_case_insensitive():
    assert categorize("MILK") == "Dairy"


def test_unknown_item_falls_back_to_other():
    # No Groq key set in test env -> should degrade to "Other", not crash
    result = categorize("totally_made_up_item_xyz")
    assert result in ("Other",)  # LLM fallback disabled without API key
