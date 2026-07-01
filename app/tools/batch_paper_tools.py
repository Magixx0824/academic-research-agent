from typing import Any, Dict, List, Optional

from app.tools.paper_tools import PaperReadingTool


class BatchPaperReadingTool:
    """
    批量论文精读工具。

    功能：
    1. 接收多个论文 file_name；
    2. 调用 PaperReadingTool 逐篇生成精读卡片；
    3. 支持 quick / full 两种模式；
    4. 返回统一的批量精读结果；
    5. 可用于前端展示和后续导出。
    """

    def __init__(self, vector_service: Any, llm_service: Any):
        self.vector_service = vector_service
        self.llm_service = llm_service
        self.paper_reader = PaperReadingTool(
            vector_service=vector_service,
            llm_service=llm_service,
        )

    def read_papers(
        self,
        file_names: List[str],
        mode: str = "quick",
        top_k: int = 6,
        sections: Optional[List[str]] = None,
        continue_on_error: bool = True,
    ) -> Dict[str, Any]:
        """
        批量生成论文精读卡片。

        参数：
        - file_names: 论文文件名列表；
        - mode: quick、full 或 custom；
        - top_k: 每个维度检索的 chunk 数量；
        - sections: 自定义精读维度。如果传入 sections，则优先使用自定义维度；
        - continue_on_error: 单篇失败时是否继续处理后续论文。

        返回：
        {
            "paper_count": 2,
            "success_count": 2,
            "failed_count": 0,
            "mode": "quick",
            "results": [...]
        }
        """
        if not file_names:
            raise ValueError("file_names 不能为空")

        if mode not in {"quick", "full", "custom"}:
            raise ValueError("mode 只能是 quick、full 或 custom")

        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")

        batch_results = []
        success_count = 0
        failed_count = 0

        for file_name in file_names:
            try:
                if sections:
                    reading_result = self.paper_reader.read_single_paper(
                        file_name=file_name,
                        sections=sections,
                        top_k=top_k,
                    )
                    actual_mode = "custom"

                elif mode == "quick":
                    reading_result = self.paper_reader.read_quick_card(
                        file_name=file_name,
                        top_k=top_k,
                    )
                    actual_mode = "quick"

                elif mode == "full":
                    reading_result = self.paper_reader.read_full_card(
                        file_name=file_name,
                        top_k=top_k,
                    )
                    actual_mode = "full"

                else:
                    raise ValueError("custom 模式必须传入 sections")

                batch_results.append(
                    {
                        "file_name": file_name,
                        "status": "success",
                        "mode": actual_mode,
                        "reading_result": reading_result,
                        "error": "",
                    }
                )
                success_count += 1

            except Exception as exc:
                failed_count += 1

                batch_results.append(
                    {
                        "file_name": file_name,
                        "status": "failed",
                        "mode": mode,
                        "reading_result": None,
                        "error": str(exc),
                    }
                )

                if not continue_on_error:
                    break

        return {
            "task_type": "batch_paper_reading",
            "task_name": "批量论文精读",
            "status": "success" if success_count > 0 else "failed",
            "mode": mode,
            "paper_count": len(file_names),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": batch_results,
        }


def _clean_text(value: Any) -> str:
    """
    将任意值转换为安全字符串。
    """
    if value is None:
        return ""

    return str(value).strip()


def _format_source(source: Dict[str, Any], index: int) -> str:
    """
    格式化单条来源信息。
    """
    distance = source.get("distance")
    retrieval_text = distance if distance is not None else (
        source.get("retrieval_type") or "keyword"
    )

    file_name = source.get("file_name") or source.get("metadata", {}).get("file_name")
    page_number = source.get("page_number") or source.get("metadata", {}).get("page_number")
    chunk_index = source.get("chunk_index") or source.get("metadata", {}).get("chunk_index")

    return (
        f"{index}. {_clean_text(file_name)} | "
        f"第 {_clean_text(page_number)} 页 | "
        f"chunk_index={_clean_text(chunk_index)} | "
        f"retrieval={_clean_text(retrieval_text)}"
    )


def _format_section_markdown(
    section: Dict[str, Any],
    paper_index: int,
    section_index: int,
) -> str:
    """
    将单个精读维度格式化为结构化 Markdown。
    """
    lines = []

    section_title = _clean_text(section.get("section_title") or "未知维度")
    question = _clean_text(section.get("question"))
    answer = _clean_text(section.get("answer"))
    uncertainty = _clean_text(section.get("uncertainty"))
    sources = section.get("sources", [])

    lines.append(f"#### {paper_index}.{section_index} {section_title}")
    lines.append("")

    lines.append("**问题**")
    lines.append("")
    lines.append(question or "未返回问题。")
    lines.append("")

    lines.append("**回答**")
    lines.append("")
    lines.append(answer or "未返回回答。")
    lines.append("")

    lines.append("**依据来源**")
    lines.append("")

    if not sources:
        lines.append("未返回来源。")
    else:
        for source_index, source in enumerate(sources, start=1):
            lines.append(_format_source(source, source_index))

    lines.append("")

    lines.append("**不确定之处**")
    lines.append("")
    lines.append(uncertainty or "未返回不确定性说明。")
    lines.append("")

    return "\n".join(lines)


def _format_single_paper_markdown(
    item: Dict[str, Any],
    paper_index: int,
) -> str:
    """
    将一篇论文的批量精读结果格式化为结构化 Markdown。
    """
    lines = []

    file_name = _clean_text(item.get("file_name") or "未知文件")
    status = _clean_text(item.get("status") or "unknown")
    mode = _clean_text(item.get("mode") or "unknown")

    lines.append(f"### {paper_index}. {file_name}")
    lines.append("")

    lines.append(f"- **处理状态**：{status}")
    lines.append(f"- **精读模式**：{mode}")

    if status != "success":
        error = _clean_text(item.get("error"))
        lines.append(f"- **错误信息**：{error or '未返回错误信息。'}")
        lines.append("")
        return "\n".join(lines)

    reading_result = item.get("reading_result")

    if not reading_result:
        lines.append("- **处理结果**：未返回精读结果。")
        lines.append("")
        return "\n".join(lines)

    section_count = reading_result.get("section_count", 0)

    lines.append(f"- **精读维度数量**：{section_count}")
    lines.append("")

    sections = reading_result.get("sections", [])

    if not sections:
        lines.append("未生成任何精读内容。")
        lines.append("")
        return "\n".join(lines)

    for section_index, section in enumerate(sections, start=1):
        lines.append(
            _format_section_markdown(
                section=section,
                paper_index=paper_index,
                section_index=section_index,
            )
        )

    return "\n".join(lines)


def format_batch_paper_reading_result(batch_result: Dict[str, Any]) -> str:
    """
    将批量论文精读结果格式化为适合 Markdown / Word 导出的结构化文本。

    说明：
    - 不再复用 format_paper_reading_card 的控制台格式；
    - 直接输出 Markdown 层级标题；
    - 导出 Word 时可被 ResultExportTool 自动识别为标题、列表和加粗文本；
    - 适合最终报告、文献初筛记录和课程汇报材料。
    """
    lines = []

    status = batch_result.get("status", "unknown")
    mode = batch_result.get("mode", "unknown")
    paper_count = batch_result.get("paper_count", 0)
    success_count = batch_result.get("success_count", 0)
    failed_count = batch_result.get("failed_count", 0)

    lines.append("## 一、任务概况")
    lines.append("")
    lines.append(f"- **任务状态**：{status}")
    lines.append(f"- **精读模式**：{mode}")
    lines.append(f"- **论文总数**：{paper_count}")
    lines.append(f"- **成功数量**：{success_count}")
    lines.append(f"- **失败数量**：{failed_count}")
    lines.append("")

    results = batch_result.get("results", [])

    lines.append("## 二、论文精读结果")
    lines.append("")

    if not results:
        lines.append("未生成任何批量精读结果。")
        return "\n".join(lines)

    for paper_index, item in enumerate(results, start=1):
        lines.append(
            _format_single_paper_markdown(
                item=item,
                paper_index=paper_index,
            )
        )

    return "\n".join(lines)