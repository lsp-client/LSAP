# Rename API

The Rename API provides the ability to rename a symbol throughout the entire workspace, with support for preview and execute modes.

## RenameRequest

| Field           | Type                     | Default     | Description                                                        |
| :-------------- | :----------------------- | :---------- | :----------------------------------------------------------------- |
| `locate`        | [`Locate`](locate.md)    | Required    | The symbol to rename.                                              |
| `new_name`      | `string`                 | Required    | The new name for the symbol.                                       |
| `mode`          | `"preview" \| "execute"` | `"preview"` | Whether to preview changes or execute them.                        |
| `rename_id`     | `string \| null`         | `null`      | ID from a previous preview (execute mode only).                    |
| `exclude_files` | `string[]`               | `[]`        | File paths or glob patterns to exclude from rename (execute mode). |

## RenameResponse

| Field               | Type                 | Description                                      |
| :------------------ | :------------------- | :----------------------------------------------- |
| `request`           | `RenameRequest`      | The original request.                            |
| `old_name`          | `string`             | The original symbol name.                        |
| `new_name`          | `string`             | The new symbol name.                             |
| `total_files`       | `number`             | Total number of files affected.                  |
| `total_occurrences` | `number`             | Total number of occurrences to rename.           |
| `changes`           | `RenameFileChange[]` | List of changes per file.                        |
| `rename_id`         | `string?`            | Unique ID for this preview (preview mode only).  |
| `applied`           | `boolean`            | `false` in preview mode, `true` in execute mode. |

### RenameFileChange

| Field       | Type           | Description                              |
| :---------- | :------------- | :--------------------------------------- |
| `file_path` | `string`       | Path to the affected file.               |
| `diffs`     | `RenameDiff[]` | List of line-level changes in this file. |

### RenameDiff

| Field      | Type     | Description                              |
| :--------- | :------- | :--------------------------------------- |
| `line`     | `number` | 1-based line number.                     |
| `original` | `string` | The original line content before rename. |
| `modified` | `string` | The modified line content after rename.  |

## Example Usage

### Scenario 1: Preview a rename operation

#### Request

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "scope": {
      "symbol_path": ["format_date"]
    }
  },
  "new_name": "format_datetime",
  "mode": "preview"
}
```

#### Markdown Rendered for LLM

````markdown
# Rename Preview: `format_date` → `format_datetime`

**ID**: `rename_abc123`
**Summary**: Affects 3 files and 8 occurrences.

## `src/utils.py`

Line 15:
```diff
- def format_date(dt: datetime) -> str:
+ def format_datetime(dt: datetime) -> str:
```

## `src/api/views.py`

Line 42:
```diff
- return {"date": format_date(obj.created_at)}
+ return {"date": format_datetime(obj.created_at)}
```

---

> [!TIP]
> To apply this rename, use `mode="execute"` with `rename_id="rename_abc123"`.
> To exclude files, add `exclude_files=["path/to/exclude.py"]` or use glob patterns like `exclude_files=["tests/*", "tests/**/*", "**/*_test.py"]`.
````

### Scenario 2: Execute a rename with glob pattern exclusions

#### Request

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "scope": {
      "symbol_path": ["format_date"]
    }
  },
  "new_name": "format_datetime",
  "mode": "execute",
  "rename_id": "rename_abc123",
  "exclude_files": ["tests/*", "tests/**/*"]
}
```

#### Markdown Rendered for LLM

````markdown
# Rename Applied: `format_date` → `format_datetime`

**Summary**: Modified 2 files with 6 occurrences.

## `src/utils.py`

Line 15:
```diff
- def format_date(dt: datetime) -> str:
+ def format_datetime(dt: datetime) -> str:
```

## `src/api/views.py`

Line 42:
```diff
- return {"date": format_date(obj.created_at)}
+ return {"date": format_datetime(obj.created_at)}
```

---

> [!NOTE]
> Rename completed successfully. Excluded files: `tests/*`, `tests/**/*`
>
> [!IMPORTANT]
> You must manually rename the symbol in the excluded files to maintain consistency.
````

## Glob Pattern Support

The `exclude_files` parameter supports glob patterns for flexible file exclusion:

- **Exact paths**: `"src/main.py"`, `"tests/test_utils.py"`
- **Filename patterns**: `"*.md"`, `"test_*.py"` (matches files by name in any directory)
- **Directory patterns**: `"tests/*"` (direct children), `"tests/**/*"` (all descendants)
- **Combined patterns**: Use multiple patterns for complex exclusions

### Pattern Examples

| Pattern           | Matches                                                |
| :---------------- | :----------------------------------------------------- |
| `"*.md"`          | All Markdown files (by filename)                       |
| `"test_*.py"`     | All files starting with `test_` (by filename)          |
| `"tests/*"`       | Direct children of `tests/` directory                  |
| `"tests/**/*"`    | All files in `tests/` and subdirectories               |
| `"docs/*.py"`     | Python files directly in `docs/` directory             |
| `"**/test_*.py"`  | All test files matching pattern in any directory       |

### Important Notes

- Patterns are matched against relative paths from the workspace root
- Use forward slashes `/` for path separators (automatically normalized)
- `**` matches zero or more directory levels
- Absolute paths and paths with `..` are rejected for security
- Multiple patterns can be combined: `["tests/*", "tests/**/*", "*.md"]`
