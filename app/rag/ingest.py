"""定时/手动：扫描 policies 目录下 PDF，按 namespace 分块并写入 FAISS。"""
from pathlib import Path
from typing import List

from langchain_core.documents import Document

from app.rag.faiss_store import create_and_save_from_docs, get_embeddings
from app.rag.pdf_loader import load_and_chunk_pdf

try:
    from config.settings import settings
    POLICIES_DIR = Path(settings.policies_dir)
    CHUNK_SIZE = getattr(settings, "chunk_size", 500)
    CHUNK_OVERLAP = getattr(settings, "chunk_overlap", 50)
except Exception:
    POLICIES_DIR = Path(__file__).resolve().parents[2] / "policies"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50


def get_policies_dir() -> Path:
    """返回政策文档根目录（相对路径时基于项目根解析）。"""
    if not POLICIES_DIR.is_absolute():
        return Path(__file__).resolve().parents[2] / POLICIES_DIR
    return POLICIES_DIR


def ingest_policies(namespace: str = "default") -> int:
    """
    扫描 policies 目录下所有 PDF，分块后写入 FAISS（指定 namespace）。
    返回本次处理的文档块数量。
    """
    root = get_policies_dir()
    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)
        return 0
    all_docs: List[Document] = []
    for pdf_path in root.glob("**/*.pdf"):
        chunks = load_and_chunk_pdf(pdf_path, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        for c in chunks:
            all_docs.append(
                Document(page_content=c["content"], metadata=c.get("metadata", {}))
            )
    if not all_docs:
        return 0
    create_and_save_from_docs(namespace, all_docs, get_embeddings())
    return len(all_docs)


def ingest_all_namespaces(namespaces: List[str] = None) -> dict:
    """对多个 namespace 分别做入库；默认仅 default。返回 { namespace: chunk_count }。"""
    if namespaces is None:
        namespaces = ["default"]
    result = {}
    for ns in namespaces:
        result[ns] = ingest_policies(ns)
    return result
