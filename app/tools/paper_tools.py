import re
from typing import Any, Dict, List, Optional, Tuple


PAPER_READING_SECTIONS: Dict[str, Dict[str, Any]] = {
    "research_background": {
        "title": "研究背景",
        "question": "请概括这篇论文的研究背景。重点说明现实背景、学术背景以及作者为什么提出该研究。",
        "retrieval_queries": [
            "abstract introduction background motivation research gap research significance",
            "research background practical background academic background research motivation",
            "引言 研究背景 现实背景 学术背景 研究意义 问题提出 研究动机",
            "why this study is proposed what gap this paper addresses",
            "专精特新企业 合作创新 组织韧性 持续创新能力 研究背景",
        ],
        "keyword_queries": [
            "abstract",
            "introduction",
            "background",
            "motivation",
            "research gap",
            "research significance",
            "purpose",
            "研究背景",
            "现实背景",
            "学术背景",
            "研究意义",
            "问题提出",
            "引言",
            "研究动机",
        ],
        "structure_keywords": [
            "abstract",
            "introduction",
            "background",
            "motivation",
            "research gap",
            "this paper",
            "this study",
            "本文",
            "本研究",
            "引言",
        ],
        "page_strategy": "front",
        "retrieval_order": ["structural", "keyword", "vector"],
        "min_contexts": 6,
    },
    "research_question": {
        "title": "研究问题",
        "question": "请概括这篇论文的核心研究问题。重点说明作者试图解释什么关系、机制或现象。",
        "retrieval_queries": [
            "research question research objective research purpose aim this paper investigates this study examines",
            "objective purpose research problem what this paper examines",
            "研究问题 研究目标 研究目的 核心问题 理论模型 作用机制",
            "research objective green innovation efficiency innovation value chain dynamic network DEA",
            "合作创新如何影响持续创新能力 组织韧性的中介作用 技术环境动荡性的调节作用",
        ],
        "keyword_queries": [
            "research question",
            "research objective",
            "objective",
            "purpose",
            "aim",
            "this paper investigates",
            "this study examines",
            "this paper aims",
            "研究问题",
            "研究目标",
            "研究目的",
            "理论模型",
            "作用机制",
            "中介作用",
            "调节作用",
        ],
        "structure_keywords": [
            "abstract",
            "introduction",
            "objective",
            "purpose",
            "aim",
            "research question",
            "this paper",
            "this study",
            "本文",
            "研究问题",
        ],
        "page_strategy": "front",
        "retrieval_order": ["vector", "structural", "keyword"],
        "min_contexts": 6,
    },
    "theoretical_basis": {
        "title": "理论基础",
        "question": "请概括这篇论文使用的理论基础或理论逻辑。重点说明作者如何构建理论分析框架。",
        "retrieval_queries": [
            "theoretical framework theory literature review hypothesis mechanism conceptual framework",
            "theory basis theoretical analysis analytical framework research hypothesis",
            "理论基础 理论分析 文献综述 理论框架 研究假设 理论模型",
            "innovation value chain green innovation efficiency dynamic network DEA theoretical framework",
            "组织韧性 中介作用 技术环境动荡性 调节作用 理论模型",
        ],
        "keyword_queries": [
            "theoretical framework",
            "theory",
            "literature review",
            "hypothesis",
            "mechanism",
            "conceptual framework",
            "理论基础",
            "理论分析",
            "文献综述",
            "研究假设",
            "理论模型",
            "组织韧性",
            "中介作用",
            "调节作用",
        ],
        "structure_keywords": [
            "literature review",
            "theoretical framework",
            "theory",
            "hypothesis",
            "mechanism",
            "model",
            "文献综述",
            "理论基础",
            "研究假设",
        ],
        "page_strategy": "front_middle",
        "retrieval_order": ["keyword", "vector", "structural"],
        "min_contexts": 6,
    },
    "data_and_method": {
        "title": "数据与方法",
        "question": "请概括这篇论文使用的数据来源、样本对象、研究方法和模型设计。",
        "retrieval_queries": [
            "data sample methodology method model variables empirical strategy",
            "data source sample period research method model design measurement",
            "methodology dynamic network DEA innovation value chain input output carry-over variable",
            "数据来源 样本 研究方法 变量测量 模型设计 实证检验",
            "问卷调查 回归模型 样本企业 变量定义 信度效度 描述性统计",
        ],
        "keyword_queries": [
            "data",
            "sample",
            "method",
            "methodology",
            "model",
            "variables",
            "measurement",
            "empirical",
            "DEA",
            "dynamic network DEA",
            "input",
            "output",
            "intermediate",
            "carry-over",
            "数据来源",
            "样本",
            "研究方法",
            "变量测量",
            "模型设计",
            "实证检验",
            "问卷调查",
            "回归",
            "信度",
            "效度",
        ],
        "structure_keywords": [
            "data",
            "method",
            "methodology",
            "model",
            "sample",
            "variables",
            "DEA",
            "empirical",
            "数据",
            "方法",
            "模型",
            "变量",
        ],
        "page_strategy": "middle",
        "retrieval_order": ["keyword", "vector", "structural"],
        "prefer_keyword": True,
        "min_contexts": 6,
    },
    "variables": {
        "title": "核心变量",
        "question": "请概括这篇论文的核心变量，包括被解释变量、解释变量、中介变量、调节变量、控制变量，或模型中的投入、产出、中间变量。",
        "retrieval_queries": [
            "variables measurement dependent variable independent variable mediator moderator control variable",
            "input output intermediate variable carry-over dynamic network DEA index indicator",
            "变量测量 被解释变量 解释变量 中介变量 调节变量 控制变量 指标体系",
            "green innovation efficiency R&D commercialization innovation value chain indicators",
            "持续创新能力 合作创新 组织韧性 技术环境动荡性 变量定义",
        ],
        "keyword_queries": [
            "variable",
            "variables",
            "measurement",
            "indicator",
            "index",
            "input",
            "output",
            "intermediate",
            "carry-over",
            "dependent variable",
            "independent variable",
            "control variable",
            "变量测量",
            "被解释变量",
            "解释变量",
            "中介变量",
            "调节变量",
            "控制变量",
            "指标",
            "投入",
            "产出",
            "持续创新能力",
            "合作创新",
            "组织韧性",
            "技术环境动荡性",
        ],
        "structure_keywords": [
            "variables",
            "measurement",
            "indicator",
            "input",
            "output",
            "intermediate",
            "table",
            "变量",
            "指标",
            "测量",
        ],
        "page_strategy": "middle",
        "retrieval_order": ["keyword", "vector", "structural"],
        "prefer_keyword": True,
        "min_contexts": 6,
    },
    "main_findings": {
        "title": "主要结论",
        "question": "请概括这篇论文的主要研究结论。重点说明实证结果、模型结果、理论发现或政策启示。",
        "retrieval_queries": [
            "results findings conclusion discussion empirical results main findings policy implications",
            "conclusions main conclusions research findings robustness results discussion",
            "major findings empirical findings conclusion and policy implications",
            "研究结论 主要结论 研究发现 实证结果 回归结果 稳健性检验 结论与启示",
            "green innovation efficiency results R&D commercialization efficiency ineffective connection",
            "合作创新 对 持续创新能力 显著正向影响 组织韧性 中介作用 技术环境动荡性 调节作用",
        ],
        "keyword_queries": [
            "results",
            "findings",
            "main findings",
            "empirical results",
            "conclusion",
            "conclusions",
            "discussion",
            "policy implications",
            "robustness",
            "ineffective connection",
            "研究结论",
            "主要结论",
            "研究发现",
            "实证结果",
            "回归结果",
            "稳健性检验",
            "显著正向",
            "正向影响",
            "中介作用",
            "调节作用",
            "异质性",
            "结论与启示",
            "管理启示",
        ],
        "structure_keywords": [
            "results",
            "findings",
            "conclusion",
            "conclusions",
            "discussion",
            "policy implications",
            "robustness",
            "结论",
            "研究发现",
            "结果",
            "启示",
        ],
        "page_strategy": "back",
        "retrieval_order": ["keyword", "structural", "vector"],
        "prefer_keyword": True,
        "min_contexts": 6,
    },
    "innovation_points": {
        "title": "创新点",
        "question": "请概括这篇论文可能的创新点，包括理论创新、方法创新、数据创新或研究视角创新。",
        "retrieval_queries": [
            "contribution novelty innovation research contribution theoretical contribution methodological contribution",
            "marginal contribution originality research perspective practical significance",
            "创新点 理论贡献 研究贡献 边际贡献 研究视角 方法创新 数据创新",
            "dynamic network DEA innovation value chain green innovation efficiency contribution",
            "本文可能的边际贡献 理论贡献 实践意义",
        ],
        "keyword_queries": [
            "contribution",
            "novelty",
            "innovation",
            "originality",
            "theoretical contribution",
            "methodological contribution",
            "practical implication",
            "创新点",
            "理论贡献",
            "研究贡献",
            "边际贡献",
            "研究视角",
            "实践意义",
            "理论意义",
        ],
        "structure_keywords": [
            "contribution",
            "novelty",
            "originality",
            "this paper contributes",
            "创新",
            "贡献",
            "边际贡献",
        ],
        "page_strategy": "front_back",
        "retrieval_order": ["keyword", "structural", "vector"],
        "min_contexts": 6,
    },
    "limitations": {
        "title": "局限性",
        "question": "请概括这篇论文可能存在的研究局限。只能依据参考资料进行判断，不能过度发挥。",
        "retrieval_queries": [
            "limitations future research shortcomings further research future study",
            "research limitation limitation and future research",
            "研究局限 不足 未来研究 展望 样本限制 数据限制 方法限制",
            "不足之处 进一步研究",
        ],
        "keyword_queries": [
            "limitations",
            "limitation",
            "future research",
            "future study",
            "shortcomings",
            "further research",
            "研究局限",
            "不足",
            "未来研究",
            "展望",
            "限于篇幅",
            "留存备索",
            "样本限制",
            "数据限制",
            "方法限制",
        ],
        "structure_keywords": [
            "limitations",
            "future research",
            "future study",
            "shortcomings",
            "limitation",
            "局限",
            "不足",
            "未来研究",
        ],
        "page_strategy": "back",
        "retrieval_order": ["keyword", "structural", "vector"],
        "prefer_keyword": True,
        "min_contexts": 6,
    },
    "research_inspiration": {
        "title": "对我研究的启发",
        "question": "请说明这篇论文对后续开展相关研究可能有什么启发。重点从选题、理论机制、变量设计和研究方法角度总结。",
        "retrieval_queries": [
            "implications theoretical implications practical implications policy implications future research",
            "research inspiration research implication variable design methodology theoretical mechanism",
            "研究启示 管理启示 理论启示 结论与启示 未来研究 变量设计 理论机制",
            "green innovation efficiency innovation value chain dynamic network DEA implication",
            "合作创新 组织韧性 持续创新能力 变量设计 理论机制",
        ],
        "keyword_queries": [
            "implications",
            "policy implications",
            "theoretical implications",
            "practical implications",
            "future research",
            "研究启示",
            "管理启示",
            "理论启示",
            "结论与启示",
            "未来研究",
            "变量设计",
            "理论机制",
        ],
        "structure_keywords": [
            "implications",
            "conclusion",
            "future research",
            "policy implications",
            "启示",
            "结论",
            "未来研究",
        ],
        "page_strategy": "back",
        "retrieval_order": ["keyword", "structural", "vector"],
        "prefer_keyword": True,
        "min_contexts": 6,
    },
}


SECTION_PROMPT_SUFFIXES: Dict[str, str] = {
    "research_background": (
        "请优先依据摘要、引言、背景、研究动机和研究缺口相关片段进行概括。"
        "如果资料中出现 Abstract、Introduction、Motivation、Research gap 等英文内容，"
        "也应据此概括，不要因为没有中文“研究背景”标题就直接回答未找到依据。"
    ),
    "research_question": (
        "请优先依据摘要、引言、研究目标、研究目的、研究问题相关片段进行概括。"
        "如果资料中出现 objective、purpose、aim、this paper investigates、this study examines 等表达，"
        "应据此判断作者试图解决的核心问题。"
    ),
    "theoretical_basis": (
        "请优先依据文献综述、理论框架、研究假设、模型设定和机制分析相关片段进行概括。"
        "如果论文主要是方法型论文，也可以概括其方法逻辑和分析框架。"
    ),
    "data_and_method": (
        "请优先依据 data、sample、method、methodology、model、variables、empirical strategy 等片段进行概括。"
        "如果论文使用 DEA、网络 DEA、动态网络 DEA 等方法，请说明其模型思想、阶段划分和指标设定。"
    ),
    "variables": (
        "请优先依据 variables、measurement、indicator、input、output、intermediate、carry-over 等片段进行概括。"
        "对于 DEA 或效率评价论文，可以将投入、产出、中间产出、结转变量和效率指标作为核心变量或指标体系说明。"
    ),
    "main_findings": (
        "请优先依据 results、findings、discussion、conclusion、policy implications 等片段进行概括。"
        "如果资料中出现结论页、结果页或政策启示页，应基于这些片段提炼主要发现。"
        "除非检索片段完全没有任何结果或结论信息，否则不要轻易回答未找到明确依据。"
    ),
    "innovation_points": (
        "请优先依据 contribution、novelty、originality、theoretical contribution、methodological contribution 等片段进行概括。"
        "如果论文没有明确写出创新点，也可以根据作者的研究视角、方法、数据或对象进行审慎归纳，但必须基于资料。"
    ),
    "limitations": (
        "请优先依据 limitations、future research、shortcomings、future study 等片段进行概括。"
        "如果资料没有明确局限性表述，可以说明现有资料未提供明确局限性，而不是自行发挥。"
    ),
    "research_inspiration": (
        "请优先依据论文的研究问题、方法、变量、结论和启示部分，总结其对后续研究的启发。"
        "可以从选题、理论机制、变量设计、模型方法和论文写作结构角度归纳。"
    ),
}


class PaperReadingTool:
    """
    单篇论文精读工具。

    功能：
    1. 针对指定论文 file_name 进行定向检索；
    2. 围绕不同精读维度生成问题；
    3. 使用向量检索 + 关键词检索 + 结构性页码补充进行混合检索；
    4. 针对英文论文增加英文结构化检索词；
    5. 调用 LLMService 生成结构化精读内容；
    6. 返回可用于展示或后续导出的论文精读卡片。
    """

    def __init__(self, vector_service: Any, llm_service: Any):
        self.vector_service = vector_service
        self.llm_service = llm_service

    @staticmethod
    def _normalize_for_keyword(text: str) -> str:
        """
        关键词匹配归一化。

        作用：
        1. 去除空白字符；
        2. 全部转为小写；
        3. 同时适配中文 PDF 抽取文本和英文论文文本。
        """
        if not text:
            return ""

        text = re.sub(r"\s+", "", text)
        return text.lower()

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        """
        将页码、chunk_index 等字段安全转换为整数。
        """
        if isinstance(value, bool):
            return default

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if match:
                return int(match.group())

        return default

    @staticmethod
    def _chunk_key(chunk: Dict[str, Any]) -> Tuple[Any, Any, Any]:
        """
        构造 chunk 去重 key。
        """
        metadata = chunk.get("metadata", {})
        return (
            metadata.get("file_name"),
            metadata.get("page_number"),
            metadata.get("chunk_index"),
        )

    def _get_all_chunks_by_file(self, file_name: str) -> List[Dict[str, Any]]:
        """
        获取指定论文的全部 chunks，并按页码和 chunk_index 排序。
        """
        if not hasattr(self.vector_service, "get_chunks_by_file"):
            return []

        all_chunks = self.vector_service.get_chunks_by_file(file_name=file_name)

        return sorted(
            all_chunks,
            key=lambda chunk: (
                self._safe_int(chunk.get("metadata", {}).get("page_number")),
                self._safe_int(chunk.get("metadata", {}).get("chunk_index")),
            ),
        )

    def _get_page_range(self, all_chunks: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        获取论文 chunk 中的最小页码和最大页码。
        """
        pages = [
            self._safe_int(chunk.get("metadata", {}).get("page_number"))
            for chunk in all_chunks
        ]
        pages = [page for page in pages if page > 0]

        if not pages:
            return 0, 0

        return min(pages), max(pages)

    @staticmethod
    def _is_reference_like(content: str) -> bool:
        """
        判断一个 chunk 是否像参考文献页。

        目的：
        - 避免“主要结论”“研究背景”等维度被 references 页面干扰；
        - 不做过度复杂判断，只做轻量过滤。
        """
        if not content:
            return False

        stripped = content.strip()
        lower_head = stripped[:500].lower()

        if re.search(r"^\s*(references|bibliography)\b", lower_head):
            return True

        if re.search(r"^\s*(参考文献|参考资料)\b", stripped[:200]):
            return True

        doi_count = lower_head.count("doi")
        journal_count = lower_head.count("journal")
        year_count = len(re.findall(r"\b(19|20)\d{2}\b", lower_head))

        if doi_count >= 2 and year_count >= 3:
            return True

        if journal_count >= 2 and year_count >= 4:
            return True

        return False

    def _keyword_score(self, content: str, keywords: List[str]) -> int:
        """
        计算关键词匹配分数。
        """
        normalized_content = self._normalize_for_keyword(content)

        if not normalized_content:
            return 0

        score = 0

        for keyword in keywords:
            if not keyword:
                continue

            normalized_keyword = self._normalize_for_keyword(keyword)

            if not normalized_keyword:
                continue

            if normalized_keyword in normalized_content:
                score += 3

                # 较长关键词命中时适当加权。
                if len(normalized_keyword) >= 8:
                    score += 1

                # 多次出现说明该 chunk 与该维度更相关。
                occurrence = normalized_content.count(normalized_keyword)
                if occurrence > 1:
                    score += min(occurrence - 1, 3)

        return score

    def _keyword_search_contexts(
        self,
        file_name: str,
        section_config: Dict[str, Any],
        top_k: int,
        all_chunks: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        基于关键词从指定论文的全部 chunks 中筛选候选片段。

        主要用于“主要结论”“数据与方法”“核心变量”等具有明确结构关键词的维度。
        """
        keyword_queries = section_config.get("keyword_queries", [])
        structure_keywords = section_config.get("structure_keywords", [])
        all_keywords = keyword_queries + structure_keywords

        if not all_keywords:
            return []

        all_chunks = all_chunks or self._get_all_chunks_by_file(file_name)

        if not all_chunks:
            return []

        _, max_page = self._get_page_range(all_chunks)
        scored_chunks = []

        for chunk in all_chunks:
            content = chunk.get("content", "")
            metadata = chunk.get("metadata", {})
            page_number = self._safe_int(metadata.get("page_number"))
            chunk_index = self._safe_int(metadata.get("chunk_index"))

            score = self._keyword_score(content, all_keywords)

            # 对后半部分关键词型维度适当加权。
            if section_config.get("prefer_keyword") and max_page:
                if page_number >= max_page - 5:
                    score += 1

            # 避免参考文献 chunk 干扰。
            if self._is_reference_like(content) and score <= 5:
                score -= 5

            if score > 0:
                keyword_chunk = dict(chunk)
                keyword_chunk["retrieval_type"] = "keyword"

                scored_chunks.append(
                    {
                        "chunk": keyword_chunk,
                        "score": score,
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                    }
                )

        scored_chunks = sorted(
            scored_chunks,
            key=lambda item: (
                -item["score"],
                item["page_number"],
                item["chunk_index"],
            ),
        )

        return [item["chunk"] for item in scored_chunks[:top_k]]

    def _page_strategy_score(
        self,
        page_number: int,
        min_page: int,
        max_page: int,
        page_strategy: str,
    ) -> float:
        """
        根据论文页码结构给 chunk 加权。
        """
        if page_number <= 0 or max_page <= 0:
            return 0.0

        total_pages = max(max_page - min_page + 1, 1)
        front_boundary = min_page + max(3, int(total_pages * 0.15))
        middle_start = min_page + int(total_pages * 0.25)
        middle_end = min_page + int(total_pages * 0.75)
        back_boundary = max_page - max(5, int(total_pages * 0.20))

        if page_strategy == "front":
            if page_number <= min_page + 2:
                return 4.0
            if page_number <= front_boundary:
                return 3.0
            return 0.0

        if page_strategy == "front_middle":
            if page_number <= front_boundary:
                return 2.5
            if middle_start <= page_number <= middle_end:
                return 1.5
            return 0.0

        if page_strategy == "middle":
            if middle_start <= page_number <= middle_end:
                return 2.5
            return 0.0

        if page_strategy == "back":
            if page_number >= max_page - 2:
                return 4.0
            if page_number >= back_boundary:
                return 3.0
            return 0.0

        if page_strategy == "front_back":
            if page_number <= front_boundary:
                return 2.0
            if page_number >= back_boundary:
                return 2.0
            return 0.0

        return 0.0

    def _structure_search_contexts(
        self,
        file_name: str,
        section_config: Dict[str, Any],
        top_k: int,
        all_chunks: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        结构性页码补充检索。

        目的：
        1. 研究背景、研究问题优先补充前部页码；
        2. 主要结论、局限性、研究启示优先补充后部页码；
        3. 数据与方法、核心变量优先补充中部页码；
        4. 降低纯语义检索对英文论文结构定位不稳定的问题。
        """
        all_chunks = all_chunks or self._get_all_chunks_by_file(file_name)

        if not all_chunks:
            return []

        page_strategy = section_config.get("page_strategy")

        if not page_strategy:
            return []

        min_page, max_page = self._get_page_range(all_chunks)
        keywords = section_config.get("structure_keywords", []) + section_config.get("keyword_queries", [])
        scored_chunks = []

        for chunk in all_chunks:
            content = chunk.get("content", "")
            metadata = chunk.get("metadata", {})
            page_number = self._safe_int(metadata.get("page_number"))
            chunk_index = self._safe_int(metadata.get("chunk_index"))

            page_score = self._page_strategy_score(
                page_number=page_number,
                min_page=min_page,
                max_page=max_page,
                page_strategy=page_strategy,
            )

            keyword_score = self._keyword_score(content, keywords)
            score = page_score + keyword_score

            # 后部结构检索要特别避免 references 页面挤占结论页。
            if self._is_reference_like(content):
                score -= 6

            if score > 0:
                structural_chunk = dict(chunk)
                structural_chunk["retrieval_type"] = "structural"

                scored_chunks.append(
                    {
                        "chunk": structural_chunk,
                        "score": score,
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                    }
                )

        reverse_page = page_strategy in {"back", "front_back"}

        scored_chunks = sorted(
            scored_chunks,
            key=lambda item: (
                -item["score"],
                -item["page_number"] if reverse_page else item["page_number"],
                item["chunk_index"],
            ),
        )

        return [item["chunk"] for item in scored_chunks[:top_k]]

    @staticmethod
    def _merge_context_groups(
        context_groups: List[List[Dict[str, Any]]],
        max_contexts: int,
    ) -> List[Dict[str, Any]]:
        """
        合并多组检索结果，并按 file_name/page_number/chunk_index 去重。
        """
        merged = []
        existing_keys = set()

        for group in context_groups:
            for item in group:
                metadata = item.get("metadata", {})
                item_key = (
                    metadata.get("file_name"),
                    metadata.get("page_number"),
                    metadata.get("chunk_index"),
                )

                if item_key not in existing_keys:
                    merged.append(item)
                    existing_keys.add(item_key)

                if len(merged) >= max_contexts:
                    return merged

        return merged

    def _search_contexts_for_section(
        self,
        file_name: str,
        section_config: Dict[str, Any],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        针对某个精读维度进行增强检索。

        做法：
        1. 使用多个 retrieval query 进行向量检索；
        2. 使用中英文关键词检索；
        3. 使用论文结构性页码补充；
        4. 按 file_name 限定在指定论文内；
        5. 按页码和 chunk_index 去重；
        6. 对关键维度设置最小上下文数量，避免 top_k 过少导致依据不足。
        """
        effective_top_k = max(top_k, section_config.get("min_contexts", top_k))
        search_top_k = max(effective_top_k * 2, 8)

        all_chunks = self._get_all_chunks_by_file(file_name)

        retrieval_queries = section_config.get("retrieval_queries") or [
            section_config["question"]
        ]

        vector_results_map = {}

        for retrieval_query in retrieval_queries:
            results = self.vector_service.search(
                query=retrieval_query,
                top_k=search_top_k,
                where={"file_name": file_name},
            )

            for item in results:
                metadata = item.get("metadata", {})
                result_key = (
                    metadata.get("file_name"),
                    metadata.get("page_number"),
                    metadata.get("chunk_index"),
                )

                old_item = vector_results_map.get(result_key)

                if old_item is None:
                    item["retrieval_type"] = "vector"
                    vector_results_map[result_key] = item
                else:
                    old_distance = old_item.get("distance")
                    new_distance = item.get("distance")

                    if old_distance is None:
                        item["retrieval_type"] = "vector"
                        vector_results_map[result_key] = item
                    elif new_distance is not None and new_distance < old_distance:
                        item["retrieval_type"] = "vector"
                        vector_results_map[result_key] = item

        vector_results = sorted(
            vector_results_map.values(),
            key=lambda item: item.get("distance", 999),
        )[:search_top_k]

        keyword_results = self._keyword_search_contexts(
            file_name=file_name,
            section_config=section_config,
            top_k=search_top_k,
            all_chunks=all_chunks,
        )

        structural_results = self._structure_search_contexts(
            file_name=file_name,
            section_config=section_config,
            top_k=search_top_k,
            all_chunks=all_chunks,
        )

        result_group_map = {
            "vector": vector_results,
            "keyword": keyword_results,
            "structural": structural_results,
        }

        retrieval_order = section_config.get(
            "retrieval_order",
            ["vector", "keyword", "structural"],
        )

        ordered_groups = [
            result_group_map[group_name]
            for group_name in retrieval_order
            if group_name in result_group_map
        ]

        return self._merge_context_groups(
            context_groups=ordered_groups,
            max_contexts=effective_top_k,
        )

    @staticmethod
    def _build_enhanced_question(section_key: str, question: str) -> str:
        """
        构造更适合论文精读的增强问题。

        对用户展示仍保留原始 question；
        实际发送给 LLM 的问题会补充结构定位提示，降低模型过早拒答的概率。
        """
        suffix = SECTION_PROMPT_SUFFIXES.get(section_key, "")

        if not suffix:
            return question

        return (
            f"{question}\n\n"
            f"补充要求：{suffix}\n"
            f"回答必须依据提供的资料片段；如果资料不足，请明确说明不足之处。"
        )

    def read_single_paper(
        self,
        file_name: str,
        sections: Optional[List[str]] = None,
        top_k: int = 6,
    ) -> Dict[str, Any]:
        """
        生成单篇论文精读结果。

        参数：
        - file_name: 要精读的论文文件名，必须与 metadata 中的 file_name 完全一致；
        - sections: 要生成的精读维度列表；如果为空，则默认生成全部维度；
        - top_k: 每个问题检索的 chunk 数量。

        返回：
        {
            "file_name": "...",
            "section_count": ...,
            "sections": [...]
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

            enhanced_question = self._build_enhanced_question(
                section_key=section_key,
                question=question,
            )

            rag_result = self.llm_service.answer_with_contexts(
                question=enhanced_question,
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
        top_k: int = 6,
    ) -> Dict[str, Any]:
        """
        生成轻量版论文精读卡片。

        默认包含：
        1. 研究背景；
        2. 研究问题；
        3. 主要结论。

        模块十八后，默认 top_k 从 4 提高到 6，
        并且内部会根据维度进行结构性补充。
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

    def read_full_card(
        self,
        file_name: str,
        top_k: int = 6,
    ) -> Dict[str, Any]:
        """
        生成完整版论文精读卡片。

        注意：
        - 默认包含全部 9 个维度；
        - 会产生 9 次 LLM API 调用；
        - 建议在真实 API 可用且余额充足时使用。
        """
        full_sections = [
            "research_background",
            "research_question",
            "theoretical_basis",
            "data_and_method",
            "variables",
            "main_findings",
            "innovation_points",
            "limitations",
            "research_inspiration",
        ]

        return self.read_single_paper(
            file_name=file_name,
            sections=full_sections,
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
                distance = source.get("distance")
                retrieval_text = distance if distance is not None else (
                    source.get("retrieval_type") or "keyword"
                )

                lines.append(
                    f"{source_index}. {source.get('file_name')} | "
                    f"第 {source.get('page_number')} 页 | "
                    f"chunk_index={source.get('chunk_index')} | "
                    f"retrieval={retrieval_text}"
                )

        lines.append("\n【不确定之处】")
        lines.append(section.get("uncertainty", ""))

    return "\n".join(lines)