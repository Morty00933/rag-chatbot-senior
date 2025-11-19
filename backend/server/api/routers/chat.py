from __future__ import annotations
from typing import List, Tuple, Dict, Any
import os
from fastapi import APIRouter, HTTPException

from ...services.embeddings import get_embeddings
from ...services.vectorstore import get_vectorstore
from ...services.retriever import HybridRetriever
from ...services.llm import get_llm
from ...schemas.chat import ChatRequest, ChatResponse, Reference
from ...services.prompting import get_system_instruction, build_user_prompt
from ...db import get_docstore

# ВАЖНО: импортируем внутри функции, чтобы не падать при старте,
# если у контейнера нет сети для скачивания модели
# (ленивая инициализация в _get_reranker()).
_reranker = None

router = APIRouter()

TOP_POOL = 24
FIRST_K = 12
FINAL_K = 6
MAX_CTX_LEN = 4000


def _get_reranker():
    """Ленивая инициализация CrossEncoderReranker, чтобы старт сервиса не падал без сети."""
    global _reranker
    if _reranker is None:
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return None
        try:
            from ...services.reranker import CrossEncoderReranker

            _reranker = CrossEncoderReranker(
                model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
            )
        except Exception as e:
            # Не выбрасываем — просто оставляем _reranker = None, чтобы был graceful degrade
            _reranker = None
    return _reranker


def _normalize_candidate(c: Any) -> Tuple[str, Dict[str, Any], float]:
    """
    Приводит кандидат к виду (chunk_id, payload, score).
    Поддерживает:
      - tuple: (chunk_id, payload, score)
      - dict: {"id":..., "payload":..., "score":...} или {"chunk_id":...}
    """
    if isinstance(c, (list, tuple)) and len(c) >= 3:
        chunk_id, payload, score = c[0], c[1], c[2]
        return str(chunk_id), (payload or {}), float(score or 0.0)

    if isinstance(c, dict):
        cid = (
            c.get("id")
            or c.get("chunk_id")
            or c.get("point_id")
            or c.get("uuid")
            or "unknown"
        )
        payload = c.get("payload") or {}
        score = c.get("score") or 0.0
        return str(cid), payload, float(score)

    # на крайний случай
    return "unknown", {}, 0.0


def _collect_contexts_and_refs(
    candidates: List[Any], max_ctx: int = 6
) -> Tuple[List[str], List[Reference]]:
    """
    По id чанков достаём тексты из docstore и формируем ссылки.
    """
    docstore = get_docstore()
    contexts: List[str] = []
    refs: List[Reference] = []

    for c in candidates[:max_ctx]:
        chunk_id, payload, score = _normalize_candidate(c)

        # сначала пробуем взять текст прямо из payload (если retriever его кладёт)
        text = (payload or {}).get("text")
        meta: Dict[str, Any] = (payload or {}).get("meta") or {}

        # если нет текста в payload — берём из docstore
        if not text:
            rec = docstore.get(chunk_id) if chunk_id and chunk_id != "unknown" else None
            if rec and isinstance(rec, dict):
                text = rec.get("text")
                meta = rec.get("meta") or meta

        if not text:
            continue  # пропускаем пустые

        filename = (meta or {}).get("filename", "unknown")
        doc_id = (meta or {}).get("document_id", "unknown")
        chunk_ord = int((meta or {}).get("chunk_ord", 0))

        safe_text = text[:MAX_CTX_LEN]
        contexts.append(safe_text)
        refs.append(
            Reference(
                document_id=str(doc_id),
                filename=str(filename),
                score=float(score),
                chunk_ord=chunk_ord,
                preview=safe_text[:200],
            )
        )

    return contexts, refs


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(req: ChatRequest) -> ChatResponse:
    q = (req.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="question is empty")

    # 1) гибридный ретрив
    retriever = HybridRetriever(get_embeddings(), get_vectorstore(), top_pool=TOP_POOL)
    try:
        first_hits = retriever.search(q, top_k=FIRST_K)
    except Exception:
        first_hits = []

    # 2) поднимаем тексты и ссылки
    contexts_raw, refs_raw = _collect_contexts_and_refs(
        first_hits, max_ctx=len(first_hits) or FIRST_K
    )

    # Если контекстов нет — честный ответ
    if not contexts_raw:
        sys_instr = get_system_instruction()
        prompt = build_user_prompt(q, [], sys_instr)
        try:
            answer = await get_llm().generate(prompt)
        except Exception:
            answer = ""
        answer = (answer or "").strip() or "я не знаю"
        return ChatResponse(answer=answer, references=[])

    # 3) попытка rerank; если не получилось — используем как есть
    order = list(range(len(contexts_raw)))
    rr = _get_reranker()
    if rr is not None:
        try:
            scores = rr.score(q, contexts_raw)  # List[float]
            order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        except Exception:
            pass  # graceful degrade

    k = min(FINAL_K, len(order))
    contexts = [contexts_raw[i] for i in order[:k]]
    refs = [refs_raw[i] for i in order[:k]]

    # 4) системная инструкция
    sys_instr = get_system_instruction()

    # 5) генерация ответа
    prompt = build_user_prompt(q, contexts, sys_instr)
    try:
        answer = await get_llm().generate(prompt)
    except Exception:
        answer = ""
    answer = (answer or "").strip() or "я не знаю"

    return ChatResponse(answer=answer, references=refs)
