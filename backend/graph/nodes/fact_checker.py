"""Fact Checker agent node.

Extracts factual claims from articles and cross-references them to determine
their status (CORROBORATED, UNVERIFIED, CONFLICTING).

Model: deepseek-r1-distill-llama-70b
"""

import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from backend.graph.state import GraphState

load_dotenv()

FACT_CHECKER_MODEL = "deepseek-r1-distill-llama-70b"

SYSTEM_PROMPT = """You are an expert fact-checker and investigative journalist.
Your task is to analyze a set of news articles and extract the key factual claims.
For each claim, cross-reference it against the provided articles to determine its status.

You MUST output ONLY a valid JSON object with a single key "claims" containing a list of objects.
Do not output markdown code blocks or any `<think>` tags in the final JSON.

Each object in the "claims" list MUST have this exact structure:
{
    "claim": "A clear, concise statement of the factual claim.",
    "status": "CORROBORATED",  // Must be one of: CORROBORATED, UNVERIFIED, CONFLICTING
    "sources": ["URL or Outlet Name of sources supporting the claim"],
    "conflicting_sources": ["URL or Outlet Name of sources contradicting the claim" - leave empty if none]
}

Status Definitions:
- CORROBORATED: The claim is supported by multiple independent sources.
- UNVERIFIED: The claim is only mentioned by one source and lacks independent confirmation.
- CONFLICTING: Different sources provide contradictory information about this claim.

Focus on the most significant and relevant claims related to the overall topic.
"""

def fact_checker_node(state: GraphState) -> dict:
    """Fact checker node: extracts and verifies claims from articles.

    Reads:
        state["articles"]
        state["topic"]

    Returns:
        dict with "claims" key containing a list of claim dictionaries.
    """
    articles = state.get("articles", [])
    topic = state.get("topic", "Unknown Topic")
    
    if not articles:
        return {"claims": []}

    llm = ChatGroq(
        model=FACT_CHECKER_MODEL,
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    # Format articles for the prompt
    articles_text = ""
    for i, article in enumerate(articles):
        title = article.get("title", "No Title")
        outlet = article.get("outlet", "Unknown")
        url = article.get("url", "No URL")
        # Truncate text to avoid blowing up context window unnecessarily
        text = article.get("full_text", "")[:2000] 
        
        articles_text += f"\n--- Article {i+1} ---\n"
        articles_text += f"Title: {title}\n"
        articles_text += f"Outlet: {outlet}\n"
        articles_text += f"Source/URL: {url}\n"
        articles_text += f"Text Snippet: {text}...\n"

    user_content = f"Topic: {topic}\n\nArticles:\n{articles_text}\n\nExtract and verify the key claims."

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    raw_content = response.content

    # Clean up DeepSeek reasoning tags if present
    if "<think>" in raw_content:
        think_end = raw_content.rfind("</think>")
        if think_end != -1:
            raw_content = raw_content[think_end + len("</think>"):].strip()

    # Try to parse JSON
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_content)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                parsed = {"claims": []}
        else:
            # Fallback
            start = raw_content.find("{")
            end = raw_content.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    parsed = json.loads(raw_content[start:end])
                except json.JSONDecodeError:
                    parsed = {"claims": []}
            else:
                parsed = {"claims": []}

    claims = parsed.get("claims", [])
    
    # Ensure all claims match the required schema minimally
    valid_claims = []
    for c in claims:
        if isinstance(c, dict) and "claim" in c and "status" in c and "sources" in c:
            if c["status"] not in ["CORROBORATED", "UNVERIFIED", "CONFLICTING"]:
                c["status"] = "UNVERIFIED"
            if "conflicting_sources" not in c:
                c["conflicting_sources"] = []
            valid_claims.append(c)

    return {"claims": valid_claims}
