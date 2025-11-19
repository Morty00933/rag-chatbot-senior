import io
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)


def test_ingest_then_chat():
    content = (
        "# Заголовок\n\n"
        "RAG система поддерживает гибридный поиск.\n"
        "Используется векторная база Qdrant и эмбеддинги SBERT.\n\n"
        "## Подраздел\n"
        "Ответы должны ссылаться на релевантные фрагменты.\n"
    ).encode("utf-8")

    files = {"file": ("kb.md", io.BytesIO(content), "text/markdown")}
    r = client.post("/ingest", files=files)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["ok"] is True
    assert data["chunks"] > 0

    q = {"question": "Какой векторный движок используется?", "top_k": 3}
    r2 = client.post("/chat", json=q)
    assert r2.status_code == 200, r2.text
    resp = r2.json()
    assert isinstance(resp["references"], list)
    assert len(resp["references"]) > 0
