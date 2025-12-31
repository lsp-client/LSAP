# Symbol API

The Symbol API provides detailed information about a specific code symbol, including its source code and documentation. It is the primary way for an Agent to understand the implementation and usage of a function, class, or variable.

## SymbolRequest

| Field    | Type                | Default  | Description                                              |
| :------- | :------------------ | :------- | :------------------------------------------------------- |
| `locate` | [`Locate`](locate.md) | Required | How to find the symbol (by text pattern or symbol path). |

## SymbolResponse

| Field            | Type               | Description                                                 |
| :--------------- | :----------------- | :---------------------------------------------------------- |
| `file_path`      | `string`           | Relative path to the file containing the symbol.            |
| `path`           | `string[]`         | Hierarchy of the symbol (e.g., `["MyClass", "my_method"]`). |
| `name`           | `string`           | Name of the symbol.                                        |
| `kind`           | `string`           | Symbol kind (e.g., `Function`, `Class`).                  |
| `detail`         | `string \| null`   | Detail information about the symbol.                       |
| `hover`          | `string \| null`   | Markdown formatted documentation for the symbol.            |
| `code`           | `string`           | The source code of the symbol.                              |
| `range`          | `Range \| null`    | Source code range of the symbol.                            |

## Example Usage

### Scenario 1: Getting function documentation and implementation

#### Request

```json
{
  "locate": {
    "file_path": "src/main.py",
    "scope": {
      "symbol_path": ["calculate_total"]
    }
  }
}
```

#### Markdown Rendered for LLM

````markdown
# Symbol: `calculate_total` (`function`) at `src/main.py`

## Implementation
```python
def calculate_total(items, tax_rate):
    return sum(item.price for item in items) * (1 + tax_rate)
```
````

### Scenario 2: Getting class information

#### Request

```json
{
  "locate": {
    "file_path": "src/models.py",
    "scope": {
      "symbol_path": ["User"]
    }
  }
}
```

#### Markdown Rendered for LLM

````markdown
# Symbol: `User` (`class`) at `src/models.py`

## Implementation
```python
class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
```
````
