# Implementation API

The Implementation API finds all concrete implementations of an abstract symbol, such as an interface method or a base class. This is a specialized mode of the Reference API with `mode="implementations"`.

## ReferenceRequest (with mode="implementations")

| Field             | Type                        | Default        | Description                                      |
| :---------------- | :-------------------------- | :------------- | :----------------------------------------------- |
| `locate`          | [`Locate`](locate.md)       | Required       | The symbol to find implementations for.          |
| `mode`            | `"implementations"`         | `"references"` | Must be set to "implementations" to use this mode. |
| `context_lines`   | `number`                    | `2`            | Number of lines around the match to include.     |
| `max_items`       | `number \| null`            | `null`         | Maximum number of implementations to return.     |
| `start_index`     | `number`                    | `0`            | Number of items to skip for pagination.          |
| `pagination_id`   | `string \| null`            | `null`         | Token to retrieve the next page of results.      |

## ReferenceResponse

| Field           | Type                 | Description                              |
| :-------------- | :------------------- | :--------------------------------------- |
| `request`       | `ReferenceRequest`   | The original request (with mode=implementations). |
| `items`         | `ReferenceItem[]`    | List of concrete implementations.        |
| `start_index`   | `number`             | Offset of the current page.              |
| `max_items`     | `number?`            | Number of items per page (if specified). |
| `total`         | `number \| null`     | Total number of implementations found.   |
| `has_more`      | `boolean`            | Whether more results are available.      |
| `pagination_id` | `string?`            | Token for retrieving the next page.      |

## Example Usage

### Scenario 1: Finding all subclasses that implement an abstract method

#### Request

```json
{
  "locate": {
    "file_path": "base.py",
    "scope": {
      "symbol_path": ["BaseWorker", "run"]
    }
  },
  "mode": "implementations",
  "context_lines": 2,
  "max_items": 2
}
```

#### Markdown Rendered for LLM

````markdown
# Implementations Found

Total implementations: 5 | Showing: 2 (Offset: 0, max_items: 2)

### `workers/local.py`:12
In `LocalWorker.run` (`Method`)

```python
def run(self):
    """Execute worker in local environment."""
    print("Running locally")
    self.execute_local()
```

### `workers/remote.py`:15
In `RemoteWorker.run` (`Method`)

```python
def run(self):
    """Execute worker via SSH connection."""
    ssh.connect(self.host)
    ssh.execute("run")
```

---

> [!TIP]
> More implementations available.
> To see more, specify a `max_items` and use: `start_index=2`
````

### Scenario 2: Finding all classes that implement an interface

#### Request

```json
{
  "locate": {
    "file_path": "src/interfaces.py",
    "scope": {
      "symbol_path": ["IRepository"]
    }
  },
  "mode": "implementations",
  "context_lines": 1,
  "max_items": 5
}
```

#### Markdown Rendered for LLM

````markdown
# Implementations Found

Total implementations: 8 | Showing: 5 (Offset: 0, max_items: 5)

### `src/repositories/user_repo.py`:10
In `UserRepository` (`Class`)

```python
class UserRepository(IRepository):
    def get(self, id):
        return self.db.query(User).filter(User.id == id).first()
```

### `src/repositories/product_repo.py`:10
In `ProductRepository` (`Class`)

```python
class ProductRepository(IRepository):
    def get(self, id):
        return self.db.query(Product).filter(Product.id == id).first()
```

### `src/repositories/order_repo.py`:10
In `OrderRepository` (`Class`)

```python
class OrderRepository(IRepository):
    def get(self, id):
        return self.db.query(Order).filter(Order.id == id).first()
```

---

> [!TIP]
> More implementations available.
> To see more, specify a `max_items` and use: `start_index=5`
````

### Scenario 3: Finding implementations with full code context

#### Request

```json
{
  "locate": {
    "file_path": "src/base.py",
    "scope": {
      "symbol_path": ["IDataSource", "query"]
    }
  },
  "mode": "implementations",
  "context_lines": 5,
  "max_items": 3
}
```

#### Markdown Rendered for LLM

````markdown
# Implementations Found

Total implementations: 4 | Showing: 3 (Offset: 0, max_items: 3)

### `src/sources/sqlite_source.py`:20
In `SQLiteDataSource.query` (`Method`)

```python
def query(self, sql, params=None):
    """Execute SQL query with optional parameters."""
    cursor = self.conn.cursor()
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        raise DataSourceError(f"Query failed: {e}")
```

### `src/sources/postgres_source.py`:22
In `PostgresDataSource.query` (`Method`)

```python
def query(self, sql, params=None):
    """Execute PostgreSQL query."""
    with self.pool.getconn() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()
```

---

> [!TIP]
> More implementations available.
> To see more, specify a `max_items` and use: `start_index=3`
````
