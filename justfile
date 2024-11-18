# Execute all the recipes
all: fmt lint test

# Format the code
fmt:
  uv run ruff format .

# Lint the source code using Mypy & Ruff
lint:
  uv run ruff check && uv run mypy src

# Execute pytest, after running the linting
test args="":
  uv run pytest --cov=src --cov-fail-under=95 {{args}}

# Shows all recipes using just -l
help:
	just -l