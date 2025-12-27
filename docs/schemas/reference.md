# Reference API

The Reference API finds all locations where a specific symbol is used across the codebase.

## ReferenceRequest

| Field             | Type                                                     | Default  | Description                                          |
| :---------------- | :------------------------------------------------------- | :------- | :--------------------------------------------------- |
| `locate`          | [`LocateText`](locate.md) \| [`LocateSymbol`](locate.md) | Required | The symbol to find references for.                   |
| `include_hover`   | `boolean`                                                | `false`  | Whether to include docs for each reference.          |
| `include_content` | `boolean`                                                | `true`   | Whether to include code snippets for each reference. |
| `max_items`       | `number \| null`                                         | `null`   | Maximum number of references to return.              |
| `start_index`     | `number`                                                 | `0`      | Number of items to skip for pagination.              |
| `pagination_id`   | `string \| null`                                         | `null`   | Token to retrieve the next page of results.          |

## ReferenceResponse

| Field           | Type                            | Description                                       |
| :-------------- | :------------------------------ | :------------------------------------------------ |
| `items`         | [`SymbolResponse`](symbol.md)[] | List of locations where the symbol is referenced. |
| `start_index`   | `number`                        | Offset of the current page.                       |
| `max_items`     | `number?`                       | Number of items per page (if specified).          |
| `total`         | `number?`                       | Total number of references (if available).        |
| `has_more`      | `boolean`                       | Whether more references exist beyond the limit.   |
| `pagination_id` | `string?`                       | Token for retrieving the next page.               |

## Example Usage

### Request

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "symbol_path": ["format_date"]
  },
  "max_items": 10
}
```

### Markdown Rendered for LLM

````markdown
# References Found

Total references: 45 | Showing: 10 (Offset: 0, Limit: 10)

- `src/ui/header.py` - `Header.render`

```python
formatted = format_date(user.last_login)
```

- `src/api/views.py` - `UserDetail.get`

```python
return {"date": format_date(obj.created_at)}
```

---

> [!TIP]
> More references available.
> To see more, specify a `max_items` and use: `start_index=10`
````
