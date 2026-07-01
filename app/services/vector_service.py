from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb


class VectorService:
    """
    Chroma 向量库服务。

    负责：
    1. 创建或连接本地 Chroma 向量数据库；
    2. 将 chunk 写入向量库；
    3. 根据用户问题检索相关 chunk；
    4. 返回 content、metadata 和 distance。
    """

    def __init__(
        self,
        persist_dir: str = "storage/chroma",
        collection_name: str = "academic_chunks",
        reset_collection: bool = False,
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name

        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.persist_dir)

        if reset_collection:
            self._delete_collection_if_exists(collection_name)

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _delete_collection_if_exists(self, collection_name: str) -> None:
        """
        如果 collection 已存在，则删除。

        主要用于测试阶段，避免重复写入旧数据。
        """
        existing_collections = self.client.list_collections()
        existing_names = [collection.name for collection in existing_collections]

        if collection_name in existing_names:
            self.client.delete_collection(name=collection_name)

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100,
    ) -> int:
        """
        将 chunks 写入 Chroma。

        输入 chunk 结构来自 rag_tools.split_documents()：
        {
            "chunk_id": "...",
            "content": "...",
            "metadata": {...}
        }

        使用 upsert，而不是 add：
        - add 遇到重复 id 会报错；
        - upsert 遇到重复 id 会更新，适合开发测试阶段反复运行。
        """
        if not chunks:
            return 0

        valid_chunks = []

        for chunk in chunks:
            chunk_id = chunk.get("chunk_id")
            content = chunk.get("content")
            metadata = chunk.get("metadata", {})

            if not chunk_id or not content:
                continue

            # Chroma metadata 只支持 str、int、float、bool 等基础类型。
            clean_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    clean_metadata[key] = value
                else:
                    clean_metadata[key] = str(value)

            valid_chunks.append(
                {
                    "id": str(chunk_id),
                    "document": str(content),
                    "metadata": clean_metadata,
                }
            )

        if not valid_chunks:
            return 0

        for start in range(0, len(valid_chunks), batch_size):
            batch = valid_chunks[start : start + batch_size]

            ids = [item["id"] for item in batch]
            documents = [item["document"] for item in batch]
            metadatas = [item["metadata"] for item in batch]

            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )

        return len(valid_chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        根据用户问题检索最相关的 chunks。

        参数：
        - query: 用户问题
        - top_k: 返回前几个最相关结果
        - where: metadata 过滤条件，例如 {"file_name": "demo_paper_cn.pdf"}

        返回：
        [
            {
                "rank": 1,
                "content": "...",
                "metadata": {...},
                "distance": 0.123
            }
        ]
        """
        if not query or not query.strip():
            raise ValueError("query 不能为空")

        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")

        result = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        return self._format_query_result(result)

    def get_chunks_by_file(self, file_name: str) -> List[Dict[str, Any]]:
        """
        根据 file_name 获取某篇论文的全部 chunks。

        该方法用于单篇论文精读中的关键词检索、页码过滤和结构化内容定位。
        """
        if not file_name or not file_name.strip():
            raise ValueError("file_name 不能为空")

        result = self.collection.get(
            where={"file_name": file_name},
            include=["documents", "metadatas"],
        )

        ids = result.get("ids", [])
        documents = result.get("documents", [])
        metadatas = result.get("metadatas", [])

        chunks = []

        for index, document in enumerate(documents):
            metadata = metadatas[index] if index < len(metadatas) else {}
            chunk_id = ids[index] if index < len(ids) else None

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "content": document,
                    "metadata": metadata,
                    "distance": None,
                }
            )

        chunks = sorted(
            chunks,
            key=lambda item: (
                item.get("metadata", {}).get("page_number") or 0,
                item.get("metadata", {}).get("chunk_index") or 0,
            ),
        )

        return chunks

    def _format_query_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        将 Chroma 原始 query 结果整理成更容易使用的结构。
        """
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        formatted_results = []

        for index, document in enumerate(documents):
            metadata = metadatas[index] if index < len(metadatas) else {}
            distance = distances[index] if index < len(distances) else None

            formatted_results.append(
                {
                    "rank": index + 1,
                    "content": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return formatted_results

    def count(self) -> int:
        """
        返回当前 collection 中的 chunk 数量。
        """
        return self.collection.count()

    def clear(self) -> None:
        """
        清空当前 collection。

        开发测试阶段可用。
        """
        self._delete_collection_if_exists(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )


def preview_search_result(result: Dict[str, Any], max_length: int = 180) -> str:
    """
    生成检索结果预览。
    """
    content = result.get("content", "").replace("\n", " ")
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."