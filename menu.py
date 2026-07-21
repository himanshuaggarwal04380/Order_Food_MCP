from dataclasses import dataclass
from decimal import Decimal

from db import get_connection, init_db


@dataclass
class MenuItem:
    """Represents a single item on the menu."""
    id: str
    name: str
    category: str
    description: str
    price: Decimal
    is_veg: str


def _row_to_menu_item(row) -> MenuItem:
    """Convert a SQLite row (price stored in paise) into a MenuItem (price in rupees)."""
    return MenuItem(
        id=row["item_id"],
        name=row["name"],
        category=row["category"],
        description=row["description"],
        price=Decimal(row["price_paise"]) / 100,
        is_veg=row["is_veg"],
    )


def get_menu() -> list[MenuItem]:
    """Return the full menu from the database."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM menu ORDER BY category, name").fetchall()
    conn.close()
    return [_row_to_menu_item(r) for r in rows]


def get_item_by_id(item_id: str) -> MenuItem | None:
    """Look up a single menu item by its ID. Returns None if not found."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM menu WHERE item_id = ?", (item_id,)
    ).fetchone()
    conn.close()
    return _row_to_menu_item(row) if row else None


# Ensure the database exists and is seeded, the moment this module is imported.
init_db()