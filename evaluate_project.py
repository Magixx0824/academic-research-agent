import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.tools.document_tools import load_documents_from_directory
from app.tools.rag_tools import split_documents
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
from app.tools.workflow_tools import AcademicResearchWorkflow


SUPPORTED_DOC_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}

DEFAULT_CHUNK_SIZE = 700
DEFAULT_OVERLAP = 100

VECTOR_PERSIST_DIR = "storage/chroma"
VECTOR_COLLECTION_NAME = "academic_chunks"


@dataclass
class EvaluationItem:
    name: str
    passed: bool
    detail: str


def find_eval_doc_dir() -> Path:
    """
    自动选择评估文档目录。

    优先使用环境变量 EVAL_DOC_DIR；
    其次使用 data/raw_docs；
    如果 data/raw_docs 没有可解析文档，则回退到 data/demo_docs。
    """
    env_doc_dir = os.getenv("EVAL_DOC_DIR")

    if env_doc_dir:
        return PROJECT_ROOT / env_doc_dir

    raw_docs_dir = PROJECT_ROOT / "data" / "raw_docs"
    demo_docs_dir = PROJECT_ROOT / "data" / "demo_docs"

    if count_supported_files(raw_docs_dir) > 0:
        return raw_docs_dir

    return demo_docs_dir


def count_supported_files(directory: Path) -> int:
    """
    统计目录下可解析文档数量。
    """
    if not directory.exists():
        return 0

    return sum(
        1
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_DOC_EXTENSIONS
    )


def get_pdf_file_names(documents: List[Dict[str, Any]]) -> List[str]:
    """
    从已解析文档中提取 PDF 文件名。
    """
    pdf_files = []

    for document in documents:
        file_name = document.get("file_name", "")
        file_type = document.get("file_type", "")

        if file_type.lower() == ".pdf" or file_name.lower().endswith(".pdf"):
            pdf_files.append(file_name)

    return sorted(list(set(pdf_files)))


def is_valid_llm_answer(answer: str) -> bool:
    """
    判断 LLM 是否返回有效回答。
    """
    if not answer or not answer.strip():
        return False

    failed_markers = [
        "真实大模型 API 调用失败",
        "API 调用失败",
        "余额不足",
        "未配置 LLM_API_KEY",
        "模型未返回有效内容",
    ]

    return not any(marker in answer for marker in failed_markers)


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_step(message: str) -> None:
    print(f"[步骤] {message}")


def evaluate_document_parsing(doc_dir: Path) -> tuple[List[Dict[str, Any]], EvaluationItem]:
    print_step(f"读取文档目录：{doc_dir}")

    total_files = count_supported_files(doc_dir)

    if total_files == 0:
        return [], EvaluationItem(
            name="文档解析成功率",
            passed=False,
            detail=f"0/0 = 0.00% | 标准：≥ 80% | 未通过。目录中没有可解析文档。",
        )

    documents = load_documents_from_directory(str(doc_dir))

    valid_documents = [
        document
        for document in documents
        if document.get("text") and document.get("char_count", 0) > 0
    ]

    ratio = len(valid_documents) / total_files
    passed = ratio >= 0.80

    return documents, EvaluationItem(
        name="文档解析成功率",
        passed=passed,
        detail=(
            f"{len(valid_documents)}/{total_files} = {ratio:.2%} | "
            f"标准：≥ 80% | {'通过' if passed else '未通过'}"
        ),
    )


def evaluate_chunking(documents: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], EvaluationItem]:
    print_step("切分文档 chunks")

    if not documents:
        return [], EvaluationItem(
            name="文本切分可用性",
            passed=False,
            detail="0 chunks | 标准：> 0 | 未通过",
        )

    chunks = split_documents(
        documents,
        chunk_size=DEFAULT_CHUNK_SIZE,
        overlap=DEFAULT_OVERLAP,
    )

    valid_chunks = [
        chunk
        for chunk in chunks
        if chunk.get("content") and chunk.get("metadata")
    ]

    passed = len(valid_chunks) > 0 and len(valid_chunks) == len(chunks)

    return chunks, EvaluationItem(
        name="文本切分可用性",
        passed=passed,
        detail=(
            f"有效 chunks：{len(valid_chunks)}/{len(chunks)} | "
            f"标准：全部 chunk 应包含 content 和 metadata | "
            f"{'通过' if passed else '未通过'}"
        ),
    )


def evaluate_vector_index(chunks: List[Dict[str, Any]]) -> tuple[Optional[VectorService], EvaluationItem]:
    print_step("清空并重建 Chroma 向量索引")

    if not chunks:
        return None, EvaluationItem(
            name="向量索引可用性",
            passed=False,
            detail="无 chunks 可写入 | 未通过",
        )

    vector_service = VectorService(
        persist_dir=VECTOR_PERSIST_DIR,
        collection_name=VECTOR_COLLECTION_NAME,
        reset_collection=True,
    )

    added_count = vector_service.add_chunks(chunks)
    stored_count = vector_service.count()

    passed = stored_count == len(chunks)

    return vector_service, EvaluationItem(
        name="向量索引可用性",
        passed=passed,
        detail=(
            f"写入 chunks：{added_count} | 向量库总数：{stored_count} | "
            f"预期：{len(chunks)} | {'通过' if passed else '未通过'}"
        ),
    )


def evaluate_retrieval(vector_service: VectorService) -> EvaluationItem:
    print_step("执行基础检索测试")

    queries = [
        "研究问题",
        "研究方法",
        "主要结论",
        "变量测量",
        "理论基础",
    ]

    hit_count = 0

    for query in queries:
        results = vector_service.search(
            query=query,
            top_k=3,
        )

        if results:
            hit_count += 1

    ratio = hit_count / len(queries)
    passed = ratio >= 0.70

    return EvaluationItem(
        name="检索命中率",
        passed=passed,
        detail=(
            f"{hit_count}/{len(queries)} = {ratio:.2%} | "
            f"标准：≥ 70% | {'通过' if passed else '未通过'}"
        ),
    )


def evaluate_rag_answer(workflow: AcademicResearchWorkflow) -> EvaluationItem:
    print_step("执行基础 RAG 问答测试")

    try:
        result = workflow.run_task(
            task_type="rag_answer",
            question="人工智能如何影响企业创新韧性？",
            top_k=2,
        )

        answer = result.get("result", {}).get("answer", "")
        sources = result.get("result", {}).get("sources", [])

        passed = is_valid_llm_answer(answer) and len(sources) > 0

        return EvaluationItem(
            name="RAG 问答可用性",
            passed=passed,
            detail=(
                f"回答长度：{len(answer)} | 来源数量：{len(sources)} | "
                f"{'通过' if passed else '未通过'}"
            ),
        )

    except Exception as error:
        return EvaluationItem(
            name="RAG 问答可用性",
            passed=False,
            detail=f"运行异常：{error}",
        )


def evaluate_single_paper_reading(
    workflow: AcademicResearchWorkflow,
    pdf_files: List[str],
) -> EvaluationItem:
    print_step("执行单篇论文精读测试")

    if not pdf_files:
        return EvaluationItem(
            name="单篇精读可用性",
            passed=False,
            detail="未找到 PDF 文件 | 未通过",
        )

    try:
        result = workflow.run_task(
            task_type="single_paper_reading",
            file_name=pdf_files[0],
            sections=["research_question"],
            top_k=3,
        )

        task_result = result.get("result", {})
        sections = task_result.get("sections", [])

        passed = (
            task_result.get("section_count", 0) == 1
            and len(sections) == 1
            and bool(sections[0].get("answer"))
        )

        return EvaluationItem(
            name="单篇精读可用性",
            passed=passed,
            detail=(
                f"测试论文：{pdf_files[0]} | 维度数量：{task_result.get('section_count', 0)} | "
                f"{'通过' if passed else '未通过'}"
            ),
        )

    except Exception as error:
        return EvaluationItem(
            name="单篇精读可用性",
            passed=False,
            detail=f"运行异常：{error}",
        )


def evaluate_paper_comparison(
    workflow: AcademicResearchWorkflow,
    pdf_files: List[str],
) -> EvaluationItem:
    print_step("执行多篇论文对比测试")

    if len(pdf_files) < 2:
        return EvaluationItem(
            name="多篇对比可用性",
            passed=True,
            detail="PDF 数量少于 2，跳过测试 | 不计为失败",
        )

    try:
        result = workflow.run_task(
            task_type="paper_comparison",
            file_names=pdf_files[:2],
            dimensions=["research_question"],
            top_k=3,
            include_synthesis=False,
        )

        task_result = result.get("result", {})
        paper_count = task_result.get("paper_count", 0)
        dimension_count = task_result.get("dimension_count", 0)
        paper_summaries = task_result.get("paper_summaries", {})

        passed = (
            paper_count == 2
            and dimension_count == 1
            and len(paper_summaries) == 2
        )

        return EvaluationItem(
            name="多篇对比可用性",
            passed=passed,
            detail=(
                f"论文数量：{paper_count} | 维度数量：{dimension_count} | "
                f"{'通过' if passed else '未通过'}"
            ),
        )

    except Exception as error:
        return EvaluationItem(
            name="多篇对比可用性",
            passed=False,
            detail=f"运行异常：{error}",
        )


def evaluate_writing_check(workflow: AcademicResearchWorkflow) -> EvaluationItem:
    print_step("执行学术写作检查测试")

    demo_text = (
        "企业创新能力是企业获得竞争优势的重要来源。随着外部环境不断变化，"
        "企业需要通过合作创新来提升自身能力。合作创新可以帮助企业获得外部资源，"
        "也可以提高企业面对风险的能力。但是现有研究对合作创新如何影响企业创新能力"
        "的机制研究还不够充分。因此，本文认为组织韧性可能在合作创新和持续创新能力之间"
        "发挥作用，同时技术环境动荡性也可能影响这种关系。"
    )

    try:
        result = workflow.run_task(
            task_type="writing_check",
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

        task_result = result.get("result", {})
        check_text = task_result.get("check_result", "")

        expected_markers = [
            "总体判断",
            "主要问题",
            "修改建议",
        ]

        hit_count = sum(1 for marker in expected_markers if marker in check_text)
        passed = hit_count >= 2 and is_valid_llm_answer(check_text)

        return EvaluationItem(
            name="写作检查可用性",
            passed=passed,
            detail=(
                f"结构化标记命中：{hit_count}/{len(expected_markers)} | "
                f"回答长度：{len(check_text)} | {'通过' if passed else '未通过'}"
            ),
        )

    except Exception as error:
        return EvaluationItem(
            name="写作检查可用性",
            passed=False,
            detail=f"运行异常：{error}",
        )


def print_summary(evaluation_items: List[EvaluationItem]) -> None:
    print("\n" + "=" * 80)
    print("评估摘要")
    print("=" * 80)

    passed_count = 0

    for item in evaluation_items:
        if item.passed:
            passed_count += 1

        print(f"{item.name}：{item.detail}")

    total_count = len(evaluation_items)
    ratio = passed_count / total_count if total_count else 0

    print("-" * 80)
    print(f"总通过项：{passed_count}/{total_count} = {ratio:.2%}")

    if passed_count == total_count:
        print("项目评估结果：通过")
    else:
        print("项目评估结果：存在未通过项，需要检查上方日志")


def main() -> None:
    print("=" * 80)
    print("开始项目评估。")
    print("注意：即将清空当前 Chroma 向量索引，并重新建立评估索引。")
    print("=" * 80)

    doc_dir = find_eval_doc_dir()
    print(f"[配置] 评估文档目录：{doc_dir}")
    print(f"[配置] chunk_size={DEFAULT_CHUNK_SIZE}, overlap={DEFAULT_OVERLAP}")
    print(f"[配置] vector_collection={VECTOR_COLLECTION_NAME}")

    evaluation_items: List[EvaluationItem] = []

    documents, parsing_item = evaluate_document_parsing(doc_dir)
    evaluation_items.append(parsing_item)

    chunks, chunking_item = evaluate_chunking(documents)
    evaluation_items.append(chunking_item)

    vector_service, vector_item = evaluate_vector_index(chunks)
    evaluation_items.append(vector_item)

    if vector_service is None:
        print_summary(evaluation_items)
        return

    retrieval_item = evaluate_retrieval(vector_service)
    evaluation_items.append(retrieval_item)

    llm_service = LLMService()

    print_step(f"当前 LLM_PROVIDER：{llm_service.provider}")
    print_step(f"当前 LLM_MODEL：{llm_service.model}")

    workflow = AcademicResearchWorkflow(
        vector_service=vector_service,
        llm_service=llm_service,
    )

    pdf_files = get_pdf_file_names(documents)

    evaluation_items.append(evaluate_rag_answer(workflow))
    evaluation_items.append(evaluate_single_paper_reading(workflow, pdf_files))
    evaluation_items.append(evaluate_paper_comparison(workflow, pdf_files))
    evaluation_items.append(evaluate_writing_check(workflow))

    print_summary(evaluation_items)


if __name__ == "__main__":
    main()