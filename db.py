import sqlite3
import csv
from pathlib import Path
from decimal import Decimal

DB_PATH = Path(__file__).parent / "cafe.db"
CSV_PATH = Path(__file__).parent / "menu.csv"


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name
    return conn


def _create_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            item_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            price_paise INTEGER NOT NULL,
            is_veg TEXT NOT NULL
        )
    """)
    conn.commit()


def _menu_table_is_empty(conn: sqlite3.Connection) -> bool:
    row = conn.execute("SELECT COUNT(*) as count FROM menu").fetchone()
    return row["count"] == 0


def _seed_from_csv(conn: sqlite3.Connection) -> None:
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                r["item_id"],
                r["name"],
                r["category"],
                r["description"],
                int(Decimal(r["price"]) * 100),  # rupees -> paise
                r["is_veg"],
            )
            for r in reader
        ]

    conn.executemany(
        """
        INSERT INTO menu (item_id, name, category, description, price_paise, is_veg)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    print(f"Seeded {len(rows)} menu items into the database.")


def init_db() -> None:
    """
    Ensure the database and schema exist, and seed from CSV only if the
    menu table is currently empty. Safe to call on every server startup.
    """
    conn = get_connection()
    _create_schema(conn)
    if _menu_table_is_empty(conn):
        _seed_from_csv(conn)
    else:
        print("Menu table already has data — skipping seed.")
    conn.close()