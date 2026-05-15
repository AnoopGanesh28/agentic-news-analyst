"""Writer agent node.

Compiles all research, claims, and bias data into a cohesive, structured
markdown report.

Model: llama-3.3-70b-versatile
"""

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from backend.graph.state import GraphState

load_dotenv()

WRITER_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an award-winning investigative journalist. Your task is to synthesize raw research data into a comprehensive, highly readable markdown report.
You will be provided with:
- The original topic
- Sub-questions investigated
- Extracted factual claims and their verification status
- Bias and framing analysis of the various media outlets
- The source articles used

Your report MUST be written in clean, standard Markdown and MUST include these exact sections:
# [Title based on the topic]

## Executive Summary
A concise overview of the entire issue and the main findings.

## Key Claims & Verification
Detail the most important factual claims, specifically noting which are corroborated and which remain unverified.

## Conflicting Narratives
Highlight where different sources disagree or present opposing facts. If none, state that the narrative is largely consistent.

## Media Bias & Framing
Summarize how different outlets covered the topic. Who was positive? Who was negative? What key phrases did they use?

## Coverage Gaps
What questions remain unanswered based on the original sub-questions? What information is missing?

## Sources
A bulleted list of the outlets and URLs used in this report.
"""

def writer_node(state: GraphState) -> dict:
    """Writer node: synthesizes research into a final markdown report.

    Reads:
        state["topic"]
        state["sub_questions"]
        state["claims"]
        state["bias_scores"]
        state["articles"]

    Writes:
        state["report"]
    """
    topic = state.get("topic", "Unknown Topic")
    sub_questions = state.get("sub_questions", [])
    claims = state.get("claims", [])
    bias_scores = state.get("bias_scores", [])
    articles = state.get("articles", [])
    
    llm = ChatGroq(
        model=WRITER_MODEL,
        temperature=0.3, # Slightly higher for more natural writing
        api_key=os.getenv("GROQ_API_KEY"),
    )

    # Format the data for the prompt
    questions_text = "\n".join([f"- {q}" for q in sub_questions])
    
    claims_text = ""
    for c in claims:
        claims_text += f"- Claim: {c.get('claim')}\n  Status: {c.get('status')}\n  Sources: {', '.join(c.get('sources', []))}\n"
        if c.get('conflicting_sources'):
            claims_text += f"  Conflicting Sources: {', '.join(c.get('conflicting_sources', []))}\n"
    
    bias_text = ""
    for b in bias_scores:
        bias_text += f"- Outlet: {b.get('outlet')}\n  Framing: {b.get('framing')}\n  Sentiment: {b.get('sentiment_score')}\n  Phrases: {', '.join(b.get('key_phrases', []))}\n"
        
    sources_text = ""
    seen_urls = set()
    for a in articles:
        url = a.get("url", "")
        outlet = a.get("outlet", "Unknown")
        if url and url not in seen_urls:
            sources_text += f"- {outlet}: {url}\n"
            seen_urls.add(url)

    user_content = (
        f"Topic: {topic}\n\n"
        f"--- Sub-Questions Investigated ---\n{questions_text}\n\n"
        f"--- Factual Claims ---\n{claims_text}\n\n"
        f"--- Media Bias & Framing ---\n{bias_text}\n\n"
        f"--- Sources Available ---\n{sources_text}\n\n"
        f"Please write the comprehensive report according to the required structure."
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    
    return {"report": response.content}
