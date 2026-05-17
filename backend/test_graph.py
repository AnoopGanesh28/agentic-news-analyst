"""End-to-end test script for the LangGraph assembly."""

import uuid
import sys
import os

# Add the parent directory to Python path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.graph.graph import app
from backend.graph.state import GraphState

def test_graph():
    # Generate a random run ID for memory checkpointing
    run_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": run_id}}
    
    print(f"Starting test run with ID: {run_id}")
    
    # Initialize the state
    initial_state = {
        "topic": "AI Regulation in the European Union",
        "iteration": 0,
        "run_id": run_id,
        "sub_questions": [],
        "search_queries": {},
        "raw_articles": [],
        "articles": [],
        "claims": [],
        "bias_scores": [],
        "critic_feedback": "",
        "report": ""
    }
    
    print("\n[+] Streaming graph events...")
    
    # Stream events to see the progression through the nodes
    for event in app.stream(initial_state, config=config, stream_mode="updates"):
        for node_name, node_state in event.items():
            print(f"--- Completed Node: {node_name} ---")
            
            if node_name == "planner":
                print(f"  Sub-questions generated: {len(node_state.get('sub_questions', []))}")
                print(f"  Search queries mapped: {list(node_state.get('search_queries', {}).keys())}")
            
            elif node_name == "researcher":
                print(f"  Raw articles appended from this parallel branch: {len(node_state.get('raw_articles', []))}")
                
            elif node_name == "post_researcher":
                print(f"  Total deduplicated articles for this iteration: {len(node_state.get('articles', []))}")
                
            elif node_name == "fact_checker":
                print(f"  Claims extracted: {len(node_state.get('claims', []))}")
                
            elif node_name == "bias_analyst":
                print(f"  Outlets analyzed for bias: {len(node_state.get('bias_scores', []))}")
                
            elif node_name == "critic":
                print(f"  Critic decision: {node_state.get('critic_feedback')}")
                print(f"  Iteration count: {node_state.get('iteration')}")
                
            elif node_name == "writer":
                print(f"  Report generated. Length: {len(node_state.get('report', ''))} characters.")
                
            print("-" * 40)
            
    # Get final state to print the report
    final_state = app.get_state(config).values
    
    if final_state and "report" in final_state:
        print("\n\n================ FINAL REPORT ================\n")
        print(final_state["report"])
        print("\n==============================================\n")
        print("End-to-End Test Completed Successfully!")
    else:
        print("\n[!] Error: Graph completed but no report was found in the final state.")

if __name__ == "__main__":
    test_graph()
