.PHONY: dev test lint seed docker-up docker-down migrate

dev:
	PYTHONPATH=src python app.py

test:
	PYTHONPATH=src pytest -q

lint:
	ruff check .

seed:
	@echo "Seed step not implemented yet."

migrate:
	PYTHONPATH=src alembic upgrade head

docker-up:
	docker compose up --build

docker-down:
	docker compose down
