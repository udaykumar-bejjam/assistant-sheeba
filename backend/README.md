# Sheeba Backend

Python 3.12 FastAPI service implementing Sheeba’s hexagonal / DDD core.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
mypy src
uvicorn src.interfaces.api.main:app --reload
```
