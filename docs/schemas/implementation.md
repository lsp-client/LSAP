# Implementation API

The Implementation API finds all concrete implementations of an abstract symbol, such as an interface method or a base class.

## ImplementationRequest

Inherits from `LocateRequest`. Since a symbol (like an interface) can have multiple implementations, this request supports pagination.

| Field             | Type                         | Default  | Description                                      |
| :---------------- | :--------------------------- | :------- | :----------------------------------------------- |
| `locate`          | `LocateText \| LocateSymbol` | Required | The symbol to find implementations for.          |
| `include_hover`   | `boolean`                    | `false`  | Whether to include docs for each implementation. |
| `include_content` | `boolean`                    | `true`   | Whether to include code for each implementation. |
| `limit`           | `number \| null`             | `null`   | Pagination limit.                                |
| `offset`          | `number`                     | `0`      | Pagination offset.                               |

## ImplementationResponse

| Field      | Type               | Description                            |
| :--------- | :----------------- | :------------------------------------- |
| `items`    | `SymbolResponse[]` | List of concrete implementations.      |
| `total`    | `number \| null`   | Total number of implementations found. |
| `has_more` | `boolean`          | Whether more results are available.    |

## Example Usage

### Scenario: Finding all subclasses that implement a method

#### Request

```json
{
  "locate": {
    "file_path": "base.py",
    "symbol_path": ["BaseWorker", "run"]
  },
  "limit": 2
}
```

#### Markdown Rendered for LLM

````markdown
### Implementations Found

**Total implementations**: 5 | **Showing**: 2 (Offset: 0, Limit: 2)

- `workers/local.py` - `LocalWorker.run`

```python
def run(self):
    print("Running locally")
```
````

- `workers/remote.py` - `RemoteWorker.run`

```python
def run(self):
    ssh.execute("run")
```

---

> [!TIP]
> **More implementations available.**
> To see more, specify a `limit` and use: `offset=2`

```

```
