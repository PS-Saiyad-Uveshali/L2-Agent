# Level 3 Migration to LiteLLM - Summary of Changes

## Date: February 14, 2026

## Overview
Migrated the Level 3 implementation from **Anthropic Claude API** to **LiteLLM Proxy** with **DeepInfra models** (Qwen series).

---

## Files Modified

### 1. **config.py**
**Changes:**
- Changed `ANTHROPIC_API_KEY` → `DEEPINFRA_API_KEY`
- Added `LITELLM_BASE_URL` = `"https://litellm-api.predev.praveg.ai/v1"`
- Changed `MODEL_NAME` to `"deepinfra/Qwen/Qwen2.5-72B-Instruct"`
- Updated validation to check for `DEEPINFRA_API_KEY`

### 2. **agent.py**
**Changes:**
- Changed `from anthropic import Anthropic` → `from openai import OpenAI`
- Renamed class `ClaudeAgent` → `LiteLLMAgent`
- Updated client initialization:
  ```python
  self.client = OpenAI(
      api_key=self.api_key,
      base_url=AgentConfig.LITELLM_BASE_URL
  )
  ```
- Changed `get_tool_definitions()` → `get_tool_definitions_openai_format()`
- **Completely rewrote agent loop:**
  - Changed from Anthropic's `messages.create()` format to OpenAI's `chat.completions.create()`
  - Added system message as first message (OpenAI format)
  - Changed tool calling handling from Anthropic format to OpenAI format
  - Updated tool results format to use `"tool"` role instead of Anthropic's format
- Updated interactive_mode() messages to show "LiteLLM Agent"

### 3. **tools.py**
**Changes:**
- **Added new method:** `get_tool_definitions_openai_format()`
  - Returns tools in OpenAI function calling format
  - Uses `"type": "function"` wrapper
  - Uses `"parameters"` instead of `"input_schema"`
- Kept original `get_tool_definitions()` method for reference

### 4. **requirements.txt**
**Changes:**
- Removed: `anthropic>=0.34.0`
- Added: `openai>=1.0.0`
- Added: `litellm>=1.0.0`
- Added: `python-dotenv>=1.0.0`

### 5. **.env.example**
**Changes:**
- Changed `ANTHROPIC_API_KEY` → `DEEPINFRA_API_KEY`

### 6. **.env**
**Updated:**
- Now contains `DEEPINFRA_API_KEY=sk-lf-...`

---

## Key Technical Differences

### Tool Definition Format

**Anthropic (Old):**
```python
{
    "name": "get_weather",
    "description": "...",
    "input_schema": {
        "type": "object",
        "properties": {...}
    }
}
```

**OpenAI/LiteLLM (New):**
```python
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "...",
        "parameters": {
            "type": "object",
            "properties": {...}
        }
    }
}
```

### Agent Loop

**Anthropic (Old):**
```python
response = client.messages.create(
    model=...,
    system=system_prompt,  # Separate parameter
    messages=[...],
    tools=[...]
)

if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            # Process tool
```

**OpenAI/LiteLLM (New):**
```python
messages = [
    {"role": "system", "content": system_prompt},  # In messages list
    {"role": "user", "content": ...}
]

response = client.chat.completions.create(
    model=...,
    messages=messages,
    tools=[...],
    tool_choice="auto"
)

if message.tool_calls:
    for tool_call in message.tool_calls:
        # Process tool
```

### Tool Result Format

**Anthropic (Old):**
```python
{
    "type": "tool_result",
    "tool_use_id": tool_use_id,
    "content": json.dumps(result)
}
```

**OpenAI/LiteLLM (New):**
```python
{
    "role": "tool",
    "tool_call_id": tool_call.id,
    "name": tool_name,
    "content": json.dumps(result)
}
```

---

## Available Models

Current configuration uses:
- **Primary:** `deepinfra/Qwen/Qwen2.5-72B-Instruct`

**Other available models from your LiteLLM proxy:**
- `deepinfra/Qwen/Qwen2.5-7B-Instruct` (smaller, faster)
- `deepinfra/Qwen/Qwen3-235B-A22B-Instruct-2507` (larger, more capable)
- `deepinfra/Qwen/Qwen3-235B-A22B-Thinking-2507` (reasoning model)
- `deepinfra/Qwen/Qwen3-Coder-480B-A35B-Instruct` (code-focused)
- And more...

---

## Testing

To test the new setup:

```powershell
cd Level-3
python agent.py
```

Try a query like:
```
Plan a Saturday in Paris at (48.8566, 2.3522). Get weather, recommend 2 mystery books, and give me a trivia question.
```

---

## Backup

Original Anthropic-based `agent.py` is saved as `agent.py.bak` for reference.

---

## Next Steps

1. ✅ Test the agent with your LiteLLM proxy
2. ✅ Verify all 5 tools work correctly
3. ⬜ Update Level-3/README.md with LiteLLM documentation
4. ⬜ Update test_agent.py if needed
5. ⬜ Update main README.md to reflect LiteLLM option

---

## Advantages of LiteLLM

1. **Unified Interface**: Use OpenAI SDK format with 100+ models
2. **Cost Effective**: DeepInfra often cheaper than Claude  
3. **Flexibility**: Easy to switch between models
4. **Tracing**: Works with Langfuse for observability
5. **Proxy Benefits**: Rate limiting, caching, load balancing

---

## Notes

- LiteLLM proxy URL: `https://litellm-api.predev.praveg.ai/v1`
- Authentication uses DeepInfra API key
- Function calling support varies by model (Qwen models generally good)
- Some models may need additional configuration
