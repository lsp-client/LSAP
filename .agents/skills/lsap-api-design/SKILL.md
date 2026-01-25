---
name: lsap-api-design
description: Guide for designing and implementing new LSAP APIs. Use when adding new capabilities to LSAP (definitions, references, rename, etc.) or when asking how to add new features to the LSAP protocol. Provides architectural patterns, implementation steps, and references to existing code examples.
---

# LSAP API Design

Guide for adding new APIs to LSAP. Study existing code as needed.

## Architecture

Three layers:

1. **Schema** (`src/lsap/schema/`): Request/Response models (Pydantic), Markdown templates
2. **Capability** (`src/lsap/capability/`): Business logic, LSP orchestration
3. **LSP** (lsp-client library): Raw protocol operations

**Key Principles:** Agent-cognitive design, Markdown-first output, semantic anchoring via `Locate`, composed capabilities

## Reference Implementations

Study these before implementing:

- **Simple**: `src/lsap/schema/definition.py` + `src/lsap/capability/definition.py`
- **Paginated**: `src/lsap/schema/reference.py` + `src/lsap/capability/reference.py`
- **Multi-mode**: `src/lsap/schema/rename.py` + `src/lsap/capability/rename.py`
- **Complex**: `src/lsap/schema/symbol.py` + `src/lsap/capability/symbol.py`

## Implementation Steps

### 1. Define Schema (`src/lsap/schema/<name>.py`)

See `src/lsap/schema/definition.py` for complete example.

Key components:

- **Request Model**: Inherit from `Request`, `LocateRequest`, or `PaginatedRequest`
- **Response Model**: Inherit from `Response` or `PaginatedResponse`
- **Markdown Template**: Liquid template in `model_config.json_schema_extra["markdown"]`

Template basics (see `docs/liquid_cheatsheet.md`):
- Conditionals: `{% if items.size == 0 %}...{% endif %}`
- Loops: `{% for item in items %}...{% endfor %}`
- Filters: `{{ mode | capitalize }}`, `{{ path | join: "." }}`

### 2. Implement Capability (`src/lsap/capability/<name>.py`)

See `src/lsap/capability/definition.py` for complete example.

Pattern:

```python
from attrs import define
from .abc import Capability

@define
class MyCapability(Capability[MyRequest, MyResponse]):
    async def __call__(self, req: MyRequest) -> MyResponse | None:
        # 1. Locate position (if needed)
        if not (loc_resp := await self.locate(req)):
            return None
        
        # 2. Call LSP operations via ensure_capability()
        # 3. Process results (use asyncer.create_task_group for parallelism)
        # 4. Return response (or None on failure)
```

**Important:** Return `None` on failure, not empty response.

### 3. Register Exports

Add to `src/lsap/capability/__init__.py` and `src/lsap/schema/__init__.py`

### 4. Add Tests

See `tests/test_definition.py` for examples. Must test: success case, not found case.

### 5. Add Documentation

Create `schema/<name>.md` with usage examples.

## Common Patterns

### Pagination

See `src/lsap/capability/reference.py` for complete pattern with `PaginationCache` and `paginate()`.

### Reading Code Context

```python
from lsap.utils.document import DocumentReader

content = await self.client.read_file(file_path)
reader = DocumentReader(content)
snippet = reader.read(context_range, trim_empty=True)
```

### Symbol Information

```python
from lsap.utils.symbol import symbol_at

symbols = await ensure_capability(
    self.client, WithRequestDocumentSymbol
).request_document_symbol_list(file_path)

if symbols and (match := symbol_at(symbols, position)):
    symbol_path, symbol = match
```

### LSP Capability Check

```python
from lsap.utils.capability import ensure_capability

result = await ensure_capability(
    self.client,
    WithRequestReferences,
    error="Fallback instructions if not supported"
).request_references(file_path, position)
```

## Common Utilities

See `src/lsap/utils/` for implementations.

**Path handling:**
- `client.from_uri(uri)` - Returns relative path by default
- `client.from_uri(uri, relative=False)` - Returns absolute path

**Position conversion:**
- `Position.from_lsp(lsp_pos)` - LSP (0-based) → LSAP (1-based)
- `lsap_pos.to_lsp()` - LSAP (1-based) → LSP (0-based)

**Hover content:**
- `clean_hover_content(hover.value)` - Removes LSP formatting artifacts

## Checklists

**Files to create:**
- `src/lsap/schema/<name>.py`
- `src/lsap/capability/<name>.py`
- `tests/test_<name>.py`
- `schema/<name>.md`

**Files to update:**
- `src/lsap/schema/__init__.py`
- `src/lsap/capability/__init__.py`

**Must verify:**
- Returns `None` on failure (not empty response)
- Uses `ensure_capability()` for LSP operations
- Concurrent operations use semaphores
- Tests cover success and failure cases

## Related Documentation

- `docs/locate_design.md` - Position resolution patterns
- `docs/liquid_cheatsheet.md` - Template syntax
- `CONTRIBUTING.md` - Development workflow
