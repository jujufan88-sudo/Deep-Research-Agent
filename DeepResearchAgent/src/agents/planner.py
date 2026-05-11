# src/agents/planner.py
"""规划 Agent — 将研究主题拆解为子问题"""

import json
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from src.utils.config import SMART_MODEL

load_dotenv()


class ResearchPlan(BaseModel):
    """研究计划的数据结构"""
    topic: str = Field(description="原始研究主题")
    sub_questions: list[str] = Field(
        description="拆解后的子研究问题列表"
    )
    research_strategy: str = Field(
        description="简要说明研究策略"
    )


def create_planner():
    """创建规划 Agent"""

    llm = ChatOpenAI(
        model=SMART_MODEL,
        temperature=0,
        api_key=os.getenv("MIMO_API_KEY"),
        base_url="https://token-plan-cn.xiaomimimo.com/v1",
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert research planner. Given a research topic,
break it down into 2 specific, answerable sub-questions.

You MUST respond with ONLY a valid JSON object in this exact format, nothing else:

{{
    "topic": "the original research topic",
    "sub_questions": ["question 1", "question 2", "question 3"],
    "research_strategy": "brief description of research strategy"
}}

Rules for good sub-questions:
1. Each sub-question should be specific enough to search for directly
2. Sub-questions should cover different aspects of the topic
3. Order them from foundational to advanced
4. Include at least one question about recent developments"""),

        ("human", "Research topic: {topic}")
    ])

    chain = prompt | llm

    return chain


def parse_plan(raw_content: str, topic: str) -> ResearchPlan:
    """从 LLM 输出中解析研究计划，带容错处理"""

    # 尝试直接解析
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        # 尝试提取 JSON 块（LLM 可能会包裹 ```json ... ```）
        import re
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            # 最后的兜底：把整段输出当作一个子问题
            data = {
                "topic": topic,
                "sub_questions": [raw_content.strip()],
                "research_strategy": "Direct search"
            }

    # 确保所有字段存在
    data.setdefault("topic", topic)
    data.setdefault("research_strategy", "General research")
    if not data.get("sub_questions"):
        data["sub_questions"] = [topic]

    return ResearchPlan(**data)


# # 测试
# if __name__ == "__main__":
#     planner = create_planner()
#
#     raw = planner.invoke({"topic": "How are companies building production LLM agents in 2025?"})
#     plan = parse_plan(raw.content, "How are companies building production LLM agents in 2025?")
#
#     print(f"Topic: {plan.topic}")
#     print(f"Strategy: {plan.research_strategy}")
#     print(f"\nSub-questions:")
#     for i, q in enumerate(plan.sub_questions, 1):
#         print(f"  {i}. {q}")
