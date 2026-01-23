# Reference API

The Reference API finds all locations where a specific symbol is used across the codebase.

## Example Usage

### Scenario 1: Finding all references of a function

Request:

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "scope": {
      "symbol_path": ["format_date"]
    }
  },
  "max_items": 10
}
```

### Scenario 2: Finding all implementations of an interface method

Request:

```json
{
  "locate": {
    "file_path": "src/base.py",
    "scope": {
      "symbol_path": ["DatabaseConnection", "connect"]
    }
  },
  "mode": "implementations",
  "max_items": 5
}
```

### Scenario 3: Finding all classes that implement an interface

Request:

```json
{
  "locate": {
    "file_path": "src/interfaces.py",
    "scope": {
      "symbol_path": ["IRepository"]
    }
  },
  "mode": "implementations",
  "max_items": 5
}
```

## References

- [ReferenceItem.json](./ReferenceItem.json)
- [ReferenceRequest.json](./ReferenceRequest.json)
- [ReferenceResponse.json](./ReferenceResponse.json)
