from pathlib import Path
from typing import Any, Dict, List


def _normalize_text(text: str) -> str:
    """
    对文本做基础清洗。

    第一版只做轻量处理：
    - 去除首尾空白
    - 统一换行
    - 避免多个空白字符影响切分
    """
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines).strip()


def _safe_stem(file_name: str) -> str:
    """
    根据文件名生成安全的 chunk_id 前缀。

    例如：
    demo_paper_cn.pdf -> demo_paper_cn
    """
    return Path(file_name).stem.replace(" ", "_")


def split_text(
    text: str,
    chunk_size: int = 700,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    """
    将一段文本切分为多个 chunk。

    参数：
    - text: 原始文本
    - chunk_size: 每个 chunk 的最大字符数
    - overlap: 相邻 chunk 的重叠字符数

    返回：
    - chunk_index: 当前文本内部的 chunk 序号，从 1 开始
    - content: chunk 正文
    - start_char: chunk 在当前文本中的起始位置
    - end_char: chunk 在当前文本中的结束位置
    - char_count: chunk 字符数
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")

    if overlap < 0:
        raise ValueError("overlap 不能小于 0")

    if overlap >= chunk_size:
        raise ValueError("overlap 必须小于 chunk_size，否则会导致死循环")

    text = _normalize_text(text)

    if not text:
        return []

    chunks: List[Dict[str, Any]] = []
    start = 0
    chunk_index = 1
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "content": chunk_text,
                    "start_char": start,
                    "end_char": end,
                    "char_count": len(chunk_text),
                }
            )
            chunk_index += 1

        if end >= text_length:
            break

        start = end - overlap

    return chunks


def split_document(
    document: Dict[str, Any],
    chunk_size: int = 700,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    """
    将 load_document() 输出的一篇文档切分成带 metadata 的 chunks。

    输入 document 结构来自 document_tools.load_document()：
    {
        "file_name": "...",
        "source_path": "...",
        "file_type": "...",
        "text": "...",
        "char_count": ...,
        "pages": [...]
    }

    输出：
    [
        {
            "chunk_id": "...",
            "content": "...",
            "metadata": {...}
        }
    ]
    """
    required_fields = ["file_name", "source_path", "file_type", "text", "pages"]
    for field in required_fields:
        if field not in document:
            raise KeyError(f"document 缺少必要字段：{field}")

    file_name = document["file_name"]
    source_path = document["source_path"]
    file_type = document["file_type"]
    file_stem = _safe_stem(file_name)

    all_chunks: List[Dict[str, Any]] = []
    global_chunk_index = 1

    pages = document.get("pages") or []

    # 优先按页切分，便于后续返回页码来源。
    # TXT / MD / DOCX 在第一模块中被处理为 page_number=1。
    for page in pages:
        page_number = page.get("page_number", 1)
        page_text = page.get("text", "")

        page_chunks = split_text(
            text=page_text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for page_chunk in page_chunks:
            chunk_id = f"{file_stem}_p{page_number:03d}_c{global_chunk_index:04d}"

            all_chunks.append(
                {
                    "chunk_id": chunk_id,
                    "content": page_chunk["content"],
                    "metadata": {
                        "file_name": file_name,
                        "source_path": source_path,
                        "file_type": file_type,
                        "page_number": page_number,
                        "chunk_index": global_chunk_index,
                        "page_chunk_index": page_chunk["chunk_index"],
                        "start_char": page_chunk["start_char"],
                        "end_char": page_chunk["end_char"],
                        "char_count": page_chunk["char_count"],
                    },
                }
            )

            global_chunk_index += 1

    if not all_chunks:
        raise ValueError(f"文档未生成任何 chunk：{file_name}")

    return all_chunks


def split_documents(
    documents: List[Dict[str, Any]],
    chunk_size: int = 700,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    """
    批量切分多篇文档。
    """
    all_chunks: List[Dict[str, Any]] = []

    for document in documents:
        try:
            chunks = split_document(
                document=document,
                chunk_size=chunk_size,
                overlap=overlap,
            )
            all_chunks.extend(chunks)
        except Exception as error:
            file_name = document.get("file_name", "未知文件")
            print(f"[切分失败] {file_name}: {error}")

    return all_chunks


def preview_chunk(chunk: Dict[str, Any], max_length: int = 120) -> str:
    """
    生成 chunk 内容预览，方便终端测试。
    """
    content = chunk.get("content", "").replace("\n", " ")
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."