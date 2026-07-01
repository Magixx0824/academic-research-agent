from typing import Any, Dict, List, Optional


DEFAULT_WRITING_CHECK_FOCUS = [
    "structure",
    "logic",
    "academic_style",
    "evidence",
    "clarity",
]


WRITING_CHECK_FOCUS_LABELS = {
    "structure": "结构完整性",
    "logic": "逻辑连贯性",
    "academic_style": "学术表达规范性",
    "evidence": "论据与文献支撑",
    "clarity": "表达清晰度",
    "redundancy": "重复与冗余",
    "mechanism": "理论机制合理性",
    "variable_consistency": "变量表述一致性",
}


class AcademicWritingCheckTool:
    """
    学术写作检查工具。

    功能：
    1. 接收一段论文文本；
    2. 从结构、逻辑、学术表达、证据支撑等角度进行检查；
    3. 输出问题诊断、修改建议和局部示范修改；
    4. 不直接代写全文，主要用于辅助用户修改已有文本。
    """

    def __init__(self, llm_service: Any):
        self.llm_service = llm_service

    def check_text(
        self,
        text: str,
        writing_goal: str = "学术论文写作检查",
        focus: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        检查一段学术文本。

        参数：
        - text: 待检查文本；
        - writing_goal: 写作目标，例如“文献综述”“理论机制”“实证结果分析”；
        - focus: 检查重点列表。

        返回：
        {
            "writing_goal": "...",
            "focus": [...],
            "char_count": ...,
            "check_result": "...",
            "sources": [...],
            "uncertainty": "..."
        }
        """
        if not text or not text.strip():
            raise ValueError("待检查文本不能为空")

        selected_focus = focus or DEFAULT_WRITING_CHECK_FOCUS

        for item in selected_focus:
            if item not in WRITING_CHECK_FOCUS_LABELS:
                raise ValueError(
                    f"未知的检查重点：{item}。"
                    f"可选值包括：{list(WRITING_CHECK_FOCUS_LABELS.keys())}"
                )

        contexts = [
            {
                "content": text,
                "metadata": {
                    "file_name": "user_draft",
                    "page_number": None,
                    "chunk_index": "writing_check_input",
                },
                "distance": None,
                "retrieval_type": "draft",
            }
        ]

        question = self._build_check_question(
            writing_goal=writing_goal,
            focus=selected_focus,
        )

        rag_result = self.llm_service.answer_with_contexts(
            question=question,
            contexts=contexts,
        )

        return {
            "writing_goal": writing_goal,
            "focus": selected_focus,
            "focus_labels": [
                WRITING_CHECK_FOCUS_LABELS[item] for item in selected_focus
            ],
            "char_count": len(text),
            "check_result": rag_result.get("answer", ""),
            "sources": rag_result.get("sources", []),
            "uncertainty": rag_result.get("uncertainty", ""),
        }

    @staticmethod
    def _build_check_question(
        writing_goal: str,
        focus: List[str],
    ) -> str:
        """
        构造写作检查问题。
        """
        focus_labels = [
            WRITING_CHECK_FOCUS_LABELS[item]
            for item in focus
        ]

        focus_text = "、".join(focus_labels)

        return (
            f"请对给定论文文本进行学术写作检查。文本用途是：{writing_goal}。"
            f"本次重点检查：{focus_text}。"
            "请严格依据给定文本进行判断，不要补充不存在的研究结果、数据或文献。"
            "输出结构必须包括："
            "1. 总体判断；"
            "2. 主要问题清单；"
            "3. 逐项修改建议；"
            "4. 可保留的优点；"
            "5. 需要补充文献或证据的位置；"
            "6. 局部示范修改。"
            "注意：不要直接重写全文，只提供有针对性的修改建议和少量示范表达。"
        )


def format_writing_check_result(check_result: Dict[str, Any]) -> str:
    """
    将写作检查结果格式化为终端可读文本。
    """
    lines = []

    lines.append("=" * 80)
    lines.append("学术写作检查结果")
    lines.append("=" * 80)

    lines.append(f"写作目标：{check_result.get('writing_goal', '')}")
    lines.append(f"文本字符数：{check_result.get('char_count', 0)}")

    lines.append("\n检查重点：")
    for label in check_result.get("focus_labels", []):
        lines.append(f"- {label}")

    lines.append("\n" + "-" * 80)
    lines.append("【检查结果】")
    lines.append("-" * 80)
    lines.append(check_result.get("check_result", ""))

    lines.append("\n" + "-" * 80)
    lines.append("【依据来源】")
    lines.append("-" * 80)

    sources = check_result.get("sources", [])

    if not sources:
        lines.append("未返回来源。")
    else:
        for index, source in enumerate(sources, start=1):
            retrieval_type = source.get("retrieval_type") or "draft"
            chunk_index = source.get("chunk_index")

            lines.append(
                f"{index}. {source.get('file_name')} | "
                f"来源类型={retrieval_type} | "
                f"文本片段={chunk_index}"
            )

    lines.append("\n" + "-" * 80)
    lines.append("【不确定之处】")
    lines.append("-" * 80)
    lines.append(check_result.get("uncertainty", ""))

    return "\n".join(lines)