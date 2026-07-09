from fastmcp import FastMCP
from menu import get_menu

mcp = FastMCP("FoodOrderServer")


@mcp.tool
def get_menu_tool() -> list[dict]:
    """
    Return the full food menu.

    Use this tool whenever the user asks what's available to order,
    what food items exist, or what the prices are. Takes no arguments.
    """
    items = get_menu()
    return [
        {"id": item.id, "name": item.name, "price": item.price}
        for item in items
    ]


if __name__ == "__main__":
    mcp.run()