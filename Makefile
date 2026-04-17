.PHONY: dev build up down restart logs shell

dev:
	docker compose stop twio-mcp || true
	uv run python -m twio_mcp.server

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose up -d --build

logs:
	docker compose logs -f twio-mcp

shell:
	docker compose exec twio-mcp /bin/bash
