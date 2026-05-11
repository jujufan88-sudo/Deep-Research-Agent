from dotenv import load_dotenv
import os

load_dotenv()

MIMO_API_KEY = os.getenv("MIMO_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

# 模型配置
FAST_MODEL = "mimo-v2.5"      # 用于简单任务：搜索查询改写、格式化
SMART_MODEL = "mimo-v2.5-pro"           # 用于复杂推理：规划、综合、评审
