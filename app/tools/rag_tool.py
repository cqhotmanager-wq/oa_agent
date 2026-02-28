"""RAG 检索工具：封装 FAISS 检索为 LangChain tool，供 Agent 调用。"""
from typing import Optional

from langchain_core.tools import tool
from langchain_core.documents import Document

from app.rag.faiss_store import search_faiss

try:
    from config.settings import settings
    RAG_TOP_K = getattr(settings, "rag_top_k", 5)
except Exception:
    RAG_TOP_K = 5


def make_rag_tool(namespace: str = "default", top_k: int = None) -> tool:
    """创建一个绑定到指定 namespace 的 RAG 检索工具，返回 top_k 条结果拼接成的字符串。"""
    k = top_k or RAG_TOP_K

    @tool
    def search_knowledge(query: str) -> str:
        """在规章制度/知识库中检索与问题相关的内容。参数：query 用户问题。"""
        docs = search_faiss(namespace, query, top_k=k)
        if not docs:
            return "未找到相关制度或文档，请换一种说法或联系管理员补充政策文档。"
        parts = [d.page_content for d in docs]
        return "\n\n---\n\n".join(parts)
    return search_knowledge
