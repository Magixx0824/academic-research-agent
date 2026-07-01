from typing import Any, Dict, List, Optional


PAPER_COMPARISON_DIMENSIONS: Dict[str, Dict[str, Any]] = {
    "research_question": {
        "title": "研究问题",
        "question": "请概括这篇论文的核心研究问题。重点说明作者试图解释什么关系、机制或现象。",
        "retrieval_queries": [
            "研究问题 研究假设 理论模型 作用机制 中介作用 调节作用",
            "核心研究问题 研究目的 research question research objective theoretical model",
            "hypothesis mechanism mediation moderation relationship",
        ],
    },
    "data_and_method": {
        "title": "数据与方法",
        "question": "请概括这篇论文使用的数据来源、样本对象、研究方法和模型设计。",
        "retrieval_queries": [
            "数据来源 样本 研究方法 变量测量 模型设计 实证检验 回归模型",
            "data sample methodology method model empirical test measurement",
            "research method data source sample regression model variable measurement",
        ],
    },
    "main_findings": {
        "title": "主要结论",
        "question": "请概括这篇论文的主要研究结论。重点说明实证结果或理论发现。",
        "retrieval_queries": [
            "研究结论 主要结论 研究发现 实证结果 回归结果 稳健性检验",
            "findings results conclusion empirical results robustness main findings",
            "significant positive effect mediation moderation conclusion implications",
        ],
    },
    "theoretical_basis": {
        "title": "理论基础",
        "question": "请概括这篇论文使用的理论基础或理论逻辑。",
        "retrieval_queries": [
            "理论基础 理论分析 理论模型 理论逻辑",
            "theory theoretical framework theoretical basis conceptual framework",
            "resource based view dynamic capability theory mechanism",
        ],
    },
    "variables": {
        "title": "核心变量",
        "question": "请概括这篇论文的核心变量，包括被解释变量、解释变量、中介变量、调节变量或控制变量。",
        "retrieval_queries": [
            "变量测量 被解释变量 解释变量 中介变量 调节变量 控制变量",
            "variables dependent variable independent variable mediator moderator control variables",
            "measurement construct operationalization",
        ],
    },
}


class PaperCompareTool:
    """
    多篇论文对比工具。

    功能：
    1. 对多篇论文在相同维度下分别生成摘要；
    2. 基于各论文摘要生成横向对比；
    3. 输出结构化对比结果，便于后续做文献综述和选题分析。
    """

    def __init__(self, vector_service: Any, llm_service: Any):
        self.vector_service = vector_service
        self.llm_service = llm_service

    def _search_contexts_for_dimension(
        self,
        file_name: str,
        dimension_config: Dict[str, Any],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        针对某篇论文和某个对比维度进行增强向量检索。

        这里使用中英文混合 retrieval query，目的是同时支持中文论文和英文论文。
        """
        retrieval_queries = dimension_config.get("retrieval_queries") or [
            dimension_config["question"]
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
                    item["retrieval_type"] = "vector"
                    merged_results[result_key] = item
                else:
                    old_distance = old_item.get("distance")
                    new_distance = item.get("distance")

                    if old_distance is None:
                        item["retrieval_type"] = "vector"
                        merged_results[result_key] = item
                    elif new_distance is not None and new_distance < old_distance:
                        item["retrieval_type"] = "vector"
                        merged_results[result_key] = item

        sorted_results = sorted(
            merged_results.values(),
            key=lambda item: item.get("distance", 999),
        )

        return sorted_results[:top_k]

    def _summarize_paper_dimension(
        self,
        file_name: str,
        dimension_key: str,
        top_k: int,
    ) -> Dict[str, Any]:
        """
        生成某篇论文在某一维度下的摘要。
        """
        if dimension_key not in PAPER_COMPARISON_DIMENSIONS:
            raise ValueError(
                f"未知的对比维度：{dimension_key}。"
                f"可选值包括：{list(PAPER_COMPARISON_DIMENSIONS.keys())}"
            )

        dimension_config = PAPER_COMPARISON_DIMENSIONS[dimension_key]
        question = dimension_config["question"]

        contexts = self._search_contexts_for_dimension(
            file_name=file_name,
            dimension_config=dimension_config,
            top_k=top_k,
        )

        rag_result = self.llm_service.answer_with_contexts(
            question=question,
            contexts=contexts,
        )

        return {
            "file_name": file_name,
            "dimension_key": dimension_key,
            "dimension_title": dimension_config["title"],
            "question": question,
            "answer": rag_result.get("answer", ""),
            "sources": rag_result.get("sources", []),
            "uncertainty": rag_result.get("uncertainty", ""),
        }

    def compare_papers(
        self,
        file_names: List[str],
        dimensions: Optional[List[str]] = None,
        top_k: int = 3,
        include_synthesis: bool = True,
    ) -> Dict[str, Any]:
        """
        对多篇论文进行横向对比。

        参数：
        - file_names: 要对比的论文文件名列表；
        - dimensions: 对比维度；如果为空，默认使用轻量版 3 个维度；
        - top_k: 每个维度检索的 chunk 数量；
        - include_synthesis: 是否生成综合对比结论。

        返回：
        {
            "file_names": [...],
            "dimensions": [...],
            "paper_summaries": {...},
            "synthesis": {...}
        }
        """
        if not file_names or len(file_names) < 2:
            raise ValueError("至少需要输入两篇论文进行对比")

        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")

        selected_dimensions = dimensions or [
            "research_question",
            "data_and_method",
            "main_findings",
        ]

        paper_summaries: Dict[str, Dict[str, Any]] = {}

        for file_name in file_names:
            paper_summaries[file_name] = {}

            for dimension_key in selected_dimensions:
                dimension_summary = self._summarize_paper_dimension(
                    file_name=file_name,
                    dimension_key=dimension_key,
                    top_k=top_k,
                )

                paper_summaries[file_name][dimension_key] = dimension_summary

        synthesis = None

        if include_synthesis:
            synthesis = self._synthesize_comparison(
                file_names=file_names,
                dimensions=selected_dimensions,
                paper_summaries=paper_summaries,
            )

        return {
            "file_names": file_names,
            "paper_count": len(file_names),
            "dimensions": selected_dimensions,
            "dimension_count": len(selected_dimensions),
            "paper_summaries": paper_summaries,
            "synthesis": synthesis,
        }

    def _synthesize_comparison(
        self,
        file_names: List[str],
        dimensions: List[str],
        paper_summaries: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        基于各论文的维度摘要生成综合对比。
        """
        context_items = []

        for file_name in file_names:
            for dimension_key in dimensions:
                dimension_summary = paper_summaries[file_name][dimension_key]
                dimension_title = dimension_summary.get("dimension_title", "")
                answer = dimension_summary.get("answer", "")

                context_items.append(
                    {
                        "content": (
                            f"论文：{file_name}\n"
                            f"维度：{dimension_title}\n"
                            f"摘要：{answer}"
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

        question = (
            "请基于以上多篇论文的维度摘要，进行横向对比分析。"
            "请从以下方面输出："
            "1. 研究问题的共同点与差异；"
            "2. 数据与方法的共同点与差异；"
            "3. 主要结论的共同点与差异；"
            "4. 对后续文献综述或研究设计的启发。"
            "要求表述清晰，不能编造摘要中没有的信息。"
        )

        rag_result = self.llm_service.answer_with_contexts(
            question=question,
            contexts=context_items,
        )

        return {
            "question": question,
            "answer": rag_result.get("answer", ""),
            "sources": rag_result.get("sources", []),
            "uncertainty": rag_result.get("uncertainty", ""),
        }


def format_paper_comparison_result(compare_result: Dict[str, Any]) -> str:
    """
    将多篇论文对比结果格式化为终端可读文本。
    """
    lines = []

    file_names = compare_result.get("file_names", [])
    dimensions = compare_result.get("dimensions", [])
    paper_summaries = compare_result.get("paper_summaries", {})

    lines.append("=" * 80)
    lines.append("多篇论文对比结果")
    lines.append("=" * 80)
    lines.append(f"论文数量：{compare_result.get('paper_count', 0)}")
    lines.append(f"对比维度数量：{compare_result.get('dimension_count', 0)}")
    lines.append("论文列表：")
    for file_name in file_names:
        lines.append(f"- {file_name}")

    for dimension_key in dimensions:
        dimension_title = PAPER_COMPARISON_DIMENSIONS[dimension_key]["title"]

        lines.append("\n" + "-" * 80)
        lines.append(f"对比维度：{dimension_title}")
        lines.append("-" * 80)

        for file_name in file_names:
            summary = paper_summaries.get(file_name, {}).get(dimension_key, {})

            lines.append(f"\n【论文】{file_name}")
            lines.append("【摘要】")
            lines.append(summary.get("answer", ""))

            lines.append("【依据来源】")
            sources = summary.get("sources", [])

            if not sources:
                lines.append("未返回来源。")
            else:
                for source_index, source in enumerate(sources, start=1):
                    distance = source.get("distance")
                    retrieval_text = distance if distance is not None else (
                        source.get("retrieval_type") or "summary"
                    )

                    lines.append(
                        f"{source_index}. {source.get('file_name')} | "
                        f"第 {source.get('page_number')} 页 | "
                        f"chunk_index={source.get('chunk_index')} | "
                        f"retrieval={retrieval_text}"
                    )

    synthesis = compare_result.get("synthesis")

    if synthesis:
        lines.append("\n" + "=" * 80)
        lines.append("综合对比分析")
        lines.append("=" * 80)

        lines.append("【回答】")
        lines.append(synthesis.get("answer", ""))

        lines.append("\n【不确定之处】")
        lines.append(synthesis.get("uncertainty", ""))

    return "\n".join(lines)