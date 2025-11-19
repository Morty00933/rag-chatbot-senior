# server/services/reranker.py
from __future__ import annotations
from typing import List, Optional, Sequence, Tuple
from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    """
    Обёртка над CrossEncoder для скoring'а пар (query, doc) и rerank'а.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        device: Optional[str] = None,
    ):
        # device=None -> auto
        self.model = CrossEncoder(model_name, device=device or "cpu")

    def score_pairs(self, queries: Sequence[str], docs: Sequence[str]) -> List[float]:
        """
        Оценить список пар (q_i, d_i). Длины должны совпадать.
        """
        assert len(queries) == len(docs), "queries and docs must have the same length"
        pairs: List[List[str]] = [[q, d] for q, d in zip(queries, docs)]
        scores = self.model.predict(pairs)  # numpy.ndarray
        return scores.tolist() if hasattr(scores, "tolist") else list(scores)

    def score(self, query: str, docs: Sequence[str]) -> List[float]:
        """
        Оценить один query против массива документов: (query, d_j) для всех j.
        """
        pairs: List[List[str]] = [[query, d] for d in docs]
        scores = self.model.predict(pairs)
        return scores.tolist() if hasattr(scores, "tolist") else list(scores)

    def rerank(self, query: str, docs: Sequence[str]) -> List[Tuple[int, float]]:
        """
        Вернуть индексы документов и их score по убыванию.
        """
        scores = self.score(query, docs)
        order = sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)
        return [(i, scores[i]) for i in order]
