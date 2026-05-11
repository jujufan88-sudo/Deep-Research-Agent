# src/workflows/research_flow.py
"""LangGraph 工作流定义 — 多 Agent 协作研究"""

import os
import json
import re
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.workflows.state import ResearchState
from src.agents.planner import create_planner, parse_plan, ResearchPlan
from src.agents.researcher import create_researcher_agent
from src.agents.synthesizer import create_synthesizer
from src.utils.config import SMART_MODEL

load_dotenv()


# ==========================================
# 共享 LLM（避免每个节点重复创建）
# ==========================================

def _get_llm(temperature=0, max_tokens=4096):
    return ChatOpenAI(
        model=SMART_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=os.getenv("MIMO_API_KEY"),
        base_url="https://token-plan-cn.xiaomimimo.com/v1",
    )


# ==========================================
# 节点函数
# ==========================================

def plan_node(state: ResearchState) -> dict:
    """规划节点：拆解主题为子问题"""
    planner = create_planner()
    raw = planner.invoke({"topic": state["topic"]})

    # 手动解析 JSON（不用 with_structured_output）
    plan = parse_plan(raw.content, state["topic"])

    return {
        "sub_questions": plan.sub_questions,
        "research_strategy": plan.research_strategy,
        "iteration": 0,
        "max_iterations": 3,
    }


def research_node(state: ResearchState) -> dict:
    """研究节点：对每个子问题执行搜索研究"""
    researcher = create_researcher_agent()
    results = []

    for i, question in enumerate(state["sub_questions"], 1):
        print(f"  研究子问题 {i}/{len(state['sub_questions'])}: {question[:50]}...")

        result = researcher.invoke({"messages": [
            {"role": "user", "content": question}
        ]})

        # 新版 create_agent 返回 messages 格式
        answer = result["messages"][-1].content

        results.append({
            "question": question,
            "answer": answer,
            "sources": [],  # 新版 agent 不返回 intermediate_steps，暂为空
        })

    return {
        "research_results": results,  # 直接覆盖，不累积
        "iteration": state["iteration"] + 1,
    }


def critique_node(state: ResearchState) -> dict:
    """评审节点：检查研究结果的质量和完整性"""
    llm = _get_llm()

    results_text = "\n\n".join([
        f"Q: {r['question']}\nA: {r['answer'][:500]}"
        for r in state["research_results"]
    ])

    messages = [
        SystemMessage(content="""You are a research quality reviewer. Evaluate research findings.
You MUST respond with EXACTLY one of these verdicts:
VERDICT: PASS
VERDICT: NEEDS_RETRY
一遍过，目前是审核阶段
Then on the next line, write:
REASON: your explanation"""),
        HumanMessage(content=f"""Topic: {state['topic']}

Findings:
{results_text}

Evaluate and respond with VERDICT: PASS or VERDICT: NEEDS_RETRY"""),
    ]

    response = llm.invoke(messages)
    verdict = response.content

    # ===== 调试信息 =====
    print(f"\n  [DEBUG] 第 {state['iteration']} 轮评审结果:")
    print(f"  [DEBUG] verdict 原文: {verdict[:200]}")
    print(f"  [DEBUG] 当前 iteration: {state['iteration']}, max: {state['max_iterations']}")
    # ====================

    # 改进判断逻辑：只有明确写 NEEDS_RETRY 才重试
    verdict_upper = verdict.upper()
    needs_retry = (
        "NEEDS_RETRY" in verdict_upper
        and "PASS" not in verdict_upper  # 如果同时出现 PASS，以 PASS 为准
        and state["iteration"] < state["max_iterations"]
    )

    print(f"  [DEBUG] needs_retry: {needs_retry}")

    return {
        "critiques": [{"verdict": verdict, "iteration": state["iteration"]}],
        "needs_retry": needs_retry,
    }



def synthesize_node(state: ResearchState) -> dict:
    """综合节点：生成最终报告"""
    synthesizer = create_synthesizer()

    findings_text = "\n\n".join([
        f"[Source {i+1}] Q: {r['question']}\nA: {r['answer']}"
        for i, r in enumerate(state["research_results"])
    ])

    report = synthesizer.invoke({
        "topic": state["topic"],
        "findings": findings_text,
    })

    return {"final_report": report.content}


# ==========================================
# 条件边
# ==========================================

def should_continue(state: ResearchState) -> str:
    if state.get("needs_retry", False):
        return "retry"
    return "done"


# ==========================================
# 构建图
# ==========================================

def build_research_graph():
    workflow = StateGraph(ResearchState)

    workflow.add_node("plan", plan_node)
    workflow.add_node("research", research_node)
    workflow.add_node("critique", critique_node)
    workflow.add_node("synthesize", synthesize_node)

    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "research")
    workflow.add_edge("research", "critique")

    workflow.add_conditional_edges(
        "critique",
        should_continue,
        {
            "retry": "research",
            "done": "synthesize",
        }
    )

    workflow.add_edge("synthesize", END)

    return workflow.compile()


# ==========================================
# 运行入口
# ==========================================

def run(topic: str) -> str:
    app = build_research_graph()

    initial_state = {
        "topic": topic,
        "sub_questions": [],
        "research_strategy": "",
        "research_results": [],
        "critiques": [],
        "needs_retry": False,
        "final_report": "",
        "iteration": 0,
        "max_iterations": 2,
    }

    final_state = app.invoke(initial_state)
    return final_state["final_report"]


if __name__ == "__main__":
    topic = input("请输入研究主题: ")
    report = run(topic)

    with open("research_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("\n报告已保存到 research_report.md")
    print(f"\n预览:\n{report[:500]}")
