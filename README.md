# Bean & Leaf Café — Food Order MCP Server

A local MCP server for a mock cafe ordering system. Built as part of an 8-week MCP internship assignment. Exposes two MCP tools — `get_menu_tool` and `place_order_tool` — backed by a real SQLite database, usable from any MCP-compatible chat client with a local LLM.

## Tech Stack & Reasoning

- **Language: Python** — fast iteration, and I already had a working Python/FastMCP/Ollama pipeline from the Week 1 orientation project.
- **MCP library: FastMCP** — minimal boilerplate; auto-generates JSON Schema from type hints, which matters for this project's strict schema requirement.
- **Local LLM: Ollama + Llama 3.1** — verified tool-calling capable in Week 1.
- **Database: SQLite** — a full SQL database that lives in a single file, no separate server process to run. Fits a local, no-infrastructure project. Accessed via Python's built-in `sqlite3` module, no extra dependency.
- **Testing: pytest** — standard Python test runner.
- **Currency: INR (₹)** — adapted from the assignment's USD example; documented explicitly throughout since it's a deliberate deviation from the brief's literal numbers.

## Project Structure

```
food-order-mcp/
├── menu.csv              # Source-of-truth menu data (editable, versioned in git)
├── cafe.db                 # SQLite database (generated, NOT committed to git)
├── db.py                    # Database connection, schema, seeding, persistence
├── menu.py                   # Business logic: menu queries (no MCP dependency)
├── order.py                   # Business logic: order calculation + validation
├── server.py                    # MCP wiring: tools exposed to the client
├── test_menu.py                  # Tests for menu.py
├── test_order.py                  # Tests for order.py
├── test_server.py                  # Tests for the MCP tool layer
├── inspect_db.py                    # Manual utility: dump full DB contents
├── reset_orders.py                   # Manual utility: clear orders/order_lines
└── README.md
```

**Layering principle (unchanged since Week 2):** business logic never depends on MCP, and MCP wiring never talks to the database directly. Each layer only calls the layer directly below it:

```
server.py  →  order.py / menu.py  →  db.py  →  cafe.db
```

This meant migrating from a hardcoded Python list to SQLite (see below) only required changing `menu.py` and `db.py` — nothing above them.

## Menu

**101 items across 11 categories**: Hot Beverages, Cold Beverages, Bakery & Pastries, Breakfast, Sandwiches & Wraps, Salads, Snacks & Sides, Desserts, Burgers, Pizza, Pasta.

Source data lives in `menu.csv` (columns: `item_id, name, category, description, price, is_veg`) — this is the file to hand-edit if the menu needs to change.

## Database Design

### Why SQLite over a hardcoded list
The original 7-item menu was a plain Python list. Per mentor direction, this was migrated to a real database so the menu can be edited without touching code, and so order history can persist across server restarts.

### Why money is stored as integer paise, not float or Decimal
SQLite has no native `Decimal` type — only `INTEGER`, `REAL`, `TEXT`, `BLOB`. Storing money as `REAL` reintroduces float rounding errors; storing it as `TEXT` prevents any numeric querying. The standard fix (used by real payment systems) is to store the smallest currency unit as an integer: ₹299.00 is stored as `29900`. Conversion to/from `Decimal` happens only at the boundary — in `menu.py` and `order.py` — matching the "convert at the boundary" principle already used at the MCP/JSON layer.

### Schema

```sql
CREATE TABLE menu (
    item_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    price_paise INTEGER NOT NULL,
    is_veg TEXT NOT NULL
);

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,
    subtotal_paise INTEGER NOT NULL,
    tax_amount_paise INTEGER NOT NULL,
    delivery_fee_paise INTEGER NOT NULL,
    total_paise INTEGER NOT NULL
);

CREATE TABLE order_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    item_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_paise INTEGER NOT NULL,
    line_total_paise INTEGER NOT NULL
);
```

`orders` and `order_lines` are a one-to-many relationship — one order, many line items — linked by the `order_id` foreign key, mirroring the in-memory `Invoice` / `list[InvoiceLine]` relationship already used in Python.

**Deliberate design choice — snapshotting, not referencing:** `order_lines` stores its own copy of `item_name` and `unit_price_paise` at the time of purchase, rather than only storing `item_id` and looking the price up from `menu` later. This is intentional: if a menu price changes after an order was placed, that order's historical invoice must still reflect what was actually charged at the time, not the current price.

### Seeding strategy: seed-once, not rebuild-every-startup
On startup, `init_db()` creates the schema if missing, then seeds the `menu` table from `menu.csv` **only if the table is currently empty**. On every subsequent startup, existing data is left untouched. This mirrors how production systems behave — the database, not the CSV, is the live source of truth after initial setup; the CSV is only the initial data dump. (The alternative — wiping and reloading from CSV on every restart — would also silently destroy order history stored in the same database, which is unsafe once real transactional data exists alongside the menu.)

### Order ID generation
Format: `YYYYMMDD-NNN` (e.g. `20260722-001`), sequential per day. Generated by querying how many orders already exist for today's date in the `orders` table and incrementing — this requires real persistence to work correctly, since a per-day sequence has no meaning without a durable count of what's already happened.

### Order persistence
`place_order()` (in `order.py`) calculates the invoice, generates the order ID, and calls `save_order()` (in `db.py`), which inserts one row into `orders` and one row per line into `order_lines`, wrapped in a single transaction — either the whole order is saved, or none of it is, preventing a half-written order (e.g. a header with no line items) if something fails mid-write.

## MCP Tools

### `get_menu_tool`
No arguments. Returns all 101 menu items (`id`, `name`, `category`, `description`, `price`, `is_veg`). Tool description explicitly covers both direct menu questions and vague ordering intent ("I want to order something") so the LLM routes both cases to showing the menu first.

### `place_order_tool`
Takes `items`: a list of `{item_id, quantity}` objects. Returns a structured invoice (order ID, date, per-line breakdown, subtotal, tax, delivery fee, total) or `{"error": "..."}` for invalid input (unknown item, bad quantity, empty order) — errors are returned as normal tool output, not raised exceptions, so the LLM can read and relay the message clearly instead of the tool call failing silently.

## Testing Strategy

- `test_menu.py` — menu size, required fields, unique IDs, lookup by ID (found/not found)
- `test_order.py` — a hand-verified **reference test case** (2× Margherita Pizza + 1× Masala Chai → ₹733.96 total), plus edge cases: unknown item, zero/negative quantity, empty order, unique order IDs across orders
- `test_server.py` — confirms both MCP tools are correctly wired and return expected shapes/values, independent of the deeper logic already covered above

Run with:
```powershell
uv run pytest -v
```

### Known issue, being addressed next
Tests that call `place_order()` currently write real rows into the production `cafe.db`, since nothing yet isolates test runs from the real database. This was discovered by inspecting the database directly and finding test-generated orders mixed in with manual test orders. Fix in progress: a `conftest.py` fixture that redirects all tests to a temporary, disposable database via `pytest`'s `monkeypatch` and `tmp_path` fixtures, combined with a one-time `reset_orders.py` cleanup of the polluted data already in `cafe.db`.

## Reference Test Case (hand-verified)

Order: 2× Margherita Pizza (`PZ01`, ₹249) + 1× Masala Chai (`HB10`, ₹89)

| | |
|---|---|
| Subtotal | ₹587.00 |
| Tax (8%) | ₹46.96 |
| Delivery Fee | ₹100.00 |
| **Total** | **₹733.96** |

Automated in `test_order.py::test_reference_order_case`.

## Live Demo Notes

Verified end-to-end via Claude Desktop with real natural-language prompts (not typed IDs):
- "What's on the menu?" → correctly triggers `get_menu_tool`
- "Two margherita pizzas and a masala chai" → correctly maps to `PZ01`×2, `HB10`×1, invoice matches the reference case exactly
- "A non-veg pizza and a drink, both of your choice" → correctly filtered the 101-item menu by dietary flag and category, chose BBQ Chicken Pizza + Cold Coffee, produced a correct ₹659.44 invoice
- "3 unicorn burgers" (invalid item) → correctly returned and relayed a clear error instead of crashing or hallucinating an item

## Deployment Notes (design-only — out of scope per assignment)

Although this project isn't deployed, the seed-once pattern was deliberately chosen to be deployment-safe: in a real deployment, code gets redeployed frequently while data must persist across those redeploys (e.g. a Docker volume, separate from the container's own filesystem). Checking "does data already exist?" before seeding — rather than unconditionally rebuilding from CSV on every startup — is the same pattern a production startup script would use, even though this project only ever runs locally.

## Status

- [x] Week 1: MCP fundamentals, hello-world server, local LLM verified
- [x] Week 2: Menu data model, mock data, lookup function, tests passing
- [x] Week 3: get_menu MCP tool, tests, live LLM demo (Claude Desktop)
- [x] Week 4: Order calculation logic, Decimal precision, validation, tests
- [x] Week 5: place_order MCP tool, live LLM demo including constraint-based ordering
- [x] Mentor-directed scope addition: full 101-item menu, SQLite migration, order persistence (orders/order_lines tables)
- [ ] Test isolation fix (conftest.py + database reset)
- [ ] Typesense fuzzy search exploration
- [ ] Week 6: Full end-to-end integration pass, README client setup guide, demo recording