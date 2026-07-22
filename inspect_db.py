import sqlite3

conn = sqlite3.connect("cafe.db")
conn.row_factory = sqlite3.Row

print("=" * 60)
print("TABLES IN DATABASE")
print("=" * 60)
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()
for t in tables:
    print(f"  - {t['name']}")

print()
print("=" * 60)
print("MENU TABLE")
print("=" * 60)
count = conn.execute("SELECT COUNT(*) as c FROM menu").fetchone()["c"]
print(f"Total menu items: {count}")

print()
print("=" * 60)
print("ORDERS TABLE")
print("=" * 60)
orders = conn.execute("SELECT * FROM orders ORDER BY order_id").fetchall()
print(f"Total orders: {len(orders)}")
for o in orders:
    print(dict(o))

print()
print("=" * 60)
print("ORDER_LINES TABLE")
print("=" * 60)
lines = conn.execute("SELECT * FROM order_lines ORDER BY order_id, id").fetchall()
print(f"Total order lines: {len(lines)}")
for l in lines:
    print(dict(l))

conn.close()