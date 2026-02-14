# Level 3: Claude Agent SDK Implementation

## Overview

This is the **Level 3 implementation** of the L2 Wizard agent, refactored to use the **Claude Agent SDK** for production-grade, maintainable AI agent development. Unlike the Level 2 implementation which used MCP (Model Context Protocol) with Ollama/Mistral, this version leverages Claude's native API with structured tool calling.

## Why SDK Version?

### Level 2 Limitations
- **MCP + Ollama**: Required running a separate MCP server process
- **Local LLM**: `mistral:7b` struggled with multi-step reasoning (ReAct pattern)
- **Complex Setup**: Multiple processes, custom protocol handling
- **Less Reliable**: ReAct agent (`agent_fun.py`) was experimental and slow

### Level 3 Improvements
- ✅ **Production API**: Uses LiteLLM proxy with DeepInfra (reliable, fast)
- ✅ **Structured Tools**: OpenAI-compatible tool calling (deterministic, well-tested)
- ✅ **Clean Architecture**: Separated concerns (tools, config, agent logic)
- ✅ **Better Reasoning**: Qwen models handle complex multi-tool scenarios
- ✅ **Maintainable**: Clear agent loop, no custom protocols
- ✅ **Testable**: Included test harness with multiple scenarios
- ✅ **Streaming Support**: Real-time response streaming
- ✅ **Web Interface**: Beautiful Gradio UI for easy interaction

## Project Structure

```
Level-3/
├── agent.py           # Main agent with streaming support
├── web_app.py         # Gradio web interface
├── tools.py          # Structured tool definitions and registry
├── config.py         # Configuration management
├── test_agent.py     # Test harness with 5 scenarios
├── setup.py          # Automated setup script
├── requirements.txt  # Python dependencies (includes gradio)
├── .env.example      # Environment variable template
└── README.md         # This file
```

## Architecture

### 1. Tool Registry (`tools.py`)
- Self-contained tool implementations
- Claude-compatible tool schemas
- Centralized execution logic
- Same 5 tools as Level 2: weather, books, jokes, dogs, trivia

### 2. Agent Loop (`agent.py`)
```
1. User sends message → Claude
2. Claude analyzes & requests tools
3. Agent executes tools
4. Results sent back to Claude
5. Claude generates final response
   (or loops back to step 2)
```

### 3. Configuration (`config.py`)
- Environment variable management
- Model selection
- Timeout and retry settings
- Validation logic

## Setup

### Prerequisites
- Python 3.9+
- DeepInfra API key (or LiteLLM-compatible API access)

### Automated Setup

```bash
cd Level-3
python setup.py
```

This will:
1. Create virtual environment
2. Install dependencies
3. Verify configuration

### Manual Setup

```bash
cd Level-3

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set API key
$env:DEEPINFRA_API_KEY='your-key'  # Windows PowerShell
export DEEPINFRA_API_KEY='your-key'  # Linux/Mac
# Or add to .env file
```

## Running the Agent

### Option 1: Web Interface (Recommended)
```bash
python web_app.py
```

This launches a beautiful Gradio web interface at `http://localhost:7860` with:
- 🎨 Clean, modern UI
- ⚡ Real-time streaming responses
- 📋 Example queries
- 💬 Chat history
- 🔧 Easy configuration

**Command-line options:**
```bash
python web_app.py --port 8080          # Custom port
python web_app.py --share              # Create shareable public link
python web_app.py --host 127.0.0.1     # Custom host
```

### Option 2: Command-Line Interface
```bash
python agent.py
```

Example session:
```
🔷 You: Plan a Saturday in Paris at (48.8566, 2.3522). Get weather, 
       recommend 2 mystery books, and give me a trivia question.

🤖 Processing: Plan a Saturday in Paris at (48.8566, 2.3522)...

[Iteration 1]
📋 Claude requested tool calls
  → Calling get_weather with {'latitude': 48.8566, 'longitude': 2.3522}
    ✓ Success
  → Calling book_recs with {'topic': 'mystery', 'limit': 2}
    ✓ Success
  → Calling trivia with {}
    ✓ Success

[Iteration 2]
✓ Final answer provided

🎯 Agent: Great! Here's your Saturday plan for Paris:

🌤️ Weather: Currently 15.2°C (59.4°F) with light winds...
📚 Mystery Books:
  1. "The Da Vinci Code" by Dan Brown (2003)
  2. "Gone Girl" by Gillian Flynn (2012)
🎯 Trivia: In what year did World War II end?
  Answers: A) 1943  B) 1945  C) 1947  D) 1950
```

### Option 3: Programmatic Use

**Non-streaming:**
```python
from agent import LiteLLMAgent

agent = LiteLLMAgent(verbose=True)
response = agent.run("Tell me a joke and show a dog pic", stream=False)
print(response)
```

**Streaming (real-time):**
```python
from agent import LiteLLMAgent

agent = LiteLLMAgent(verbose=False)
for chunk in agent.run("What's the weather in Paris?", stream=True):
    print(chunk, end="", flush=True)
```

## Running Tests

```bash
python test_agent.py
```

The test harness runs 5 scenarios:
1. **Weather Query** - Basic single-tool test
2. **Book Recommendations** - Parameter handling
3. **Entertainment Package** - Multiple simple tools
4. **Complex Multi-Tool** - Level 2 core scenario
5. **Trivia Question** - Another single-tool test

Example output:
```
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪
L2 WIZARD - LEVEL 3 TEST HARNESS
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪

✓ Agent initialized with model: claude-3-5-sonnet-20241022

======================================================================
TEST: Weather Query
======================================================================
...
✅ TEST PASSED - Agent completed successfully

======================================================================
TEST SUMMARY
======================================================================
Total Tests: 5
✅ Passed: 5
❌ Failed: 0
Success Rate: 100.0%

🎉 ALL TESTS PASSED!
```

## What Changed from Level 2?

| Aspect | Level 2 | Level 3 |
|--------|---------|---------|
| **LLM** | Ollama (local mistral:7b) | LiteLLM + DeepInfra (Qwen) |
| **Protocol** | MCP (stdio server) | Direct API calls |
| **Tool Calling** | Custom MCP tools | OpenAI-compatible tools |
| **Agent Pattern** | ReAct (unreliable) + Simple | Clean SDK loop |
| **Architecture** | Monolithic scripts | Separated concerns |
| **Configuration** | Hardcoded | Centralized config |
| **Testing** | Manual `test_all_tools.py` | Structured test harness |
| **Dependencies** | mcp, fastmcp, ollama | openai, litellm, gradio |
| **Streaming** | ❌ No | ✅ Yes |
| **Web UI** | ❌ No | ✅ Gradio interface |

## Tool Permissions

All tools connect to **public, free APIs**:
- ✅ No authentication required
- ✅ No API keys needed (except DeepInfra for LLM)
- ✅ Rate limits exist but are generous
- ✅ All tools are read-only

### Tool Details
| Tool | API | Capability |
|------|-----|------------|
| `get_weather` | Open-Meteo | Current weather for coords |
| `book_recs` | Google Books | Book search by topic |
| `random_joke` | JokeAPI | Safe jokes |
| `random_dog` | Dog CEO | Random dog images |
| `trivia` | Open Trivia DB | Multiple-choice questions |

## Known Limitations

1. **API Key Required**: Must have DeepInfra/LiteLLM API key
2. **Internet Required**: All tools need external API access
3. **Coordinates Manual**: Weather requires lat/long (no city→coords conversion)
4. **No State Persistence**: Each run is independent (no memory between sessions)
5. **Rate Limits**: External APIs may throttle heavy usage
6. **English Only**: Book search and trivia are English-centric
7. **Model Specific**: Function calling quality depends on model (Qwen works well)

## Context Management

### Persisted Within a Run
- ✅ Full conversation history (user messages + tool results)
- ✅ Tool call history
- ✅ Claude's reasoning chain

### NOT Persisted Between Runs
- ❌ Previous conversations
- ❌ User preferences
- ❌ Tool call statistics
- ❌ Cached results

Each `agent.run()` call starts fresh. To add persistence, you would need to:
- Store conversation history in a database
- Implement session management
- Add caching layer for tool results

## How to Run Each Version

### Level 2 (Original)
```bash
cd ..  # Back to repository root

# Option 1: Simple orchestrator (recommended)
python agent_simple.py

# Option 2: ReAct agent (experimental)
python agent_fun.py

# Prerequisites: Ollama + mistral:7b model
ollama pull mistral:7b
```

### Level 3 (SDK)
```bash
cd Level-3

# Activate environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Set API key
export DEEPINFRA_API_KEY='your-key'

# Run web interface
python web_app.py

# Or run CLI
python agent.py

# Run tests
python test_agent.py
```

## Migration Guide

If you want to migrate your own Level 2 agent:

1. **Extract Tools**: Move tool logic to separate `tools.py` with schemas
2. **Create Config**: Centralize settings in `config.py`
3. **Implement Loop**: Use Claude's tool calling API pattern
4. **Add Tests**: Create test scenarios covering key use cases
5. **Document**: Explain why SDK, what changed, how to run

Key SDK concepts:
- **Tool Schemas**: Describe tools in Claude format
- **Tool Results**: Return JSON strings to Claude
- **Stop Reasons**: Handle `tool_use` vs `end_turn`
- **Message History**: Maintain conversation state

## Troubleshooting

### "DEEPINFRA_API_KEY is required"
```powershell
# Set the environment variable
$env:DEEPINFRA_API_KEY='your-key-here'
# Or add to .env file:
# DEEPINFRA_API_KEY=your-key-here
```

### "Module not found"
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate  # Windows
# Then reinstall
pip install -r requirements.txt
```

### API Rate Limits
- LiteLLM/DeepInfra have usage limits
- The agent handles errors gracefully
- Monitor usage via your LiteLLM dashboard

### Web Interface Not Loading
```bash
# Install gradio if missing
pip install gradio>=4.0.0

# Check if port is already in use
python web_app.py --port 8080
```

### Tool Failures
- Check internet connection
- External APIs may have downtime
- Agent handles tool errors gracefully

## Future Enhancements

- [x] **Streaming responses** - ✅ Implemented with real-time output
- [x] **Web interface** - ✅ Implemented with Gradio
- [ ] **Memory/context** - Store conversation history across sessions
- [ ] **Async tools** - Parallel execution for faster responses
- [ ] **City→coords** - Geocoding API integration
- [ ] **Voice input** - Speech-to-text for web UI
- [ ] **Export chat** - Download conversation history
- [ ] **Logging** - Structured logging to files
- [ ] **Metrics** - Track tool usage, latency
- [ ] **Caching** - Avoid redundant API calls
- [ ] **Multi-language** - Support for non-English queries

## License

MIT (same as Level 2)

## Contributing

See main repository README.

---

## Screenshots

### Web Interface
![Gradio Interface](https://via.placeholder.com/800x450?text=Gradio+Web+Interface)

*The web interface provides a modern, user-friendly way to interact with the agent.*

---

Built with [LiteLLM](https://litellm.ai/) + [DeepInfra](https://deepinfra.com/) + [Gradio](https://gradio.app/)
