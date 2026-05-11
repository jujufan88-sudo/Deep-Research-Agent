# src/memory/long_term.py
"""长期记忆 — 基于向量数据库的历史研究存储"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from datetime import datetime


class ResearchMemory:
    """存储和检索历史研究结果"""

    def __init__(self, persist_dir: str = "./chroma_db"):
        # 使用本地模型，不需要 API key
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",  # 中文优化，体积小，效果好
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self.vectorstore = Chroma(
            collection_name="research_history",
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
        )

    def save_research(self, topic: str, report: str, metadata: dict = None):
        """保存一次研究结果"""
        meta = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {}),
        }

        chunks = self._split_report(report)

        for i, chunk in enumerate(chunks):
            self.vectorstore.add_texts(
                texts=[chunk],
                metadatas=[{**meta, "chunk_index": i}],
            )

        print(f"  已保存 {len(chunks)} 个文本块到长期记忆")

    def search_similar(self, query: str, k: int = 5) -> list[dict]:
        """搜索与查询相关的历史研究"""
        results = self.vectorstore.similarity_search_with_score(query, k=k)

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": score,
            }
            for doc, score in results
        ]

    def _split_report(self, report: str, chunk_size: int = 1000) -> list[str]:
        """按段落切分报告"""
        paragraphs = report.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [report]
