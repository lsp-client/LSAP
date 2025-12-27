# Completion API

The Completion API (IntelliSense) provides context-aware code suggestions at a specific position. For an Agent, this is primarily an **exploration and discovery tool** to find available methods or properties in a private or unfamiliar codebase.

## CompletionRequest

| Field           | Type                                                     | Default  | Description                                 |
| :-------------- | :------------------------------------------------------- | :------- | :------------------------------------------ |
| `locate`        | [`LocateText`](locate.md) \| [`LocateSymbol`](locate.md) | Required | Where to trigger the completion.            |
| `max_items`     | `number \| null`                                         | `15`     | Maximum number of suggestions to return.    |
| `start_index`   | `number`                                                 | `0`      | Number of items to skip.                    |
| `pagination_id` | `string \| null`                                         | `null`   | Token to retrieve the next page of results. |

> [!TIP]
> To trigger completion after a dot (e.g., `user.`), use [`LocateText`](locate.md) with `find="user."` and `find_end="end"`.

## CompletionResponse

| Field           | Type               | Description                                 |
| :-------------- | :----------------- | :------------------------------------------ |
| `items`         | `CompletionItem[]` | List of suggestions sorted by relevance.    |
| `start_index`   | `number`           | Offset of the current page.                 |
| `max_items`     | `number?`          | Number of items per page (if specified).    |
| `total`         | `number?`          | Total number of suggestions (if available). |
| `has_more`      | `boolean`          | Whether more results are available.         |
| `pagination_id` | `string?`          | Token for retrieving the next page.         |

### CompletionItem

| Field           | Type      | Description                               |
| :-------------- | :-------- | :---------------------------------------- |
| `label`         | `string`  | The suggestion name (e.g., `get_data`).   |
| `kind`          | `string`  | Type (Method, Property, Class, etc.).     |
| `detail`        | `string?` | Short info like signature or type.        |
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
    "find_end": "end"
  },
  "max_items": 5
}
```

#### Markdown Rendered for LLM

```markdown
# Code Completion at the requested location

| Symbol      | Kind     | Detail                 |
| :---------- | :------- | :--------------------- |
| `connect`   | Method   | (timeout: int) -> bool |
| `send_json` | Method   | (data: dict) -> None   |
| `is_active` | Property | bool                   |

## Top Suggestion Detail: `connect`

Establishes a connection to the server...

---

> [!TIP]
> Use these symbols to construct your next code edit. You can focus on a specific method to get more details.
```
