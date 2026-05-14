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


## Tech Stack

- **Backend:** FastAPI (Python), Vercel Serverless Functions
- **Frontend:** React (Vite)
- **Agent Framework:** LangGraph, LangChain
- **LLM Provider:** Groq
- **Tools/APIs:** NewsAPI, Guardian Open Platform, NY Times Article Search, Tavily Search, Newspaper3k

