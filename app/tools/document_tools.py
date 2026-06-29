from pathlib import Path
from typing import Dict, List, Any

from pypdf import PdfReader
from docx import Document as DocxDocument


SUPPORTED_SUFFIXES = {".txt", ".md", ".pdf", ".docx"}


def load_txt(file_path: str) -> str:
    """
    读取 TXT 或 Markdown 文档。

    为了兼容中文文件，依次尝试 utf-8、utf-8-sig、gbk 编码。
    """
    path = Path(file_path)

    encodings = ["utf-8", "utf-8-sig", "gbk"]
    last_error = None

    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding, errors="strict")
        except UnicodeDecodeError as error:
            last_error = error

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"无法识别文件编码，请检查文件是否为标准文本文件。原始错误：{last_error}",
    )


def load_pdf(file_path: str) -> Dict[str, Any]:
    """
    读取非扫描版 PDF 文档。

    返回：
    - text: 全文合并文本
    - pages: 按页保存的文本，方便后续做页码级引用
    """
    reader = PdfReader(file_path)
    pages: List[Dict[str, Any]] = []
    all_texts: List[str] = []

    for page_index, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        page_text = page_text.strip()

        pages.append(
            {
                "page_number": page_index,
                "text": page_text,
                "char_count": len(page_text),
            }
        )

        if page_text:
            all_texts.append(page_text)

    return {
        "text": "\n\n".join(all_texts).strip(),
        "pages": pages,
    }


def load_docx(file_path: str) -> str:
    """
    读取 Word docx 文档正文。

    第一版只读取段落文本，不处理表格、批注、脚注和图片。
    """
    doc = DocxDocument(file_path)

    paragraphs = []
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs).strip()


def load_document(file_path: str) -> Dict[str, Any]:
    """
    统一文档读取入口。

    输入：
    - file_path: 文档路径

    输出：
    - file_name: 文件名
    - source_path: 原始路径
    - file_type: 文件后缀
    - text: 文档正文
    - char_count: 正文字符数
    - pages: 页级信息。PDF 按页保存；TXT/MD/DOCX 暂时作为单页处理。
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")

    if not path.is_file():
        raise ValueError(f"路径不是文件：{file_path}")

    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(
            f"暂不支持的文件类型：{suffix}。当前支持：{sorted(SUPPORTED_SUFFIXES)}"
        )

    if suffix in {".txt", ".md"}:
        text = load_txt(str(path)).strip()
        pages = [
            {
                "page_number": 1,
                "text": text,
                "char_count": len(text),
            }
        ]

    elif suffix == ".pdf":
        pdf_result = load_pdf(str(path))
        text = pdf_result["text"]
        pages = pdf_result["pages"]

    elif suffix == ".docx":
        text = load_docx(str(path)).strip()
        pages = [
            {
                "page_number": 1,
                "text": text,
                "char_count": len(text),
            }
        ]

    else:
        raise ValueError(f"暂不支持的文件类型：{suffix}")

    if not text.strip():
        raise ValueError(
            f"未能从文件中提取到有效文本：{file_path}。"
            f"如果这是 PDF，可能是扫描版或图片型 PDF。"
        )

    return {
        "file_name": path.name,
        "source_path": str(path),
        "file_type": suffix,
        "text": text,
        "char_count": len(text),
        "pages": pages,
    }


def load_documents_from_directory(directory_path: str) -> List[Dict[str, Any]]:
    """
    批量读取一个文件夹中的支持格式文档。

    注意：
    - 只读取当前文件夹第一层文件；
    - 不递归读取子文件夹；
    - 不支持的文件会被跳过。
    """
    directory = Path(directory_path)

    if not directory.exists():
        raise FileNotFoundError(f"文件夹不存在：{directory_path}")

    if not directory.is_dir():
        raise ValueError(f"路径不是文件夹：{directory_path}")

    documents = []

    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_SUFFIXES:
            try:
                document = load_document(str(file_path))
                documents.append(document)
            except Exception as error:
                print(f"[读取失败] {file_path.name}: {error}")

    return documents