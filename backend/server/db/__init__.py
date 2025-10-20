from __future__ import annotations
import os
from ..core.config import settings
from .docstore import LocalDocStore

__docstore_singleton: LocalDocStore | None = None


def get_docstore() -> LocalDocStore:
    global __docstore_singleton
    if __docstore_singleton is None:
        base = settings.DOCSTORE_PATH
        os.makedirs(base, exist_ok=True)
        __docstore_singleton = LocalDocStore(base)
    return __docstore_singleton


def reset_docstore() -> None:
    """Drop the cached docstore instance (useful in tests)."""

    global __docstore_singleton
    __docstore_singleton = None
