# Workspace API

The Workspace API provides global symbol search capabilities across the entire project.

## WorkspaceSymbolRequest

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `query` | `string` | Required | Search string for symbols. |
| `limit` | `number \| null` | `null` | Maximum number of results to return. |
| `offset` | `number` | `0` | Number of results to skip for pagination. |

## WorkspaceSymbolResponse

| Field | Type | Description |
| :--- | :--- | :--- |
| `items` | `WorkspaceSymbolItem[]` | List of matching symbols. |
| `total` | `number \| null` | Total number of matches found globally. |
| `has_more` | `boolean` | Whether more results are available beyond the current page. |

## Example Usage

### Request
```json
{
  "query": "AuthService",
  "limit": 5
}
```

### Markdown Rendered for LLM
```markdown
### Workspace Symbols matching `AuthService`
**Total found**: 12 | **Showing**: 5 (Offset: 0, Limit: 5)

- **AuthService** (`Class`) in `src/auth/service.py`
- **IAuthService** (`Interface`) in `src/auth/interfaces.py`
- **MockAuthService** (`Class`) in `tests/mocks.py`
- ...

---
> [!TIP]
> **More results available.**
> To fetch the next page, specify a `limit` and use: `offset=5`
```
