"""定义研究流程的共享状态"""

from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
import operator


class SubResearch(BaseModel):
    """单个子问题的研究结果"""
    question: str
    answer: str
    sources: list[str] = Field(default_factory=list)
    confidence: str = "medium"


class ResearchState(TypedDict):
    """整个研究流程的共享状态"""

    # 输入
    topic: str

    # 规划阶段产出
    sub_questions: list[str]
    research_strategy: str

    # 研究阶段（不用 operator.add，直接覆盖，避免重试时重复）
    research_results: list[dict]

    # 评审阶段
    critiques: list[dict]
    needs_retry: bool

    # 最终输出
    final_report: str

    # 控制流
    iteration: int
    max_iterations: int
