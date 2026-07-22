import sqlite3
import csv
from pathlib import Path
from decimal import Decimal

DB_PATH = Path(__file__).parent / "cafe.db"
CSV_PATH = Path(__file__).parent / "menu.csv"


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            order_date TEXT NOT NULL,
            subtotal_paise INTEGER NOT NULL,
            tax_amount_paise INTEGER NOT NULL,
            delivery_fee_paise INTEGER NOT NULL,
            total_paise INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL REFERENCES orders(order_id),
            item_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price_paise INTEGER NOT NULL,
            line_total_paise INTEGER NOT NULL
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
                r["item_id"], r["name"], r["category"], r["description"],
                int(Decimal(r["price"]) * 100), r["is_veg"],
            )
            for r in reader
        ]
    conn.executemany(
        "INSERT INTO menu (item_id, name, category, description, price_paise, is_veg) VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"Seeded {len(rows)} menu items into the database.")


def init_db() -> None:
    """Ensure DB/schema exist, seed menu from CSV only if empty. Safe to call every startup."""
    conn = get_connection()
    _create_schema(conn)
    if _menu_table_is_empty(conn):
        _seed_from_csv(conn)
    conn.close()


def generate_order_id(order_date_str: str) -> str:
    """
    Generate a sequential, human-readable order ID like '20260720-001'.
    Sequence resets daily, based on how many orders already exist for that date.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as count FROM orders WHERE order_date = ?", (order_date_str,)
    ).fetchone()
    conn.close()
    seq = row["count"] + 1
    compact_date = order_date_str.replace("-", "")
    return f"{compact_date}-{seq:03d}"


def save_order(invoice) -> None:
    """
    Persist a completed Invoice: one row in `orders`, one row per line in
    `order_lines`. Wrapped in a transaction — either everything is saved,
    or nothing is, so an order can never end up half-written.
    """
    conn = get_connection()
    try:
        with conn:  # `with conn` = transaction: commits on success, rolls back on any error
            conn.execute(
                """
                INSERT INTO orders
                    (order_id, order_date, subtotal_paise, tax_amount_paise, delivery_fee_paise, total_paise)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice.order_id,
                    str(invoice.order_date),
                    int(invoice.subtotal * 100),
                    int(invoice.tax_amount * 100),
                    int(invoice.delivery_fee * 100),
                    int(invoice.total * 100),
                ),
            )
            for line in invoice.lines:
                conn.execute(
                    """
                    INSERT INTO order_lines
                        (order_id, item_id, item_name, quantity, unit_price_paise, line_total_paise)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        invoice.order_id,
                        line.item_id,
                        line.name,
                        line.quantity,
                        int(line.unit_price * 100),
                        int(line.line_total * 100),
                    ),
                )
    finally:
        conn.close()