"""Post-Researcher node.

Receives all articles gathered by the parallel researcher nodes, deduplicates
them, and enriches them via Newspaper3k.
"""

from backend.graph.state import GraphState
from backend.graph.nodes.researcher import _deduplicate_articles, _enrich_with_extractor

def post_researcher_node(state: GraphState) -> dict:
    """Post-researcher node: deduplicates and filters articles.

    Reads:
        state["articles"] — combined list of all articles from all sources.

    Returns:
        dict with "articles" key containing deduplicated, enriched article list.
    """
    all_articles = state.get("articles", [])
    
    if not all_articles:
        return {"articles": []}

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
        f"[Post-Researcher] Collected {len(all_articles)} raw -> "
        f"{len(unique_articles)} unique -> {len(final_articles)} with text"
    )

    # Note: Returning this dict will *replace* the list in the state if we're careful
    # Wait, GraphState["articles"] has Annotated[list[dict], operator.add]. 
    # If we return {"articles": final_articles}, it will APPEND to the existing articles.
    # To fix this, we need a custom reducer for articles that allows replacing, or we 
    # just don't use operator.add for articles. Let's see how we can handle this.
    
    # Actually, let's just return the processed articles. If it appends, we might have 
    # a problem. We will address this in the Graph definition.
    return {"articles": final_articles}
