# Workspace API

The Workspace API provides global symbol search capabilities across the entire project.

## WorkspaceSymbolRequest

| Field           | Type             | Default  | Description                                 |
| :-------------- | :--------------- | :------- | :------------------------------------------ |
| `query`         | `string`         | Required | Search string for symbols.                  |
| `include_hover` | `boolean`        | `true`   | Whether to include documentation for symbols. |
| `include_code`  | `boolean`        | `true`   | Whether to include source code of symbols.    |
| `max_items`     | `number \| null` | `null`   | Maximum number of results to return.        |
| `start_index`   | `number`         | `0`      | Number of results to skip for pagination.   |
| `pagination_id` | `string \| null` | `null`   | Token to retrieve the next page of results. |

## WorkspaceSymbolResponse

| Field           | Type                    | Description                                                 |
| :-------------- | :---------------------- | :---------------------------------------------------------- |
| `request`       | `WorkspaceSymbolRequest` | The original request.                                       |
| `items`         | `WorkspaceSymbolItem[]` | List of matching symbols.                                   |
| `start_index`   | `number`                | Offset of the current page.                                 |
| `max_items`     | `number?`               | Number of items per page (if specified).                    |
| `total`         | `number \| null`        | Total number of matches found globally.                     |
| `has_more`      | `boolean`               | Whether more results are available beyond the current page. |
| `pagination_id` | `string?`               | Token for retrieving the next page.                         |

### WorkspaceSymbolItem

| Field          | Type               | Description                                       |
| :------------- | :----------------- | :------------------------------------------------ |
| `file_path`    | `string`           | Relative path to the file.                        |
| `name`         | `string`           | Name of the symbol.                              |
| `path`         | `string[]`         | Hierarchy of the symbol.                         |
| `kind`         | `string`           | Symbol kind (e.g., `Function`, `Class`).         |
| `detail`       | `string \| null`   | Detail information about the symbol.              |
| `hover`        | `string \| null`   | Markdown documentation for the symbol.             |
| `code`         | `string \| null`   | The source code of the symbol (if requested).   |
| `container_name`| `string \| null`   | Name of the containing symbol (e.g., class name).|

## Example Usage

### Scenario 1: Searching for authentication-related symbols

#### Request

```json
{
  "query": "AuthService",
  "include_hover": true,
  "include_code": false,
  "max_items": 5
}
```

#### Markdown Rendered for LLM

```markdown
# Workspace Symbols matching `AuthService`

Total found: 12 | Showing: 5 (Offset: 0, max_items: 5)

### AuthService (`class`)
- Location: `src/auth/service.py` (in `__init__`)
- Detail: Main authentication service for user login/logout

Provides authentication and session management functionality.

### IAuthService (`interface`)
- Location: `src/auth/interfaces.py`
- Detail: Authentication service interface

Defines the contract for authentication implementations.

### MockAuthService (`class`)
- Location: `tests/mocks.py` (in `__init__`)
- Detail: Mock authentication service for testing

---

> [!TIP]
> More results available.
> To fetch the next page, specify a `max_items` and use: `start_index=5`
```

### Scenario 2: Searching for symbols with code snippets

#### Request

```json
{
  "query": "connect",
  "include_hover": true,
  "include_code": true,
  "max_items": 3
}
```

#### Markdown Rendered for LLM

```markdown
# Workspace Symbols matching `connect`

Total found: 8 | Showing: 3 (Offset: 0, max_items: 3)

### connect (`method`)
- Location: `src/db/connection.py` (in `DatabaseConnection`)
- Detail: Establishes database connection

Connects to the database using configured credentials.

```python
def connect(self):
    self.conn = psycopg2.connect(
        host=self.host,
        user=self.user,
        password=self.password
    )
```

### connect (`method`)
- Location: `src/api/client.py` (in `APIClient`)
- Detail: Connects to the remote API server

```python
def connect(self):
    self.session = requests.Session()
    self.session.verify = self.verify_ssl
```

---

> [!TIP]
> More results available.
> To fetch the next page, specify a `max_items` and use: `start_index=3`
```
