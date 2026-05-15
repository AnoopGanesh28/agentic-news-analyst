"""Newspaper3k article extractor tool.

Extracts the full article text and metadata from any URL.
Used as a fallback when news APIs return only snippets or truncated content.
"""

from newspaper import Article as NewspaperArticle
from langchain_core.tools import StructuredTool


def extract_article(url: str) -> dict:
    """Extract full article text from a URL using Newspaper3k.

    Args:
        url: The article URL to extract text from.

    Returns:
        An article dict with keys: title, outlet, url, published_at,
        full_text. Returns an error message in full_text on failure.
    """
    # Derive outlet name from the domain
    try:
        outlet = url.split("/")[2] if url else "Unknown"
    except IndexError:
        outlet = "Unknown"

    try:
        article = NewspaperArticle(url)
        article.download()
        article.parse()

        return {
            "title": article.title or "",
            "outlet": outlet,
            "url": url,
            "published_at": (
                article.publish_date.isoformat() if article.publish_date else ""
            ),
            "full_text": article.text or "",
        }
    except Exception as e:
        return {
            "title": "",
            "outlet": outlet,
            "url": url,
            "published_at": "",
            "full_text": f"Error extracting article: {str(e)}",
        }


extractor_tool = StructuredTool.from_function(
    func=extract_article,
    name="extract_article",
    description="Extract the full article text and metadata from a given URL using Newspaper3k. Use as a fallback when APIs return truncated content.",
)
