# RAG Chatbot

Полнофункциональный Retrieval-Augmented Generation стек: FastAPI‑бэкенд с Celery‑воркером и Qdrant, фронтенд на React/Vite и docker-compose окружение с Ollama, Redis и стеком наблюдаемости (Prometheus + Grafana + Loki). Репозиторий можно использовать как готовую стартовую площадку для внутренних ассистентов и чат‑ботов поверх корпоративной базы знаний.

## Возможности

- **Загрузка документов.** REST‑эндпоинт `/ingest` принимает текстовые файлы, разбивает их Markdown‑осведомлённым алгоритмом, сохраняет исходные чанки на диск и индексирует эмбеддинги в Qdrant.
- **Диалог с цитированием.** Эндпоинт `/chat` выполняет гибридный ретривел, rerank, добавляет контексты в промпт и возвращает ссылки на первоисточники.
- **Гибкая деградация.** Все тяжёлые зависимости инициализируются лениво: сервис стартует даже без скачанных моделей, а ошибки в reranker'е не ломают чат.
- **Наблюдаемость.** API и Celery‑воркер экспортируют метрики Prometheus, docker-compose поднимает Grafana и Loki для дашбордов и логов.
- **UI для пользователей.** Простое Vite‑приложение с вкладками «Chat/Upload», историей диалогов в localStorage и прогресс‑баром загрузок.

## Структура репозитория

```
.
├── backend/              # FastAPI, Celery, сервисы индексирования
│   ├── server/api        # Роутеры /chat, /ingest, /health
│   ├── server/services   # Embeddings, retriever, vector store, LLM, промпты
│   ├── server/tasks      # Celery worker + метрики Prometheus
│   └── tests             # Pytest-ы (интеграция и E2E)
├── frontend/             # React/Vite интерфейс с Tailwind
├── compose/              # Конфигурация Prometheus/Grafana/Loki
├── docker-compose.yml    # Полное окружение (API, worker, frontend, Qdrant…)
├── Makefile              # Шорткаты для docker compose
├── sample.md             # Пример входного документа
└── README.md
```

## Требования

- Docker 24+ и docker compose plugin
- Make 4.x (необязательно, но упрощает запуск)
- Node.js 20 (для локальной разработки фронтенда вне Docker)
- Python 3.11 (для локальных запусков/тестов backend без контейнеров)

## Быстрый старт (docker-compose)

1. Скопируйте переменные окружения:
   ```bash
   cp .env.example .env  # создайте файл, если его нет
   ```
   Если `.env.example` отсутствует, создайте `.env` вручную (см. [Конфигурация](#конфигурация)).
2. Поднимите базовые сервисы и скачайте модель Ollama:
   ```bash
   make base              # qdrant + redis + ollama
   make pull-model        # скачает qwen2.5:3b в Ollama
   ```
3. Запустите остальное окружение (API, worker, frontend, мониторинг):
   ```bash
   make up
   ```
4. Откройте UI: <http://localhost:5173>. API доступно на <http://localhost:8010>, Prometheus — <http://localhost:9090>, Grafana — <http://localhost:3000>, Loki — <http://localhost:3100>.
5. Остановить окружение: `make down`.

> Команды `make up` и `make down` проксируют `docker compose up/down`. Можно запускать `docker compose up --build` напрямую, если make недоступен.

## Локальная разработка без Docker

### Backend (FastAPI + Celery)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn server.main:app --reload --port 8000
```

Параллельно запустите Celery‑воркер:

```bash
celery -A server.tasks.worker.app worker -l info
```

> Вам понадобятся запущенные экземпляры Redis и Qdrant. Можно использовать контейнеры из `docker-compose` (`docker compose up qdrant redis`) либо управляемые сервисы.

### Frontend (React/Vite)

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Настройки API‑базы берутся из `frontend/.env` или `VITE_API_BASE_URL` (по умолчанию `http://localhost:8010`).

## Конфигурация

Backend читает переменные окружения через `backend/server/core/config.py`. Основные параметры:

| Переменная | Назначение | Значение по умолчанию |
|------------|------------|------------------------|
| `ENV` | режим (`dev`/`prod`) | `dev` |
| `API_HOST`, `API_PORT` | адрес FastAPI | `0.0.0.0`, `8000` |
| `CORS_ORIGINS` | разрешённые Origin-ы (через запятую) | `http://localhost:5173` |
| `MAX_UPLOAD_MB` | лимит размера файла (MB) | `25` |
| `JWT_SECRET`, `JWT_EXPIRES_MIN` | заготовка под JWT-аутентификацию | `change_me`, `60` |
| `LLM_PROVIDER`, `LLM_MODEL` | источник и модель генерации (Ollama/OpenAI/HF) | `ollama`, `qwen2.5:3b` |
| `OLLAMA_HOST` | адрес Ollama API | `http://ollama:11434` |
| `OPENAI_API_KEY`, `HF_API_TOKEN` | ключи для альтернативных LLM | пусто |
| `EMBED_PROVIDER`, `EMBED_MODEL`, `EMBED_DIM` | настройки эмбеддингов | `sbert`, `sentence-transformers/all-MiniLM-L6-v2`, `384` |
| `VECTOR_BACKEND`, `QDRANT_URL`, `QDRANT_COLLECTION` | векторное хранилище | `qdrant`, `http://qdrant:6333`, `kb` |
| `DB_URL` | URL базы SQLAlchemy (doc metadata) | `sqlite+aiosqlite:///./data/app.db` |
| `DOCSTORE_PATH` | файловое хранилище чанков | `./data/chunks` |
| `REDIS_URL` | брокер для Celery | `redis://redis:6379/0` |
| `PROMETHEUS_ENABLED`, `API_METRICS_PATH`, `WORKER_METRICS_PORT` | метрики API/worker | `True`, `/metrics`, `8001` |

Создайте `.env` на корне проекта и переопределите нужные значения.

## API

| Метод | Путь | Описание |
|-------|------|----------|
| `GET /health` | Проверка состояния сервиса (используется тестами и Prometheus). |
| `POST /ingest` | Multipart‑загрузка файла (`file`). Возвращает `document_id`, `document_hash`, количество чанков. |
| `POST /chat` | Тело `{ "question": string }`. Возвращает `answer` и массив `references` (id документа, имя файла, превью, счёт). |
| `GET /metrics` | Метрики Prometheus FastAPI‑процесса (если включено). |
| `GET /admin/reindex` | Заглушка (в планах полный административный API). |

Документация Swagger/OpenAPI доступна по адресу <http://localhost:8010/docs>.

## Поток индексации и поиска

1. Пользователь загружает файл через UI или `POST /ingest`.
2. `split_with_metadata` режет текст на чанки (Markdown‑осведомлённые, 800 символов, overlap 120) и обогащает их метаданными.
3. Docstore (`backend/data/chunks`) сохраняет исходный текст, чтобы чат мог вытаскивать превью.
4. `Indexer` получает эмбеддинги (SentenceTransformers) и апсертит данные в Qdrant.
5. Во время запроса `/chat` `HybridRetriever` выполняет символьный и векторный поиск, reranker (CrossEncoder) сортирует результаты, и в промпт передаётся максимум 6 контекстов.
6. `get_llm()` по умолчанию вызывает Ollama (Qwen2.5 3B) и возвращает ответ вместе с ссылками на источники.

## Мониторинг и логи

- **Prometheus** собирает `/metrics` из API и HTTP‑сервер воркера (`WORKER_METRICS_PORT`).
- **Grafana** преднастроена на чтение данных Prometheus и Loki (дашборды в `compose/grafana`).
- **Loki** собирает stdout/stderr контейнеров docker-compose, можно подключить к Grafana Explore.

## Тесты

Backend покрыт pytest‑ами для ingestion, поиска и E2E‑цепочки «загрузить файл → получить ответ с ссылками». Запуск:

```bash
cd backend
pytest
```

## Полезные советы

- Для экспериментов используйте `sample.md` / `test.md` — это готовые документы для индексации.
- Логи Celery и API легко посмотреть через `make logs`.
- Если нужно сменить модель Ollama, обновите `LLM_MODEL` в `.env` и выполните `curl -X POST http://localhost:11434/api/pull -d '{"name":"<model>"}'`.
- Значение `MAX_UPLOAD_MB` пока не принудительно проверяется на сервере, но UI подсказывает пользователям про оптимальные размеры файлов.

