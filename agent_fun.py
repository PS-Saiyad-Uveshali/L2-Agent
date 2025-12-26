# agent_fun.py
import asyncio, json, sys
from typing import Dict, Any, List
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from ollama import chat

SYSTEM = (
    "You are a helpful assistant that calls tools step-by-step to complete tasks.\n"
    "IMPORTANT: Call ONE tool at a time, wait for the result, then decide the next action.\n\n"
    "Process:\n"
    "1. If you need information from a tool, call it\n"
    "2. After receiving tool results, decide: call another tool OR give final answer\n"
    "3. Only use 'final' action when you have ALL needed information\n\n"
    "Examples:\n"
    'User: "What\'s the weather in NYC?"\n'
    'Step 1 - You: {"action":"get_weather","args":{"latitude":40.7,"longitude":-74.0}}\n'
    'Step 1 - Result: {"temperature":20,"wind_speed":10}\n'
    'Step 2 - You: {"action":"final","answer":"NYC weather: 20°C, wind 10 mph"}\n\n'
    "Rules:\n"
    "- Return ONLY valid JSON, no extra text\n"
    "- Call tool: {\"action\":\"tool_name\",\"args\":{...}}\n"
    "- Final answer: {\"action\":\"final\",\"answer\":\"...\"}\n"
)

def llm_json(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    resp = chat(model="mistral:7b", messages=messages, 
                format="json", options={"temperature": 0.1})
    txt = resp["message"]["content"].strip()
    
    try:
        return json.loads(txt)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parse failed: {e}")
        print(f"Raw output: {txt}")
        # Fallback
        return {"action": "final", "answer": "Error: Could not parse model response"}

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

    # Create system prompt with actual tool names and descriptions
    tool_desc = "\n".join([f"- {t.name}: {t.description}" for t in tools])
    system_with_tools = (
        SYSTEM + "\n\nAvailable tools:\n" + tool_desc + 
        "\n\nIMPORTANT: Use exact tool names. Return ONE action at a time."
    )
    history = [{"role": "system", "content": system_with_tools}]
    try:
        while True:
            user = input("\nYou: ").strip()
            if not user or user.lower() in {"exit","quit"}: break
            history.append({"role": "user", "content": user})

            for step in range(10):  # allow more steps for multiple tool calls
                decision = llm_json(history)
                action = decision.get('action')
                print(f"[Step {step+1}] Action: {action}")
                
                if action == "final":
                    answer = decision.get("answer","")
                    # Check if answer contains JSON (model didn't actually call tools)
                    if '{"action"' in answer or step == 0:
                        print("   ⚠️ Premature final - forcing tool call")
                        history.append({"role":"assistant","content": "I need to call tools first, not just describe them."})
                        continue
                    print("\nAgent:", answer)
                    history.append({"role":"assistant","content": answer})
                    break

                tname = action
                args = decision.get("args", {})
                if tname not in tool_index:
                    history.append({"role":"assistant","content": f"(unknown tool {tname})"})
                    print(f"   ⚠️ Unknown tool. Available: {list(tool_index.keys())}")
                    continue

                try:
                    result = await session.call_tool(tname, args)
                    payload = result.content[0].text if result.content else result.model_dump_json()
                    print(f"   ✓ Result: {payload[:100]}...")
                    history.append({"role":"assistant","content": f"[tool:{tname}] {payload}"})
                except Exception as e:
                    print(f"   ✗ Error: {e}")
                    history.append({"role":"assistant","content": f"[tool:{tname} failed: {str(e)}]"})
    finally:
        await exit_stack.aclose()

if __name__ == "__main__":
    asyncio.run(main())