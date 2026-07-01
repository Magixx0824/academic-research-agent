import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from app.tools.workflow_tools import format_workflow_result


DEFAULT_EXPORT_DIR = "outputs/reports"


@dataclass
class ExportResult:
    """
    导出结果信息。
    """
    success: bool
    file_path: str
    file_name: str
    export_format: str
    detail: str


class ResultExportTool:
    """
    结果导出工具。

    功能：
    1. 将 workflow 输出结果导出为 Markdown；
    2. 将 workflow 输出结果导出为 Word docx；
    3. 统一管理导出目录和文件命名；
    4. 为后续 Streamlit 下载功能提供文件生成能力。
    """

    def __init__(self, output_dir: str = DEFAULT_EXPORT_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_filename(text: str) -> str:
        """
        将任务名称、标题等文本转换为安全文件名。
        """
        if not text:
            return "export_result"

        text = text.strip()
        text = re.sub(r"[\\/:*?\"<>|]", "_", text)
        text = re.sub(r"\s+", "_", text)
        text = text[:80]

        return text or "export_result"

    @staticmethod
    def _timestamp() -> str:
        """
        生成时间戳，避免文件名重复。
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _build_file_path(
        self,
        file_stem: Optional[str],
        export_format: str,
        task_type: Optional[str] = None,
    ) -> Path:
        """
        构造导出文件路径。
        """
        if file_stem:
            safe_stem = self._safe_filename(file_stem)
        elif task_type:
            safe_stem = self._safe_filename(task_type)
        else:
            safe_stem = "academic_result"

        file_name = f"{safe_stem}_{self._timestamp()}.{export_format}"
        return self.output_dir / file_name

    def export_workflow_result(
        self,
        workflow_result: Dict[str, Any],
        export_format: str = "md",
        file_stem: Optional[str] = None,
    ) -> ExportResult:
        """
        导出统一 workflow 结果。

        参数：
        - workflow_result: AcademicResearchWorkflow.run_task() 的返回结果；
        - export_format: md 或 docx；
        - file_stem: 文件名前缀，可选。
        """
        if not workflow_result:
            raise ValueError("workflow_result 不能为空")

        if export_format not in {"md", "docx"}:
            raise ValueError("export_format 只能是 md 或 docx")

        task_type = workflow_result.get("task_type", "workflow_result")
        formatted_text = format_workflow_result(workflow_result)

        title = workflow_result.get("task_name", "学术研究工作流结果")

        if export_format == "md":
            return self.export_markdown(
                content=formatted_text,
                file_stem=file_stem or task_type,
                title=title,
            )

        return self.export_docx(
            content=formatted_text,
            file_stem=file_stem or task_type,
            title=title,
        )

    def export_text(
        self,
        content: str,
        export_format: str = "md",
        file_stem: Optional[str] = None,
        title: str = "学术研究结果",
    ) -> ExportResult:
        """
        导出普通文本内容。

        适用于后续扩展：例如直接导出某个 Markdown 字符串。
        """
        if not content or not content.strip():
            raise ValueError("content 不能为空")

        if export_format == "md":
            return self.export_markdown(
                content=content,
                file_stem=file_stem,
                title=title,
            )

        if export_format == "docx":
            return self.export_docx(
                content=content,
                file_stem=file_stem,
                title=title,
            )

        raise ValueError("export_format 只能是 md 或 docx")

    def export_markdown(
        self,
        content: str,
        file_stem: Optional[str] = None,
        title: str = "学术研究结果",
    ) -> ExportResult:
        """
        导出 Markdown 文件。
        """
        file_path = self._build_file_path(
            file_stem=file_stem,
            export_format="md",
        )

        markdown_content = (
            f"# {title}\n\n"
            f"> 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"---\n\n"
            f"{content}\n"
        )

        file_path.write_text(markdown_content, encoding="utf-8")

        return ExportResult(
            success=True,
            file_path=str(file_path),
            file_name=file_path.name,
            export_format="md",
            detail=f"Markdown 文件导出成功：{file_path}",
        )

    def export_docx(
        self,
        content: str,
        file_stem: Optional[str] = None,
        title: str = "学术研究结果",
    ) -> ExportResult:
        """
        导出 Word docx 文件。

        说明：
        - 该函数采用轻量格式化；
        - 不做复杂 Markdown 渲染；
        - 主要用于生成可编辑的 Word 版本。
        """
        try:
            from docx import Document
        except ImportError as error:
            raise ImportError(
                "未安装 python-docx。请先执行：pip install python-docx"
            ) from error

        file_path = self._build_file_path(
            file_stem=file_stem,
            export_format="docx",
        )

        document = Document()

        document.add_heading(title, level=1)
        document.add_paragraph(
            f"导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        document.add_paragraph("")

        for line in content.splitlines():
            clean_line = line.strip()

            if not clean_line:
                document.add_paragraph("")
                continue

            if clean_line.startswith("="):
                continue

            if clean_line.startswith("-" * 5):
                continue

            if clean_line.startswith("【") and clean_line.endswith("】"):
                document.add_heading(clean_line.strip("【】"), level=2)
                continue

            if clean_line.startswith("任务类型："):
                document.add_paragraph(clean_line)
                continue

            if clean_line.startswith("任务名称："):
                document.add_paragraph(clean_line)
                continue

            if clean_line.startswith("任务状态："):
                document.add_paragraph(clean_line)
                continue

            if clean_line.startswith("# "):
                document.add_heading(clean_line.replace("# ", "", 1), level=1)
                continue

            if clean_line.startswith("## "):
                document.add_heading(clean_line.replace("## ", "", 1), level=2)
                continue

            if clean_line.startswith("### "):
                document.add_heading(clean_line.replace("### ", "", 1), level=3)
                continue

            document.add_paragraph(clean_line)

        document.save(file_path)

        return ExportResult(
            success=True,
            file_path=str(file_path),
            file_name=file_path.name,
            export_format="docx",
            detail=f"Word 文件导出成功：{file_path}",
        )


def format_export_result(export_result: ExportResult) -> str:
    """
    将导出结果格式化为终端可读文本。
    """
    lines = []

    lines.append("=" * 80)
    lines.append("结果导出完成")
    lines.append("=" * 80)
    lines.append(f"导出状态：{'成功' if export_result.success else '失败'}")
    lines.append(f"导出格式：{export_result.export_format}")
    lines.append(f"文件名称：{export_result.file_name}")
    lines.append(f"文件路径：{export_result.file_path}")
    lines.append(f"说明：{export_result.detail}")

    return "\n".join(lines)