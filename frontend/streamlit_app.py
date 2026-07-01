import sys
from datetime import datetime
from pathlib import Path
from typing import List

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
from app.tools.export_tools import ResultExportTool


DEFAULT_DOC_DIR = "data/demo_docs"
RAW_DOC_DIR = "data/raw_docs"
SUPPORTED_UPLOAD_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


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
def init_services() -> tuple[
    VectorService,
    LLMService,
    AcademicResearchWorkflow,
    ResultExportTool,
]:
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

    export_tool = ResultExportTool(
        output_dir="outputs/reports",
    )

    return vector_service, llm_service, workflow, export_tool


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

def sanitize_uploaded_filename(file_name: str) -> str:
    """
    清洗上传文件名，避免路径穿越和非法字符。
    """
    safe_name = Path(file_name).name
    safe_name = safe_name.strip()
    safe_name = "".join(
        "_" if char in r'\/:*?"<>|' else char
        for char in safe_name
    )

    return safe_name or "uploaded_file"


def save_uploaded_files(
    uploaded_files,
    save_dir: str,
    overwrite: bool = True,
) -> List[str]:
    """
    保存 Streamlit 上传的文件。

    返回：
    - 已保存文件路径列表。
    """
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    saved_paths = []

    for uploaded_file in uploaded_files:
        file_name = sanitize_uploaded_filename(uploaded_file.name)
        file_suffix = Path(file_name).suffix.lower()

        if file_suffix not in SUPPORTED_UPLOAD_EXTENSIONS:
            continue

        target_path = save_path / file_name

        if target_path.exists() and not overwrite:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_path = save_path / f"{target_path.stem}_{timestamp}{target_path.suffix}"

        with open(target_path, "wb") as file:
            file.write(uploaded_file.getbuffer())

        saved_paths.append(str(target_path))

    return saved_paths


def clear_workflow_results() -> None:
    """
    清理已经生成的任务结果。

    用于：
    - 重建索引后；
    - 上传新文件并重建索引后。

    避免页面仍显示旧索引条件下生成的结果。
    """
    keys_to_clear = [
        "rag_answer_workflow_result",
        "single_paper_reading_workflow_result",
        "paper_comparison_workflow_result",
        "literature_review_workflow_result",
        "writing_check_workflow_result",
        "rag_answer_md_path",
        "rag_answer_docx_path",
        "single_paper_reading_md_path",
        "single_paper_reading_docx_path",
        "paper_comparison_md_path",
        "paper_comparison_docx_path",
        "literature_review_md_path",
        "literature_review_docx_path",
        "writing_check_md_path",
        "writing_check_docx_path",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)

def read_file_bytes(file_path: str) -> bytes:
    """
    读取导出文件的二进制内容，用于 Streamlit 下载按钮。
    """
    with open(file_path, "rb") as file:
        return file.read()


def get_file_name_from_path(file_path: str) -> str:
    """
    从路径中提取文件名，兼容 Windows 和类 Unix 路径。
    """
    return Path(file_path).name


def build_export_file_stem(task_type: str) -> str:
    """
    根据任务类型构造导出文件名前缀。
    """
    task_name_map = {
        "rag_answer": "rag_answer_result",
        "single_paper_reading": "single_paper_reading_result",
        "paper_comparison": "paper_comparison_result",
        "literature_review": "literature_review_result",
        "writing_check": "writing_check_result",
    }

    return task_name_map.get(task_type, "workflow_result")


def clear_export_paths(button_key_prefix: str) -> None:
    """
    新生成任务结果后，清理旧导出路径，避免下载到上一次任务的文件。
    """
    st.session_state.pop(f"{button_key_prefix}_md_path", None)
    st.session_state.pop(f"{button_key_prefix}_docx_path", None)


def render_export_buttons(
    workflow_result: dict,
    export_tool: ResultExportTool,
    button_key_prefix: str,
) -> None:
    """
    渲染 Markdown 和 Word 导出按钮。

    注意：
    - Streamlit 点击按钮会触发 rerun；
    - 因此导出文件路径必须存入 st.session_state；
    - 下载按钮每次 rerun 都从 session_state 中读取已生成文件。
    """
    if not workflow_result:
        return

    task_type = workflow_result.get("task_type", "workflow_result")
    file_stem = build_export_file_stem(task_type)

    st.markdown("### 导出结果")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "生成 Markdown 文件",
            key=f"{button_key_prefix}_export_md",
        ):
            export_result = export_tool.export_workflow_result(
                workflow_result=workflow_result,
                export_format="md",
                file_stem=file_stem,
            )

            st.session_state[f"{button_key_prefix}_md_path"] = export_result.file_path
            st.success(f"Markdown 文件已生成：{export_result.file_name}")

        md_path = st.session_state.get(f"{button_key_prefix}_md_path")

        if md_path and Path(md_path).exists():
            st.download_button(
                label="下载 Markdown",
                data=read_file_bytes(md_path),
                file_name=get_file_name_from_path(md_path),
                mime="text/markdown",
                key=f"{button_key_prefix}_download_md",
            )

    with col2:
        if st.button(
            "生成 Word 文件",
            key=f"{button_key_prefix}_export_docx",
        ):
            export_result = export_tool.export_workflow_result(
                workflow_result=workflow_result,
                export_format="docx",
                file_stem=file_stem,
            )

            st.session_state[f"{button_key_prefix}_docx_path"] = export_result.file_path
            st.success(f"Word 文件已生成：{export_result.file_name}")

        docx_path = st.session_state.get(f"{button_key_prefix}_docx_path")

        if docx_path and Path(docx_path).exists():
            st.download_button(
                label="下载 Word",
                data=read_file_bytes(docx_path),
                file_name=get_file_name_from_path(docx_path),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                key=f"{button_key_prefix}_download_docx",
            )


def render_sidebar(vector_service: VectorService) -> None:
    """
    侧边栏：索引配置、文件上传与索引状态。
    """
    st.sidebar.header("索引设置")

    if "doc_dir" not in st.session_state:
        st.session_state["doc_dir"] = DEFAULT_DOC_DIR

    # 用 pending 机制避免在 widget 创建后直接修改同名 session_state。
    if "_pending_doc_dir" in st.session_state:
        st.session_state["doc_dir"] = st.session_state.pop("_pending_doc_dir")

    doc_dir = st.sidebar.text_input(
        "文档目录",
        help="默认使用 data/demo_docs。上传文件后通常切换为 data/raw_docs。",
        key="doc_dir",
    )

    chunk_size = st.sidebar.number_input(
        "chunk_size",
        min_value=200,
        max_value=2000,
        value=700,
        step=100,
        key="sidebar_chunk_size",
    )

    overlap = st.sidebar.number_input(
        "overlap",
        min_value=0,
        max_value=500,
        value=100,
        step=50,
        key="sidebar_overlap",
    )

    st.session_state["chunk_size"] = chunk_size
    st.session_state["overlap"] = overlap

    st.sidebar.divider()

    try:
        current_count = vector_service.count()
    except Exception:
        current_count = 0

    st.sidebar.write(f"当前向量库 chunk 数量：**{current_count}**")
    st.sidebar.write(f"当前文档目录：`{doc_dir}`")

    if st.sidebar.button("重建向量索引", key="rebuild_vector_index"):
        with st.spinner("正在读取文档、切分文本并写入向量库..."):
            chunk_count = rebuild_vector_index(
                vector_service=vector_service,
                doc_dir=doc_dir,
                chunk_size=chunk_size,
                overlap=overlap,
            )

        clear_workflow_results()
        st.sidebar.success(f"索引重建完成，写入 {chunk_count} 个 chunks。")

    st.sidebar.divider()

    with st.sidebar.expander("上传文档并自动索引", expanded=False):
        upload_dir = st.text_input(
            "上传保存目录",
            value=RAW_DOC_DIR,
            key="upload_save_dir",
            help="上传文件默认保存到 data/raw_docs。",
        )

        uploaded_files = st.file_uploader(
            "上传文档",
            type=["txt", "md", "pdf", "docx"],
            accept_multiple_files=True,
            key="uploaded_research_files",
        )

        overwrite = st.checkbox(
            "同名文件覆盖",
            value=True,
            key="upload_overwrite",
        )

        auto_rebuild = st.checkbox(
            "上传后自动重建索引",
            value=True,
            key="upload_auto_rebuild",
        )

        if st.button("保存上传文件", key="save_uploaded_files"):
            if not uploaded_files:
                st.warning("请先选择需要上传的文件。")
                return

            saved_paths = save_uploaded_files(
                uploaded_files=uploaded_files,
                save_dir=upload_dir,
                overwrite=overwrite,
            )

            if not saved_paths:
                st.error("没有成功保存的文件。请检查文件格式是否受支持。")
                return

            st.success(f"成功保存 {len(saved_paths)} 个文件。")

            with st.expander("已保存文件", expanded=False):
                for path in saved_paths:
                    st.write(path)

            if auto_rebuild:
                with st.spinner("正在基于上传目录重建向量索引..."):
                    chunk_count = rebuild_vector_index(
                        vector_service=vector_service,
                        doc_dir=upload_dir,
                        chunk_size=chunk_size,
                        overlap=overlap,
                    )

                clear_workflow_results()

                # 下一次 rerun 时自动切换文档目录。
                st.session_state["_pending_doc_dir"] = upload_dir

                st.success(
                    f"上传目录索引重建完成，写入 {chunk_count} 个 chunks。"
                )
                st.info(
                    "当前文档目录将在页面刷新后切换为上传保存目录。"
                )

                st.rerun()


def render_rag_answer(
    workflow: AcademicResearchWorkflow,
    export_tool: ResultExportTool,
) -> None:
    st.subheader("基础 RAG 问答")

    question = st.text_area(
        "请输入问题",
        value="人工智能如何影响企业创新韧性？",
        height=100,
        key="rag_answer_question",
    )

    top_k = st.slider(
        "检索片段数量 top_k",
        1,
        10,
        3,
        key="rag_answer_top_k",
    )

    if st.button("运行 RAG 问答", key="run_rag_answer"):
        with st.spinner("正在检索并生成回答..."):
            result = workflow.run_task(
                task_type="rag_answer",
                question=question,
                top_k=top_k,
            )

        st.session_state["rag_answer_workflow_result"] = result
        clear_export_paths("rag_answer")

    saved_result = st.session_state.get("rag_answer_workflow_result")

    if not saved_result:
        st.info("请先点击“运行 RAG 问答”生成结果。")
        return

    rag_result = saved_result["result"]

    st.markdown("### 回答")
    st.write(rag_result.get("answer", ""))

    st.markdown("### 依据来源")
    sources = rag_result.get("sources", [])

    if not sources:
        st.info("未返回来源。")
    else:
        for index, source in enumerate(sources, start=1):
            distance = source.get("distance")
            retrieval_text = distance if distance is not None else (
                source.get("retrieval_type") or "unknown"
            )

            st.write(
                f"{index}. {source.get('file_name')} | "
                f"第 {source.get('page_number')} 页 | "
                f"chunk_index={source.get('chunk_index')} | "
                f"retrieval={retrieval_text}"
            )

    st.markdown("### 不确定之处")
    st.write(rag_result.get("uncertainty", ""))

    render_export_buttons(
        workflow_result=saved_result,
        export_tool=export_tool,
        button_key_prefix="rag_answer",
    )


def render_single_paper_reading(
    workflow: AcademicResearchWorkflow,
    export_tool: ResultExportTool,
) -> None:
    st.subheader("单篇论文精读")

    doc_dir = st.session_state.get("doc_dir", DEFAULT_DOC_DIR)
    pdf_files = get_available_pdf_files(doc_dir)

    if not pdf_files:
        st.warning("当前文档目录下没有 PDF 文件。")
        return

    file_name = st.selectbox(
        "选择论文",
        pdf_files,
        key="single_paper_file_name",
    )

    mode = st.radio(
        "精读模式",
        options=["quick", "full"],
        format_func=lambda x: "快速精读（3 个维度）" if x == "quick" else "完整精读（9 个维度）",
        horizontal=True,
        key="single_paper_mode",
    )

    top_k = st.slider(
        "每个维度检索片段数量 top_k",
        1,
        8,
        4,
        key="single_paper_top_k",
    )

    if st.button("生成单篇精读卡片", key="run_single_paper_reading"):
        with st.spinner("正在生成单篇论文精读卡片..."):
            result = workflow.run_task(
                task_type="single_paper_reading",
                file_name=file_name,
                mode=mode,
                top_k=top_k,
            )

        st.session_state["single_paper_reading_workflow_result"] = result
        clear_export_paths("single_paper_reading")

    saved_result = st.session_state.get("single_paper_reading_workflow_result")

    if not saved_result:
        st.info("请先点击“生成单篇精读卡片”。")
        return

    reading_result = saved_result["result"]

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

    render_export_buttons(
        workflow_result=saved_result,
        export_tool=export_tool,
        button_key_prefix="single_paper_reading",
    )


def render_paper_comparison(
    workflow: AcademicResearchWorkflow,
    export_tool: ResultExportTool,
) -> None:
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
        key="paper_comparison_file_names",
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
        key="paper_comparison_dimensions",
    )

    top_k = st.slider(
        "每个维度检索片段数量 top_k",
        1,
        8,
        4,
        key="paper_comparison_top_k",
    )

    include_synthesis = st.checkbox(
        "生成综合对比分析",
        value=True,
        key="paper_comparison_include_synthesis",
    )

    if st.button("生成多篇论文对比", key="run_paper_comparison"):
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

        st.session_state["paper_comparison_workflow_result"] = result
        clear_export_paths("paper_comparison")

    saved_result = st.session_state.get("paper_comparison_workflow_result")

    if not saved_result:
        st.info("请先点击“生成多篇论文对比”。")
        return

    compare_result = saved_result["result"]

    st.markdown("### 对比结果")
    st.write(f"论文数量：{compare_result.get('paper_count')}")
    st.write(f"对比维度数量：{compare_result.get('dimension_count')}")

    paper_summaries = compare_result.get("paper_summaries", {})

    for dimension_key in compare_result.get("dimensions", []):
        st.markdown(f"## 对比维度：{dimension_key}")

        for current_file_name in compare_result.get("file_names", []):
            summary = paper_summaries.get(current_file_name, {}).get(dimension_key, {})

            with st.expander(
                f"{current_file_name} - {summary.get('dimension_title', dimension_key)}"
            ):
                st.write(summary.get("answer", ""))

    synthesis = compare_result.get("synthesis")

    if synthesis:
        st.markdown("### 综合对比分析")
        st.write(synthesis.get("answer", ""))

    render_export_buttons(
        workflow_result=saved_result,
        export_tool=export_tool,
        button_key_prefix="paper_comparison",
    )


def render_literature_review(
    workflow: AcademicResearchWorkflow,
    export_tool: ResultExportTool,
) -> None:
    st.subheader("文献综述框架生成")

    doc_dir = st.session_state.get("doc_dir", DEFAULT_DOC_DIR)
    pdf_files = get_available_pdf_files(doc_dir)

    if len(pdf_files) < 2:
        st.warning("至少需要 2 篇 PDF 论文生成综述框架。")
        return

    topic = st.text_input(
        "综述主题",
        value="企业创新能力与数字技术应用的影响机制",
        key="literature_review_topic",
    )

    file_names = st.multiselect(
        "选择参与综述的论文",
        options=pdf_files,
        default=pdf_files[:2],
        key="literature_review_file_names",
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
        key="literature_review_dimensions",
    )

    top_k = st.slider(
        "每个维度检索片段数量 top_k",
        1,
        8,
        4,
        key="literature_review_top_k",
    )

    if st.button("生成文献综述框架", key="run_literature_review"):
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

        st.session_state["literature_review_workflow_result"] = result
        clear_export_paths("literature_review")

    saved_result = st.session_state.get("literature_review_workflow_result")

    if not saved_result:
        st.info("请先点击“生成文献综述框架”。")
        return

    review_result = saved_result["result"]

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

    render_export_buttons(
        workflow_result=saved_result,
        export_tool=export_tool,
        button_key_prefix="literature_review",
    )


def render_writing_check(
    workflow: AcademicResearchWorkflow,
    export_tool: ResultExportTool,
) -> None:
    st.subheader("学术写作检查")

    writing_goal = st.text_input(
        "写作目标",
        value="理论机制段落写作检查",
        key="writing_check_goal",
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
        key="writing_check_text",
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
        key="writing_check_focus",
    )

    if st.button("运行写作检查", key="run_writing_check"):
        with st.spinner("正在检查文本..."):
            result = workflow.run_task(
                task_type="writing_check",
                text=text,
                writing_goal=writing_goal,
                focus=focus,
            )

        st.session_state["writing_check_workflow_result"] = result
        clear_export_paths("writing_check")

    saved_result = st.session_state.get("writing_check_workflow_result")

    if not saved_result:
        st.info("请先点击“运行写作检查”。")
        return

    check_result = saved_result["result"]

    st.markdown("### 检查结果")
    st.write(check_result.get("check_result", ""))

    st.markdown("### 不确定之处")
    st.write(check_result.get("uncertainty", ""))

    render_export_buttons(
        workflow_result=saved_result,
        export_tool=export_tool,
        button_key_prefix="writing_check",
    )


def main() -> None:
    st.set_page_config(
        page_title="Academic Research Agent",
        page_icon="📚",
        layout="wide",
    )

    st.title("学术论文阅读与写作辅助 Agent")
    st.caption("Academic Research Workflow Agent")

    vector_service, llm_service, workflow, export_tool = init_services()

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
        key="selected_task",
    )

    if task == "基础 RAG 问答":
        render_rag_answer(workflow, export_tool)

    elif task == "单篇论文精读":
        render_single_paper_reading(workflow, export_tool)

    elif task == "多篇论文对比":
        render_paper_comparison(workflow, export_tool)

    elif task == "文献综述框架生成":
        render_literature_review(workflow, export_tool)

    elif task == "学术写作检查":
        render_writing_check(workflow, export_tool)


if __name__ == "__main__":
    main()