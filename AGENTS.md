# AGENTS.md

## Development Commands

- Lint & format: `ruff check --fix && ruff format`
- Type checking: `ty check <dir_or_file>`
- Run tests: `uv run pytest`
- Use `uv` for Python related commands.

## Code Style Guidelines

- Python: 3.12+ required

## Schema Design

- LLM-Agent centric design: Can agent build/understand the schema effectively?
- Simplify Templates: Move complex logic from templates into data models.
- Avoid advanced Pydantic features (e.g., `@computed_field`) to ensure clean and compatible JSON schema exports.

## Template Design

- Always read [cheetsheet](docs/liquid_cheatsheet.md) before writing Liquid templates.
- Validate templates after writing.
