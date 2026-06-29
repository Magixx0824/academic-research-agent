from app.tools.document_tools import load_document, load_documents_from_directory


def preview_text(text: str, max_length: int = 300) -> str:
    """
    只显示前 max_length 个字符，避免终端输出过长。
    """
    text = text.replace("\n", " ")
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def test_single_txt():
    print("=" * 80)
    print("测试 1：读取单个 TXT 文件")
    print("=" * 80)

    file_path = "data/demo_docs/demo_note.txt"
    document = load_document(file_path)

    print(f"文件名：{document['file_name']}")
    print(f"文件类型：{document['file_type']}")
    print(f"字符数：{document['char_count']}")
    print(f"页数/页块数：{len(document['pages'])}")
    print(f"内容预览：{preview_text(document['text'])}")


def test_batch_documents():
    print("\n" + "=" * 80)
    print("测试 2：批量读取 demo_docs 文件夹")
    print("=" * 80)

    directory_path = "data/demo_docs"
    documents = load_documents_from_directory(directory_path)

    print(f"成功读取文档数量：{len(documents)}")

    for index, document in enumerate(documents, start=1):
        print("-" * 80)
        print(f"序号：{index}")
        print(f"文件名：{document['file_name']}")
        print(f"文件类型：{document['file_type']}")
        print(f"字符数：{document['char_count']}")
        print(f"页数/页块数：{len(document['pages'])}")
        print(f"内容预览：{preview_text(document['text'])}")


if __name__ == "__main__":
    test_single_txt()
    test_batch_documents()