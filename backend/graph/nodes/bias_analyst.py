"""Bias Analyst agent node.

Groups articles by outlet, scores sentiment, assigns framing labels,
and extracts key framing phrases.

Model: llama-3.3-70b-versatile
"""

import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from backend.graph.state import GraphState

load_dotenv()

BIAS_ANALYST_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert media analyst. Your task is to analyze how different media outlets are covering a specific topic.
Given a list of articles grouped by outlet, you must determine the bias, sentiment, and framing of each outlet.

You MUST output ONLY a valid JSON object with a single key "bias_scores" containing a list of objects.
Do not output markdown code blocks or any explanation.

Each object in the "bias_scores" list MUST have this exact structure:
{
    "outlet": "Name of the Outlet",
    "sentiment_score": 0.0, // Float from -1.0 (very negative) to 1.0 (very positive)
    "framing": "neutral", // Must be one of: positive, neutral, negative
    "key_phrases": ["phrase 1", "phrase 2", "phrase 3"] // 2-4 short phrases demonstrating the framing
}

Analyze each outlet's overall stance based on their articles provided.
"""

def bias_analyst_node(state: GraphState) -> dict:
    """Bias analyst node: evaluates media bias and framing per outlet.

    Reads:
        state["articles"]
        state["topic"]

    Returns:
        dict with "bias_scores" key containing a list of outlet bias dictionaries.
    """
    articles = state.get("articles", [])
    topic = state.get("topic", "Unknown Topic")
    
    if not articles:
        return {"bias_scores": []}

    # Group articles by outlet
    outlets_data = {}
    for article in articles:
        outlet = article.get("outlet", "Unknown")
        if outlet not in outlets_data:
            outlets_data[outlet] = []
        
        title = article.get("title", "")
        text = article.get("full_text", "")[:1000] # Truncate per article
        outlets_data[outlet].append(f"Headline: {title}\nExcerpt: {text}...")

    # Format the grouped articles for the prompt
    grouped_text = ""
    for outlet, texts in outlets_data.items():
        grouped_text += f"\n=== Outlet: {outlet} ===\n"
        for i, text in enumerate(texts):
            grouped_text += f"Article {i+1}:\n{text}\n\n"

    llm = ChatGroq(
        model=BIAS_ANALYST_MODEL,
        temperature=0.1,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    user_content = f"Topic: {topic}\n\nArticles by Outlet:\n{grouped_text}\n\nAnalyze the bias and framing for each outlet."

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    raw_content = response.content

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
                parsed = {"bias_scores": []}
        else:
            # Fallback
            start = raw_content.find("{")
            end = raw_content.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    parsed = json.loads(raw_content[start:end])
                except json.JSONDecodeError:
                    parsed = {"bias_scores": []}
            else:
                parsed = {"bias_scores": []}

    bias_scores = parsed.get("bias_scores", [])
    
    # Validate and clean up
    valid_scores = []
    for score in bias_scores:
        if isinstance(score, dict) and "outlet" in score and "sentiment_score" in score and "framing" in score and "key_phrases" in score:
            if score["framing"] not in ["positive", "neutral", "negative"]:
                score["framing"] = "neutral"
            try:
                score["sentiment_score"] = float(score["sentiment_score"])
            except ValueError:
                score["sentiment_score"] = 0.0
            valid_scores.append(score)

    return {"bias_scores": valid_scores}
