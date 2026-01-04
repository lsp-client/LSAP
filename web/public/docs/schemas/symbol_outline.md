# Symbol Outline API

The Symbol Outline API returns a hierarchical tree of all symbols defined within a specific file. This allows an Agent to understand the structure of a file without reading the entire source code.

## SymbolOutlineRequest

| Field       | Type     | Default  | Description                           |
| :---------- | :------- | :------- | :------------------------------------ |
| `file_path` | `string` | Required | Relative path to the file to inspect. |

## SymbolOutlineResponse

| Field       | Type                 | Description                                 |
| :---------- | :------------------- | :------------------------------------------ |
| `file_path` | `string`             | Relative path to the file.                  |
| `items`     | `SymbolDetailInfo[]` | List of symbols in the file (hierarchical). |

### SymbolDetailInfo

| Field    | Type            | Description                                      |
| :------- | :-------------- | :----------------------------------------------- |
| `name`   | `string`        | Name of the symbol.                              |
| `path`   | `string[]`      | Hierarchy of the symbol.                         |
| `kind`   | `string`        | Symbol kind (e.g., `Class`, `Function`).         |
| `detail` | `string`        | Detail information about the symbol.             |
| `hover`  | `string`        | Markdown formatted documentation for the symbol. |
| `range`  | `Range \| null` | Source code range of the symbol.                 |

## Example Usage

### Scenario 1: Getting outline for a model file

#### Request

```json
{
  "file_path": "src/models.py"
}
```

#### Markdown Rendered for LLM

```markdown
# Symbol Outline for `src/models.py`

## User (`class`)

Represents a user in the system with authentication credentials.
User model for authentication and profile management.

### `__init__` (`method`)

Initializes the user instance with username and email.

### get_full_name (`method`)

Returns the user's full name.

## APIClient (`class`)

HTTP client for making API requests.

### request (`method`)

Makes an HTTP request to the specified URL.
```

### Scenario 2: Getting outline for a controller file

#### Request

```json
{
  "file_path": "src/controllers.py"
}
```

#### Markdown Rendered for LLM

```markdown
# Symbol Outline for `src/controllers.py`

## AuthController (`class`)

Handles authentication and authorization logic.

### login (`method`)

Authenticates user credentials.

### logout (`method`)

Logs out the current session.

## UserController (`class`)

Manages user-related operations.

### create (`method`)

Creates a new user account.

### update (`method`)

Updates user profile information.
```
