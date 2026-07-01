import os
import sys
from pathlib import Path
from typing import List, Optional

import streamlit as st


# 让 Streamlit 能够从项目根目录导入 app 包
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.tools.document_tools import load_documents_from_directory
from app.tools.rag_tools import split_documents
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
from app.tools.workflow_tools import AcademicResearchWorkflow


DEFAULT_DOC_DIR = "data/demo_docs"


def get_available_pdf_files(directory_path: str) -> List[str]:
    """
    获取指定目录下的 PDF 文件名。
    """
    directory = Path(directory_path)

    if not directory.exists():
        return []

    return sorted([
        path.name
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() == ".pdf"
    ])


@st.cache_resource
def init_services() -> tuple[VectorService, LLMService, AcademicResearchWorkflow]:
    """
    初始化核心服务。

    注意：
    - cache_resource 可以避免每次页面交互都重新初始化模型和向量库；
    - 向量库内容是否最新，需要通过“重建索引”按钮控制。
    """
    vector_service = VectorService(
        persist_dir="storage/chroma",
        collection_name="academic_chunks",
        reset_collection=False,
    )

    llm_service = LLMService()

    workflow = AcademicResearchWorkflow(
        vector_service=vector_service,
        llm_service=llm_service,
    )

    return vector_service, llm_service, workflow


def rebuild_vector_index(
    vector_service: VectorService,
    doc_dir: str,
    chunk_size: int,
    overlap: int,
) -> int:
    """
    重新读取文档、切分 chunk，并写入向量库。
    """
    documents = load_documents_from_directory(doc_dir)

    if not documents:
        return 0

    chunks = split_documents(
        documents,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    vector_service.clear()
    vector_service.add_chunks(chunks)

    return len(chunks)


def render_sidebar(vector_service: VectorService) -> None:
    """
    侧边栏：索引配置与状态。
    """
    st.sidebar.header("索引设置")

    doc_dir = st.sidebar.text_input(
        "文档目录",
        value=DEFAULT_DOC_DIR,
        help="默认使用 data/demo_docs。也可以改为 data/raw_docs。",
    )

    chunk_size = st.sidebar.number_input(
        "chunk_size",
        min_value=200,
        max_value=2000,
        value=700,
        step=100,
    )

    overlap = st.sidebar.number_input(
        "overlap",
        min_value=0,
        max_value=500,
        value=100,
        step=50,
    )

    st.session_state["doc_dir"] = doc_dir
    st.session_state["chunk_size"] = chunk_size
    st.session_state["overlap"] = overlap

    st.sidebar.divider()

    try:
        current_count = vector_service.count()
    except Exception:
        current_count = 0

    st.sidebar.write(f"当前向量库 chunk 数量：**{current_count}**")

    if st.sidebar.button("重建向量索引"):
        with st.spinner("正在读取文档、切分文本并写入向量库..."):
            chunk_count = rebuild_vector_index(
                vector_service=vector_service,
                doc_dir=doc_dir,
                chunk_size=chunk_size,
                overlap=overlap,
            )

        st.sidebar.success(f"索引重建完成，写入 {chunk_count} 个 chunks。")


def render_rag_answer(workflow: AcademicResearchWorkflow) -> None:
    st.subheader("基础 RAG 问答")

    question = st.text_area(
        "请输入问题",
        value="人工智能如何影响企业创新韧性？",
        height=100,
    )

    top_k = st.slider("检索片段数量 top_k", 1, 10, 3)

    if st.button("运行 RAG 问答"):
        with st.spinner("正在检索并生成回答..."):
            result = workflow.run_task(
                task_type="rag_answer",
                question=question,
                top_k=top_k,
            )

        rag_result = result["result"]

        st.markdown("### 回答")
        st.write(rag_result.get("answer", ""))

        st.markdown("### 依据来源")
        sources = rag_result.get("sources", [])

        if not sources:
            st.info("未返回来源。")
        else:
            for index, source in enumerate(sources, start=1):
                st.write(
                    f"{index}. {source.get('file_name')} | "
                    f"第 {source.get('page_number')} 页 | "
                    f"chunk_index={source.get('chunk_index')} | "
                    f"retrieval={source.get('distance')}"
                )

        st.markdown("### 不确定之处")
        st.write(rag_result.get("uncertainty", ""))


def render_single_paper_reading(workflow: AcademicResearchWorkflow) -> None:
    st.subheader("单篇论文精读")

    doc_dir = st.session_state.get("doc_dir", DEFAULT_DOC_DIR)
    pdf_files = get_available_pdf_files(doc_dir)

    if not pdf_files:
        st.warning("当前文档目录下没有 PDF 文件。")
        return

    file_name = st.selectbox("选择论文", pdf_files)

    mode = st.radio(
        "精读模式",
        options=["quick", "full"],
        format_func=lambda x: "快速精读（3 个维度）" if x == "quick" else "完整精读（9 个维度）",
        horizontal=True,
    )

    top_k = st.slider("每个维度检索片段数量 top_k", 1, 8, 4)

    if st.button("生成单篇精读卡片"):
        with st.spinner("正在生成单篇论文精读卡片..."):
            result = workflow.run_task(
                task_type="single_paper_reading",
                file_name=file_name,
                mode=mode,
                top_k=top_k,
            )

        reading_result = result["result"]

        st.markdown("### 精读结果")
        st.write(f"论文文件：{reading_result.get('file_name')}")
        st.write(f"精读维度数量：{reading_result.get('section_count')}")

        for section in reading_result.get("sections", []):
            with st.expander(section.get("section_title", "未知维度"), expanded=False):
                st.markdown("**问题**")
                st.write(section.get("question", ""))

                st.markdown("**回答**")
                st.write(section.get("answer", ""))

                st.markdown("**依据来源**")
                for index, source in enumerate(section.get("sources", []), start=1):
                    distance = source.get("distance")
                    retrieval_text = distance if distance is not None else (
                        source.get("retrieval_type") or "keyword"
                    )

                    st.write(
                        f"{index}. {source.get('file_name')} | "
                        f"第 {source.get('page_number')} 页 | "
                        f"chunk_index={source.get('chunk_index')} | "
                        f"retrieval={retrieval_text}"
                    )


def render_paper_comparison(workflow: AcademicResearchWorkflow) -> None:
    st.subheader("多篇论文对比")

    doc_dir = st.session_state.get("doc_dir", DEFAULT_DOC_DIR)
    pdf_files = get_available_pdf_files(doc_dir)

    if len(pdf_files) < 2:
        st.warning("至少需要 2 篇 PDF 论文进行对比。")
        return

    file_names = st.multiselect(
        "选择要对比的论文",
        options=pdf_files,
        default=pdf_files[:2],
    )

    dimensions = st.multiselect(
        "选择对比维度",
        options=[
            "research_question",
            "data_and_method",
            "main_findings",
            "theoretical_basis",
            "variables",
        ],
        default=[
            "research_question",
            "data_and_method",
            "main_findings",
        ],
    )

    top_k = st.slider("每个维度检索片段数量 top_k", 1, 8, 4)

    include_synthesis = st.checkbox("生成综合对比分析", value=True)

    if st.button("生成多篇论文对比"):
        if len(file_names) < 2:
            st.error("请至少选择 2 篇论文。")
            return

        with st.spinner("正在生成多篇论文对比结果..."):
            result = workflow.run_task(
                task_type="paper_comparison",
                file_names=file_names,
                dimensions=dimensions,
                top_k=top_k,
                include_synthesis=include_synthesis,
            )

        compare_result = result["result"]

        st.markdown("### 对比结果")
        st.write(f"论文数量：{compare_result.get('paper_count')}")
        st.write(f"对比维度数量：{compare_result.get('dimension_count')}")

        paper_summaries = compare_result.get("paper_summaries", {})

        for dimension_key in compare_result.get("dimensions", []):
            st.markdown(f"## 对比维度：{dimension_key}")

            for file_name in file_names:
                summary = paper_summaries.get(file_name, {}).get(dimension_key, {})

                with st.expander(f"{file_name} - {summary.get('dimension_title', dimension_key)}"):
                    st.write(summary.get("answer", ""))

        synthesis = compare_result.get("synthesis")

        if synthesis:
            st.markdown("### 综合对比分析")
            st.write(synthesis.get("answer", ""))


def render_literature_review(workflow: AcademicResearchWorkflow) -> None:
    st.subheader("文献综述框架生成")

    doc_dir = st.session_state.get("doc_dir", DEFAULT_DOC_DIR)
    pdf_files = get_available_pdf_files(doc_dir)

    if len(pdf_files) < 2:
        st.warning("至少需要 2 篇 PDF 论文生成综述框架。")
        return

    topic = st.text_input(
        "综述主题",
        value="企业创新能力与数字技术应用的影响机制",
    )

    file_names = st.multiselect(
        "选择参与综述的论文",
        options=pdf_files,
        default=pdf_files[:2],
    )

    dimensions = st.multiselect(
        "选择综述参考维度",
        options=[
            "research_question",
            "data_and_method",
            "main_findings",
            "theoretical_basis",
            "variables",
        ],
        default=[
            "research_question",
            "data_and_method",
            "main_findings",
        ],
    )

    top_k = st.slider("每个维度检索片段数量 top_k", 1, 8, 4)

    if st.button("生成文献综述框架"):
        if len(file_names) < 2:
            st.error("请至少选择 2 篇论文。")
            return

        with st.spinner("正在生成文献综述框架..."):
            result = workflow.run_task(
                task_type="literature_review",
                topic=topic,
                file_names=file_names,
                dimensions=dimensions,
                top_k=top_k,
            )

        review_result = result["result"]

        st.markdown("### 文献综述框架")
        st.write(review_result.get("framework", ""))

        st.markdown("### 依据来源")
        for index, source in enumerate(review_result.get("sources", []), start=1):
            retrieval_type = source.get("retrieval_type") or "summary"
            chunk_index = source.get("chunk_index")

            st.write(
                f"{index}. {source.get('file_name')} | "
                f"来源类型={retrieval_type} | "
                f"摘要维度={chunk_index}"
            )


def render_writing_check(workflow: AcademicResearchWorkflow) -> None:
    st.subheader("学术写作检查")

    writing_goal = st.text_input(
        "写作目标",
        value="理论机制段落写作检查",
    )

    text = st.text_area(
        "请输入需要检查的论文文本",
        value=(
            "企业创新能力是企业获得竞争优势的重要来源。随着外部环境不断变化，"
            "企业需要通过合作创新来提升自身能力。合作创新可以帮助企业获得外部资源，"
            "也可以提高企业面对风险的能力。但是现有研究对合作创新如何影响企业创新能力"
            "的机制研究还不够充分。因此，本文认为组织韧性可能在合作创新和持续创新能力之间"
            "发挥作用，同时技术环境动荡性也可能影响这种关系。"
        ),
        height=220,
    )

    focus = st.multiselect(
        "选择检查重点",
        options=[
            "structure",
            "logic",
            "academic_style",
            "evidence",
            "clarity",
            "redundancy",
            "mechanism",
            "variable_consistency",
        ],
        default=[
            "structure",
            "logic",
            "academic_style",
            "evidence",
            "mechanism",
        ],
    )

    if st.button("运行写作检查"):
        with st.spinner("正在检查文本..."):
            result = workflow.run_task(
                task_type="writing_check",
                text=text,
                writing_goal=writing_goal,
                focus=focus,
            )

        check_result = result["result"]

        st.markdown("### 检查结果")
        st.write(check_result.get("check_result", ""))

        st.markdown("### 不确定之处")
        st.write(check_result.get("uncertainty", ""))


def main() -> None:
    st.set_page_config(
        page_title="Academic Research Agent",
        page_icon="📚",
        layout="wide",
    )

    st.title("学术论文阅读与写作辅助 Agent")
    st.caption("Academic Research Workflow Agent")

    vector_service, llm_service, workflow = init_services()

    render_sidebar(vector_service)

    st.sidebar.divider()
    st.sidebar.write(f"当前 LLM_PROVIDER：`{llm_service.provider}`")
    st.sidebar.write(f"当前 LLM_MODEL：`{llm_service.model}`")

    task = st.sidebar.radio(
        "选择任务",
        options=[
            "基础 RAG 问答",
            "单篇论文精读",
            "多篇论文对比",
            "文献综述框架生成",
            "学术写作检查",
        ],
    )

    if task == "基础 RAG 问答":
        render_rag_answer(workflow)

    elif task == "单篇论文精读":
        render_single_paper_reading(workflow)

    elif task == "多篇论文对比":
        render_paper_comparison(workflow)

    elif task == "文献综述框架生成":
        render_literature_review(workflow)

    elif task == "学术写作检查":
        render_writing_check(workflow)


if __name__ == "__main__":
    main()