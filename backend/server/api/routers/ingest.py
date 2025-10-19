from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from ...services.embeddings import get_embeddings
from ...services.vectorstore import get_vectorstore
from ...services.indexing import Indexer
from ...services.chunking import split_with_metadata
from ...db import get_docstore

router = APIRouter()

class IngestResponse(BaseModel):
    ok: bool
    document_id: int
    filename: str
    chunks: int

@router.post("", response_model=IngestResponse, tags=["ingest"])
async def ingest_file(file: UploadFile = File(...)):
    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(400, "Empty file")

    try:
        text = content_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        raise HTTPException(400, f"Decode error: {e}")

    # Примитивный стабильный id (в проде — из БД)
    document_id = abs(hash((file.filename, len(text)))) % (10**9)

    rich_chunks = split_with_metadata(
        text=text,
        filename=file.filename,
        document_id=document_id,
        chunk_size=800,
        overlap=120,
        strip_html=True,
        markdown_aware=True
    )
    if not rich_chunks:
        raise HTTPException(400, "No chunks produced")

    chunks: List[str] = []
    metas: List[Dict] = []
    items_for_store: List[tuple[str, Dict]] = []

    for idx, rc in enumerate(rich_chunks):
        cid = f"{document_id}:{idx}"
        meta = {
            "chunk_id": cid,
            "chunk_index": idx,
            "filename": file.filename,
            "document_id": document_id,
            "heading": rc.get("heading", ""),
            "level": rc.get("level", "0"),
            "span": rc.get("span", [0, 0])
        }
        metas.append(meta)
        chunks.append(rc["text"])
        items_for_store.append((cid, {"meta": meta, "text": rc["text"]}))

    # Persist сырые тексты
    get_docstore().bulk_put(items_for_store)

    # Апсерт в векторку
    indexer = Indexer(get_embeddings(), get_vectorstore())
    n = indexer.upsert_chunks(chunks, metas)

    return IngestResponse(ok=True, document_id=document_id, filename=file.filename, chunks=n)
