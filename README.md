# Agentic News Analyst

`agentic-news-analyst` is a multi-agent AI system that autonomously researches a news topic, cross-references claims across outlets, detects bias and sentiment, identifies conflicting narratives, and produces a structured analytical briefing. 

## Features

- **Multi-Agent Orchestration:** Uses LangGraph to orchestrate a cyclic Planner → Researcher → Fact-Checker → Critic → Writer loop.
- **Self-Correcting:** The Critic agent evaluates if the coverage is sufficient and forces a re-plan if it is lacking.
- **Zero-Cost Multi-Model Architecture (via Groq):** Routes tasks dynamically to the best open-source models:
  - **DeepSeek R1 Distill Llama 70B** for planning, cross-referencing, and routing logic.
  - **Qwen 2.5 32B** for fast parallel tool calling and extraction.
  - **Llama 3.3 70B** for nuanced bias analysis, natural language generation, and reporting.
- **Parallel Research:** Fanned-out API queries across NewsAPI, Guardian, NY Times, and Tavily for blazing-fast research.
- **Live Streaming:** Server-Sent Events (SSE) stream the agents' live progress to a React frontend.
- **Serverless Ready:** Built to deploy effortlessly to Vercel (both FastAPI backend and React frontend).

## Architecture Diagram

```mermaid
flowchart TD
    A[Planner Agent] -->|Sub-questions & Queries| B{Parallel Researchers}
    B -->|NewsAPI| C[Article Extractor]
    B -->|Guardian API| C
    B -->|NYT API| C
    B -->|Tavily Web Search| C
    C -->|Raw Articles| D[Fact-Checker Agent]
    D -->|Extracted Claims & Corroboration| E[Bias Analyst Agent]
    E -->|Sentiment & Framing Scores| F[Critic Agent]
    
    F -->|Coverage Insufficient (Refine)| A
    F -->|Coverage Approved (Pass)| G[Writer Agent]
    
    G --> H[Final Structured Briefing]
```

*(UI Screenshots coming soon...)*

## Tech Stack

- **Backend:** FastAPI (Python), Vercel Serverless Functions
- **Frontend:** React (Vite)
- **Agent Framework:** LangGraph, LangChain
- **LLM Provider:** Groq
- **Tools/APIs:** NewsAPI, Guardian Open Platform, NY Times Article Search, Tavily Search, Newspaper3k

## Quickstart (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AnoopGanesh28/agentic-news-analyst.git
   cd agentic-news-analyst
   ```

2. **Set up environment variables:**
   Copy the `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   *Note: Groq API keys are completely free!*

3. **Install Backend Dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Install Frontend Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

5. **Run the Application:**
   * **Backend:** `uvicorn backend.main:app --reload`
   * **Frontend:** `npm run dev` (in the `frontend` directory)

## Vercel Deployment

This project is configured out-of-the-box for **Vercel Serverless**.

1. Connect your GitHub repository to Vercel.
2. The root `vercel.json` file automatically configures the FastAPI backend as Serverless Python Functions under the `/api/*` route.
3. Set the build command to standard Vite commands, but ensure the root directory deployment config handles the monorepo structure.
4. In your Vercel Project Settings, add all the environment variables from your `.env` file.
5. Deploy!
