.PHONY: typecheck lint lint-check format test

typecheck:
 uv run mypy src
lint:
 uv run ruff check src --fix
lint-check:
 uv run ruff check src
format:
 uv run ruff format src
test:
 uv run pytest