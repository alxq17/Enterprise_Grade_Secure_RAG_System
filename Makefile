.PHONY: up down full-up full-down test eval ingest lint

up:
	docker compose -f docker/docker-compose.yml up -d qdrant

down:
	docker compose -f docker/docker-compose.yml down

full-up:
	docker compose --env-file .env -f docker/docker-compose.yml --profile full up -d --build

full-down:
	docker compose -f docker/docker-compose.yml --profile full down

ingest:
	python -m scripts.ingest --recreate

test:
	pytest tests/unit/ tests/integration/ -v

eval:
	python scripts/run_eval.py --mini

lint:
	ruff check src/ tests/