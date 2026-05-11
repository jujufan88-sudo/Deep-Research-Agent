# src/tools/wiki_search.py
"""Wikipedia 搜索工具"""

from langchain_core.tools import tool
import wikipedia


@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for encyclopedic information about a topic.

    Args:
        query: The search query for Wikipedia.

    Returns:
        A summary of the Wikipedia article and its URL.
    """
    try:
        # 先搜索最相关的页面标题
        page_titles = wikipedia.search(query, results=3)

        results = []
        for title in page_titles[:2]:  # 取前2个
            try:
                page = wikipedia.page(title, auto_suggest=False)
                summary = page.summary[:600]
                results.append(
                    f"Title: {page.title}\n"
                    f"URL: {page.url}\n"
                    f"Summary: {summary}...\n"
                )
            except wikipedia.DisambiguationError as e:
                # 歧义页面，取第一个选项重试
                try:
                    page = wikipedia.page(e.options[0])
                    summary = page.summary[:600]
                    results.append(f"Title: {page.title}\nSummary: {summary}...\n")
                except Exception:
                    continue
            except wikipedia.PageError:
                continue

        return "\n---\n".join(results) if results else "No Wikipedia articles found."
    except Exception as e:
        return f"Wikipedia search error: {str(e)}"
