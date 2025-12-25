# Diagnostics API

The Diagnostics API reports syntax errors, type mismatches, and other linting issues found in a specific file.

## FileDiagnosticsRequest

| Field          | Type                                       | Default  | Description                              |
| :------------- | :----------------------------------------- | :------- | :--------------------------------------- |
| `file_path`    | `string`                                   | Required | Relative path to the file.               |
| `min_severity` | `"Error" \| "Warning" \| "Info" \| "Hint"` | `"Hint"` | Minimum severity to report.              |
| `limit`        | `number \| null`                           | `null`   | Maximum number of diagnostics to return. |
| `offset`       | `number`                                   | `0`      | Pagination offset.                       |

## FileDiagnosticsResponse

| Field         | Type           | Description                                         |
| :------------ | :------------- | :-------------------------------------------------- |
| `diagnostics` | `Diagnostic[]` | List of issues found.                               |
| `has_more`    | `boolean`      | Whether more issues exist beyond the current limit. |

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
