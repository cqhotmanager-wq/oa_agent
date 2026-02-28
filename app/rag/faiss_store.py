"""FAISS 向量存储：多 namespace 索引、保存/加载、相似度检索。"""
from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

try:
    from config.settings import settings
except Exception:
    settings = None


def get_embeddings() -> Embeddings:
    """获取嵌入模型：有配置用 OpenAI 兼容接口，否则用 FakeEmbeddings 便于本地测试。"""
    if settings and getattr(settings, "openai_api_key", None):
        return OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url,
        )
    from langchain_community.embeddings import FakeEmbeddings
    return FakeEmbeddings(size=384)


def get_faiss_index_dir() -> Path:
    """返回 FAISS 索引根目录（可配置），不存在则创建。"""
    if settings and getattr(settings, "faiss_index_dir", None):
        base = Path(settings.faiss_index_dir)
    else:
        base = Path(__file__).resolve().parents[2] / "data" / "faiss"
    base.mkdir(parents=True, exist_ok=True)
    return base


def path_for_namespace(namespace: str) -> Path:
    """某 namespace 对应的 FAISS 索引文件路径（不含扩展名的目录形式由 save_local 决定）。"""
    return get_faiss_index_dir() / f"{namespace}.faiss"


def save_faiss(store: FAISS, namespace: str) -> None:
    """将 FAISS 向量库保存到磁盘，以 namespace 为索引名。"""
    path = path_for_namespace(namespace)
    path.parent.mkdir(parents=True, exist_ok=True)
    store.save_local(str(path.parent), index_name=namespace)


def load_faiss(namespace: str, embeddings: Optional[Embeddings] = None) -> Optional[FAISS]:
    """从磁盘加载指定 namespace 的 FAISS 索引；不存在返回 None。"""
    base = path_for_namespace(namespace).parent
    index_path = base / f"{namespace}.faiss"
    if not index_path.exists():
        return None
    emb = embeddings or get_embeddings()
    return FAISS.load_local(str(base), emb, allow_dangerous_deserialization=True, index_name=namespace)


def create_and_save_from_docs(
    namespace: str,
    documents: List[Document],
    embeddings: Optional[Embeddings] = None,
) -> FAISS:
    """用文档列表构建 FAISS 并保存到该 namespace；返回构建好的 store。"""
    emb = embeddings or get_embeddings()
    store = FAISS.from_documents(documents, emb)
    save_faiss(store, namespace)
    return store


def search_faiss(namespace: str, query: str, top_k: int = 5) -> List[Document]:
    """在指定 namespace 的 FAISS 中做相似度检索，返回 top_k 条 Document。"""
    store = load_faiss(namespace)
    if store is None:
        return []
    return store.similarity_search(query, k=top_k)
