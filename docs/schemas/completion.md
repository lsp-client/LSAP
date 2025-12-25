# Completion API

The Completion API (IntelliSense) provides context-aware code suggestions at a specific position. For an Agent, this is primarily an **exploration and discovery tool** to find available methods or properties in a private or unfamiliar codebase.

## CompletionRequest

Inherits from `LocateRequest`.

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `locate` | `LocateText \| LocateSymbol` | Required | Where to trigger the completion. |
| `limit` | `number` | `15` | Maximum number of suggestions to return to avoid token bloat. |

> [!TIP]
> To trigger completion after a dot (e.g., `user.`), use `LocateText` with `find="user."` and `position="end"`.

## CompletionResponse

| Field | Type | Description |
| :--- | :--- | :--- |
| `items` | `CompletionItem[]` | List of suggestions sorted by relevance. |

### CompletionItem

| Field | Type | Description |
| :--- | :--- | :--- |
| `label` | `string` | The suggestion name (e.g., `get_data`). |
| `kind` | `string` | Type (Method, Property, Class, etc.). |
| `detail` | `string?` | Short info like signature or type. |
| `documentation` | `string?` | Full markdown documentation for the item. |

## Example Usage

### Scenario: Discovering methods on an object
#### Request
```json
{
  "locate": {
    "file_path": "src/main.py",
    "line": 15,
    "find": "client.",
    "position": "end"
  },
  "limit": 5
}
```

#### Markdown Rendered for LLM
```markdown
### Code Completion at the requested location

| Symbol | Kind | Detail |
| :--- | :--- | :--- |
| `connect` | Method | (timeout: int) -> bool |
| `send_json` | Method | (data: dict) -> None |
| `is_active` | Property | bool |

#### Top Suggestion Detail: `connect`
Establishes a connection to the server...
```
