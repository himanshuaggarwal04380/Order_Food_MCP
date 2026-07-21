from decimal import Decimal
from menu import get_menu, get_item_by_id


def test_menu_has_items():
    menu = get_menu()
    assert len(menu) == 101


def test_menu_items_have_required_fields():
    for item in get_menu():
        assert item.id
        assert item.name
        assert item.category
        assert isinstance(item.price, Decimal)
        assert item.price > 0
        assert item.is_veg in ("Veg", "Non-Veg")


def test_menu_ids_are_unique():
    menu = get_menu()
    ids = [item.id for item in menu]
    assert len(ids) == len(set(ids))


def test_get_item_by_id_found():
    item = get_item_by_id("HB01")
    assert item is not None
    assert item.name == "Espresso"


def test_get_item_by_id_not_found():
    item = get_item_by_id("does-not-exist")
    assert item is None