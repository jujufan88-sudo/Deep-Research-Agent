# src/agents/synthesizer.py
"""综合 Agent — 将所有研究结果整合为结构化报告"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.utils.config import SMART_MODEL
import os
from dotenv import load_dotenv

load_dotenv()

def create_synthesizer():
    """创建报告综合 Agent"""

    llm = ChatOpenAI(
        model="mimo-v2.5",
        temperature=0.3,
        max_tokens=819,
        api_key=os.getenv("MIMO_API_KEY"),
        base_url="https://token-plan-cn.xiaomimimo.com/v1",
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert research report writer. Given research findings
from multiple sources, synthesize them into a comprehensive, well-structured report.

Report format:
# [Title]

## Executive Summary
[2-3 sentence overview of key findings]

## Key Findings
### [Finding 1 Topic]
[Detailed analysis with evidence]

### [Finding 2 Topic]
[Detailed analysis with evidence]

[... more findings as needed]

## Analysis & Implications
[Your analytical interpretation of what the findings mean]

## Limitations & Gaps
[What information was missing or uncertain]

## References
[Numbered list of all sources cited]

Rules:
1. Every claim must be backed by a cited source
2. Flag any conflicting information between sources
3. Distinguish between facts and inferences
4. Use clear, professional language
5. Be comprehensive but concise"""),

        ("human", """Research Topic: {topic}

Research Findings:
{findings}

Please synthesize these findings into a comprehensive research report.""")
    ])

    chain = prompt | llm

    return chain


# # 测试
# if __name__ == "__main__":
#     synthesizer = create_synthesizer()
#
#     # 模拟研究结果
#     mock_findings = """
# [Source 1 - Web Search] LangGraph is a library for building stateful,
# multi-actor applications with LLMs. It extends LangChain with cyclic graph
# capabilities. Released by LangChain Inc in early 2024.
#
# [Source 2 - ArXiv Paper] State machine approaches to agent orchestration
# show 23% improvement in task completion over simple chain-based approaches.
# Key advantage: explicit state management enables error recovery.
#
# [Source 3 - Web Search] Companies like Replit, LinkedIn, and Elastic are
# using LangGraph in production. LangGraph Platform offers deployment features.
# """
#
#     result = synthesizer.invoke({
#         "topic": "LangGraph for production agent systems",
#         "findings": mock_findings
#     })
#
#     print(result.content)
