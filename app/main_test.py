from app.tools.document_tools import load_document, load_documents_from_directory
from app.tools.rag_tools import split_document, split_documents, preview_chunk


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

    return document


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

    return documents


def test_single_document_chunking(document):
    print("\n" + "=" * 80)
    print("测试 3：单个文档 chunk 切分")
    print("=" * 80)

    chunks = split_document(
        document=document,
        chunk_size=120,
        overlap=30,
    )

    print(f"原始文件：{document['file_name']}")
    print(f"生成 chunk 数量：{len(chunks)}")

    for chunk in chunks[:3]:
        print("-" * 80)
        print(f"chunk_id：{chunk['chunk_id']}")
        print(f"metadata：{chunk['metadata']}")
        print(f"内容预览：{preview_chunk(chunk)}")

    return chunks


def test_batch_chunking(documents):
    print("\n" + "=" * 80)
    print("测试 4：批量文档 chunk 切分")
    print("=" * 80)

    chunks = split_documents(
        documents=documents,
        chunk_size=700,
        overlap=100,
    )

    print(f"输入文档数量：{len(documents)}")
    print(f"生成 chunk 总数：{len(chunks)}")

    file_chunk_count = {}
    for chunk in chunks:
        file_name = chunk["metadata"]["file_name"]
        file_chunk_count[file_name] = file_chunk_count.get(file_name, 0) + 1

    print("\n各文档 chunk 数量：")
    for file_name, count in file_chunk_count.items():
        print(f"- {file_name}: {count}")

    print("\n前 5 个 chunk 预览：")
    for chunk in chunks[:5]:
        print("-" * 80)
        print(f"chunk_id：{chunk['chunk_id']}")
        print(f"来源：{chunk['metadata']['file_name']} | 第 {chunk['metadata']['page_number']} 页")
        print(f"字符数：{chunk['metadata']['char_count']}")
        print(f"内容预览：{preview_chunk(chunk)}")

    return chunks


if __name__ == "__main__":
    txt_document = test_single_txt()
    documents = test_batch_documents()
    test_single_document_chunking(txt_document)
    test_batch_chunking(documents)