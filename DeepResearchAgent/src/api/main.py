# src/api/main.py
"""FastAPI 接口 — 提供 HTTP 服务"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json

from src.workflows.research_flow import build_research_graph, ResearchState
from src.memory.long_term import ResearchMemory

app = FastAPI(title="Deep Research Agent API", version="1.0.0")

# CORS 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局实例
research_graph = build_research_graph()
research_memory = ResearchMemory()


class ResearchRequest(BaseModel):
    topic: str
    max_sub_questions: int = 5
    save_to_memory: bool = True


class ResearchResponse(BaseModel):
    topic: str
    report: str
    sub_questions: list[str]
    num_sources: int


@app.post("/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    """执行一次深度研究"""
    try:
        initial_state = {
            "topic": request.topic,
            "sub_questions": [],
            "research_strategy": "",
            "research_results": [],
            "critiques": [],
            "needs_retry": False,
            "final_report": "",
            "iteration": 0,
            "max_iterations": 2,
        }

        final_state = research_graph.invoke(initial_state)

        # 保存到长期记忆
        if request.save_to_memory:
            research_memory.save_research(
                topic=request.topic,
                report=final_state["final_report"],
            )

        return ResearchResponse(
            topic=request.topic,
            report=final_state["final_report"],
            sub_questions=final_state["sub_questions"],
            num_sources=len(final_state.get("research_results", [])),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search-memory")
async def search_memory(query: str, k: int = 5):
    """搜索历史研究记忆"""
    results = research_memory.search_similar(query, k=k)
    return {"query": query, "results": results}


@app.get("/health")
async def health():
    return {"status": "ok"}


# 启动: uvicorn src.api.main:app --reload --port 8000
