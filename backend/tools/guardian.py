"""Guardian API tool wrapper.

Calls the Guardian Open Platform /search endpoint with show-fields=bodyText
to retrieve full article body text.
"""

import os

import httpx
from dotenv import load_dotenv
from langchain_core.tools import StructuredTool

load_dotenv()

GUARDIAN_BASE_URL = "https://content.guardianapis.com/search"


def search_guardian(query: str, page_size: int = 10) -> list[dict]:
    """Search the Guardian API for articles matching the given query.

    Args:
        query: The search term to look for.
        page_size: Number of results to return (default 10).

    Returns:
        A list of article dicts with keys: title, outlet, url,
        published_at, full_text.
    """
    api_key = os.getenv("GUARDIAN_API_KEY")
    if not api_key:
        raise ValueError("GUARDIAN_API_KEY environment variable is not set.")

    params = {
        "q": query,
        "api-key": api_key,
        "show-fields": "bodyText,headline",
        "page-size": page_size,
        "order-by": "relevance",
    }

    response = httpx.get(GUARDIAN_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    articles = []
    for result in data.get("response", {}).get("results", []):
        fields = result.get("fields", {})
        articles.append({
            "title": fields.get("headline", result.get("webTitle", "")),
            "outlet": "The Guardian",
            "url": result.get("webUrl", ""),
            "published_at": result.get("webPublicationDate", ""),
            "full_text": fields.get("bodyText", ""),
        })

    return articles


guardian_tool = StructuredTool.from_function(
    func=search_guardian,
    name="search_guardian",
    description="Search the Guardian API for articles on a given query. Returns articles with full body text.",
)
