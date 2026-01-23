# Symbol API

The Symbol API provides detailed information about a specific code symbol,
including its source code and documentation. It is the primary way for an
Agent to understand the implementation and usage of a function, class, or variable.

## Example Usage

### Scenario 1: Getting function documentation and implementation

Request:

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

### Scenario 2: Getting class information

Request:

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

## References

- [SymbolRequest.json](./SymbolRequest.json)
- [SymbolResponse.json](./SymbolResponse.json)
