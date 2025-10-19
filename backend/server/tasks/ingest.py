from __future__ import annotations
from .celery_app import celery_app
from ..services.embeddings import get_embeddings
from ..services.vectorstore import get_vectorstore
from ..services.indexing import Indexer
from ..services.chunking import split_text

@celery_app.task(name="ingest.text")
def ingest_text(doc_id: int, filename: str, content: str):
    chunks = split_text(content)
    metas = [{"chunk_id": f"{doc_id}:{i}", "chunk_index": i, "filename": filename, "document_id": doc_id} for i in range(len(chunks))]
    indexer = Indexer(get_embeddings(), get_vectorstore())
    indexer.upsert_chunks(chunks, metas)
    return {"ok": True, "doc_id": doc_id, "chunks": len(chunks)}