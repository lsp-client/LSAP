# AGENTS.md

## Development Commands

- Lint & format: `ruff check --fix && ruff format`
- Type checking: `ty check <dir_or_file>`
- Run tests: `uv run pytest`

## Code Style Guidelines

- Python: 3.12+ required
- Imports & Formatting: use ruff
- Async: Use async/await, `asyncer.TaskGroup` for concurrency

## Testing

- Run `uv sync --upgrade` before testing and fixing type errors
