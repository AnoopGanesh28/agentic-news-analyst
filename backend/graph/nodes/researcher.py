"""Researcher agent node.

Executes search queries across all news API tools in parallel, extracts
full article text via Newspaper3k when needed, and deduplicates results.

Model: qwen/qwen3-32b (great tool calling + fast via Groq)
"""

import os

from dotenv import load_dotenv

from backend.graph.state import GraphState
from backend.tools.newsapi import search_newsapi
from backend.tools.guardian import search_guardian
from backend.tools.nytimes import search_nytimes
from backend.tools.tavily import search_tavily
from backend.tools.extractor import extract_article

load_dotenv()

# Minimum character count for article text before triggering extractor fallback
MIN_TEXT_LENGTH = 200


def _deduplicate_articles(articles: list[dict]) -> list[dict]:
    """Remove duplicate articles based on URL."""
    seen_urls = set()
    unique = []
    for article in articles:
        url = article.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(article)
        elif not url:
            # Keep articles without URLs (rare edge case)
            unique.append(article)
    return unique


def _enrich_with_extractor(articles: list[dict]) -> list[dict]:
    """Use Newspaper3k extractor to fill in truncated article text."""
    enriched = []
    for article in articles:
        full_text = article.get("full_text", "")
        url = article.get("url", "")

        # If text is too short and we have a URL, try extracting full text
        if len(full_text) < MIN_TEXT_LENGTH and url:
            try:
                extracted = extract_article(url)
                extracted_text = extracted.get("full_text", "")
                if (
                    extracted_text
                    and not extracted_text.startswith("Error")
                    and len(extracted_text) > len(full_text)
                ):
                    article["full_text"] = extracted_text
                    # Also update title if it was empty
                    if not article.get("title") and extracted.get("title"):
                        article["title"] = extracted["title"]
            except Exception:
                pass  # Keep the original truncated text

        enriched.append(article)
    return enriched


def _search_source(source: str, queries: list[str]) -> list[dict]:
    """Execute search queries for a single API source.

    Args:
        source: The API source name (newsapi, guardian, nytimes, tavily).
        queries: List of search query strings.

    Returns:
        Combined list of article dicts from all queries for this source.
    """
    search_funcs = {
        "newsapi": search_newsapi,
        "guardian": search_guardian,
        "nytimes": search_nytimes,
        "tavily": search_tavily,
    }

    func = search_funcs.get(source)
    if not func:
        return []

    all_articles = []
    for query in queries:
        try:
            results = func(query)
            all_articles.extend(results)
        except Exception as e:
            # Log but don't crash — other sources may still succeed
            print(f"[Researcher] Error querying {source} with '{query}': {e}")

    return all_articles


def researcher_node(state: GraphState) -> dict:
    """Researcher node: fetches articles from all news APIs based on planner queries.

    Reads:
        state["search_queries"] — dict mapping source names to query lists.

    Returns:
        dict with "articles" key containing deduplicated, enriched article list.
    """
    search_queries = state.get("search_queries", {})

    if not search_queries:
        return {"articles": []}

    # Collect articles from all sources
    all_articles = []
    for source, queries in search_queries.items():
        source_articles = _search_source(source, queries)
        all_articles.extend(source_articles)

    # Deduplicate by URL
    unique_articles = _deduplicate_articles(all_articles)

    # Enrich truncated articles with full text via Newspaper3k
    enriched_articles = _enrich_with_extractor(unique_articles)

    # Filter out articles with no meaningful text
    final_articles = [
        a for a in enriched_articles
        if a.get("full_text", "").strip()
    ]

    print(
        f"[Researcher] Collected {len(all_articles)} raw -> "
        f"{len(unique_articles)} unique -> {len(final_articles)} with text"
    )

    return {"articles": final_articles}
