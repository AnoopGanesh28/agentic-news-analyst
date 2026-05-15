"""Tavily Search API tool wrapper.

Uses the langchain-tavily package to perform real-time web searches optimized
for LLM agents, then normalizes results into the project's Article schema.
"""

import os

from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_core.tools import StructuredTool

load_dotenv()


def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using Tavily Search API for real-time results.

    Args:
        query: The search term to look for.
        max_results: Maximum number of results to return (default 5).

    Returns:
        A list of article dicts with keys: title, outlet, url,
        published_at, full_text.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set.")

    tool = TavilySearch(max_results=max_results)
    raw = tool.invoke(query)

    # TavilySearch returns a dict with a "results" key containing the list
    if isinstance(raw, dict):
        results = raw.get("results", [])
    elif isinstance(raw, list):
        results = raw
    else:
        results = []

    articles = []
    for result in results:
        url = result.get("url", "")
        # Extract domain name as the outlet
        try:
            outlet = url.split("/")[2] if url else "Unknown"
        except IndexError:
            outlet = "Unknown"

        articles.append({
            "title": result.get("title", ""),
            "outlet": outlet,
            "url": url,
            "published_at": "",  # Tavily does not provide publish dates
            "full_text": result.get("content", ""),
        })

    return articles


tavily_tool = StructuredTool.from_function(
    func=search_tavily,
    name="search_tavily",
    description="Search the web using Tavily for real-time news articles and information. Best for finding the latest coverage on a topic.",
)
