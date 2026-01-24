# Rename API

The Rename API provides the ability to rename a symbol throughout the entire workspace,
with support for preview and execute modes.

## Example Usage

### Scenario 1: Preview a rename operation

Request:

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

### Scenario 2: Execute a rename with glob pattern exclusions

Request:

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

## Glob Pattern Support

The `exclude_files` parameter supports glob patterns for flexible file exclusion:

- **Exact paths**: `"src/main.py"`, `"tests/test_utils.py"`
- **Filename patterns**: `"*.md"`, `"test_*.py"` (matches files by name in any directory)
- **Directory patterns**: `"tests/*"` (direct children), `"tests/**/*"` (all descendants)
- **Combined patterns**: Use multiple patterns for complex exclusions

### Pattern Examples

| Pattern | Matches |
| :--- | :--- |
| `"*.md"` | All Markdown files (by filename) |
| `"test_*.py"` | All files starting with test_ (by filename) |
| `"tests/*"` | Direct children of tests/ directory |
| `"tests/**/*"` | All files in tests/ and subdirectories |
| `"docs/*.py"` | Python files directly in docs/ directory |
| `"**/test_*.py"` | All test files matching pattern in any directory |

## Important Notes

- Patterns are matched against relative paths from the workspace root
- Use forward slashes `/` for path separators (automatically normalized)
- `**` matches zero or more directory levels
- Absolute paths and paths with `..` are rejected for security
- Multiple patterns can be combined: `["tests/*", "tests/**/*", "*.md"]`

## References

- [RenameDiff.json](./RenameDiff.json)
- [RenameExecuteRequest.json](./RenameExecuteRequest.json)
- [RenameExecuteResponse.json](./RenameExecuteResponse.json)
- [RenameFileChange.json](./RenameFileChange.json)
- [RenamePreviewRequest.json](./RenamePreviewRequest.json)
- [RenamePreviewResponse.json](./RenamePreviewResponse.json)
