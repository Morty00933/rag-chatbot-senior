from typing import List
from .base import Orm


class IngestResult(Orm):
    ok: bool
    count: int
    document_ids: List[int]
