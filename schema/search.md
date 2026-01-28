# Search API

The Search API provides fast, fuzzy symbol search across the entire workspace.
Results are concise for quick discovery—use the Inspect API to get detailed
information about specific symbols.

## Example Usage

### Scenario 1: Quick class search

Request:

```json
{
  "query": "AuthService",
  "kinds": ["class"],
  "max_items": 10
}
```

### Scenario 2: Fuzzy search for functions

Request:

```json
{
  "query": "calc",
  "kinds": ["function", "method"]
}
```

### Scenario 3: Pagination

Request:

```json
{
  "query": "test",
  "max_items": 5,
  "start_index": 0
}
```

## References

- [SearchItem.json](./SearchItem.json)
- [SearchRequest.json](./SearchRequest.json)
- [SearchResponse.json](./SearchResponse.json)
