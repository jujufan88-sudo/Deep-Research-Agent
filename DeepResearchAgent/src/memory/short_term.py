# src/memory/short_term.py
"""短期记忆 — 对话上下文管理"""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from collections import deque


class ConversationMemory:
    """管理对话历史，支持滑动窗口截断"""

    def __init__(self, max_messages: int = 20):
        self.messages: deque = deque(maxlen=max_messages)
        self.system_prompt = ""

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def add_user_message(self, content: str):
        self.messages.append(HumanMessage(content=content))

    def add_ai_message(self, content: str):
        self.messages.append(AIMessage(content=content))

    def get_messages(self) -> list:
        """获取完整对话历史"""
        msgs = []
        if self.system_prompt:
            msgs.append(SystemMessage(content=self.system_prompt))
        msgs.extend(list(self.messages))
        return msgs

    def get_context_string(self) -> str:
        """获取纯文本格式的对话历史"""
        lines = []
        for msg in self.messages:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            lines.append(f"{role}: {msg.content[:200]}")
        return "\n".join(lines)

    def clear(self):
        self.messages.clear()
