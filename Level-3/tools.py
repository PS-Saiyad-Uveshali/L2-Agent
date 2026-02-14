"""Tool definitions for the L2 Wizard Agent."""

from typing import Any, Dict, List
import requests
import html
from config import AgentConfig


class ToolRegistry:
    """Registry of all available tools with structured definitions."""
    
    @staticmethod
    def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get current weather at coordinates via Open-Meteo API.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            
        Returns:
            Dict with current weather data including temperature, weather_code, wind_speed
        """
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "timezone": "auto",
        }
        r = requests.get(url, params=params, timeout=AgentConfig.TOOL_TIMEOUT)
        r.raise_for_status()
        return r.json().get("current", {})
    
    @staticmethod
    def book_recs(topic: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get book recommendations for a topic via Google Books API.
        
        Args:
            topic: Search topic (e.g., "mystery", "science fiction")
            limit: Number of results to return (default: 5, max: 10)
            
        Returns:
            Dict with topic and list of book results (title, author, year, id)
        """
        r = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": topic, "maxResults": min(limit, 10)},
            timeout=AgentConfig.TOOL_TIMEOUT
        )
        r.raise_for_status()
        items = r.json().get("items", [])
        picks: List[Dict[str, Any]] = []
        for item in items[:limit]:
            vol = item.get("volumeInfo", {})
            picks.append({
                "title": vol.get("title"),
                "author": vol.get("authors", ["Unknown"])[0] if vol.get("authors") else "Unknown",
                "year": vol.get("publishedDate", "N/A")[:4] if vol.get("publishedDate") else "N/A",
                "id": item.get("id"),
            })
        return {"topic": topic, "results": picks}
    
    @staticmethod
    def random_joke() -> Dict[str, Any]:
        """
        Get a random safe joke from JokeAPI.
        
        Returns:
            Dict with a single joke string
        """
        r = requests.get(
            "https://v2.jokeapi.dev/joke/Any?type=single&safe-mode",
            timeout=AgentConfig.TOOL_TIMEOUT
        )
        r.raise_for_status()
        data = r.json()
        return {"joke": data.get("joke", "No joke found")}
    
    @staticmethod
    def random_dog() -> Dict[str, Any]:
        """
        Get a random dog image URL from Dog CEO API.
        
        Returns:
            Dict with random dog image URL
        """
        r = requests.get(
            "https://dog.ceo/api/breeds/image/random",
            timeout=AgentConfig.TOOL_TIMEOUT
        )
        r.raise_for_status()
        return r.json()
    
    @staticmethod
    def trivia() -> Dict[str, Any]:
        """
        Get a random multiple-choice trivia question from Open Trivia Database.
        
        Returns:
            Dict with question, correct_answer, incorrect_answers, category, difficulty
        """
        r = requests.get(
            "https://opentdb.com/api.php?amount=1&type=multiple",
            timeout=AgentConfig.TOOL_TIMEOUT
        )
        r.raise_for_status()
        data = r.json().get("results", [])
        if not data:
            return {"error": "no trivia"}
        q = data[0]
        q["question"] = html.unescape(q["question"])
        q["correct_answer"] = html.unescape(q["correct_answer"])
        q["incorrect_answers"] = [html.unescape(x) for x in q["incorrect_answers"]]
        return q
    
    @classmethod
    def get_tool_definitions(cls) -> List[Dict[str, Any]]:
        """
        Get Claude-compatible tool definitions for all available tools.
        
        Returns:
            List of tool definition dicts in Claude API format
        """
        return [
            {
                "name": "get_weather",
                "description": "Get current weather at coordinates via Open-Meteo API. Returns temperature, weather code, and wind speed.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Latitude coordinate (-90 to 90)"
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude coordinate (-180 to 180)"
                        }
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "book_recs",
                "description": "Get book recommendations for a topic via Google Books API. Returns list of books with title, author, and year.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Search topic (e.g., 'mystery', 'science fiction', 'history')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5, max: 10)",
                            "default": 5
                        }
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "random_joke",
                "description": "Get a random safe joke from JokeAPI. Returns a single joke string.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "random_dog",
                "description": "Get a random dog image URL from Dog CEO API. Returns an image URL.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "trivia",
                "description": "Get a random multiple-choice trivia question from Open Trivia Database. Returns question, correct answer, and incorrect answers.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    @classmethod
    def get_tool_definitions_openai_format(cls) -> List[Dict[str, Any]]:
        """
        Get OpenAI/LiteLLM-compatible tool definitions for all available tools.
        
        Returns:
            List of tool definition dicts in OpenAI function calling format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather at coordinates via Open-Meteo API. Returns temperature, weather code, and wind speed.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "description": "Latitude coordinate (-90 to 90)"
                            },
                            "longitude": {
                                "type": "number",
                                "description": "Longitude coordinate (-180 to 180)"
                            }
                        },
                        "required": ["latitude", "longitude"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "book_recs",
                    "description": "Get book recommendations for a topic via Google Books API. Returns list of books with title, author, and year.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Search topic (e.g., 'mystery', 'science fiction', 'history')"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5, max: 10)",
                                "default": 5
                            }
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "random_joke",
                    "description": "Get a random safe joke from JokeAPI. Returns a single joke string.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "random_dog",
                    "description": "Get a random dog image URL from Dog CEO API. Returns an image URL.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "trivia",
                    "description": "Get a random multiple-choice trivia question from Open Trivia Database. Returns question, correct answer, and incorrect answers.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]
    
    @classmethod
    def execute_tool(cls, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with given input.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool_name is not recognized
        """
        tool_map = {
            "get_weather": cls.get_weather,
            "book_recs": cls.book_recs,
            "random_joke": cls.random_joke,
            "random_dog": cls.random_dog,
            "trivia": cls.trivia,
        }
        
        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        try:
            return tool_map[tool_name](**tool_input)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
