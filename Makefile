.PHONY: dev build run restart logs

dev:
	docker stop twio-mcp || true
	uv run python -m twio_mcp.server

build:
	docker build -t twio-mcp .

run:
	docker run -d --name twio-mcp -p 8584:8584 --restart unless-stopped twio-mcp

restart: build
	docker rm -f twio-mcp || true
	$(MAKE) run

logs:
	docker logs -f twio-mcp
