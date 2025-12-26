# test_all_tools.py
import asyncio
import sys
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_all_tools():
    """Test all tools from server_fun.py"""
    server_path = "server_fun.py"
    exit_stack = AsyncExitStack()
    
    # Connect to MCP server
    stdio = await exit_stack.enter_async_context(
        stdio_client(StdioServerParameters(command="python", args=[server_path]))
    )
    r_in, w_out = stdio
    session = await exit_stack.enter_async_context(ClientSession(r_in, w_out))
    await session.initialize()

    tools = (await session.list_tools()).tools
    print(f"✓ Connected to server. Found {len(tools)} tools:\n")
    
    try:
        # Test 1: get_weather
        print("1️⃣ Testing get_weather (New York)...")
        result = await session.call_tool("get_weather", {
            "latitude": 40.7128,
            "longitude": -74.0060
        })
        weather = result.content[0].text if result.content else "No data"
        print(f"   Result: {weather}\n")
        
        # Test 2: book_recs
        print("2️⃣ Testing book_recs (mystery, limit=2)...")
        result = await session.call_tool("book_recs", {
            "topic": "mystery",
            "limit": 2
        })
        books = result.content[0].text if result.content else "No data"
        print(f"   Result: {books}\n")
        
        # Test 3: random_joke
        print("3️⃣ Testing random_joke...")
        result = await session.call_tool("random_joke", {})
        joke = result.content[0].text if result.content else "No data"
        print(f"   Result: {joke}\n")
        
        # Test 4: random_dog
        print("4️⃣ Testing random_dog...")
        result = await session.call_tool("random_dog", {})
        dog = result.content[0].text if result.content else "No data"
        print(f"   Result: {dog}\n")
        
        # Test 5: trivia
        print("5️⃣ Testing trivia...")
        result = await session.call_tool("trivia", {})
        trivia_q = result.content[0].text if result.content else "No data"
        print(f"   Result: {trivia_q}\n")
        
        print("✅ All tools tested successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await exit_stack.aclose()

if __name__ == "__main__":
    asyncio.run(test_all_tools())
