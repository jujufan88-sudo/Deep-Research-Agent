# src/agents/researcher.py
"""研究 Agent — 使用 ReAct 模式执行信息检索"""
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.prebuilt import ToolNode

from src.tools.tool_registry import SEARCH_TOOLS

load_dotenv()

SYSTEM_PROMPT = """You are a thorough research assistant. Your job is to find accurate,
up-to-date information on a given topic by searching multiple sources.

Important rules:
1. Always search at least 2 different sources to cross-verify information
2. Include specific facts, numbers, and details from your search results
3. If search results conflict, note the discrepancy
4. Cite sources by mentioning where you found each piece of information."""


def create_researcher_agent():
    """创建研究 Agent"""

    llm = ChatOpenAI(
        model="mimo-v2.5",
        temperature=0,
        max_tokens=4096,
        api_key=os.getenv("MIMO_API_KEY"),
        base_url="https://token-plan-cn.xiaomimimo.com/v1",
    )

    # 先创建带错误处理的 ToolNode
    tool_node = ToolNode(
        tools=SEARCH_TOOLS,
        handle_tool_errors=True,  # 关键：工具出错时不抛异常，而是把错误信息返回给 LLM
    )

    agent = create_agent(
        model=llm,
        tools=SEARCH_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent


# # 测试
# if __name__ == "__main__":
#     researcher = create_researcher_agent()
#
#     result = researcher.invoke({
#         "messages": [
#             {"role": "user", "content": "回复我一个1—10的随机整数"}
#         ]
#     })
#
#     print("\n" + "=" * 60)
#     print("FINAL ANSWER:")
#     print("=" * 60)
#     print(result["messages"][-1].content)
