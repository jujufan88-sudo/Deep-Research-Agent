# src/tools/arxiv_search.py
"""ArXiv 学术论文搜索工具"""

from langchain_core.tools import tool
import arxiv


@tool
def search_arxiv(query: str) -> str:
    """Search ArXiv for academic papers related to a given topic.

    Args:
        query: The search query for academic papers.

    Returns:
        A string containing paper titles, authors, publication dates, and abstracts.
    """
    client = arxiv.Client(
        page_size=20,          # 每页少取一些
        delay_seconds=3.0,     # 每次请求间隔 3 秒（关键！）
        num_retries=3          # 失败重试次数
    )
    search = arxiv.Search(
        query=query,
        max_results=20,        # 不要一次拉 100 条
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending
    )


    results = []
    for i, paper in enumerate(client.results(search), 1):
        title = paper.title
        authors = ", ".join([a.name for a in paper.authors[:3]])
        published = paper.published.strftime("%Y-%m-%d")
        summary = paper.summary[:500]
        url = paper.entry_id

        results.append(
            f"[{i}] {title}\n"
            f"    Authors: {authors}\n"
            f"    Published: {published}\n"
            f"    URL: {url}\n"
            f"    Summary: {summary}...\n"
        )

    return "\n".join(results) if results else "No papers found."
