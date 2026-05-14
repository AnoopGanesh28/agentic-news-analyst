from typing import TypedDict, Annotated
import operator


class GraphState(TypedDict):
    topic: str
    sub_questions: list[str]
    search_queries: dict[str, list[str]]
    articles: Annotated[list[dict], operator.add]  # parallel nodes append to this
    claims: list[dict]
    bias_scores: list[dict]
    critic_feedback: str
    iteration: int
    report: str
    run_id: str
