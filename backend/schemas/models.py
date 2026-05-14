from pydantic import BaseModel
from typing import Literal


class PlannerOutput(BaseModel):
    sub_questions: list[str]
    queries: dict[str, list[str]]  # {"newsapi": [...], "tavily": [...], ...}


class Article(BaseModel):
    title: str
    outlet: str
    url: str
    published_at: str
    full_text: str


class Claim(BaseModel):
    claim: str
    status: Literal["CORROBORATED", "UNVERIFIED", "CONFLICTING"]
    sources: list[str]
    conflicting_sources: list[str] = []


class OutletBias(BaseModel):
    outlet: str
    sentiment_score: float       # -1.0 (negative) to 1.0 (positive)
    framing: Literal["positive", "neutral", "negative"]
    key_phrases: list[str]


class CriticOutput(BaseModel):
    decision: Literal["pass", "refine"]
    feedback: str = ""
