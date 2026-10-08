.PHONY: test lint typecheck backend-install frontend-install slice

backend-install:
	cd backend && pip install -e ".[dev]"

frontend-install:
	cd frontend && npm install

test:
	cd backend && pytest -q

lint:
	cd backend && ruff check src tests

typecheck:
	cd backend && mypy src

slice:
	cd backend && pytest -q tests/unit/application/test_vertical_slice.py tests/api/test_calls_api.py
