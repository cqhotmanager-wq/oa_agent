"""PDF 解析与分块：按页加载文本、按长度与重叠分块。"""
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_pdf_text(pdf_path: Path) -> List[str]:
    """加载单个 PDF 的文本，按页返回非空字符串列表。"""
    loader = PyPDFLoader(str(pdf_path))
    pages = loader.load()
    return [p.page_content for p in pages if p.page_content.strip()]


def chunk_texts(
    texts: List[str],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[dict]:
    """将文本列表按指定大小与重叠分块，返回 [{"content": "...", "metadata": {...}}, ...]。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    result = []
    for i, text in enumerate(texts):
        for chunk in splitter.split_text(text):
            result.append({"content": chunk, "metadata": {"source_index": i}})
    return result


def load_and_chunk_pdf(
    pdf_path: Path,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[dict]:
    """加载 PDF 全文后按 chunk_size/chunk_overlap 分块，metadata 中记录来源文件名。"""
    texts = load_pdf_text(pdf_path)
    if not texts:
        return []
    full = "\n\n".join(texts)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = splitter.split_text(full)
    return [{"content": c, "metadata": {"source": str(pdf_path.name)}} for c in chunks]
