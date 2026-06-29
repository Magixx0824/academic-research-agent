from typing import Any, Dict, List, Optional


PAPER_READING_SECTIONS: Dict[str, Dict[str, Any]] = {
    "research_background": {
        "title": "研究背景",
        "question": "请概括这篇论文的研究背景。重点说明现实背景、学术背景以及作者为什么提出该研究。",
        "retrieval_queries": [
            "研究背景 现实背景 学术背景 研究意义 专精特新企业 合作创新 组织韧性 持续创新能力",
            "引言 问题提出 外部冲击 技术环境动荡 专精特新企业 持续创新",
        ],
    },
    "research_question": {
        "title": "研究问题",
        "question": "请概括这篇论文的核心研究问题。重点说明作者试图解释什么关系、机制或现象。",
        "retrieval_queries": [
            "研究问题 研究假设 理论模型 合作创新 组织韧性 持续创新能力",
            "合作创新如何影响专精特新企业持续创新能力 组织韧性的中介作用 技术环境动荡性的调节作用",
        ],
    },
    "theoretical_basis": {
        "title": "理论基础",
        "question": "请概括这篇论文使用的理论基础或理论逻辑。重点说明作者如何构建理论分析框架。",
        "retrieval_queries": [
            "理论基础 理论分析 研究假设 合作创新 组织韧性 持续创新能力",
            "组织韧性 中介作用 技术环境动荡性 调节作用 理论模型",
        ],
    },
    "data_and_method": {
        "title": "数据与方法",
        "question": "请概括这篇论文使用的数据来源、样本对象、研究方法和模型设计。",
        "retrieval_queries": [
            "数据来源 样本 研究方法 变量测量 模型设计 实证检验",
            "问卷调查 回归模型 样本企业 变量定义 信度效度",
        ],
    },
    "variables": {
        "title": "核心变量",
        "question": "请概括这篇论文的核心变量，包括被解释变量、解释变量、中介变量、调节变量或控制变量。",
        "retrieval_queries": [
            "变量测量 被解释变量 解释变量 中介变量 调节变量 控制变量",
            "持续创新能力 合作创新 组织韧性 技术环境动荡性 变量定义",
        ],
    },
    "main_findings": {
        "title": "主要结论",
        "question": "请概括这篇论文的主要研究结论。重点说明实证结果或理论发现。",
        "retrieval_queries": [
            "研究结论 主要结论 研究发现 实证结果 回归结果 稳健性检验",
            "合作创新 对 持续创新能力 显著正向影响 组织韧性 中介作用 技术环境动荡性 调节作用",
            "结论与启示 研究结论 专精特新企业 持续创新能力 合作创新 组织韧性",
        ],
    },
    "innovation_points": {
        "title": "创新点",
        "question": "请概括这篇论文可能的创新点，包括理论创新、方法创新、数据创新或研究视角创新。",
        "retrieval_queries": [
            "创新点 理论贡献 研究贡献 边际贡献 研究视角",
            "合作创新 组织韧性 专精特新企业 持续创新能力 技术环境动荡性",
        ],
    },
    "limitations": {
        "title": "局限性",
        "question": "请概括这篇论文可能存在的研究局限。只能依据参考资料进行判断，不能过度发挥。",
        "retrieval_queries": [
            "研究局限 不足 未来研究 展望 限于篇幅 留存备索",
            "样本限制 数据限制 方法限制 稳健性检验 未来研究方向",
        ],
    },
    "research_inspiration": {
        "title": "对我研究的启发",
        "question": "请说明这篇论文对后续开展相关研究可能有什么启发。重点从选题、理论机制、变量设计和研究方法角度总结。",
        "retrieval_queries": [
            "研究启示 管理启示 理论启示 结论与启示 未来研究",
            "合作创新 组织韧性 持续创新能力 变量设计 理论机制",
        ],
    },
}


class PaperReadingTool:
    """
    单篇论文精读工具。

    功能：
    1. 针对指定论文 file_name 进行定向检索；
    2. 围绕不同精读维度生成问题；
    3. 调用 LLMService 生成结构化精读内容；
    4. 返回可用于展示或后续导出的论文精读卡片。
    """

    def __init__(self, vector_service: Any, llm_service: Any):
        self.vector_service = vector_service
        self.llm_service = llm_service

    def _search_contexts_for_section(
        self,
        file_name: str,
        section_config: Dict[str, Any],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        针对某个精读维度进行增强检索。

        做法：
        1. 使用多个 retrieval query 进行本地向量检索；
        2. 按 file_name 限定在指定论文内；
        3. 按页码和 chunk_index 去重；
        4. 保留距离较小的 top_k 个结果。
        """
        retrieval_queries = section_config.get("retrieval_queries") or [
            section_config["question"]
        ]

        merged_results = {}

        for retrieval_query in retrieval_queries:
            results = self.vector_service.search(
                query=retrieval_query,
                top_k=top_k,
                where={"file_name": file_name},
            )

            for item in results:
                metadata = item.get("metadata", {})
                result_key = (
                    metadata.get("file_name"),
                    metadata.get("page_number"),
                    metadata.get("chunk_index"),
                )

                old_item = merged_results.get(result_key)

                if old_item is None:
                    merged_results[result_key] = item
                else:
                    old_distance = old_item.get("distance")
                    new_distance = item.get("distance")

                    if old_distance is None:
                        merged_results[result_key] = item
                    elif new_distance is not None and new_distance < old_distance:
                        merged_results[result_key] = item

        sorted_results = sorted(
            merged_results.values(),
            key=lambda item: item.get("distance", 999),
        )

        return sorted_results[:top_k]

    def read_single_paper(
        self,
        file_name: str,
        sections: Optional[List[str]] = None,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        生成单篇论文精读结果。

        参数：
        - file_name: 要精读的论文文件名，必须与 metadata 中的 file_name 完全一致
        - sections: 要生成的精读维度列表；如果为空，则默认生成全部维度
        - top_k: 每个问题检索的 chunk 数量

        返回：
        {
            "file_name": "...",
            "sections": [
                {
                    "section_key": "...",
                    "section_title": "...",
                    "question": "...",
                    "answer": "...",
                    "sources": [...],
                    "uncertainty": "..."
                }
            ]
        }
        """
        if not file_name or not file_name.strip():
            raise ValueError("file_name 不能为空")

        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")

        selected_sections = sections or list(PAPER_READING_SECTIONS.keys())
        section_results = []

        for section_key in selected_sections:
            if section_key not in PAPER_READING_SECTIONS:
                raise ValueError(
                    f"未知的精读维度：{section_key}。"
                    f"可选值包括：{list(PAPER_READING_SECTIONS.keys())}"
                )

            section_config = PAPER_READING_SECTIONS[section_key]
            section_title = section_config["title"]
            question = section_config["question"]

            contexts = self._search_contexts_for_section(
                file_name=file_name,
                section_config=section_config,
                top_k=top_k,
            )

            rag_result = self.llm_service.answer_with_contexts(
                question=question,
                contexts=contexts,
            )

            section_results.append(
                {
                    "section_key": section_key,
                    "section_title": section_title,
                    "question": question,
                    "answer": rag_result.get("answer", ""),
                    "sources": rag_result.get("sources", []),
                    "uncertainty": rag_result.get("uncertainty", ""),
                }
            )

        return {
            "file_name": file_name,
            "section_count": len(section_results),
            "sections": section_results,
        }

    def read_quick_card(
        self,
        file_name: str,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        生成轻量版论文精读卡片。

        该函数用于开发阶段验收，减少 API 调用次数。
        """
        quick_sections = [
            "research_background",
            "research_question",
            "main_findings",
        ]

        return self.read_single_paper(
            file_name=file_name,
            sections=quick_sections,
            top_k=top_k,
        )


def format_paper_reading_card(reading_result: Dict[str, Any]) -> str:
    """
    将单篇论文精读结果格式化为终端可读文本。
    """
    lines = []

    file_name = reading_result.get("file_name", "未知文件")
    section_count = reading_result.get("section_count", 0)

    lines.append("=" * 80)
    lines.append("单篇论文精读卡片")
    lines.append("=" * 80)
    lines.append(f"论文文件：{file_name}")
    lines.append(f"精读维度数量：{section_count}")

    sections = reading_result.get("sections", [])

    if not sections:
        lines.append("\n未生成任何精读内容。")
        return "\n".join(lines)

    for index, section in enumerate(sections, start=1):
        lines.append("\n" + "-" * 80)
        lines.append(f"{index}. {section.get('section_title', '未知维度')}")
        lines.append("-" * 80)

        lines.append("【问题】")
        lines.append(section.get("question", ""))

        lines.append("\n【回答】")
        lines.append(section.get("answer", ""))

        lines.append("\n【依据来源】")
        sources = section.get("sources", [])

        if not sources:
            lines.append("未返回来源。")
        else:
            for source_index, source in enumerate(sources, start=1):
                lines.append(
                    f"{source_index}. {source.get('file_name')} | "
                    f"第 {source.get('page_number')} 页 | "
                    f"chunk_index={source.get('chunk_index')} | "
                    f"distance={source.get('distance')}"
                )

        lines.append("\n【不确定之处】")
        lines.append(section.get("uncertainty", ""))

    return "\n".join(lines)