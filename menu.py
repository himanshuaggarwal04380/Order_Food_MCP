from dataclasses import dataclass


@dataclass
class MenuItem:
    """Represents a single item on the menu."""
    id: str
    name: str
    price: float


# Mock menu data — a plain list of MenuItem objects.
MENU: list[MenuItem] = [
    MenuItem(id="p1", name="Margherita Pizza", price=299),
    MenuItem(id="p2", name="Pepperoni Pizza", price=359),
    MenuItem(id="p3", name="Farmhouse Pizza", price=359),
    MenuItem(id="b1", name="Veggie Burger", price=99),
    MenuItem(id="b2", name="Chicken Burger", price=129),
    MenuItem(id="dr1", name="Cold Coffee", price=69),
    MenuItem(id="dr2", name="Mango Shake", price=79),
]


def get_menu() -> list[MenuItem]:
    """Return the full menu."""
    return MENU


def get_item_by_id(item_id: str) -> MenuItem | None:
    """Look up a single menu item by its ID. Returns None if not found."""
    for item in MENU:
        if item.id == item_id:
            return item
    return None