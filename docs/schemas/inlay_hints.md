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

- `file_path`: Path to the file.
- `range`: Optional range to focus on.

### InlineValueRequest

Fetches runtime values for a range.

- `file_path`: Path to the file.
- `range`: Required range (execution context).

## Response: DecoratedContentResponse

Instead of returning raw JSON lists of positions (which are hard for LLMs to reason about), LSAP returns a **Decorated Content** view.

| Field               | Type     | Description                                             |
| :------------------ | :------- | :------------------------------------------------------ |
| `file_path`         | `string` | The file being read.                                    |
| `decorated_content` | `string` | Source code with hints and values injected as comments. |

## Example Usage

### Scenario: Understanding a complex function call

#### Request (InlayHintRequest)

```json
{
  "file_path": "src/api.py",
  "range": { ... }
}
```

#### Markdown Rendered for LLM

````markdown
### Code with Annotations: `src/api.py`

```python
# The hints help the Agent know which argument is which
client.post(/* url:= */ "https://api.com", /* data:= */ payload, /* verify:= */ False)
```
````

````

### Scenario: Debugging an Error
#### Request (InlineValueRequest)
```json
{
  "file_path": "src/logic.py",
  "range": { "start": {"line": 10, ...}, "end": {"line": 20, ...} }
}
````

#### Markdown Rendered for LLM

````markdown
### Code with Annotations: `src/logic.py`

```python
def process(items):
    for i in items:
        # The value is injected at the end of the line
        total += i.price  // value: i.price = None
        # Agent can now see that i.price is None, causing the crash!
```
````

```

```
