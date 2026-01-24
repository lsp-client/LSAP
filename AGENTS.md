# AGENTS.md

## Development Commands

- Lint & format: `ruff check --fix && ruff format`
- Type checking: `ty check <dir_or_file>`
- Run tests: `uv run pytest`
- Python commands: always use `uv`

## Code Style Guidelines

- Python: 3.12+ required
- Imports & Formatting: use ruff
- Async: Use async/await, `asyncer.TaskGroup` for concurrency

## Implementation Guidelines

- Path Handling: `client.from_uri()` returns relative paths by default. Use `relative=False` explicitly when absolute paths are required (e.g., for path comparisons in exclusion sets).

## API Design

- **Skill**: MUST use `lsap-api-design` skill first before designing new APIs

## Testing

- Run `uv sync --upgrade` before testing and fixing type errors
