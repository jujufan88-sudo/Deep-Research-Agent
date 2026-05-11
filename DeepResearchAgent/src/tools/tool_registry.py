from src.tools.Web_Search import search_web
from src.tools.Code_Executor import execute_python_code
from src.tools.Wiki_Search import search_wikipedia
from src.tools.Arxiv_Search import search_arxiv

# 所有工具列表，传给 Agent 使用
ALL_TOOLS = [search_web, search_arxiv, search_wikipedia, execute_python_code]

# 按用途分组
SEARCH_TOOLS = [search_web, search_arxiv, search_wikipedia]
RESEARCH_TOOLS = [search_web, search_arxiv]
ANALYSIS_TOOLS = [execute_python_code]
