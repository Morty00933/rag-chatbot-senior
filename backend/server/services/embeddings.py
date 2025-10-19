from __future__ import annotations
from .interfaces import Embeddings
from ..core.config import settings
from sentence_transformers import SentenceTransformer
from typing import List

_model_cache: SentenceTransformer | None = None

class SbertEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        global _model_cache
        if _model_cache and _model_cache._model_card == model_name:  # type: ignore[attr-defined]
            self.model = _model_cache
        else:
            self.model = SentenceTransformer(model_name)
            # hacky mark to avoid reloads
            setattr(self.model, "_model_card", model_name)
            _model_cache = self.model

    def embed(self, texts: List[str]) -> List[List[float]]:
        vecs = self.model.encode(texts, normalize_embeddings=True).tolist()
        return vecs


def get_embeddings() -> Embeddings:
    provider = settings.EMBED_PROVIDER
    if provider == "sbert":
        return SbertEmbeddings(settings.EMBED_MODEL)
    raise NotImplementedError(f"Unsupported EMBED_PROVIDER={provider}")