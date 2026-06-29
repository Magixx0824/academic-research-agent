import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv


load_dotenv()


class LLMService:
    """
    RAG 问答生成服务。

    当前支持两种模式：
    1. mock：不调用真实大模型，只根据检索结果生成一个可测试回答；
    2. api：调用 OpenAI-compatible API，后续接入真实模型时使用。
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.provider = provider or os.getenv("LLM_PROVIDER", "mock")
        self.model = model or os.getenv("LLM_MODEL", "mock-model")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "")

    def build_rag_prompt(
        self,
        question: str,
        contexts: List[Dict[str, Any]],
    ) -> str:
        """
        构造 RAG prompt。

        输入：
        - question: 用户问题
        - contexts: vector_service.search() 返回的检索结果

        输出：
        - prompt 字符串
        """
        if not question or not question.strip():
            raise ValueError("question 不能为空")

        if not contexts:
            context_text = "未检索到相关资料。"
        else:
            context_blocks = []

            for item in contexts:
                metadata = item.get("metadata", {})
                file_name = metadata.get("file_name", "未知文件")
                page_number = metadata.get("page_number", "未知页码")
                chunk_index = metadata.get("chunk_index", "未知chunk")
                content = item.get("content", "")

                context_blocks.append(
                    f"【来源】{file_name} | 第 {page_number} 页 | chunk_index={chunk_index}\n"
                    f"【内容】{content}"
                )

            context_text = "\n\n".join(context_blocks)

        prompt = f"""
你是一个严谨的学术论文阅读助手。请只依据【参考资料】回答【用户问题】。

要求：
1. 不要编造参考资料中没有的信息。
2. 如果参考资料不能支持明确回答，请回答“现有资料中未找到明确依据”。
3. 回答时要保持学术表达，避免口语化。
4. 只输出“回答正文”，不要单独输出“依据来源”和“不确定之处”。
5. 不要编造文献、页码、作者或数据来源。
6. 如果回答中涉及多个观点，请分点说明。
7. 如果参考资料之间存在概念不一致，请明确指出。

【参考资料】
{context_text}

【用户问题】
{question}
""".strip()

        return prompt

    def answer_with_contexts(
        self,
        question: str,
        contexts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        基于检索结果生成 RAG 回答。

        返回：
        {
            "question": "...",
            "answer": "...",
            "sources": [...],
            "uncertainty": "...",
            "prompt": "..."
        }
        """
        prompt = self.build_rag_prompt(question=question, contexts=contexts)
        sources = self._build_sources(contexts)

        if self.provider.lower() == "mock":
            answer = self._mock_answer(question=question, contexts=contexts)
        else:
            answer = self._api_answer(prompt=prompt)

        uncertainty = self._build_uncertainty(contexts)

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "uncertainty": uncertainty,
            "prompt": prompt,
        }

    def _mock_answer(
        self,
        question: str,
        contexts: List[Dict[str, Any]],
    ) -> str:
        """
        本地 mock 回答。

        目的：
        - 在没有真实 API Key 的情况下验证 RAG 流程；
        - 检查检索结果、来源返回、prompt 构造是否正常。
        """
        if not contexts:
            return "现有资料中未找到明确依据。"

        top_context = contexts[0]
        top_content = top_context.get("content", "").replace("\n", " ")
        top_content = top_content[:350]

        return (
            "根据当前检索到的资料，可以形成一个初步回答："
            f"{top_content}……"
            "需要注意，该回答由 mock 模式生成，仅用于验证 RAG 流程是否跑通；"
            "正式版本应接入真实大模型 API 后再生成更完整的学术化回答。"
        )

    def _api_answer(self, prompt: str) -> str:
        """
        调用 OpenAI-compatible API。

        后续如果使用 DeepSeek、通义千问、智谱等兼容 OpenAI SDK 的服务，
        可以复用这个函数。
        """
        if not self.api_key:
            raise ValueError(
                "当前 LLM_PROVIDER 不是 mock，但未配置 LLM_API_KEY。"
                "请在 .env 中配置 API Key，或将 LLM_PROVIDER 设置为 mock。"
            )

        try:
            from openai import OpenAI
        except ImportError as error:
            raise ImportError(
                "未安装 openai 包。请先执行：pip install openai"
            ) from error

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url if self.base_url else None,
        )

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个严谨的学术论文阅读助手。",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.2,
            )

            answer = response.choices[0].message.content
            return answer.strip() if answer else "模型未返回有效内容。"

        except Exception as error:
            error_text = str(error)

            if "Insufficient Balance" in error_text or "402" in error_text:
                return (
                    "真实大模型 API 调用失败：当前模型服务账户余额不足。"
                    "请检查 API 账户余额，或将 LLM_PROVIDER 设置为 mock 后继续本地流程测试。"
                )

            if (
                "401" in error_text
                or "Unauthorized" in error_text
                or "authentication" in error_text.lower()
                or "api key" in error_text.lower()
            ):
                return (
                    "真实大模型 API 调用失败：API Key 无效或未授权。"
                    "请检查 .env 中的 LLM_API_KEY 是否正确。"
                )

            if "404" in error_text or "model" in error_text.lower():
                return (
                    "真实大模型 API 调用失败：模型名称或接口地址可能不正确。"
                    "请检查 LLM_MODEL 和 LLM_BASE_URL。"
                )

            if (
                "timeout" in error_text.lower()
                or "connection" in error_text.lower()
                or "connect" in error_text.lower()
                or "network" in error_text.lower()
            ):
                return (
                    "真实大模型 API 调用失败：网络连接或请求超时。"
                    "请检查网络环境、代理设置或稍后重试。"
                )

            return f"真实大模型 API 调用失败，错误信息：{error_text}"

    def _build_sources(self, contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        从检索结果中整理来源信息。
        """
        sources = []

        for item in contexts:
            metadata = item.get("metadata", {})

            sources.append(
                {
                    "file_name": metadata.get("file_name"),
                    "page_number": metadata.get("page_number"),
                    "chunk_index": metadata.get("chunk_index"),
                    "distance": item.get("distance"),
                }
            )

        return sources

    def _build_uncertainty(self, contexts: List[Dict[str, Any]]) -> str:
        """
        生成不确定性说明。
        """
        if not contexts:
            return "未检索到相关资料，因此无法形成有依据的回答。"

        return (
            "当前回答仅依据向量检索返回的片段生成。"
            "如果检索片段未覆盖论文的完整研究设计、变量定义或实证结果，"
            "回答可能存在遗漏，需要结合更多上下文进一步核验。"
        )


def format_rag_answer(rag_result: Dict[str, Any]) -> str:
    """
    将 RAG 回答结果格式化为终端可读文本。
    """
    lines = []

    lines.append("【问题】")
    lines.append(rag_result.get("question", ""))

    lines.append("\n【回答】")
    lines.append(rag_result.get("answer", ""))

    lines.append("\n【依据来源】")
    sources = rag_result.get("sources", [])

    if not sources:
        lines.append("未返回来源。")
    else:
        for index, source in enumerate(sources, start=1):
            lines.append(
                f"{index}. {source.get('file_name')} | "
                f"第 {source.get('page_number')} 页 | "
                f"chunk_index={source.get('chunk_index')} | "
                f"distance={source.get('distance')}"
            )

    lines.append("\n【不确定之处】")
    lines.append(rag_result.get("uncertainty", ""))

    return "\n".join(lines)