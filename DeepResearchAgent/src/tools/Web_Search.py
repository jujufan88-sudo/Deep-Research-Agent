# from langchain_core.tools import tool
# from tavily import TavilyClient
# from src.utils.config import TAVILY_API_KEY
# import re
#
#
# def get_tavily_client() -> TavilyClient:
#     return TavilyClient(api_key=TAVILY_API_KEY)
#
#
# def _clean_query(query: str) -> str:
#     """移除 site: 等搜索引擎专用语法，保留实际搜索词。"""
#     # 去掉所有 site:xxx 之类的内容
#     cleaned = re.sub(r'\b\w+:', '', query)
#     # 去掉多余空格
#     cleaned = re.sub(r'\s+', ' ', cleaned).strip()
#     return cleaned if cleaned else query.strip()
#
#
# @tool
# def search_web(query: str) -> str:
#     """Search the web for current information on a given topic.
#
#     Args:
#         query: The search query string. Use plain keywords, do not use search engine operators like site:.
#
#     Returns:
#         A string containing the search results with titles, URLs, and content snippets.
#     """
#     client = get_tavily_client()
#
#     # 清理无效的搜索引擎语法
#     clean_query = _clean_query(query)
#     if not clean_query:
#         return "错误：请提供实际的搜索关键词，不要只使用 site: 等运算符。请用普通关键词重新搜索。"
#
#     try:
#         response = client.search(query=clean_query, max_results=5)
#     except Exception as e:
#         return f"搜索出错: {e}。请换一组关键词重试。"
#
#     results = []
#     for i, result in enumerate(response.get("results", []), 1):
#         title = result.get("title", "No title")
#         url = result.get("url", "")
#         content = result.get("content", "No content")
#         results.append(f"[{i}] {title}\n    URL: {url}\n    {content}\n")
#
#     return "\n".join(results) if results else "No results found."
#
#
#




from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun


# 初始化 DuckDuckGo 搜索，不需要 API Key
search = DuckDuckGoSearchRun(max_results=5)


@tool
def search_web(query: str) -> str:
    """Search the web for current information on a given topic using DuckDuckGo.

    Args:
        query: The search query string. Use plain keywords for best results.

    Returns:
        A string containing the search results with titles, links, and snippets.
    """
    if not query or not query.strip():
        return "错误：请提供搜索关键词。"

    try:
        result = search.run(query)
        return result if result else "No results found."
    except Exception as e:
        return f"搜索出错: {e}。请换一组关键词重试。"
