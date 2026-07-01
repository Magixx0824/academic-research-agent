from typing import Any, Dict, List, Optional

from app.tools.paper_tools import (
    PaperReadingTool,
    format_paper_reading_card,
)


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
        - mode: quick 或 full；
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


def format_batch_paper_reading_result(batch_result: Dict[str, Any]) -> str:
    """
    将批量论文精读结果格式化为 Markdown / 终端可读文本。
    """
    lines = []

    lines.append("# 批量论文精读结果")
    lines.append("")
    lines.append(f"任务状态：{batch_result.get('status', 'unknown')}")
    lines.append(f"精读模式：{batch_result.get('mode', 'unknown')}")
    lines.append(f"论文总数：{batch_result.get('paper_count', 0)}")
    lines.append(f"成功数量：{batch_result.get('success_count', 0)}")
    lines.append(f"失败数量：{batch_result.get('failed_count', 0)}")
    lines.append("")

    results = batch_result.get("results", [])

    if not results:
        lines.append("未生成任何批量精读结果。")
        return "\n".join(lines)

    for index, item in enumerate(results, start=1):
        file_name = item.get("file_name", "未知文件")
        status = item.get("status", "unknown")

        lines.append("---")
        lines.append("")
        lines.append(f"## {index}. {file_name}")
        lines.append("")
        lines.append(f"处理状态：{status}")
        lines.append("")

        if status != "success":
            lines.append(f"错误信息：{item.get('error', '')}")
            lines.append("")
            continue

        reading_result = item.get("reading_result")

        if not reading_result:
            lines.append("未返回精读结果。")
            lines.append("")
            continue

        formatted_card = format_paper_reading_card(reading_result)

        # 去掉终端格式中的长横线，让批量 Markdown 更清晰。
        formatted_card = formatted_card.replace("=" * 80, "")
        formatted_card = formatted_card.replace("-" * 80, "")

        lines.append(formatted_card)
        lines.append("")

    return "\n".join(lines)