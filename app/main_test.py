from app.tools.document_tools import load_document, load_documents_from_directory
from app.tools.rag_tools import split_document, split_documents, preview_chunk
from app.services.vector_service import VectorService, preview_search_result
from app.services.llm_service import LLMService, format_rag_answer
from app.tools.paper_tools import PaperReadingTool, format_paper_reading_card
from app.tools.compare_tools import PaperCompareTool, format_paper_comparison_result
from app.tools.review_tools import LiteratureReviewTool, format_literature_review_framework
from app.tools.writing_tools import AcademicWritingCheckTool, format_writing_check_result
from app.tools.workflow_tools import AcademicResearchWorkflow, format_workflow_result

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


def test_vector_index_and_search(chunks):
    print("\n" + "=" * 80)
    print("测试 5：Chroma 向量库写入与检索")
    print("=" * 80)

    vector_service = VectorService(
        persist_dir="storage/chroma",
        collection_name="academic_chunks",
        reset_collection=True,
    )

    inserted_count = vector_service.add_chunks(chunks)
    total_count = vector_service.count()

    print(f"本次写入 chunk 数量：{inserted_count}")
    print(f"向量库当前 chunk 总数：{total_count}")

    test_queries = [
        "这篇论文使用了什么研究方法？",
        "人工智能如何影响企业创新韧性？",
        "What is the role of digital technology in customer relationship performance?",
    ]

    for query in test_queries:
        print("\n" + "-" * 80)
        print(f"检索问题：{query}")

        results = vector_service.search(query=query, top_k=3)

        print(f"返回结果数量：{len(results)}")

        for result in results:
            metadata = result["metadata"]
            print("-" * 40)
            print(f"rank：{result['rank']}")
            print(f"distance：{result['distance']}")
            print(
                f"来源：{metadata.get('file_name')} | "
                f"第 {metadata.get('page_number')} 页 | "
                f"chunk_index={metadata.get('chunk_index')}"
            )
            print(f"内容预览：{preview_search_result(result)}")

    return vector_service

def test_rag_answer(vector_service):
    print("\n" + "=" * 80)
    print("测试 6：基础 RAG 问答生成")
    print("=" * 80)

    llm_service = LLMService()
    print(f"当前 LLM_PROVIDER：{llm_service.provider}")
    print(f"当前 LLM_MODEL：{llm_service.model}")

    test_questions = [
        "人工智能如何影响企业创新韧性？",
    ]

    for question in test_questions:
        print("\n" + "-" * 80)
        print(f"RAG 问题：{question}")

        contexts = vector_service.search(
            query=question,
            top_k=2,
        )

        rag_result = llm_service.answer_with_contexts(
            question=question,
            contexts=contexts,
        )

        print(format_rag_answer(rag_result))

def test_single_paper_reading(vector_service):
    print("\n" + "=" * 80)
    print("测试 7：单篇论文精读工具")
    print("=" * 80)

    llm_service = LLMService()

    print(f"当前 LLM_PROVIDER：{llm_service.provider}")
    print(f"当前 LLM_MODEL：{llm_service.model}")

    paper_tool = PaperReadingTool(
        vector_service=vector_service,
        llm_service=llm_service,
    )

    reading_result = paper_tool.read_full_card(
        file_name="demo_paper_cn.pdf",
        top_k=4,
    )

    print(format_paper_reading_card(reading_result))

    return reading_result

def test_paper_comparison(vector_service):
    print("\n" + "=" * 80)
    print("测试 8：多篇论文对比工具")
    print("=" * 80)

    llm_service = LLMService()

    print(f"当前 LLM_PROVIDER：{llm_service.provider}")
    print(f"当前 LLM_MODEL：{llm_service.model}")

    compare_tool = PaperCompareTool(
        vector_service=vector_service,
        llm_service=llm_service,
    )

    compare_result = compare_tool.compare_papers(
        file_names=[
            "demo_paper_cn.pdf",
            "demo_paper_en.pdf",
        ],
        dimensions=[
            "research_question",
            "data_and_method",
            "main_findings",
        ],
        top_k=4,
        include_synthesis=True,
    )

    print(format_paper_comparison_result(compare_result))

    return compare_result

def test_literature_review_framework(vector_service):
    print("\n" + "=" * 80)
    print("测试 9：文献综述框架生成工具")
    print("=" * 80)

    llm_service = LLMService()

    print(f"当前 LLM_PROVIDER：{llm_service.provider}")
    print(f"当前 LLM_MODEL：{llm_service.model}")

    review_tool = LiteratureReviewTool(
        vector_service=vector_service,
        llm_service=llm_service,
    )

    review_result = review_tool.generate_review_framework(
        topic="企业创新能力与数字技术应用的影响机制",
        file_names=[
            "demo_paper_cn.pdf",
            "demo_paper_en.pdf",
        ],
        dimensions=[
            "research_question",
            "data_and_method",
            "main_findings",
        ],
        top_k=4,
    )

    print(format_literature_review_framework(review_result))

    return review_result

def test_academic_writing_check():
    print("\n" + "=" * 80)
    print("测试 10：学术写作检查工具")
    print("=" * 80)

    llm_service = LLMService()

    print(f"当前 LLM_PROVIDER：{llm_service.provider}")
    print(f"当前 LLM_MODEL：{llm_service.model}")

    writing_tool = AcademicWritingCheckTool(
        llm_service=llm_service,
    )

    demo_text = """
    企业创新能力是企业获得竞争优势的重要来源。随着外部环境不断变化，企业需要通过合作创新
    来提升自身能力。合作创新可以帮助企业获得外部资源，也可以提高企业面对风险的能力。
    但是现有研究对合作创新如何影响企业创新能力的机制研究还不够充分。因此，本文认为组织韧性
    可能在合作创新和持续创新能力之间发挥作用，同时技术环境动荡性也可能影响这种关系。
    """

    check_result = writing_tool.check_text(
        text=demo_text,
        writing_goal="理论机制段落写作检查",
        focus=[
            "structure",
            "logic",
            "academic_style",
            "evidence",
            "mechanism",
        ],
    )

    print(format_writing_check_result(check_result))

    return check_result

def test_academic_research_workflow(vector_service):
    print("\n" + "=" * 80)
    print("测试 11：统一学术研究工作流")
    print("=" * 80)

    llm_service = LLMService()

    print(f"当前 LLM_PROVIDER：{llm_service.provider}")
    print(f"当前 LLM_MODEL：{llm_service.model}")

    workflow = AcademicResearchWorkflow(
        vector_service=vector_service,
        llm_service=llm_service,
    )

    workflow_result = workflow.run_task(
        task_type="rag_answer",
        question="人工智能如何影响企业创新韧性？",
        top_k=2,
    )

    print(format_workflow_result(workflow_result))

    return workflow_result

if __name__ == "__main__":
    txt_document = test_single_txt()
    documents = test_batch_documents()
    test_single_document_chunking(txt_document)
    chunks = test_batch_chunking(documents)
    vector_service = test_vector_index_and_search(chunks)
    test_rag_answer(vector_service)

    # 第五模块已验收，默认注释，避免重复消耗 API。
    # test_single_paper_reading(vector_service)

    # 第六模块已验收，默认注释，避免重复消耗 API。
    # test_paper_comparison(vector_service)

    # 第七模块已验收，默认注释，避免重复消耗 API。
    # test_literature_review_framework(vector_service)

    # 第八模块已验收，默认注释，避免重复消耗 API。
    # test_academic_writing_check()

    test_academic_research_workflow(vector_service)