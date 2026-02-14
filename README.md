# L2 Wizard - AI Agent Evolution 🎉

A multi-level AI agent project showcasing the evolution from MCP-based local agents (Level 2) to production-ready Claude SDK agents (Level 3).

## 📚 Project Evolution

This repository contains **two implementations** of the same agent capabilities:

- **Level 2**: Original MCP-based agent using Ollama/Mistral (local)
- **Level 3**: Refactored Claude SDK agent (production-ready)

Both provide the same five tools: weather, books, jokes, dogs, and trivia.

## 🚀 Features

- **Weather Information** - Get current weather for any coordinates
- **Book Recommendations** - Discover books by topic via Google Books API
- **Random Jokes** - Programming and general jokes from JokeAPI
- **Dog Pictures** - Random cute dog images from Dog CEO API
- **Trivia Questions** - Multiple-choice trivia from Open Trivia Database

## 📊 Level 2 vs Level 3 Comparison

| Feature | Level 2 (MCP) | Level 3 (SDK) |
|---------|---------------|---------------|
| **LLM** | Ollama (local mistral:7b) | Claude API (hosted) |
| **Architecture** | MCP stdio server + client | Direct API integration |
| **Tool Calling** | Custom MCP protocol | Native Claude tools |
| **Reliability** | Experimental (ReAct struggles) | Production-ready |
| **Setup** | Ollama + Python dependencies | Python + API key |
| **Cost** | Free (local) | Paid (Claude API) |
| **Performance** | Slow, limited reasoning | Fast, strong reasoning |
| **Maintenance** | Multiple processes | Single process |
| **Testing** | Basic tool tests | Comprehensive test harness |

**Recommendation**: Use **Level 3** for production. Use **Level 2** for learning MCP or offline development.

## 📁 Project Structure

```
l2-wizard/
├── Level-3/           # 🆕 SDK-based agent (production-ready)
│   ├── agent.py           # Main Claude SDK agent
│   ├── tools.py           # Structured tool definitions
│   ├── config.py          # Configuration management
│   ├── test_agent.py      # Test harness
│   ├── setup.py           # Automated setup
│   ├── requirements.txt   # Dependencies
│   └── README.md          # Level 3 documentation
├── server_fun.py      # Level 2: MCP server with 5 tools
├── agent_fun.py       # Level 2: ReAct-style agent (experimental)
├── agent_simple.py    # Level 2: Simple orchestrator (recommended)
├── test_all_tools.py  # Level 2: Tool testing script
└── README.md          # This file
```

## 🛠️ Quick Start

### Level 3 (Recommended - Production Ready)

```bash
cd Level-3
python setup.py
$env:ANTHROPIC_API_KEY='your-key-here'  # Windows PowerShell
python agent.py
```

📖 **See [Level-3/README.md](Level-3/README.md) for complete documentation**

### Level 2 (Learning/Offline)

```bash
# Install Ollama and pull model
ollama pull mistral:7b

# Install dependencies
pip install mcp fastmcp ollama requests

# Run agent
python agent_simple.py
```

---

## 🛠️ Setup

### Level 2 Setup (MCP + Ollama)

### Prerequisites

- Python 3.9+
- Ollama with `mistral:7b` model installed

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd l2-wizard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install mcp fastmcp ollama requests
   ```

4. **Install Ollama and pull model**
   ```bash
   ollama pull mistral:7b
   ```

## 🎮 Usage (Level 2)

### Option 1: Simple Agent (Recommended)

Fast, reliable agent that parses requests and calls tools directly:

```bash
python agent_simple.py
```

**Example:**
```
You: Plan a cozy Saturday in New York at (40.7128, -74.0060). 
     Include the current weather, 2 book ideas about mystery, one joke, and a dog pic.
```

### Option 2: ReAct Agent (Experimental)

LLM-driven agent using ReAct pattern (slower, less reliable):

```bash
python agent_fun.py
```

### Test All Tools

To verify all tools work correctly:

```bash
python test_all_tools.py
```

## 🔧 Available Tools

### 1. `get_weather`
Get current weather data for coordinates.

**Parameters:**
- `latitude` (float): Latitude coordinate
- `longitude` (float): Longitude coordinate

**Example:**
```json
{"latitude": 40.7128, "longitude": -74.0060}
```

### 2. `book_recs`
Get book recommendations by topic.

**Parameters:**
- `topic` (str): Search topic (e.g., "mystery", "science fiction")
- `limit` (int): Number of results (default: 5, max: 10)

**Example:**
```json
{"topic": "mystery", "limit": 2}
```

### 3. `random_joke`
Get a random safe joke.

**Parameters:** None

### 4. `random_dog`
Get a random dog image URL.

**Parameters:** None

### 5. `trivia`
Get a random trivia question with multiple-choice answers.

**Parameters:** None

## 📊 Architecture

### MCP Server (`server_fun.py`)
- Implements 5 tools using FastMCP
- Runs as a stdio server
- Each tool connects to external APIs

### Simple Agent (`agent_simple.py`)
1. Parses user request with regex
2. Identifies needed tools
3. Calls all tools in parallel/sequence
4. Uses LLM to synthesize friendly response

### ReAct Agent (`agent_fun.py`)
1. LLM decides which tool to call
2. Executes tool and adds result to history
3. LLM decides next action (loop)
4. Returns final answer when done

**Note:** ReAct approach struggles with `mistral:7b` for multi-step reasoning. Use `agent_simple.py` for better results.

## 🌐 External APIs Used

- **Weather**: [Open-Meteo](https://open-meteo.com/) - Free weather API
- **Books**: [Google Books API](https://developers.google.com/books) - No API key required
- **Jokes**: [JokeAPI](https://jokeapi.dev/) - Free joke API
- **Dogs**: [Dog CEO](https://dog.ceo/dog-api/) - Random dog pictures
- **Trivia**: [Open Trivia DB](https://opentdb.com/) - Free trivia questions

## 🐛 Troubleshooting

### "Model not found" error
```bash
ollama pull mistral:7b
```

### SSL Certificate errors
The code disables SSL verification for Open Library (previously used). Now using Google Books API which works properly.

### Agent gets stuck returning "None"
This is a known limitation of `mistral:7b` with the ReAct pattern. Use `agent_simple.py` instead.

### Slow responses
- Check your internet connection
- Verify Ollama is running
- Consider using a faster model like `llama3.1:8b`

## 📝 Example Queries

```
"What's the weather in Paris at (48.8566, 2.3522)?"

"Recommend 3 science fiction books"

"Tell me a joke and show me a dog pic"

"Give me a trivia question"

"Plan a weekend in Tokyo (35.6762, 139.6503) with weather, 2 mystery books, and a joke"
```

## 🚧 Known Limitations

### Level 2
1. **ReAct Agent**: `mistral:7b` struggles with multi-step tool calling
2. **Coordinates**: Weather requires manual coordinate input
3. **Book Search**: Limited to Google Books availability
4. **Rate Limits**: External APIs may have rate limits
5. **Local Model**: Requires Ollama installation

### Level 3
1. **API Cost**: Requires paid Anthropic API key
2. **Coordinates**: Weather still requires lat/long (no city→coords conversion)
3. **No Persistence**: Each run is independent (no memory between sessions)

## 🔄 Migration from Level 2 to Level 3

To understand the migration process and architecture changes:

1. **Read the comparison**: See `Level-3/README.md` for detailed differences
2. **Review architecture**: Compare `agent_simple.py` vs `Level-3/agent.py`
3. **Tool structure**: Compare `server_fun.py` vs `Level-3/tools.py`
4. **Run tests**: `python Level-3/test_agent.py` validates all scenarios

**Key Changes:**
- MCP server → Direct API calls
- Custom tool protocol → Claude native tools
- Ollama → Claude API
- Regex parsing → AI-driven tool selection
- Single script → Modular architecture

See [Level-3/README.md](Level-3/README.md) for complete migration guide.

## 🔮 Future Improvements

### Level 2
- [ ] Add city name → coordinates conversion
- [ ] Implement caching for repeated tool calls
- [ ] Better LLM model support (llama3.1:8b)
- [ ] Async parallel tool execution

### Level 3
- [ ] Streaming responses for real-time output
- [ ] Memory/context persistence across sessions
- [ ] City → coordinates geocoding
- [ ] Web UI interface (Gradio/Streamlit)
- [ ] Structured logging and metrics
- [ ] Result caching layer

### Both
- [ ] Add more tools (news, restaurants, movies)
- [ ] Enhanced error handling
- [ ] Multi-language support

## 📄 License

MIT

## 👥 Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

Built with [MCP](https://github.com/modelcontextprotocol/python-sdk) and [Ollama](https://ollama.ai/)
