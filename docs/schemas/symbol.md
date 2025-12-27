# Symbol API

The Symbol API provides detailed information about a specific code symbol, including its source code and documentation. It is the primary way for an Agent to understand the implementation and usage of a function, class, or variable.

## SymbolRequest

| Field             | Type                                                     | Default  | Description                                              |
| :---------------- | :------------------------------------------------------- | :------- | :------------------------------------------------------- |
| `locate`          | [`LocateText`](locate.md) \| [`LocateSymbol`](locate.md) | Required | How to find the symbol (by text snippet or symbol path). |
| `include_hover`   | `boolean`                                                | `true`   | Whether to include documentation/hover information.      |
| `include_code`    | `boolean`                                                | `true`   | Whether to include the source code of the symbol.        |

## SymbolResponse

| Field            | Type               | Description                                                 |
| :--------------- | :----------------- | :---------------------------------------------------------- |
| `file_path`      | `string`           | Relative path to the file containing the symbol.            |
| `path`           | `string[]`         | Hierarchy of the symbol (e.g., `["MyClass", "my_method"]`). |
| `name`           | `string`           | Name of the symbol.                                        |
| `kind`           | `string`           | Symbol kind (e.g., `Function`, `Class`).                  |
| `detail`         | `string \| null`   | Detail information about the symbol.                       |
| `hover`          | `string \| null`   | Markdown formatted documentation for the symbol.            |
| `code`           | `string \| null`   | The source code of the symbol.                              |

## Example Usage

### Scenario 1: Getting function documentation and implementation

#### Request

```json
{
  "locate": {
    "file_path": "src/main.py",
    "symbol_path": ["calculate_total"]
  },
  "include_hover": true,
  "include_code": true
}
```

#### Markdown Rendered for LLM

````markdown
# Symbol: `calculate_total` (`function`) at `src/main.py`

## Detail
(total_price, tax_rate: float) -> float

## Documentation
Calculates the total price of items in the cart, including tax.

## Content
```python
def calculate_total(items, tax_rate):
    return sum(item.price for item in items) * (1 + tax_rate)
```
````

### Scenario 2: Getting class information only (no code)

#### Request

```json
{
  "locate": {
    "file_path": "src/models.py",
    "symbol_path": ["User"]
  },
  "include_hover": true,
  "include_code": false
}
```

#### Markdown Rendered for LLM

````markdown
# Symbol: `models.User` (`class`) at `src/models.py`

## Detail
User model for authentication and profile management

## Documentation
Represents a user in the system with authentication credentials and profile information.
````
