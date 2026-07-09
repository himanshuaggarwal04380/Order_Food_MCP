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
uv run pytest test_menu.py -v
```

## Status

- [done] Week 1: MCP fundamentals, hello-world server, local LLM verified
- [done] Week 2: Menu data model, mock data, lookup function, tests passing
- [done] Week 3: get_menu MCP tool, tests, live LLM demo (Claude Desktop)
- [ ] Week 4: Order logic (pricing, validation)

## Week 3 Demo

Verified `get_menu_tool` end-to-end in Claude Desktop: asked "What food can I order?" 
in natural language (no explicit tool mention), and the LLM correctly called 
`get_menu_tool` and returned the full 8-item menu in chat.

Also verified via MCP Inspector: tool discoverable, returns valid JSON with ( cmd - npx @modelcontextprotocol/inspector uv run server.py )
id/name/price for all 8 items.