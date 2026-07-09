import asyncio
from fastmcp import Client
from server import mcp


def test_get_menu_tool_works():
    async def run():
        async with Client(mcp) as client:
            result = await client.call_tool("get_menu_tool", {})
            assert len(result.data) == 7

    asyncio.run(run())