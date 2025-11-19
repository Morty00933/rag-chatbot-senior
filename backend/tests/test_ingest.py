import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def _client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    monkeypatch.setenv("DOCSTORE_PATH", str(tmp_path))

    from server.core import config as core_config

    core_config.get_settings.cache_clear()
    core_config.settings = core_config.get_settings()

    from server import db

    db.reset_docstore()

    from server.main import app

    return TestClient(app)


def _ingest(
    client: TestClient, filename: str, content: bytes, content_type: str = "text/plain"
):
    files = {"file": (filename, io.BytesIO(content), content_type)}
    response = client.post("/ingest", files=files)
    assert response.status_code == 200, response.text
    return response.json()


def test_document_identity_is_deterministic(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    client = _client(monkeypatch, tmp_path)

    payload_text = (
        "# Заголовок\n\n"
        "RAG система поддерживает гибридный поиск.\n"
        "Используется векторная база Qdrant и эмбеддинги SBERT.\n\n"
        "## Подраздел\n"
        "Ответы должны ссылаться на релевантные фрагменты.\n"
    )
    payload = payload_text.encode("utf-8")
    first = _ingest(client, "hello.md", payload, content_type="text/markdown")
    second = _ingest(client, "hello.md", payload, content_type="text/markdown")

    assert first["document_id"] == second["document_id"]
    assert first["document_hash"] == second["document_hash"]

    modified = _ingest(
        client,
        "hello.md",
        (payload_text + "\nНовые сведения о системе.").encode("utf-8"),
        content_type="text/markdown",
    )
    assert modified["document_hash"] != first["document_hash"]


def test_metadata_written_to_docstore(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    payload = (
        "# Руководство\n\n"
        "Документ описывает внутреннее устройство чат-бота с расширенным поиском."
        "\n\n### Функции\n- Индексация\n- Ответы со ссылками\n"
    ).encode("utf-8")
    response = _ingest(client, "knowledge.md", payload, content_type="text/markdown")

    from server import db

    store = db.get_docstore()
    chunk_ids = store.list_by_document(response["document_id"])
    assert chunk_ids, "chunks must be persisted to docstore"

    stored = store.get(chunk_ids[0])

    meta = stored["meta"]
    assert meta["document_sha256"] == response["document_hash"]
    assert meta["chunk_total"] == response["chunks"]
    assert meta["document_size"] == len(payload)
    assert meta["content_type"] == "text/markdown"
