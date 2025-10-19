```makefile
.PHONY: up base pull-model down logs ps restart

base:
	docker compose up -d qdrant redis ollama

pull-model:
	curl -X POST http://localhost:11434/api/pull -d '{"name":"qwen2.5:3b"}'

up: base
	docker compose up --build -d api worker frontend prometheus grafana loki

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

restart:
	docker compose restart
