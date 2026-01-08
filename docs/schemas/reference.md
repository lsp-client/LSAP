# Reference API

The Reference API finds all locations where a specific symbol is used across the codebase.

## ReferenceRequest

| Field           | Type                                  | Default        | Description                                             |
| :-------------- | :------------------------------------ | :------------- | :------------------------------------------------------ |
| `locate`        | [`Locate`](locate.md)                 | Required       | The symbol to find references for.                      |
| `mode`          | `"references"` \| `"implementations"` | `"references"` | Whether to find references or concrete implementations. |
| `context_lines` | `number`                              | `2`            | Number of lines around the match to include.            |
| `max_items`     | `number \| null`                      | `null`         | Maximum number of references to return.                 |
| `start_index`   | `number`                              | `0`            | Number of items to skip for pagination.                 |
| `pagination_id` | `string \| null`                      | `null`         | Token to retrieve the next page of results.             |

## ReferenceResponse

| Field           | Type               | Description                                       |
| :-------------- | :----------------- | :------------------------------------------------ |
| `request`       | `ReferenceRequest` | The original request.                             |
| `items`         | `ReferenceItem[]`  | List of locations where the symbol is referenced. |
| `start_index`   | `number`           | Offset of the current page.                       |
| `max_items`     | `number?`          | Number of items per page (if specified).          |
| `total`         | `number?`          | Total number of references (if available).        |
| `has_more`      | `boolean`          | Whether more references exist beyond the limit.   |
| `pagination_id` | `string?`          | Token for retrieving the next page.               |

### ReferenceItem

| Field      | Type                       | Description                                      |
| :--------- | :------------------------- | :----------------------------------------------- |
| `location` | [`Location`](locate.md)    | The location of the reference.                   |
| `code`     | `string`                   | Surrounding code snippet.                        |
| `symbol`   | `SymbolDetailInfo \| null` | The symbol containing this reference (optional). |

## Example Usage

### Scenario 1: Finding all references of a function

#### Request

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

#### Markdown Rendered for LLM

````markdown
# References Found

Total references: 45 | Showing: 10 (Offset: 0, Limit: 10)

### `src/ui/header.py`:28

In `Header.render` (`Method`)

```python
formatted = format_date(user.last_login)
```

### `src/api/views.py`:42

In `UserDetail.get` (`Method`)

```python
return {"date": format_date(obj.created_at)}
```

---

> [!TIP]
> More references available.
> To see more, specify a `max_items` and use: `start_index=10`
````

### Scenario 2: Finding all implementations of an interface method

#### Request

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

#### Markdown Rendered for LLM

````markdown
# Implementations Found

Total implementations: 8 | Showing: 5 (Offset: 0, Limit: 5)

### `src/mysql.py`:15

In `MySQLConnection.connect` (`Method`)

```python
def connect(self):
    self.pool = mysql.connector.connect(
        host=self.host,
        user=self.user,
        password=self.password
    )
```

### `src/postgres.py`:18

In `PostgresConnection.connect` (`Method`)

```python
def connect(self):
    self.conn = psycopg2.connect(
        host=self.host,
        user=self.user,
        password=self.password,
        database=self.database
    )
```

---

> [!TIP]
> More implementations available.
> To see more, specify a `max_items` and use: `start_index=5`
````
