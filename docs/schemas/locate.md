# Locate API

The Locate API provides a unified way to specify a position or range in the codebase. It is used as a base for many other requests like [`SymbolRequest`](symbol.md), [`ReferenceRequest`](reference.md), and [`CallHierarchyRequest`](call_hierarchy.md).

## LocateRequest

One of `LocateText` or `LocateSymbol`.

### LocateText

Finds a position based on a text search.

| Field       | Type                         | Default   | Description                                   |
| :---------- | :--------------------------- | :-------- | :-------------------------------------------- |
| `file_path` | `string`                     | Required  | Path to search in.                            |
| `line`      | `number \| [number, number]` | `null`    | Specific line number or range `[start, end]`. |
| `find`      | `string`                     | Required  | String snippet to find.                       |
| `find_end`  | `"start" \| "end"`           | `"end"`   | Match the start or end of the snippet.        |

### LocateSymbol

Finds a position based on a symbol path.

| Field         | Type       | Default  | Description                                   |
| :------------ | :--------- | :------- | :-------------------------------------------- |
| `file_path`   | `string`   | Required | Path to search in.                            |
| `symbol_path` | `string[]` | Required | Hierarchy list (e.g., `["Class", "Method"]`). |

## LocateResponse

| Field       | Type       | Description                                     |
| :---------- | :--------- | :---------------------------------------------- |
| `file_path` | `string`   | Resolved file path.                             |
| `position`  | `Position` | The coordinates (line, character) of the match. |

## Common Types

### Position

| Field       | Type     | Description                 |
| :---------- | :------- | :-------------------------- |
| `line`      | `number` | 0-indexed line number.      |
| `character` | `number` | 0-indexed character offset. |

### Range

| Field   | Type       | Description                 |
| :------ | :--------- | :-------------------------- |
| `start` | `Position` | Start position (inclusive). |
| `end`   | `Position` | End position (exclusive).   |

## Example Usage

### Request (LocateText)

```json
{
  "locate": {
    "file_path": "src/main.py",
    "line": [10, 50],
    "find": "def my_func",
    "find_end": "start"
  }
}
```

### Markdown Rendered for LLM

```markdown
Located `src/main.py` at 12:5
```
