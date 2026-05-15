"""Critic agent node.

Evaluates whether the collected research meaningfully addresses all sub-questions.
Returns "pass" if sufficient, or "refine" with specific feedback if more research is needed.

Model: deepseek-r1-distill-llama-70b
"""

import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from backend.graph.state import GraphState

load_dotenv()

CRITIC_MODEL = "deepseek-r1-distill-llama-70b"

SYSTEM_PROMPT = """You are an exacting editor-in-chief reviewing an investigative research report.
Your job is to determine if the collected articles and factual claims adequately answer the original sub-questions.

You MUST output ONLY a valid JSON object. No markdown formatting, no `<think>` tags, just JSON.

The JSON MUST match this exact structure:
{
    "decision": "pass", // Or "refine" if the research is lacking
    "feedback": "If refine, provide 1-2 short sentences on what is missing. If pass, leave empty."
}

Criteria for "pass":
- Most of the sub-questions have some relevant claims extracted.
- The articles provide a decently well-rounded view of the topic.

Criteria for "refine":
- A major sub-question is completely ignored or lacks sources.
- The facts are too sparse to form a coherent report.

Be practical. If the information is reasonably sufficient, output "pass". Do not get stuck in an endless loop.
"""

def critic_node(state: GraphState) -> dict:
    """Critic node: evaluates research sufficiency and routes graph execution.

    Reads:
        state["topic"]
        state["sub_questions"]
        state["claims"]
        state["iteration"]

    Writes:
        state["critic_feedback"]
        state["iteration"] (increments)
    """
    iteration = state.get("iteration", 0)
    
    # Hard pass at iteration 3 to prevent infinite loops
    if iteration >= 3:
        return {
            "critic_feedback": "pass",
            "iteration": iteration + 1
        }

    sub_questions = state.get("sub_questions", [])
    claims = state.get("claims", [])
    topic = state.get("topic", "Unknown Topic")
    
    # Fast-fail if we have no sub-questions or claims
    if not sub_questions or not claims:
        return {
            "critic_feedback": "Missing foundational data (sub-questions or claims). Please research again.",
            "iteration": iteration + 1
        }

    llm = ChatGroq(
        model=CRITIC_MODEL,
        temperature=0.1,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    claims_text = ""
    for i, c in enumerate(claims):
        claims_text += f"{i+1}. {c.get('claim')} (Status: {c.get('status')})\n"

    questions_text = "\n".join([f"- {q}" for q in sub_questions])

    user_content = (
        f"Topic: {topic}\n\n"
        f"Original Sub-Questions:\n{questions_text}\n\n"
        f"Extracted Factual Claims:\n{claims_text}\n\n"
        f"Evaluate if the claims adequately address the sub-questions."
    )

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
                parsed = {"decision": "pass", "feedback": ""}
        else:
            # Fallback
            start = raw_content.find("{")
            end = raw_content.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    parsed = json.loads(raw_content[start:end])
                except json.JSONDecodeError:
                    parsed = {"decision": "pass", "feedback": ""}
            else:
                parsed = {"decision": "pass", "feedback": ""}

    decision = parsed.get("decision", "pass")
    if decision not in ["pass", "refine"]:
        decision = "pass"

    feedback = parsed.get("feedback", "")
    if decision == "pass":
        feedback = "pass" # Align with the build-plan conditional check

    return {
        "critic_feedback": feedback,
        "iteration": iteration + 1
    }
