# Diagnostics API

The Diagnostics API reports syntax errors, type mismatches, and other linting issues found in a specific file.

## FileDiagnosticsRequest

| Field           | Type                                              | Default  | Description                              |
| :-------------- | :------------------------------------------------ | :------- | :--------------------------------------- |
| `file_path`     | `string`                                          | Required | Relative path to the file.               |
| `min_severity`  | `"Error"` \| `"Warning"` \| `"Information"` \| `"Hint"` | `"Hint"` | Minimum severity to report.              |
| `max_items`     | `number \| null`                                  | `null`   | Maximum number of diagnostics to return. |
| `start_index`   | `number`                                          | `0`      | Pagination offset.                       |
| `pagination_id` | `string \| null`                                  | `null`   | Token for retrieving next page.          |

## FileDiagnosticsResponse

| Field           | Type           | Description                                         |
| :-------------- | :------------- | :-------------------------------------------------- |
| `file_path`     | `string`       | The file being inspected.                           |
| `diagnostics`   | `Diagnostic[]` | List of issues found.                               |
| `start_index`   | `number`       | Offset of the current page.                         |
| `max_items`     | `number?`      | Number of items per page (if specified).            |
| `total`         | `number?`      | Total number of diagnostics (if available).         |
| `has_more`      | `boolean`      | Whether more issues exist beyond the current limit. |
| `pagination_id` | `string?`      | Token for retrieving the next page.                 |

### Diagnostic

| Field     | Type                                | Description                        |
| :-------- | :---------------------------------- | :--------------------------------- |
| `range`   | `Range`                             | The range of the diagnostic.       |
| `severity`| `"Error"` \| `"Warning"` \| `"Information"` \| `"Hint"` | Severity level. |
| `message` | `string`                            | The diagnostic message.            |
| `source`  | `string \| null`                    | The source of the diagnostic.      |
| `code`    | `string \| int \| null`             | The diagnostic code.               |

## WorkspaceDiagnosticsRequest

| Field           | Type                                              | Default  | Description                              |
| :-------------- | :------------------------------------------------ | :------- | :--------------------------------------- |
| `min_severity`  | `"Error"` \| `"Warning"` \| `"Information"` \| `"Hint"` | `"Hint"` | Minimum severity to report.              |
| `max_items`     | `number \| null`                                  | `null`   | Maximum number of diagnostics to return. |
| `start_index`   | `number`                                          | `0`      | Pagination offset.                       |
| `pagination_id` | `string \| null`                                  | `null`   | Token for retrieving next page.          |

## WorkspaceDiagnosticsResponse

| Field           | Type                        | Description                                         |
| :-------------- | :-------------------------- | :-------------------------------------------------- |
| `items`         | `WorkspaceDiagnosticItem[]` | List of issues found across the workspace.          |
| `start_index`   | `number`                    | Offset of the current page.                         |
| `max_items`     | `number?`                   | Number of items per page (if specified).            |
| `total`         | `number?`                   | Total number of diagnostics (if available).         |
| `has_more`      | `boolean`                   | Whether more issues exist beyond the current limit. |
| `pagination_id` | `string?`                   | Token for retrieving the next page.                 |

### WorkspaceDiagnosticItem

| Field     | Type     | Description                        |
| :-------- | :------- | :--------------------------------- |
| `range`   | `Range`  | The range of the diagnostic.       |
| `severity`| `string` | Severity level.                    |
| `message` | `string` | The diagnostic message.            |
| `source`  | `string \| null` | The source of the diagnostic.  |
| `code`    | `string \| int \| null` | The diagnostic code. |
| `file_path`| `string`| The file containing the diagnostic.|

## Example Usage

### Scenario 1: Getting all diagnostics for a file

#### Request

```json
{
  "file_path": "src/buggy.py",
  "min_severity": "Hint"
}
```

#### Markdown Rendered for LLM

```markdown
# Diagnostics for `src/buggy.py`
Total issues: 5 | Showing: 5

| Line:Col | Severity | Message |
| :--- | :--- | :--- |
| 10:5 | Error | Undefined variable 'x' |
| 15:3 | Warning | Unused import 'sys' |
| 20:1 | Information | Function 'unused_func' is never called |
| 25:10 | Hint | Consider using f-string instead of % formatting |
```

### Scenario 2: Getting only errors and warnings

#### Request

```json
{
  "file_path": "src/buggy.py",
  "min_severity": "Warning",
  "max_items": 10
}
```

#### Markdown Rendered for LLM

```markdown
# Diagnostics for `src/buggy.py`
Total issues: 2 | Showing: 2 (Offset: 0, Limit: 10)

| Line:Col | Severity | Message |
| :--- | :--- | :--- |
| 10:5 | Error | Undefined variable 'x' |
| 15:3 | Warning | Unused import 'sys' |
```

### Scenario 3: Paginated diagnostics for large files

#### Request

```json
{
  "file_path": "src/large_file.py",
  "min_severity": "Information",
  "max_items": 5,
  "start_index": 0
}
```

#### Markdown Rendered for LLM

```markdown
# Diagnostics for `src/large_file.py`
Total issues: 23 | Showing: 5 (Offset: 0, Limit: 5)

| Line:Col | Severity | Message |
| :--- | :--- | :--- |
| 5:1 | Warning | Variable 'temp' shadows built-in |
| 12:8 | Information | Variable 'counter' could be const |
| 18:15 | Information | Consider using enumerate() |
| 25:3 | Warning | Unused variable 'unused' |
| 32:1 | Hint | Missing type annotation for 'process' |

---

> [!TIP]
> More issues available.
> To see the rest, specify a `max_items` and use: `start_index=5`
```

### Scenario 4: Getting workspace-wide diagnostics

#### Request

```json
{
  "min_severity": "Error",
  "max_items": 10
}
```

#### Markdown Rendered for LLM

```markdown
# Workspace Diagnostics
Total issues: 15 | Showing: 10 (Offset: 0, Limit: 10)

| File | Line:Col | Severity | Message |
| :--- | :--- | :--- | :--- |
| `src/auth.py` | 10:5 | Error | Undefined variable 'auth_token' |
| `src/db.py` | 25:12 | Error | Type mismatch: expected str, got int |
| `src/utils.py` | 42:1 | Error | Missing function documentation |

---

> [!TIP]
> More issues available.
> To see the rest, specify a `max_items` and use: `start_index=10`
```
