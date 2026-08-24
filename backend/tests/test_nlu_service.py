"""
Tests for the rule-based NLU parser — the highest-risk, most-scrutinized
piece of logic in this app, so it gets the most test coverage.
"""
from app.services.nlu_service import parse_with_rules


def test_simple_add():
    result = parse_with_rules("add milk")
    assert result.action == "add"
    assert result.item == "milk"
    assert result.quantity == 1


def test_add_with_alternate_phrasing():
    result = parse_with_rules("I want to buy bananas")
    assert result.action == "add"
    assert result.item == "bananas"


def test_add_with_need_phrasing():
    result = parse_with_rules("I need apples")
    assert result.action == "add"
    assert result.item == "apples"


def test_add_with_quantity_and_unit():
    result = parse_with_rules("add 2 bottles of water")
    assert result.action == "add"
    assert result.item == "water"
    assert result.quantity == 2
    assert result.unit == "bottles"


def test_add_with_word_number():
    result = parse_with_rules("add two apples")
    assert result.action == "add"
    assert result.quantity == 2
    assert result.item == "apples"


def test_remove_simple():
    result = parse_with_rules("remove milk from my list")
    assert result.action == "remove"
    assert result.item == "milk"


def test_remove_delete_phrasing():
    result = parse_with_rules("delete bananas")
    assert result.action == "remove"
    assert result.item == "bananas"


def test_search_find():
    result = parse_with_rules("find me organic apples")
    assert result.action == "search"
    assert "apples" in result.item


def test_unrecognized_phrase_returns_none():
    # Rules should NOT force a match on nonsense input — that's what the
    # LLM fallback exists for.
    result = parse_with_rules("what's the weather like today")
    assert result is None


def test_empty_string_returns_none():
    result = parse_with_rules("")
    assert result is None
