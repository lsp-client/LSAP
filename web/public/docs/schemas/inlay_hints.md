# Inlay Hints & Inline Values API

LSAP provides the ability to read code with "decorations" that inject static type hints, parameter names, and runtime variable values directly into the text as comments. This helps the Agent understand implicit logic and current execution state.

## Concepts

### 1. Inlay Hints

Static markers computed by the language server.

- **Parameter Hints**: Show the names of arguments in function calls (e.g., `func(/* name:= */ "val")`).
- **Type Hints**: Show inferred types for variables (e.g., `let x /* :int */ = 5`).

### 2. Inline Values

Dynamic markers showing runtime values, typically used during debugging or error analysis.

- **Variable Values**: Show the current state (e.g., `x = 10 // value: x=10`).

---

## Requests

### InlayHintRequest

Fetches static hints for a range.

| Field       | Type            | Default  | Description                 |
| :---------- | :-------------- | :------- | :-------------------------- |
| `file_path` | `string`        | Required | Path to the file.           |
| `range`     | `Range \| null` | `null`   | Optional range to focus on. |

### InlineValueRequest

Fetches runtime values for a range.

| Field       | Type     | Default  | Description                         |
| :---------- | :------- | :------- | :---------------------------------- |
| `file_path` | `string` | Required | Path to the file.                   |
| `range`     | `Range`  | Required | Required range (execution context). |

## Response: DecoratedContentResponse

Instead of returning raw JSON lists of positions (which are hard for LLMs to reason about), LSAP returns a **Decorated Content** view.

| Field               | Type     | Description                                             |
| :------------------ | :------- | :------------------------------------------------------ |
| `file_path`         | `string` | The file being read.                                    |
| `decorated_content` | `string` | Source code with hints and values injected as comments. |

## Example Usage

### Scenario 1: Getting type hints for a function

#### Request (InlayHintRequest)

```json
{
  "file_path": "src/api.py",
  "range": {
    "start": {"line": 10, "character": 0},
    "end": {"line": 15, "character": 0}
  }
}
```

#### Markdown Rendered for LLM

````markdown
# Code with Annotations: `src/api.py`

```python
def process_data(items /* :list */):
    result /* :dict */ = {}
    for item /* :dict */ in items:
        key /* :str */ = item['id']
        result[key] = item['value']
    return result
```

---

> [!NOTE]
> Annotations like `/* :type */` or `/* param:= */` are injected for clarity.
> Runtime values (if any) are shown as `// value: x=42`.
````

### Scenario 2: Getting parameter hints for a function call

#### Request (InlayHintRequest)

```json
{
  "file_path": "src/utils.py",
  "range": {
    "start": {"line": 20, "character": 0},
    "end": {"line": 20, "character": 80}
  }
}
```

#### Markdown Rendered for LLM

````markdown
# Code with Annotations: `src/utils.py`

```python
response = api_client.post(/* url:= */ "https://api.com/data", /* json:= */ payload, /* timeout:= */ 30, /* verify:= */ False)
```

---

> [!NOTE]
> Annotations like `/* :type */` or `/* param:= */` are injected for clarity.
> Runtime values (if any) are shown as `// value: x=42`.
````

### Scenario 3: Debugging an error with runtime values

#### Request (InlineValueRequest)

```json
{
  "file_path": "src/logic.py",
  "range": {
    "start": {"line": 10, "character": 0},
    "end": {"line": 20, "character": 0}
  }
}
```

#### Markdown Rendered for LLM

````markdown
# Code with Annotations: `src/logic.py`

```python
def process(items):
    total = 0  // value: total = 0
    for i in items:
        price = i.price  // value: i.price = None
        total += price  // value: total = None
    return total  // value: total = None
```

---

> [!NOTE]
> Annotations like `/* :type */` or `/* param:= */` are injected for clarity.
> Runtime values (if any) are shown as `// value: x=42`.
````

### Scenario 4: Combined type and parameter hints

#### Request (InlayHintRequest)

```json
{
  "file_path": "src/service.py"
}
```

#### Markdown Rendered for LLM

````markdown
# Code with Annotations: `src/service.py`

```python
class DataService:
    def __init__(self):
        self.client /* :APIClient */ = APIClient()
        self.cache /* :dict */ = {}

    def get_user(self, user_id /* :int */) /* :Optional[User] */:
        if user_id /* :int */ in self.cache /* :dict */:
            return self.cache[user_id]
        user = self.client.get(/* endpoint:= */ f'/users/{user_id}')
        return user
```

---

> [!NOTE]
> Annotations like `/* :type */` or `/* param:= */` are injected for clarity.
> Runtime values (if any) are shown as `// value: x=42`.
````
