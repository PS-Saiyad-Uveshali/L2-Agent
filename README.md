# L2 Wizard - MCP Agent with Fun Tools 🎉

An AI agent system built with the Model Context Protocol (MCP) that connects to multiple fun APIs to help plan activities, get information, and entertain you.

## 🚀 Features

- **Weather Information** - Get current weather for any coordinates
- **Book Recommendations** - Discover books by topic via Google Books API
- **Random Jokes** - Programming and general jokes from JokeAPI
- **Dog Pictures** - Random cute dog images from Dog CEO API
- **Trivia Questions** - Multiple-choice trivia from Open Trivia Database

## 📁 Project Structure

```
l2-wizard/
├── server_fun.py      # MCP server with 5 tool implementations
├── agent_fun.py       # ReAct-style agent (experimental, slower)
├── agent_simple.py    # Simple orchestrator (recommended, fast)
├── test_all_tools.py  # Tool testing script
└── README.md          # This file
```

## 🛠️ Setup

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

## 🎮 Usage

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

1. **ReAct Agent**: `mistral:7b` struggles with multi-step tool calling
2. **Coordinates**: Weather requires manual coordinate input
3. **Book Search**: Limited to Google Books availability
4. **Rate Limits**: External APIs may have rate limits

## 🔮 Future Improvements

- [ ] Add city name → coordinates conversion
- [ ] Implement caching for repeated tool calls
- [ ] Add more tools (news, restaurants, movies)
- [ ] Better LLM model support (GPT-4, Claude)
- [ ] Web UI interface
- [ ] Async parallel tool execution

## 📄 License

MIT

## 👥 Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

Built with [MCP](https://github.com/modelcontextprotocol/python-sdk) and [Ollama](https://ollama.ai/)
