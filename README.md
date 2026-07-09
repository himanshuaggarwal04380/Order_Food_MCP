**Design principle:** business logic (`menu.py`) is kept fully independent of MCP wiring (`server.py`), so it can be tested in milliseconds without a running server or LLM.

## Menu Design

8 items, each with a unique `id`, `name`, and `price` (float, for now):

| ID | Name | Price |
|---|---|---|
| p1 | Margherita Pizza | 299 |
| p2 | Pepperoni Pizza | 349 |
| b1 | Veggie Burger | 349 |
| b2 | Chicken Burger | 129 |
| p3 | Farmhouse Pizza | 99 |
| dr1 | Cold Coffee | 69 |
| dr2 | Mango Shake | 79 |

## Testing Strategy

Tests in `test_menu.py` cover:
- Menu size is within the 5–10 item range
- Every item has valid id/name/price
- All IDs are unique
- Lookup by valid ID returns the correct item
- Lookup by invalid ID returns `None` (not an exception)

Run with:
```powershell
uv run pytest -v
```

## Status

- [x] Week 1: MCP fundamentals, hello-world server, local LLM verified
- [x] Week 2: Menu data model, mock data, lookup function, tests passing
- [ ] Week 3: `get_menu` MCP tool