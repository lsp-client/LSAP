# Hover API

The Hover API provides quick access to documentation, type information, or other relevant metadata for a symbol at a specific location. It's useful for getting context without navigating to the definition.

## HoverRequest

| Field       | Type                                                     | Default  | Description                           |
| :---------- | :------------------------------------------------------- | :------- | :------------------------------------ |
| `locate`    | [`LocateText`](locate.md) \| [`LocateSymbol`](locate.md) | Required | The location to get hover info for.    |

## HoverResponse

| Field      | Type          | Description                                       |
| :--------- | :------------ | :------------------------------------------------ |
| `contents`  | `string`      | The hover content, usually in markdown format.    |
| `range`     | `Range \| null` | The range to which this hover applies (optional). |

## Example Usage

### Scenario 1: Getting documentation for a function

#### Request

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "line": 42,
    "find": "calculate"
  }
}
```

#### Markdown Rendered for LLM

```markdown
# Hover Information

```python
def calculate(x: int, y: int) -> int
```

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
    "line": 15,
    "find": "config"
  }
}
```

#### Markdown Rendered for LLM

```markdown
# Hover Information

```python
config: Config
```

Configuration object containing application settings such as database connection, API endpoints, and logging preferences.
```

### Scenario 3: Getting hover for a class method

#### Request

```json
{
  "locate": {
    "file_path": "src/models/user.py",
    "symbol_path": ["User", "save"]
  }
}
```

#### Markdown Rendered for LLM

```markdown
# Hover Information

```python
def save(self) -> bool
```

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
    "line": 5,
    "find": "numpy"
  }
}
```

#### Markdown Rendered for LLM

```markdown
# Hover Information

```python
import numpy
```

NumPy is the fundamental package for scientific computing in Python. It provides support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays.

**Documentation:** https://numpy.org/doc/
```
