from rank_bm25 import BM25Okapi
from typing import List, Tuple
import re

_token = re.compile(r"\w+", re.UNICODE)

class BM25:
    def __init__(self, corpus: List[str]):
        self.docs = [ [t.lower() for t in _token.findall(d)] for d in corpus ]
        self.model = BM25Okapi(self.docs)

    def search(self, query: str, top_k: int) -> List[Tuple[int, float]]:
        q = [t.lower() for t in _token.findall(query)]
        scores = self.model.get_scores(q)
        pairs = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [(i, float(s)) for i, s in pairs]