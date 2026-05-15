"""NY Times Article Search API tool wrapper.

Calls /articlesearch.json and extracts lead_paragraph + abstract as
the article text.
"""

import os

import httpx
from dotenv import load_dotenv
from langchain_core.tools import StructuredTool

load_dotenv()

NYT_BASE_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"


def search_nytimes(query: str, page: int = 0) -> list[dict]:
    """Search the NY Times Article Search API for articles matching the query.

    Args:
        query: The search term to look for.
        page: Results page number (0-indexed, default 0).

    Returns:
        A list of article dicts with keys: title, outlet, url,
        published_at, full_text.
    """
    api_key = os.getenv("NYT_API_KEY")
    if not api_key:
        raise ValueError("NYT_API_KEY environment variable is not set.")

    params = {
        "q": query,
        "api-key": api_key,
        "page": page,
    }

    response = httpx.get(NYT_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    articles = []
    for doc in data.get("response", {}).get("docs", []):
        lead = doc.get("lead_paragraph", "") or ""
        abstract = doc.get("abstract", "") or ""
        # Combine lead_paragraph and abstract; deduplicate if identical
        if lead and abstract and lead != abstract:
            full_text = f"{lead}\n\n{abstract}"
        else:
            full_text = lead or abstract

        articles.append({
            "title": doc.get("headline", {}).get("main", ""),
            "outlet": "The New York Times",
            "url": doc.get("web_url", ""),
            "published_at": doc.get("pub_date", ""),
            "full_text": full_text,
        })

    return articles


nytimes_tool = StructuredTool.from_function(
    func=search_nytimes,
    name="search_nytimes",
    description="Search the NY Times Article Search API for articles on a given query. Returns articles with lead paragraph and abstract.",
)
