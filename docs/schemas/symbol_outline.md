# Symbol Outline API

The Symbol Outline API returns a hierarchical tree of all symbols defined within a specific file. This allows an Agent to understand the structure of a file without reading the entire source code.

## SymbolOutlineRequest

| Field              | Type       | Default  | Description                                                                     |
| :----------------- | :--------- | :------- | :------------------------------------------------------------------------------ |
| `file_path`        | `string`   | Required | Relative path to the file to inspect.                                           |
| `display_code_for` | `string[]` | `[]`     | List of symbol names to include their full source code content in the response. |

## SymbolOutlineResponse

| Field       | Type                  | Description                            |
| :---------- | :-------------------- | :------------------------------------- |
| `file_path` | `string`              | Relative path to the file.             |
| `items`     | `SymbolOutlineItem[]` | List of top-level symbols in the file. |

### SymbolOutlineItem

| Field            | Type                  | Description                                                  |
| :--------------- | :-------------------- | :----------------------------------------------------------- |
| `name`           | `string`              | Name of the symbol.                                          |
| `kind`           | `string`              | Type of the symbol (e.g., `Class`, `Function`, `Interface`). |
| `range`          | `Range`               | Range of the symbol in the file.                             |
| `children`       | `SymbolOutlineItem[]` | Nested symbols (e.g., methods within a class).               |
| `symbol_content` | `string`              | The source code of the symbol, if requested.                 |

## Example Usage

### Request

```json
{
  "file_path": "src/models.py",
  "display_code_for": ["get_full_name"]
}
```

### Markdown Rendered for LLM

````markdown
### Symbol Outline for `src/models.py`

- **User** (`Class`)
  - \***\*init\*\*** (`Method`)
  - **get_full_name** (`Method`)

    ```python
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    ```

- **APIClient** (`Class`)
  - **request** (`Method`)
````
