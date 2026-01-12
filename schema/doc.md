# Doc API

The Doc API provides quick access to documentation, type information, or other
relevant metadata for a symbol at a specific location. It's useful for getting
context without navigating to the definition.

## Example Usage

### Scenario 1: Getting documentation for a function

Request:

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "find": "def calculate"
  }
}
```

### Scenario 2: Getting type information for a variable

Request:

```json
{
  "locate": {
    "file_path": "src/main.py",
    "find": "config"
  }
}
```

### Scenario 3: Getting documentation for a class method

Request:

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

### Scenario 4: Getting documentation for an imported module

Request:

```json
{
  "locate": {
    "file_path": "src/main.py",
    "find": "import numpy"
  }
}
```

## References

- [DocRequest.json](./DocRequest.json)
- [DocResponse.json](./DocResponse.json)
