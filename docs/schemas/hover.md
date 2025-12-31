# Hover API

The Hover API provides quick access to documentation, type information, or other relevant metadata for a symbol at a specific location. It's useful for getting context without navigating to the definition.

## HoverRequest

| Field    | Type                | Default  | Description                           |
| :------- | :------------------ | :------- | :------------------------------------ |
| `locate` | [`Locate`](locate.md) | Required | The location to get hover info for.   |

## HoverResponse

| Field      | Type          | Description                                       |
| :--------- | :------------ | :------------------------------------------------ |
| `contents` | `string`      | The hover content, usually in markdown format.    |

## Example Usage

### Scenario 1: Getting documentation for a function

#### Request

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "find": "def calculate"
  }
}
```

#### Markdown Rendered for LLM

```markdown
# Hover Information

Calculates the sum of two integers and returns the result.

**Parameters:**
- `x`: First integer to add
- `y`: Second integer to add

**Returns:** The sum of x and y
```

### Scenario 2: Getting type information for a variable

#### Request

```json
{
  "locate": {
    "file_path": "src/main.py",
    "find": "config"
  }
}
```

#### Markdown Rendered for LLM

```markdown
# Hover Information

Configuration object containing application settings such as database connection, API endpoints, and logging preferences.
```

### Scenario 3: Getting hover for a class method

#### Request

```json
{
  "locate": {
    "file_path": "src/models/user.py",
    "scope": {
      "symbol_path": ["User", "save"]
    }
  }
}
```

#### Markdown Rendered for LLM

```markdown
# Hover Information

Saves the current user instance to the database.

**Returns:** `True` if save was successful, `False` otherwise.

**Raises:** `DatabaseError` if there's an issue connecting to the database.
```

### Scenario 4: Getting hover for an imported module

#### Request

```json
{
  "locate": {
    "file_path": "src/main.py",
    "find": "import numpy"
  }
}
```

#### Markdown Rendered for LLM

```markdown
# Hover Information

NumPy is the fundamental package for scientific computing in Python. It provides support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays.

**Documentation:** https://numpy.org/doc/
```
