# Implementation API

The Implementation API finds all concrete implementations of an abstract symbol, such as an interface method or a base class.

## ImplementationRequest

Inherits from `LocateRequest`. Since a symbol (like an interface) can have multiple implementations, this request supports pagination.

| Field             | Type                         | Default  | Description                                      |
| :---------------- | :--------------------------- | :------- | :----------------------------------------------- |
| `locate`          | `LocateText \| LocateSymbol` | Required | The symbol to find implementations for.          |
| `include_hover`   | `boolean`                    | `false`  | Whether to include docs for each implementation. |
| `include_content` | `boolean`                    | `true`   | Whether to include code for each implementation. |
| `max_items`       | `number \| null`             | `null`   | Maximum number of implementations to return.     |
| `start_index`     | `number`                     | `0`      | Number of items to skip for pagination.          |
| `pagination_id`   | `string \| null`             | `null`   | Token to retrieve the next page of results.      |

## ImplementationResponse

Inherits from `PaginatedResponse`.

| Field      | Type               | Description                            |
| :--------- | :----------------- | :------------------------------------- |
| `items`    | `SymbolResponse[]` | List of concrete implementations.      |
| `start_index` | `number`        | Offset of the current page.            |
| `max_items` | `number?`         | Number of items per page (if specified). |
| `total`    | `number \| null`   | Total number of implementations found. |
| `has_more` | `boolean`          | Whether more results are available.    |
| `pagination_id`| `string?`      | Token for retrieving the next page.    |

## Example Usage

### Scenario: Finding all subclasses that implement a method

#### Request

```json
{
  "locate": {
    "file_path": "base.py",
    "symbol_path": ["BaseWorker", "run"]
  },
  "max_items": 2
}
```

#### Markdown Rendered for LLM

````markdown
### Implementations Found

Total implementations: 5 | Showing: 2 (Offset: 0, Limit: 2)

- `workers/local.py` - `LocalWorker.run`

```python
def run(self):
    print("Running locally")
```

- `workers/remote.py` - `RemoteWorker.run`

```python
def run(self):
    ssh.execute("run")
```

---

> [!TIP]
> More implementations available.
> To see more, specify a `max_items` and use: `start_index=2`
````
