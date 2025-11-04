.PHONY: help install test format lint clean docker-up docker-down init-db run-etl run-api

help:
	@echo "Hyperliquid TWAP Data Service - Make Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install Python dependencies"
	@echo "  make docker-up    - Start Docker services"
	@echo "  make init-db      - Initialize database schema"
	@echo ""
	@echo "Development:"
	@echo "  make run-api      - Start API server"
	@echo "  make run-etl      - Run ETL on sample data"
	@echo "  make test         - Run tests"
	@echo "  make format       - Format code with black"
	@echo "  make lint         - Lint code with ruff"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    - Start all services"
	@echo "  make docker-down  - Stop all services"
	@echo "  make docker-logs  - View logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove generated files"

install:
	pip install -r requirements.txt

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

init-db:
	python -m src.db.init

run-api:
	uvicorn src.api.main:app --reload

run-etl:
	python tests/create_sample_data.py
	python -m src.etl.run --local-file tests/data/sample_twap.parquet

test:
	pytest -v

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term

format:
	black src/ tests/

lint:
	ruff check src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

.DEFAULT_GOAL := help
