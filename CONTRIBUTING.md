# Contributing to LSAP

Thank you for your interest in contributing to LSAP! This project aims to empower Coding Agents with repository-scale intelligence through a structured orchestration layer over LSP.

## Project Structure

LSAP is a multi-language monorepo:

- **`src/lsap_schema/`**: Core protocol definitions and models (Python).
- **`python/`**: Python SDK and reference implementation.
- **`typescript/`**: TypeScript type definitions and Zod schemas.
- **`docs/`**: Protocol documentation and Liquid templates.
- **`web/`**: Documentation site.

## Development Setup

### Prerequisites

- **Python**: 3.12+ (managed via `uv`)
- **Node.js/TypeScript**: `bun` recommended
- **General**: `just` (command runner)

### Initial Setup

```bash
# Install Python dependencies
uv sync

# Install TypeScript dependencies
cd typescript && bun install
```

## Development Workflow

### Python & Schema

The source of truth for LSAP schemas is the Python implementation in `src/lsap_schema/`.

- **Linting & Formatting**: `uv run ruff check --fix && uv run ruff format`
- **Testing**: `uv run pytest`
- **Schema Codegen**: After modifying Python models, sync them to TypeScript:
  ```bash
  just codegen
  ```

### TypeScript

- **Build/Check**: `cd typescript && bun run index.ts` (or appropriate entry point)

## Design Guidelines

### Schema Design
- **Agent-Centric**: Design schemas that are easy for LLMs to generate and consume.
- **Clean Exports**: Avoid advanced Pydantic features (like `@computed_field`) that don't translate well to standard JSON Schema.
- **Simplicity**: Move complex logic from templates into the data models.

### Template Design
- **Liquid Templates**: We use Liquid for generating Markdown reports. Refer to [`docs/liquid_cheatsheet.md`](docs/liquid_cheatsheet.md).
- **Validation**: Always validate templates with sample data after modification.

## Pull Request Process

1.  **Propose Changes**: If you wish to contribute a new API design or significantly improve an existing one, please start by opening a **Discussion** on GitHub. Once the proposal gains sufficient consensus, it should be converted into an **Issue** for scheduling by the core management team.
2.  **Create a Branch**: Use descriptive names like `feat/add-new-capability` or `fix/issue-description`.
3.  **Verify Changes**:
    - Run tests: `uv run pytest`.
    - Run linting: `ruff check`.
    - If schema changed, run `just codegen`.
4.  **Submit PR**: Provide a clear summary of changes and reference the relevant Issue.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
