# Reference API

The Reference API finds all locations where a specific symbol is used across the codebase.

## ReferenceRequest

Inherits from `LocateRequest`.

| Field             | Type             | Default | Description                                          |
| :---------------- | :--------------- | :------ | :--------------------------------------------------- |
| `include_hover`   | `boolean`        | `false` | Whether to include docs for each reference.          |
| `include_content` | `boolean`        | `true`  | Whether to include code snippets for each reference. |
| `limit`           | `number \| null` | `null`  | Pagination limit.                                    |
| `offset`          | `number`         | `0`     | Pagination offset.                                   |

## ReferenceResponse

| Field      | Type               | Description                                       |
| :--------- | :----------------- | :------------------------------------------------ |
| `items`    | `SymbolResponse[]` | List of locations where the symbol is referenced. |
| `has_more` | `boolean`          | Whether more references exist beyond the limit.   |

## Example Usage

### Request

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "symbol_path": ["format_date"]
  },
  "limit": 10
}
```

### Markdown Rendered for LLM

````markdown
### References Found

**Total references**: 45 | **Showing**: 10 (Offset: 0, Limit: 10)

- `src/ui/header.py` - `Header.render`

```python
formatted = format_date(user.last_login)
```
````

- `src/api/views.py` - `UserDetail.get`

```python
return {"date": format_date(obj.created_at)}
```

---

> [!TIP]
> **More references available.**
> To see more, specify a `limit` and use: `offset=10`

```

```
