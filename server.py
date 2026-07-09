from fastmcp import FastMCP
from menu import get_menu

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
    arguments. Takes no arguments.
    
    """
    
    items = get_menu()
    return [
        {"id": item.id, "name": item.name, "price": str(item.price)}
        for item in items
    ]
    

if __name__ == "__main__":
    mcp.run()