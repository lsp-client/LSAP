# Definition & Navigation API

The Navigation API provides the ability to jump from a symbol usage to its primary declaration or definition.

## DefinitionRequest

| Field             | Type                                                     | Default  | Description                            |
| :---------------- | :------------------------------------------------------- | :------- | :------------------------------------- |
| `locate`          | [`LocateText`](locate.md) \| [`LocateSymbol`](locate.md) | Required | The starting location (the reference). |
| `mode`            | `"definition" \| "declaration" \| "type_definition"`   | `"definition"` | The type of location to find.         |
| `include_hover`   | `boolean`                                                | `true`   | Whether to include documentation.      |
| `include_code`    | `boolean`                                                | `true`   | Whether to include source code.        |

## DefinitionResponse

Inherits from [`SymbolInfo`](symbol.md) and `Response`.

| Field            | Type               | Description                                          |
| :--------------- | :----------------- | :--------------------------------------------------- |
| `file_path`      | `string`           | Relative path to the file containing the definition. |
| `path`           | `string[]`         | Hierarchy of the symbol.                             |
| `name`           | `string`           | Name of the symbol.                                  |
| `kind`           | `string`           | Symbol kind (e.g., `Function`, `Class`).            |
| `detail`         | `string \| null`   | Detail information about the symbol.                |
| `hover`          | `string \| null`   | Markdown documentation for the symbol.               |
| `code`           | `string \| null`   | The source code of the definition.                   |
| `request`        | `DefinitionRequest`| The original request.                                |

## Example Usage

### Scenario 1: Finding the definition of a method

If an Agent is reading `main.py` and sees `client.send_message()`, it can find the definition of `send_message`.

#### Request

```json
{
  "locate": {
    "file_path": "main.py",
    "line": 15,
    "find": "send_message"
  },
  "mode": "definition",
  "include_code": true
}
```

#### Markdown Rendered for LLM

````markdown
# Definition Result

### `client.py`: send_message (`Method`)

Sends a message to the server.

## Content
```python
def send_message(self, text: str):
    self.connection.post(text)
```
````

### Scenario 2: Finding the declaration (useful in languages with header files)

#### Request

```json
{
  "locate": {
    "file_path": "main.cpp",
    "line": 20,
    "find": "process_data"
  },
  "mode": "declaration",
  "include_code": true
}
```

#### Markdown Rendered for LLM

````markdown
# Declaration Result

### `utils.h`: process_data (`Function`)

Declaration of the data processing function.

## Content
```cpp
void process_data(const std::vector<int>& data);
```
````

### Scenario 3: Finding the type definition of a variable

#### Request

```json
{
  "locate": {
    "file_path": "main.py",
    "line": 30,
    "find": "result"
  },
  "mode": "type_definition",
  "include_code": true
}
```

#### Markdown Rendered for LLM

````markdown
# Type definition Result

### `models.py`: Result (`Class`)

Represents the result of an operation with success/failure status.

## Content
```python
class Result:
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
```
````
