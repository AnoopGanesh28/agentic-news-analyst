"""LangChain StructuredTool wrappers for all news API integrations."""

from .newsapi import newsapi_tool, search_newsapi
from .guardian import guardian_tool, search_guardian
from .nytimes import nytimes_tool, search_nytimes
from .tavily import tavily_tool, search_tavily
from .extractor import extractor_tool, extract_article

__all__ = [
    "newsapi_tool",
    "search_newsapi",
    "guardian_tool",
    "search_guardian",
    "nytimes_tool",
    "search_nytimes",
    "tavily_tool",
    "search_tavily",
    "extractor_tool",
    "extract_article",
]
