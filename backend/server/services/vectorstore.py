from __future__ import annotations
from typing import List, Tuple, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from .interfaces import VectorStore
from ..core.config import settings

class QdrantVS(VectorStore):
    def __init__(self, url: str, collection: str, dim: int):
        self.client = QdrantClient(url=url)
        self.collection = collection
        self.dim = dim
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        names = {c.name for c in self.client.get_collections().collections}
        if self.collection not in names:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE),
            )

    def upsert(
        self,
        ids: List[str],
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
    ) -> None:
        points = [PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
        # wait=True, чтобы дождаться записи перед ответом API
        self.client.upsert(collection_name=self.collection, points=points, wait=True)

    def search(self, query: List[float], top_k: int) -> List[Tuple[dict, float]]:
        res = self.client.search(
            collection_name=self.collection,
            query_vector=query,
            limit=max(1, top_k),
            with_payload=True,
        )
        return [(p.payload or {}, float(p.score)) for p in res]

def get_vectorstore() -> VectorStore:
    if settings.VECTOR_BACKEND == "qdrant":
        return QdrantVS(settings.QDRANT_URL, settings.QDRANT_COLLECTION, settings.EMBED_DIM)
    raise NotImplementedError(f"Unsupported VECTOR_BACKEND={settings.VECTOR_BACKEND}")
