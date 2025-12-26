# Diagnostics API

The Diagnostics API reports syntax errors, type mismatches, and other linting issues found in a specific file.

## FileDiagnosticsRequest

| Field          | Type                                         | Default  | Description                              |
| :------------- | :------------------------------------------- | :------- | :--------------------------------------- |
| `file_path`    | `string`                                     | Required | Relative path to the file.               |
| `min_severity` | `"Error" \| "Warning" \| "Information" \| "Hint"` | `"Hint"` | Minimum severity to report.              |
| `max_items`    | `number \| null`                             | `null`   | Maximum number of diagnostics to return. |
| `start_index`  | `number`                                     | `0`      | Pagination offset.                       |
| `pagination_id`| `string \| null`                             | `null`   | Token for retrieving next page.          |

## FileDiagnosticsResponse

Inherits from `PaginatedResponse`.

| Field         | Type           | Description                                         |
| :------------ | :------------- | :-------------------------------------------------- |
| `file_path`   | `string`       | The file being inspected.                           |
| `diagnostics` | `Diagnostic[]` | List of issues found.                               |
| `start_index` | `number`       | Offset of the current page.                         |
| `max_items`   | `number?`      | Number of items per page (if specified).            |
| `total`       | `number?`      | Total number of diagnostics (if available).         |
| `has_more`    | `boolean`      | Whether more issues exist beyond the current limit. |
| `pagination_id`| `string?`     | Token for retrieving the next page.                 |

## Example Usage

### Request

```json
{
  "file_path": "src/buggy.py",
  "min_severity": "Warning"
}
```

### Markdown Rendered for LLM

```markdown
### Diagnostics for `src/buggy.py`

Total issues: 2 | Showing: 2

- Error: Undefined variable 'x' (at line 10, col 5)
- Warning: Unused import 'sys' (at line 2, col 1)
```
