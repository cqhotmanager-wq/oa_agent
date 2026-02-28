"""测试 RAG 检索与 PDF 分块."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from app.rag.faiss_store import get_embeddings, load_faiss, search_faiss
from app.rag.pdf_loader import chunk_texts, load_and_chunk_pdf


def test_chunk_texts():
    texts = ["第一段内容。", "第二段内容更长一些。" * 50]
    chunks = chunk_texts(texts, chunk_size=100, chunk_overlap=10)
    assert len(chunks) >= 1
    assert "content" in chunks[0] and "metadata" in chunks[0]


def test_search_faiss_empty_namespace():
    # 未构建过的 namespace 应返回空
    docs = search_faiss("__nonexistent_ns__", "测试", top_k=2)
    assert docs == []
