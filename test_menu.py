from menu import MENU, get_menu, get_item_by_id
from decimal import Decimal


def test_menu_items_have_required_fields():
    """Every item must have a non-empty id, name, and a positive price."""
    for item in get_menu():
        assert item.id
        assert item.name
        assert isinstance(item.price, Decimal)
        assert item.price > 0


def test_menu_ids_are_unique():
    """No two items should share the same ID."""
    ids = [item.id for item in MENU]
    assert len(ids) == len(set(ids))


def test_get_item_by_id_found():
    """Looking up a real ID should return the matching item."""
    item = get_item_by_id("p1")
    assert item is not None
    assert item.name == "Margherita Pizza"


def test_get_item_by_id_not_found():
    """Looking up a fake ID should return None, not raise an error."""
    item = get_item_by_id("does-not-exist")
    assert item is None