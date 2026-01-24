# Outline API

The Outline API returns a hierarchical tree of all symbols defined within a specific file.
This allows an Agent to understand the structure of a file without reading the entire
source code.

## Example Usage

### Scenario 1: Getting outline for a model file

Request:

```json
{
  "file_path": "src/models.py"
}
```

### Scenario 2: Getting outline for a controller file

Request:

```json
{
  "file_path": "src/controllers.py"
}
```

### Scenario 3: Getting outline for a specific class

Request:

```json
{
  "file_path": "src/models.py",
  "scope": {
    "symbol_path": ["MyClass"]
  }
}
```

## References

- [OutlineRequest.json](./OutlineRequest.json)
- [OutlineResponse.json](./OutlineResponse.json)
