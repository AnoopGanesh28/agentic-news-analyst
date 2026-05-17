import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.graph.graph import app as graph_app
from backend.graph.state import GraphState

app = FastAPI(title="Agentic News Analyst API")

# Allow CORS for local Vite dev and future Vercel domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for local execution
# Note: This works locally but on Serverless (e.g., Vercel) this memory is lost between requests.
active_runs: Dict[str, asyncio.Queue] = {}
run_metadata: Dict[str, dict] = {}

class AnalyzeRequest(BaseModel):
    topic: str

async def run_graph_background(run_id: str, topic: str):
    """Background task to run the LangGraph pipeline and push events to the queue."""
    queue = active_runs.get(run_id)
    if not queue:
        return
    
    config = {"configurable": {"thread_id": run_id}}
    
    initial_state = {
        "topic": topic,
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
    
    try:
        # We must use async stream since we are in an async function putting to an asyncio.Queue
        async for event in graph_app.astream(initial_state, config=config, stream_mode="updates"):
            # Put the event in the queue
            await queue.put(event)
            
        # Put a sentinel value to indicate completion
        await queue.put(None)
        run_metadata[run_id]["status"] = "completed"
    except Exception as e:
        print(f"Error in background task: {e}")
        await queue.put({"error": str(e)})
        await queue.put(None)
        run_metadata[run_id]["status"] = "failed"

@app.post("/api/analyze")
async def start_analysis(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Starts a new analysis run in the background."""
    run_id = str(uuid.uuid4())
    
    # Initialize queue and metadata
    active_runs[run_id] = asyncio.Queue()
    run_metadata[run_id] = {
        "run_id": run_id,
        "topic": request.topic,
        "status": "running",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Start the LangGraph execution in the background
    background_tasks.add_task(run_graph_background, run_id, request.topic)
    
    return {"run_id": run_id}

@app.get("/api/analyze/{run_id}/stream")
async def stream_analysis(run_id: str, request: Request):
    """Streams SSE events from the LangGraph execution."""
    queue = active_runs.get(run_id)
    
    if not queue:
        raise HTTPException(status_code=404, detail="Run ID not found or already completed.")
        
    async def event_generator():
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                    
                # Wait for the next event from the graph
                event = await queue.get()
                
                # Sentinel value indicating completion
                if event is None:
                    # Clean up the queue from active runs
                    if run_id in active_runs:
                        del active_runs[run_id]
                    yield f"data: {json.dumps({'event': 'done'})}\n\n"
                    break
                    
                # Yield the event as SSE
                yield f"data: {json.dumps(event)}\n\n"
        except asyncio.CancelledError:
            pass
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/analyze/{run_id}/report")
async def get_report(run_id: str):
    """Fetches the completed report from the LangGraph checkpointer."""
    if run_id not in run_metadata:
        raise HTTPException(status_code=404, detail="Run ID not found.")
        
    config = {"configurable": {"thread_id": run_id}}
    state = graph_app.get_state(config)
    
    if not state or not state.values:
        raise HTTPException(status_code=404, detail="State not found in checkpointer.")
        
    report = state.values.get("report")
    if not report:
        raise HTTPException(status_code=400, detail="Report not yet generated.")
        
    return {"run_id": run_id, "report": report}

@app.get("/api/runs")
async def list_runs():
    """Lists all historical runs."""
    return {"runs": list(run_metadata.values())}
