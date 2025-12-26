# Symbol API

The Symbol API provides detailed information about a specific code symbol, including its source code and documentation. It is the primary way for an Agent to understand the implementation and usage of a function, class, or variable.

## SymbolRequest

Inherits from `LocateRequest`.

| Field             | Type                         | Default  | Description                                                         |
| :---------------- | :--------------------------- | :------- | :------------------------------------------------------------------ |
| `locate`          | `LocateText \| LocateSymbol` | Required | How to find the symbol (by text snippet or symbol path).            |
| `include_hover`   | `boolean`                    | `true`   | Whether to include documentation/hover information in the response. |
| `include_content` | `boolean`                    | `true`   | Whether to include the source code of the symbol.                   |

## SymbolResponse

| Field            | Type               | Description                                                 |
| :--------------- | :----------------- | :---------------------------------------------------------- |
| `file_path`      | `string`           | Relative path to the file containing the symbol.            |
| `symbol_path`    | `string[]`         | Hierarchy of the symbol (e.g., `["MyClass", "my_method"]`). |
| `symbol_content` | `string \| null`   | The source code of the symbol.                              |
| `hover`          | `string \| null`   | Markdown formatted documentation for the symbol.            |
| `parameters`     | `ParameterInfo[]?` | Structured parameter info (from Signature Help).            |

### ParameterInfo

| Field           | Type      | Description                                       |
| :-------------- | :-------- | :------------------------------------------------ |
| `name`          | `string`  | Parameter name.                                   |
| `label`         | `string`  | Full signature label (e.g., `timeout: int = 10`). |
| `documentation` | `string?` | Parameter-specific docstring.                     |

## Example Usage

### Request

```json
{
  "locate": {
    "file_path": "src/main.py",
    "symbol_path": ["calculate_total"]
  },
  "include_hover": true,
  "include_content": true
}
```

### Markdown Rendered for LLM

````markdown
# Symbol: `calculate_total` in `src/main.py`

## Overview

Calculates the total price of items in the cart, including tax.

## Implementation

```python
def calculate_total(items, tax_rate):
    return sum(item.price for item in items) * (1 + tax_rate)
```
````
