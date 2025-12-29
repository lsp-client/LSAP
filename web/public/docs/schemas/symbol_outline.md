# Symbol Outline API

The Symbol Outline API returns a hierarchical tree of all symbols defined within a specific file. This allows an Agent to understand the structure of a file without reading the entire source code.

## SymbolOutlineRequest

| Field             | Type       | Default  | Description                                                      |
| :---------------- | :--------- | :------- | :--------------------------------------------------------------- |
| `file_path`       | `string`   | Required | Relative path to the file to inspect.                            |
| `include_hover`   | `boolean`  | `true`   | Whether to include documentation/hover information for symbols.   |
| `include_code`    | `boolean`  | `true`   | Whether to include the source code of the symbols.               |

## SymbolOutlineResponse

| Field       | Type                  | Description                            |
| :---------- | :-------------------- | :------------------------------------- |
| `file_path` | `string`              | Relative path to the file.             |
| `items`     | `SymbolInfo[]`        | List of symbols in the file (hierarchical). |

### SymbolInfo

| Field   | Type              | Description                                         |
| :------ | :---------------- | :-------------------------------------------------- |
| `name`  | `string`          | Name of the symbol.                                |
| `path`  | `string[]`        | Hierarchy of the symbol.                          |
| `kind`  | `string`          | Symbol kind (e.g., `Class`, `Function`).          |
| `detail`| `string \| null`  | Detail information about the symbol.               |
| `hover` | `string \| null`  | Markdown formatted documentation for the symbol.   |
| `code`  | `string \| null`  | The source code of the symbol, if requested.      |

## Example Usage

### Scenario 1: Getting full outline with code for a model file

#### Request

```json
{
  "file_path": "src/models.py",
  "include_hover": true,
  "include_code": true
}
```

#### Markdown Rendered for LLM

````markdown
# Symbol Outline for `src/models.py`

## User (`class`)
Represents a user in the system with authentication credentials.

### __init__ (`method`)
```python
def __init__(self, username: str, email: str):
    self.username = username
    self.email = email
```

### get_full_name (`method`)
Returns the user's full name.
```python
def get_full_name(self):
    return f"{self.first_name} {self.last_name}"
```

## APIClient (`class`)
HTTP client for making API requests.

### request (`method`)
```python
def request(self, method: str, url: str, data: dict = None):
    # Implementation...
```
````

### Scenario 2: Getting outline without code for quick navigation

#### Request

```json
{
  "file_path": "src/controllers.py",
  "include_hover": true,
  "include_code": false
}
```

#### Markdown Rendered for LLM

````markdown
# Symbol Outline for `src/controllers.py`

## AuthController (`class`)
Handles authentication and authorization logic.

### login (`method`)
Authenticates user credentials.

### logout (`method`)
Logs out the current user session.

## UserController (`class`)
Manages user-related operations.

### create (`method`)
Creates a new user account.

### update (`method`)
Updates user profile information.

### delete (`method`)
Deletes a user account.
````
````
