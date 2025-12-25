# Locate API

The Locate API provides a unified way to specify a position or range in the codebase. It is used as a base for many other requests like `SymbolRequest`, `ReferenceRequest`, and `CallGraphRequest`.

## LocateRequest

One of `LocateText` or `LocateSymbol`.

### LocateText
Finds a position based on a text search.
- `file_path`: Path to search in.
- `line`: Specific line number or range `[start, end]`.
- `find`: String snippet to find.
- `position`: `"start"` or `"end"` of the snippet.

### LocateSymbol
Finds a position based on a symbol path.
- `file_path`: Path to search in.
- `symbol_path`: Hierarchy list (e.g., `["Class", "Method"]`).

## LocateResponse

| Field | Type | Description |
| :--- | :--- | :--- |
| `file_path` | `string` | Resolved file path. |
| `position` | `Position` | The coordinates (line, character) of the match. |

## Example Usage

### Request (LocateText)
```json
{
  "locate": {
    "file_path": "src/main.py",
    "line": [10, 50],
    "find": "def my_func",
    "position": "start"
  }
}
```

### Markdown Rendered for LLM
```markdown
Located `src/main.py` at 12:5
```
