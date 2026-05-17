"""Main LangGraph assembly.

Wires all agent nodes together into a runnable state graph with memory checkpointing.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from langgraph.checkpoint.memory import MemorySaver

from backend.graph.state import GraphState, ResearcherState
from backend.graph.nodes import (
    planner_node,
    researcher_node,
    post_researcher_node,
    fact_checker_node,
    bias_analyst_node,
    critic_node,
    writer_node,
)


def map_researcher(state: GraphState) -> list[Send]:
    """Map function to spawn parallel researcher nodes for each source."""
    search_queries = state.get("search_queries", {})
    if not search_queries:
        # If no queries, just go to post_researcher directly (or return empty list and let graph figure it out)
        # LangGraph requires us to return Send objects or a direct edge. 
        # But wait, map functions must return Send objects or node names.
        # Actually, if we return an empty list of Sends, it will complete the parallel branch immediately.
        return []

    return [
        Send("researcher", ResearcherState(source=source, queries=queries))
        for source, queries in search_queries.items()
    ]


def route_critic(state: GraphState) -> str:
    """Conditional routing from critic: loop back to planner or finalize."""
    if state.get("critic_feedback") == "pass" or state.get("iteration", 0) >= 3:
        return "writer"
    return "planner"


# Initialize the state graph
builder = StateGraph(GraphState)

# Add all nodes
builder.add_node("planner", planner_node)
builder.add_node("researcher", researcher_node)
builder.add_node("post_researcher", post_researcher_node)
builder.add_node("fact_checker", fact_checker_node)
builder.add_node("bias_analyst", bias_analyst_node)
builder.add_node("critic", critic_node)
builder.add_node("writer", writer_node)

# Add edges
builder.add_edge(START, "planner")

# Parallel fan-out from planner to researcher
builder.add_conditional_edges("planner", map_researcher, ["researcher"])

# Fan-in from researcher to post_researcher
builder.add_edge("researcher", "post_researcher")

# Linear flow for the rest
builder.add_edge("post_researcher", "fact_checker")
builder.add_edge("post_researcher", "bias_analyst")

# Wait, fact_checker and bias_analyst are parallel.
# Both need to finish before critic runs.
builder.add_edge("fact_checker", "critic")
builder.add_edge("bias_analyst", "critic")

# Conditional loop from critic
builder.add_conditional_edges(
    "critic",
    route_critic,
    {"planner": "planner", "writer": "writer"}
)

builder.add_edge("writer", END)

# Compile with memory checkpointing
memory = MemorySaver()
app = builder.compile(checkpointer=memory)
