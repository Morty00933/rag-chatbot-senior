from __future__ import annotations
from typing import Any, Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Histogram,
    generate_latest,
)
import time

from .core.config import settings
from .api.routers import health, ingest, chat, admin

app = FastAPI(title="RAG API", version="0.1.0")


@app.get("/")
def root() -> dict[str, list[str] | str]:
    return {"status": "ok", "see": ["/docs", "/healthz", "/metrics"]}


# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
api_requests_total = Counter(
    "api_requests_total", "Total API requests", ["method", "route", "status"]
)
api_latency_hist = Histogram(
    "api_request_latency_seconds", "API request latency in seconds", ["route"]
)


@app.middleware("http")
async def metrics_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start = time.perf_counter()
    response: Response
    try:
        response = await call_next(request)
        return response
    finally:
        route = request.url.path
        status = str(response.status_code) if response else "500"
        api_requests_total.labels(request.method, route, status).inc()
        api_latency_hist.labels(route).observe(time.perf_counter() - start)


@app.get("/healthz", tags=["health"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get(settings.API_METRICS_PATH, tags=["metrics"])
async def metrics() -> PlainTextResponse | JSONResponse:
    if not settings.PROMETHEUS_ENABLED:
        return JSONResponse({"detail": "metrics disabled"}, status_code=404)
    data = generate_latest(REGISTRY)
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


# Подключаем роутеры
app.include_router(health.router, prefix="")
app.include_router(ingest.router, prefix="/ingest")
app.include_router(chat.router, prefix="")
app.include_router(admin.router, prefix="/admin")
