from typing import Any, Dict, List, Optional

from app.tools.compare_tools import PaperCompareTool


DEFAULT_REVIEW_DIMENSIONS = [
    "research_question",
    "theoretical_basis",
    "data_and_method",
    "variables",
    "main_findings",
]


class LiteratureReviewTool:
    """
    文献综述框架生成工具。

    功能：
    1. 接收研究主题和多篇论文文件名；
    2. 调用 PaperCompareTool 获取多篇论文的结构化摘要；
    3. 基于摘要生成文献综述框架；
    4. 输出可用于论文写作的综述结构。
    """

    def __init__(self, vector_service: Any, llm_service: Any):
        self.vector_service = vector_service
        self.llm_service = llm_service
        self.compare_tool = PaperCompareTool(
            vector_service=vector_service,
            llm_service=llm_service,
        )

    def generate_review_framework(
        self,
        topic: str,
        file_names: List[str],
        dimensions: Optional[List[str]] = None,
        top_k: int = 4,
    ) -> Dict[str, Any]:
        """
        生成文献综述框架。

        参数：
        - topic: 文献综述主题；
        - file_names: 参与综述的论文文件名列表；
        - dimensions: 用于生成综述的对比维度；
        - top_k: 每个维度检索的 chunk 数量。

        返回：
        {
            "topic": "...",
            "file_names": [...],
            "compare_result": {...},
            "framework": "...",
            "sources": [...],
            "uncertainty": "..."
        }
        """
        if not topic or not topic.strip():
            raise ValueError("topic 不能为空")

        if not file_names or len(file_names) < 2:
            raise ValueError("至少需要输入两篇论文生成文献综述框架")

        selected_dimensions = dimensions or DEFAULT_REVIEW_DIMENSIONS

        compare_result = self.compare_tool.compare_papers(
            file_names=file_names,
            dimensions=selected_dimensions,
            top_k=top_k,
            include_synthesis=False,
        )

        framework_contexts = self._build_framework_contexts(
            compare_result=compare_result,
        )

        question = self._build_review_question(
            topic=topic,
            file_names=file_names,
            dimensions=selected_dimensions,
        )

        rag_result = self.llm_service.answer_with_contexts(
            question=question,
            contexts=framework_contexts,
        )

        return {
            "topic": topic,
            "file_names": file_names,
            "paper_count": len(file_names),
            "dimensions": selected_dimensions,
            "dimension_count": len(selected_dimensions),
            "compare_result": compare_result,
            "framework": rag_result.get("answer", ""),
            "sources": rag_result.get("sources", []),
            "uncertainty": rag_result.get("uncertainty", ""),
        }

    def _build_framework_contexts(
        self,
        compare_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        将多篇论文对比摘要转换为 LLMService 可接收的 contexts。

        注意：
        - 这里的 contexts 来源是“结构化摘要”，不是原始 PDF chunk；
        - metadata 中用 chunk_index 标记维度名称。
        """
        contexts = []

        paper_summaries = compare_result.get("paper_summaries", {})
        dimensions = compare_result.get("dimensions", [])

        for file_name, dimension_map in paper_summaries.items():
            for dimension_key in dimensions:
                dimension_summary = dimension_map.get(dimension_key, {})

                dimension_title = dimension_summary.get("dimension_title", "")
                answer = dimension_summary.get("answer", "")

                if not answer:
                    continue

                contexts.append(
                    {
                        "content": (
                            f"论文文件：{file_name}\n"
                            f"综述维度：{dimension_title}\n"
                            f"维度摘要：{answer}"
                        ),
                        "metadata": {
                            "file_name": file_name,
                            "page_number": None,
                            "chunk_index": dimension_key,
                        },
                        "distance": None,
                        "retrieval_type": "summary",
                    }
                )

        return contexts

    @staticmethod
    def _build_review_question(
        topic: str,
        file_names: List[str],
        dimensions: List[str],
    ) -> str:
        """
        构造文献综述框架生成问题。
        """
        file_list_text = "、".join(file_names)
        dimension_text = "、".join(dimensions)

        return (
            f"请基于给定文献摘要，围绕“{topic}”生成一个中文文献综述框架。"
            f"涉及论文包括：{file_list_text}。"
            f"当前参考维度包括：{dimension_text}。"
            "请严格依据参考资料，不要编造不存在的文献、作者、数据或结论。"
            "输出结构必须包括以下部分："
            "1. 综述主题界定；"
            "2. 已有研究的主要脉络；"
            "3. 可划分的文献类别；"
            "4. 已有研究的共同结论；"
            "5. 已有研究的差异与分歧；"
            "6. 现有研究不足；"
            "7. 后续研究方向；"
            "8. 可用于论文写作的文献综述章节框架。"
            "如果参考文献数量较少或主题差异较大，需要明确说明综述结论的局限。"
        )


def format_literature_review_framework(review_result: Dict[str, Any]) -> str:
    """
    将文献综述框架结果格式化为终端可读文本。
    """
    lines = []

    lines.append("=" * 80)
    lines.append("文献综述框架生成结果")
    lines.append("=" * 80)

    lines.append(f"综述主题：{review_result.get('topic', '')}")
    lines.append(f"论文数量：{review_result.get('paper_count', 0)}")
    lines.append(f"综述维度数量：{review_result.get('dimension_count', 0)}")

    lines.append("\n论文列表：")
    for file_name in review_result.get("file_names", []):
        lines.append(f"- {file_name}")

    lines.append("\n" + "-" * 80)
    lines.append("【文献综述框架】")
    lines.append("-" * 80)
    lines.append(review_result.get("framework", ""))

    lines.append("\n" + "-" * 80)
    lines.append("【依据来源】")
    lines.append("-" * 80)

    sources = review_result.get("sources", [])

    if not sources:
        lines.append("未返回来源。")
    else:
        for index, source in enumerate(sources, start=1):
            distance = source.get("distance")
            retrieval_text = distance if distance is not None else (
                source.get("retrieval_type") or "summary"
            )

            lines.append(
                f"{index}. {source.get('file_name')} | "
                f"第 {source.get('page_number')} 页 | "
                f"chunk_index={source.get('chunk_index')} | "
                f"retrieval={retrieval_text}"
            )

    lines.append("\n" + "-" * 80)
    lines.append("【不确定之处】")
    lines.append("-" * 80)
    lines.append(review_result.get("uncertainty", ""))

    return "\n".join(lines)