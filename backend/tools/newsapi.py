"""NewsAPI tool wrapper.

Calls https://newsapi.org/v2/everything and returns articles normalized
to the project's Article schema format.
"""

import os

import httpx
from dotenv import load_dotenv
from langchain_core.tools import StructuredTool

load_dotenv()

NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"


def search_newsapi(query: str, page_size: int = 10) -> list[dict]:
    """Search NewsAPI for articles matching the given query.

    Args:
        query: The search term to look for.
        page_size: Number of results to return (max 100, default 10).

    Returns:
        A list of article dicts with keys: title, outlet, url,
        published_at, full_text.
    """
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise ValueError("NEWSAPI_KEY environment variable is not set.")

    params = {
        "q": query,
        "apiKey": api_key,
        "pageSize": page_size,
        "sortBy": "relevancy",
    }

    response = httpx.get(NEWSAPI_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    articles = []
    for item in data.get("articles", []):
        articles.append({
            "title": item.get("title", ""),
            "outlet": item.get("source", {}).get("name", "Unknown"),
            "url": item.get("url", ""),
            "published_at": item.get("publishedAt", ""),
            # NewsAPI free tier truncates content; extractor.py is the fallback
            "full_text": item.get("description", "") or "",
        })

    return articles


newsapi_tool = StructuredTool.from_function(
    func=search_newsapi,
    name="search_newsapi",
    description="Search NewsAPI for articles on a given query. Returns a list of articles with title, outlet, URL, published date, and text.",
)
