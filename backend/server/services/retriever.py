from __future__ import annotations
from typing import Any, Dict, List, Tuple
from .interfaces import Embeddings, VectorStore


class HybridRetriever:
    """
    Пока используем dense-кандидаты из VectorStore, rerank делаем в chat.py,
    где есть доступ к текстам DocStore (так надёжнее).
    Возврат: (chunk_id, payload(meta), score)
    """

    def __init__(self, embed: Embeddings, vs: VectorStore, top_pool: int = 24):
        self.embed = embed
        self.vs = vs
        self.top_pool = top_pool

    def search(self, question: str, top_k: int = 6) -> List[Tuple[str, Dict[str, Any], float]]:
        top_k = max(1, min(20, top_k))
        qv = self.embed.embed([question])[0]
        vs_hits: List[Tuple[Dict[str, Any], float]] = self.vs.search(
            qv, self.top_pool
        )  # (payload, score)
        vs_hits_sorted = sorted(vs_hits, key=lambda x: float(x[1]), reverse=True)[:top_k]
        results: List[Tuple[str, Dict[str, Any], float]] = []
        for payload, score in vs_hits_sorted:
            cid = payload.get("chunk_id")
            if not cid:
                continue
            results.append((cid, payload, float(score)))
        return results
