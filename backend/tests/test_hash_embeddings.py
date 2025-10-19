import hashlib

from server.services.embeddings import HashEmbeddings


def _expected_vector(text: str, dim: int) -> list[float]:
    buckets = [0.0] * dim
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:8], "big") % dim
        buckets[idx] += 1.0
    norm = sum(v * v for v in buckets) ** 0.5 or 1.0
    return [v / norm for v in buckets]


def test_hash_embeddings_matches_sha256_distribution():
    dim = 16
    embedder = HashEmbeddings(dim)
    text = "Тестовые данные для хеша"

    expected = _expected_vector(text, dim)
    result = embedder.embed([text])[0]

    assert result == expected


def test_hash_embeddings_consistent_for_multiple_inputs():
    dim = 8
    embedder = HashEmbeddings(dim)

    vec1 = embedder.embed(["Раз два три"])[0]
    vec2 = embedder.embed(["раз два три"])[0]
    vec3 = embedder.embed(["раз  два   три"])[0]

    assert vec1 == vec2 == vec3
