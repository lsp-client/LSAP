# Completion API

The Completion API (IntelliSense) provides context-aware code suggestions at a specific position. For an Agent, this is primarily an **exploration and discovery tool** to find available methods or properties in a private or unfamiliar codebase.

## CompletionRequest

| Field           | Type                      | Default  | Description                                 |
| :-------------- | :------------------------ | :------- | :------------------------------------------ |
| `locate`        | [`Locate`](locate.md)     | Required | Where to trigger the completion.            |
| `max_items`     | `number \| null`          | `15`     | Maximum number of suggestions to return.    |
| `start_index`   | `number`                  | `0`      | Number of items to skip.                    |
| `pagination_id` | `string \| null`          | `null`   | Token to retrieve the next page of results. |

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
| `insert_text`   | `string?` | The actual snippet that would be inserted.|

## Example Usage

### Scenario 1: Discovering methods on an object after dot

#### Request

```json
{
  "locate": {
    "file_path": "src/main.py",
    "find": "client."
  },
  "max_items": 5
}
```

#### Markdown Rendered for LLM

```markdown
# Code Completion

## Top Suggestion Detail: `connect`
Establishes a connection to the server using the configured credentials. Returns true if successful.



| Symbol | Kind | Detail |
| :--- | :--- | :--- |
| `connect` | Method | (timeout: int = 30) -> bool |
| `send_json` | Method | (data: dict, retry: int = 3) -> None |
| `is_active` | Property | bool |
| `disconnect` | Method | () -> None |
| `get_status` | Method | () -> dict |

---
> [!TIP]
> More results available. Use `start_index` to fetch more.

---
> [!TIP]
> Use these symbols to construct your next code edit. You can focus on a specific method to get more details.
```

### Scenario 2: Getting completions with more items and pagination

#### Request

```json
{
  "locate": {
    "file_path": "src/api.py",
    "find": "response."
  },
  "max_items": 10,
  "start_index": 0
}
```

#### Markdown Rendered for LLM

```markdown
# Code Completion

## Top Suggestion Detail: `json`
Returns the response body parsed as JSON. Raises JSONDecodeError if invalid.



| Symbol | Kind | Detail |
| :--- | :--- | :--- |
| `json` | Method | () -> dict |
| `text` | Property | str |
| `status_code` | Property | int |
| `headers` | Property | dict |
| `cookies` | Property | dict |
| `raise_for_status` | Method | () -> None |
| `content` | Property | bytes |
| `iter_content` | Method | (chunk_size: int = None) -> iterator |
| `close` | Method | () -> None |
| `is_redirect` | Property | bool |

---
> [!TIP]
> Use `pagination_id="abc123"` to fetch more suggestions.

---
> [!TIP]
> Use these symbols to construct your next code edit. You can focus on a specific method to get more details.
```

### Scenario 3: No completion suggestions available

#### Request

```json
{
  "locate": {
    "file_path": "src/main.py",
    "find": "unknown_var."
  }
}
```

#### Markdown Rendered for LLM

```markdown
# Code Completion

No completion suggestions found.
```
