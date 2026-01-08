# Search API

The Search API provides fast, fuzzy symbol search across the entire workspace. Results are concise for quick discovery—use the [Symbol API](symbol.md) to get detailed information about specific symbols.

## SearchRequest

| Field           | Type                   | Default  | Description                                     |
| :-------------- | :--------------------- | :------- | :---------------------------------------------- |
| `query`         | `string`               | Required | Search pattern (exact, prefix, or fuzzy match). |
| `kinds`         | `SymbolKind[] \| null` | `null`   | Filter by symbol kinds (e.g., `["class"]`).     |
| `max_items`     | `number \| null`       | `null`   | Maximum number of results to return.            |
| `start_index`   | `number`               | `0`      | Number of results to skip for pagination.       |
| `pagination_id` | `string \| null`       | `null`   | Token to retrieve the next page of results.     |

## SearchResponse

| Field           | Type             | Description                              |
| :-------------- | :--------------- | :--------------------------------------- |
| `request`       | `SearchRequest`  | The original request.                    |
| `items`         | `SearchItem[]`   | List of matching symbols.                |
| `start_index`   | `number`         | Offset of the current page.              |
| `max_items`     | `number?`        | Number of items per page (if specified). |
| `total`         | `number \| null` | Total number of matches found.           |
| `has_more`      | `boolean`        | Whether more results are available.      |
| `pagination_id` | `string?`        | Token for retrieving the next page.      |

### SearchItem

| Field       | Type             | Description                                  |
| :---------- | :--------------- | :------------------------------------------- |
| `name`      | `string`         | Symbol name.                                 |
| `kind`      | `SymbolKind`     | Symbol kind (e.g., `class`, `function`).     |
| `file_path` | `string`         | Path to the file containing the symbol.      |
| `line`      | `number \| null` | 1-based line number where symbol is defined. |
| `container` | `string \| null` | Parent symbol name (e.g., class for method). |

## Example Usage

### Scenario 1: Quick class search

#### Request

```json
{
  "query": "AuthService",
  "kinds": ["class"],
  "max_items": 10
}
```

#### Markdown Rendered for LLM

```markdown
# Search: `AuthService`

Found 3 results (showing 3)

- `AuthService` (class): `src/auth/service.py:15`
- `MockAuthService` (class): `tests/mocks.py:8` (in `tests`)
- `AuthServiceConfig` (class): `src/auth/config.py:5`
```

### Scenario 2: Fuzzy search for functions

#### Request

```json
{
  "query": "calc",
  "kinds": ["function", "method"]
}
```

#### Markdown Rendered for LLM

```markdown
# Search: `calc`

Found 5 results

- `calculate_total` (function): `src/utils.py:42`
- `calculate_tax` (function): `src/tax.py:10`
- `calc_discount` (method): `src/pricing.py:88` (in `PriceCalculator`)
- `recalculate` (method): `src/cart.py:120` (in `Cart`)
- `calc` (function): `src/math_utils.py:5`
```

### Scenario 3: Pagination

#### Request

```json
{
  "query": "test",
  "max_items": 5,
  "start_index": 0
}
```

#### Markdown Rendered for LLM

```markdown
# Search: `test`

Found 23 results (showing 5)

- `test_auth` (function): `tests/test_auth.py:10`
- `test_login` (function): `tests/test_auth.py:25`
- `test_logout` (function): `tests/test_auth.py:40`
- `TestUser` (class): `tests/test_models.py:8`
- `test_create_user` (method): `tests/test_models.py:15` (in `TestUser`)

> More results available. Use `start_index=5` for next page.
```
