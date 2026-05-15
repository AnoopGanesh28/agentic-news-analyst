"""Planner agent node.

Breaks a user-provided topic into 4-6 targeted sub-questions and generates
search queries mapped to each news API source.

Model: deepseek-r1-distill-llama-70b (strong reasoning/planning via Groq)
"""

import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from backend.graph.state import GraphState

load_dotenv()

PLANNER_MODEL = "deepseek-r1-distill-llama-70b"

SYSTEM_PROMPT = """You are a senior investigative research planner. Given a news topic, your job is to:

1. Break it down into 4-6 specific sub-questions that, when answered together, provide a comprehensive multi-angle understanding of the topic.
2. For each sub-question, generate 2-3 targeted search queries optimized for different news APIs.

You MUST respond with ONLY valid JSON (no markdown, no explanation) in this exact format:
{
  "sub_questions": ["question1", "question2", ...],
  "queries": {
    "newsapi": ["query1", "query2", ...],
    "guardian": ["query1", "query2", ...],
    "nytimes": ["query1", "query2", ...],
    "tavily": ["query1", "query2", ...]
  }
}

Guidelines:
- Sub-questions should cover different angles: causes, effects, stakeholders, timelines, controversies, and future implications.
- Search queries should be concise and keyword-focused (not full sentences).
- Tailor queries to each API's strengths: NewsAPI for breaking news, Guardian for in-depth analysis, NYTimes for investigative reporting, Tavily for the broadest web coverage.
"""


def planner_node(state: GraphState) -> dict:
    """Planner node: generates sub-questions and API-specific search queries.

    Reads:
        state["topic"] — the user-provided topic to analyze.
        state["critic_feedback"] — optional feedback from the critic for refinement.

    Returns:
        dict with "sub_questions" and "search_queries" keys to merge into state.
    """
    llm = ChatGroq(
        model=PLANNER_MODEL,
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    topic = state["topic"]
    critic_feedback = state.get("critic_feedback", "")

    user_content = f"Topic to analyze: {topic}"
    if critic_feedback and critic_feedback != "pass":
        user_content += (
            f"\n\nPrevious analysis was reviewed by a critic who provided this "
            f"feedback. Adjust your plan accordingly:\n{critic_feedback}"
        )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    raw_content = response.content

    # DeepSeek R1 may wrap response in <think>...</think> tags; strip them
    if "<think>" in raw_content:
        # Extract content after the closing </think> tag
        think_end = raw_content.rfind("</think>")
        if think_end != -1:
            raw_content = raw_content[think_end + len("</think>"):].strip()

    # Parse JSON from the response
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code fences
        import re
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_content)
        if json_match:
            parsed = json.loads(json_match.group(1).strip())
        else:
            # Last resort: find first { and last }
            start = raw_content.find("{")
            end = raw_content.rfind("}") + 1
            if start != -1 and end > start:
                parsed = json.loads(raw_content[start:end])
            else:
                raise ValueError(
                    f"Planner failed to produce valid JSON. Raw output:\n{raw_content}"
                )

    return {
        "sub_questions": parsed["sub_questions"],
        "search_queries": parsed["queries"],
    }
