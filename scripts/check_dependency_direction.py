#!/usr/bin/env python3
"""Fail if domain modules import FastAPI/SQLAlchemy/HTTP clients/SDKs."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "backend" / "src"
FORBIDDEN_PREFIXES = (
    "fastapi",
    "sqlalchemy",
    "httpx",
    "redis",
    "openai",
    "twilio",
    "google",
    "alembic",
    "uvicorn",
)

DOMAIN_GLOBS = [
    "*/domain/*.py",
    "shared/domain/*.py",
]


def iter_domain_files() -> list[Path]:
    files: list[Path] = []
    for pattern in DOMAIN_GLOBS:
        files.extend(ROOT.glob(pattern))
    # Also catch nested domain packages
    files.extend(ROOT.glob("**/domain/**/*.py"))
    return sorted(set(files))


def imports_of(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def main() -> int:
    violations: list[str] = []
    for path in iter_domain_files():
        if path.name == "__init__.py" and path.stat().st_size == 0:
            continue
        for name in imports_of(path):
            root = name.split(".")[0]
            if root in FORBIDDEN_PREFIXES or name.startswith(FORBIDDEN_PREFIXES):
                violations.append(f"{path.relative_to(ROOT)} imports {name}")
    if violations:
        print("Dependency rule violations:")
        for v in violations:
            print(f"  - {v}")
        return 1
    print(f"OK: scanned {len(iter_domain_files())} domain modules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
