# agent_simple.py - Simpler approach with direct tool orchestration
import asyncio, json, sys, re
from typing import Dict, Any, List
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from ollama import chat

async def main():
    server_path = sys.argv[1] if len(sys.argv) > 1 else "server_fun.py"
    exit_stack = AsyncExitStack()
    stdio = await exit_stack.enter_async_context(
        stdio_client(StdioServerParameters(command="python", args=[server_path]))
    )
    r_in, w_out = stdio
    session = await exit_stack.enter_async_context(ClientSession(r_in, w_out))
    await session.initialize()

    tools = (await session.list_tools()).tools
    tool_index = {t.name: t for t in tools}
    print("Connected tools:", list(tool_index.keys()))

    try:
        while True:
            user = input("\n🔷 You: ").strip()
            if not user or user.lower() in {"exit","quit"}: break
            
            # Parse user request to identify needed tools
            print("\n🤖 Analyzing request...")
            
            tool_calls = []
            results = {}
            
            # Check for weather request
            coord_match = re.search(r'\(?\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)?', user)
            if 'weather' in user.lower() and coord_match:
                lat, lon = float(coord_match.group(1)), float(coord_match.group(2))
                tool_calls.append(('get_weather', {'latitude': lat, 'longitude': lon}))
            
            # Check for book request
            book_match = re.search(r'(\d+)\s+book|book.*?(\d+)', user.lower())
            if 'book' in user.lower():
                limit = 2
                if book_match:
                    limit = int(book_match.group(1) or book_match.group(2))
                topic = 'mystery' if 'mystery' in user.lower() else 'fiction'
                tool_calls.append(('book_recs', {'topic': topic, 'limit': limit}))
            
            # Check for joke
            if 'joke' in user.lower():
                tool_calls.append(('random_joke', {}))
            
            # Check for dog pic
            if 'dog' in user.lower():
                tool_calls.append(('random_dog', {}))
            
            # Check for trivia
            if 'trivia' in user.lower() or 'question' in user.lower():
                tool_calls.append(('trivia', {}))
            
            if not tool_calls:
                print("❌ No tools identified. Try mentioning: weather, books, joke, dog, or trivia")
                continue
            
            print(f"📋 Calling {len(tool_calls)} tools: {[t[0] for t in tool_calls]}\n")
            
            # Execute all tool calls
            for i, (tname, args) in enumerate(tool_calls, 1):
                try:
                    print(f"[{i}/{len(tool_calls)}] Calling {tname}...")
                    result = await session.call_tool(tname, args)
                    payload = result.content[0].text if result.content else result.model_dump_json()
                    results[tname] = json.loads(payload) if payload.startswith('{') else payload
                    print(f"   ✓ Success")
                except Exception as e:
                    print(f"   ✗ Failed: {e}")
                    results[tname] = {"error": str(e)}
            
            # Synthesize response with LLM
            print("\n💭 Generating response...\n")
            
            results_text = "\n".join([f"- {k}: {json.dumps(v, indent=2)}" for k, v in results.items()])
            
            prompt = (
                f"User asked: {user}\n\n"
                f"Tool results:\n{results_text}\n\n"
                "Create a friendly, complete response incorporating all the information above. "
                "Format weather in Celsius and Fahrenheit. Present book titles with authors. "
                "Make it conversational and helpful."
            )
            
            response = chat(
                model="mistral:7b",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates friendly responses from tool results."},
                    {"role": "user", "content": prompt}
                ],
                options={"temperature": 0.7}
            )
            
            answer = response["message"]["content"]
            print(f"🎯 Agent: {answer}\n")
            
    finally:
        await exit_stack.aclose()

if __name__ == "__main__":
    asyncio.run(main())
