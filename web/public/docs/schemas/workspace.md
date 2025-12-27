# Workspace API

The Workspace API provides global symbol search capabilities across the entire project.

## WorkspaceSymbolRequest

| Field           | Type             | Default  | Description                                 |
| :-------------- | :--------------- | :------- | :------------------------------------------ |
| `query`         | `string`         | Required | Search string for symbols.                  |
| `max_items`     | `number \| null` | `null`   | Maximum number of results to return.        |
| `start_index`   | `number`         | `0`      | Number of results to skip for pagination.   |
| `pagination_id` | `string \| null` | `null`   | Token to retrieve the next page of results. |

## WorkspaceSymbolResponse

| Field           | Type                    | Description                                                 |
| :-------------- | :---------------------- | :---------------------------------------------------------- |
| `query`         | `string`                | The search string used to find the symbols.                 |
| `items`         | `WorkspaceSymbolItem[]` | List of matching symbols.                                   |
| `start_index`   | `number`                | Offset of the current page.                                 |
| `max_items`     | `number?`               | Number of items per page (if specified).                    |
| `total`         | `number \| null`        | Total number of matches found globally.                     |
| `has_more`      | `boolean`               | Whether more results are available beyond the current page. |
| `pagination_id` | `string?`               | Token for retrieving the next page.                         |

## Example Usage

### Request

```json
{
  "query": "AuthService",
  "max_items": 5
}
```

### Markdown Rendered for LLM

```markdown
# Workspace Symbols matching `AuthService`

Total found: 12 | Showing: 5 (Offset: 0, max_items: 5)

- AuthService (`Class`) in `src/auth/service.py`
- IAuthService (`Interface`) in `src/auth/interfaces.py`
- MockAuthService (`Class`) in `tests/mocks.py`
- ...

---

> [!TIP]
> More results available.
> To fetch the next page, specify a `max_items` and use: `start_index=5`
```
