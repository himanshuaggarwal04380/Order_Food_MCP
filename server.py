from fastmcp import FastMCP
from menu import get_menu
from order import place_order, OrderLineItem, OrderError

mcp = FastMCP("FoodOrderServer")


@mcp.tool
def get_menu_tool() -> list[dict]:
    """
    Return the full food menu.

    Use this tool whenever the user asks what's available to order, what
    food items exist, what the prices are, or expresses general intent to
    order food without specifying particular items yet (e.g. "I want to
    order something", "I'm hungry", "what can I get"). Showing the menu
    is the natural first step before an order can be placed. Takes no
    arguments.
    """
    items = get_menu()
    return [
        {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "description": item.description,
            "price": str(item.price),
            "is_veg": item.is_veg,
        }
        for item in items
    ]


@mcp.tool
def place_order_tool(items: list[dict]) -> dict:
    """
    Place a food order and return a structured invoice.

    Call this after the user has confirmed what they want to order.
    'items' must be a list of objects, each with:
      - item_id (string): the menu item's ID, from get_menu_tool
      - quantity (integer): how many of that item, must be positive

    Example: [{"item_id": "PZ01", "quantity": 2}, {"item_id": "HB10", "quantity": 1}]

    Returns a structured invoice with per-line breakdown, subtotal, tax,
    delivery fee, and grand total. Format the result as a clean, monospace
    text invoice for the user — do not just describe it in prose.

    If any item_id is invalid or a quantity is not positive, this tool
    returns an error message instead of an invoice — relay that message
    to the user clearly so they can correct their order.
    """
    try:
        line_items = [
            OrderLineItem(item_id=i["item_id"], quantity=i["quantity"])
            for i in items
        ]
        invoice = place_order(line_items)
    except OrderError as e:
        return {"error": str(e)}
    except (KeyError, TypeError) as e:
        return {"error": f"Malformed order input: {e}"}

    return {
        "order_id": invoice.order_id,
        "order_date": str(invoice.order_date),
        "lines": [
            {
                "name": line.name,
                "quantity": line.quantity,
                "unit_price": str(line.unit_price),
                "line_total": str(line.line_total),
            }
            for line in invoice.lines
        ],
        "subtotal": str(invoice.subtotal),
        "tax_rate": str(invoice.tax_rate),
        "tax_amount": str(invoice.tax_amount),
        "delivery_fee": str(invoice.delivery_fee),
        "total": str(invoice.total),
    }


if __name__ == "__main__":
    mcp.run()