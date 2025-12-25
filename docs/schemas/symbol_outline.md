# Symbol Outline API

The Symbol Outline API returns a hierarchical tree of all symbols defined within a specific file. This allows an Agent to understand the structure of a file without reading the entire source code.

## SymbolOutlineRequest

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `file_path` | `string` | Required | Relative path to the file to inspect. |

## SymbolOutlineResponse

| Field | Type | Description |
| :--- | :--- | :--- |
| `file_path` | `string` | Relative path to the file. |
| `items` | `SymbolOutlineItem[]` | List of top-level symbols in the file. |

### SymbolOutlineItem

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | `string` | Name of the symbol. |
| `kind` | `string` | Type of the symbol (e.g., `Class`, `Function`, `Interface`). |
| `range` | `Range` | Range of the symbol in the file. |
| `children` | `SymbolOutlineItem[]` | Nested symbols (e.g., methods within a class). |

## Example Usage

### Request
```json
{
  "file_path": "src/models.py"
}
```

### Markdown Rendered for LLM
```markdown
### Symbol Outline for `src/models.py`

- **User** (`Class`)
  - **__init__** (`Method`)
  - **get_full_name** (`Method`)
- **APIClient** (`Class`)
  - **request** (`Method`)
```
