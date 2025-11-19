from __future__ import annotations
import json
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple


class LocalDocStore:
    def __init__(self, base_dir: str):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _chunk_path(self, chunk_id: str) -> str:
        safe = chunk_id.replace("/", "_")
        return os.path.join(self.base_dir, f"{safe}.json")

    def put(self, chunk_id: str, record: Dict[str, Any]) -> None:
        path = self._chunk_path(chunk_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False)

    def get(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        path = self._chunk_path(chunk_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
            return data

    def bulk_put(self, items: Iterable[Tuple[str, Dict[str, Any]]]) -> None:
        for cid, rec in items:
            self.put(cid, rec)

    def list_by_document(self, document_id: int) -> List[str]:
        prefix = f"{document_id}:"
        return [
            fn[:-5]
            for fn in os.listdir(self.base_dir)
            if fn.endswith(".json") and fn.startswith(prefix)
        ]
