# server_fun.py
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any, List
import requests, html

mcp = FastMCP("FunTools")

# ---- Weather (Open-Meteo) ----
@mcp.tool()
def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:
    """Current weather at coordinates via Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "timezone": "auto",
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("current", {})

# ---- Book recs (Google Books API) ----
@mcp.tool()
def book_recs(topic: str, limit: int = 5) -> Dict[str, Any]:
    """Simple book suggestions for a topic via Google Books API."""
    r = requests.get("https://www.googleapis.com/books/v1/volumes",
                     params={"q": topic, "maxResults": min(limit, 10)}, timeout=20)
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

# ---- Jokes (JokeAPI) ----
@mcp.tool()
def random_joke() -> Dict[str, Any]:
    """Return a safe, single-line joke."""
    r = requests.get("https://v2.jokeapi.dev/joke/Any?type=single&safe-mode", timeout=20)
    r.raise_for_status()
    data = r.json()
    return {"joke": data.get("joke", "No joke found")}

# ---- Dog pic (Dog CEO) ----
@mcp.tool()
def random_dog() -> Dict[str, Any]:
    """Return a random dog image URL."""
    r = requests.get("https://dog.ceo/api/breeds/image/random", timeout=20)
    r.raise_for_status()
    return r.json()

# ---- (Optional) Trivia (Open Trivia DB) ----
@mcp.tool()
def trivia() -> Dict[str, Any]:
    """Return one multiple-choice trivia question."""
    r = requests.get("https://opentdb.com/api.php?amount=1&type=multiple", timeout=20)
    r.raise_for_status()
    data = r.json().get("results", [])
    if not data: return {"error": "no trivia"}
    q = data[0]
    q["question"] = html.unescape(q["question"])
    q["correct_answer"] = html.unescape(q["correct_answer"])
    q["incorrect_answers"] = [html.unescape(x) for x in q["incorrect_answers"]]
    return q

if __name__ == "__main__":
    mcp.run()  # stdio server