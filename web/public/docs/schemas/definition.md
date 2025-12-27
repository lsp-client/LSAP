# Definition & Navigation API

The Navigation API provides the ability to jump from a symbol usage to its primary declaration or definition.

## Navigation Requests

All navigation requests inherit from [`LocateRequest`](locate.md) and identify a starting position in the code.

### 1. DeclarationRequest

Finds the **declaration** of a symbol. Useful in languages like C/C++ where declarations (headers) are separate from definitions.

### 2. DefinitionRequest

Finds the **definition** of a symbol. This is the most common navigation, leading to the actual implementation of a function or class.

### 3. TypeDefinitionRequest

Finds the **type definition** of a symbol. For an instance variable, this leads to the class/struct definition.

## Common Fields

| Field             | Type                                                     | Default  | Description                            |
| :---------------- | :------------------------------------------------------- | :------- | :------------------------------------- |
| `locate`          | [`LocateText`](locate.md) \| [`LocateSymbol`](locate.md) | Required | The starting location (the reference). |
| `include_hover`   | `boolean`                                                | `true`   | Whether to include documentation.      |
| `include_content` | `boolean`                                                | `true`   | Whether to include source code.        |

## DefinitionResponse

Inherits from [`SymbolResponse`](symbol.md).

| Field            | Type               | Description                                          |
| :--------------- | :----------------- | :--------------------------------------------------- |
| `file_path`      | `string`           | Relative path to the file containing the definition. |
| `symbol_path`    | `string[]`         | Hierarchy of the symbol.                             |
| `symbol_content` | `string \| null`   | The source code of the definition.                   |
| `hover`          | `string \| null`   | Markdown documentation for the symbol.               |
| `parameters`     | `ParameterInfo[]?` | Structured parameter info.                           |

## Example Usage

### Scenario: Finding the definition of a variable

If an Agent is reading `main.py` and sees `client.send_message()`, it can find the definition of `send_message`.

#### Request

```json
{
  "locate": {
    "file_path": "main.py",
    "line": 15,
    "find": "send_message"
  },
  "include_content": true
}
```

#### Markdown Rendered for LLM

````markdown
# Navigation Result

## Implementation / Declaration

```python
def send_message(self, text: str):
    self.connection.post(text)
```
````
