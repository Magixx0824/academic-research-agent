from typing import Any, Dict, List, Optional

from app.services.llm_service import format_rag_answer
from app.tools.paper_tools import PaperReadingTool, format_paper_reading_card
from app.tools.compare_tools import PaperCompareTool, format_paper_comparison_result
from app.tools.review_tools import LiteratureReviewTool, format_literature_review_framework
from app.tools.writing_tools import AcademicWritingCheckTool, format_writing_check_result


SUPPORTED_WORKFLOW_TASKS = {
    "rag_answer": "基础 RAG 问答",
    "single_paper_reading": "单篇论文精读",
    "paper_comparison": "多篇论文对比",
    "literature_review": "文献综述框架生成",
    "writing_check": "学术写作检查",
}


class AcademicResearchWorkflow:
    """
    学术研究工作流统一编排工具。

    功能：
    1. 为前面已经开发的工具提供统一调用入口；
    2. 根据 task_type 自动分发到对应工具；
    3. 返回统一结构，方便后续接入 Streamlit 或 FastAPI；
    4. 避免前端或调用层直接操作多个工具类。
    """

    def __init__(self, vector_service: Any, llm_service: Any):
        self.vector_service = vector_service
        self.llm_service = llm_service

        self.paper_reading_tool = PaperReadingTool(
            vector_service=vector_service,
            llm_service=llm_service,
        )

        self.paper_compare_tool = PaperCompareTool(
            vector_service=vector_service,
            llm_service=llm_service,
        )

        self.review_tool = LiteratureReviewTool(
            vector_service=vector_service,
            llm_service=llm_service,
        )

        self.writing_check_tool = AcademicWritingCheckTool(
            llm_service=llm_service,
        )

    def run_task(self, task_type: str, **kwargs) -> Dict[str, Any]:
        """
        统一任务入口。

        参数：
        - task_type: 任务类型；
        - kwargs: 不同任务所需的参数。

        支持任务：
        - rag_answer
        - single_paper_reading
        - paper_comparison
        - literature_review
        - writing_check
        """
        if task_type not in SUPPORTED_WORKFLOW_TASKS:
            raise ValueError(
                f"未知任务类型：{task_type}。"
                f"可选任务包括：{list(SUPPORTED_WORKFLOW_TASKS.keys())}"
            )

        if task_type == "rag_answer":
            result = self._run_rag_answer(**kwargs)

        elif task_type == "single_paper_reading":
            result = self._run_single_paper_reading(**kwargs)

        elif task_type == "paper_comparison":
            result = self._run_paper_comparison(**kwargs)

        elif task_type == "literature_review":
            result = self._run_literature_review(**kwargs)

        elif task_type == "writing_check":
            result = self._run_writing_check(**kwargs)

        else:
            raise ValueError(f"暂不支持的任务类型：{task_type}")

        return {
            "task_type": task_type,
            "task_name": SUPPORTED_WORKFLOW_TASKS[task_type],
            "status": "success",
            "result": result,
        }

    @staticmethod
    def _require_param(kwargs: Dict[str, Any], param_name: str) -> Any:
        """
        获取必需参数。
        """
        value = kwargs.get(param_name)

        if value is None:
            raise ValueError(f"缺少必需参数：{param_name}")

        if isinstance(value, str) and not value.strip():
            raise ValueError(f"参数不能为空：{param_name}")

        return value

    def _run_rag_answer(self, **kwargs) -> Dict[str, Any]:
        """
        执行基础 RAG 问答。
        """
        question = self._require_param(kwargs, "question")
        top_k = kwargs.get("top_k", 3)
        where = kwargs.get("where")

        contexts = self.vector_service.search(
            query=question,
            top_k=top_k,
            where=where,
        )

        return self.llm_service.answer_with_contexts(
            question=question,
            contexts=contexts,
        )

    def _run_single_paper_reading(self, **kwargs) -> Dict[str, Any]:
        """
        执行单篇论文精读。
        """
        file_name = self._require_param(kwargs, "file_name")
        top_k = kwargs.get("top_k", 4)
        mode = kwargs.get("mode", "quick")
        sections = kwargs.get("sections")

        if sections:
            return self.paper_reading_tool.read_single_paper(
                file_name=file_name,
                sections=sections,
                top_k=top_k,
            )

        if mode == "quick":
            return self.paper_reading_tool.read_quick_card(
                file_name=file_name,
                top_k=top_k,
            )

        if mode == "full":
            return self.paper_reading_tool.read_full_card(
                file_name=file_name,
                top_k=top_k,
            )

        raise ValueError("mode 只能是 quick 或 full")

    def _run_paper_comparison(self, **kwargs) -> Dict[str, Any]:
        """
        执行多篇论文对比。
        """
        file_names = self._require_param(kwargs, "file_names")
        dimensions = kwargs.get("dimensions")
        top_k = kwargs.get("top_k", 4)
        include_synthesis = kwargs.get("include_synthesis", True)

        return self.paper_compare_tool.compare_papers(
            file_names=file_names,
            dimensions=dimensions,
            top_k=top_k,
            include_synthesis=include_synthesis,
        )

    def _run_literature_review(self, **kwargs) -> Dict[str, Any]:
        """
        执行文献综述框架生成。
        """
        topic = self._require_param(kwargs, "topic")
        file_names = self._require_param(kwargs, "file_names")
        dimensions = kwargs.get("dimensions")
        top_k = kwargs.get("top_k", 4)

        return self.review_tool.generate_review_framework(
            topic=topic,
            file_names=file_names,
            dimensions=dimensions,
            top_k=top_k,
        )

    def _run_writing_check(self, **kwargs) -> Dict[str, Any]:
        """
        执行学术写作检查。
        """
        text = self._require_param(kwargs, "text")
        writing_goal = kwargs.get("writing_goal", "学术论文写作检查")
        focus = kwargs.get("focus")

        return self.writing_check_tool.check_text(
            text=text,
            writing_goal=writing_goal,
            focus=focus,
        )


def format_workflow_result(workflow_result: Dict[str, Any]) -> str:
    """
    将统一工作流结果格式化为终端可读文本。
    """
    task_type = workflow_result.get("task_type")
    task_name = workflow_result.get("task_name")
    status = workflow_result.get("status")
    result = workflow_result.get("result", {})

    lines = []

    lines.append("=" * 80)
    lines.append("统一学术研究工作流结果")
    lines.append("=" * 80)
    lines.append(f"任务类型：{task_type}")
    lines.append(f"任务名称：{task_name}")
    lines.append(f"任务状态：{status}")

    lines.append("\n" + "=" * 80)
    lines.append("任务输出")
    lines.append("=" * 80)

    if task_type == "rag_answer":
        lines.append(format_rag_answer(result))

    elif task_type == "single_paper_reading":
        lines.append(format_paper_reading_card(result))

    elif task_type == "paper_comparison":
        lines.append(format_paper_comparison_result(result))

    elif task_type == "literature_review":
        lines.append(format_literature_review_framework(result))

    elif task_type == "writing_check":
        lines.append(format_writing_check_result(result))

    else:
        lines.append(str(result))

    return "\n".join(lines)