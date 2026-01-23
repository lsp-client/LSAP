# Definition & Navigation API

The Navigation API provides the ability to jump from a symbol usage to its primary
declaration or definition.

## Example Usage

### Scenario 1: Finding the definition of a method

If an Agent is reading `main.py` and sees `client.send_message()`, it can find
the definition of `send_message`.

Request:

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

### Scenario 2: Finding the declaration (useful in languages with header files)

Request:

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

### Scenario 3: Finding the type definition of a variable

Request:

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

## References

- [DefinitionRequest.json](./DefinitionRequest.json)
- [DefinitionResponse.json](./DefinitionResponse.json)
