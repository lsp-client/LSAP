# Rename API (Refactoring)

The Rename API provides a **safe, two-phase** workspace-wide symbol renaming capability. It automates the task of updating all references to a symbol (variable, function, class, etc.) across multiple files.

## Design Philosophy

This API is designed with **security**, **agent-friendliness**, and **minimal context usage** in mind:

1. **Two-Phase Operation**: Preview first (default), then execute explicitly
2. **Minimal Context by Default**: Returns compact summaries, detailed diffs only on request
3. **Scope Control**: Can limit changes to specific files/directories
4. **Clear State Communication**: Response clearly indicates if changes were made or not

## RenameRequest

| Field          | Type                  | Default     | Description                                                              |
| :------------- | :-------------------- | :---------- | :----------------------------------------------------------------------- |
| `locate`       | [`Locate`](locate.md) | Required    | The location of the symbol to rename.                                    |
| `new_name`     | `string`              | Required    | The target name for the symbol.                                          |
| `mode`         | `"preview" \| "execute"` | `"preview"` | Operation mode: preview (safe, no changes) or execute (applies changes). |
| `show_diffs`   | `boolean`             | `false`     | Include detailed line-by-line diffs (increases context usage).           |
| `scope_filter` | `Path[]?`             | `null`      | Optional: Limit rename to specific files/directories.                    |
| `max_files`    | `number?`             | `null`      | Optional: Maximum number of files to show in preview.                    |

## RenameResponse

| Field               | Type                 | Description                                                        |
| :------------------ | :------------------- | :----------------------------------------------------------------- |
| `old_name`          | `string`             | The original symbol name that was (or will be) renamed.            |
| `new_name`          | `string`             | The new symbol name.                                               |
| `status`            | `"preview" \| "completed"` | Operation status: 'preview' (no changes) or 'completed' (applied). |
| `scope_description` | `string`             | Human-readable description of the rename scope.                    |
| `total_files`       | `number`             | Total number of files that contain the symbol.                     |
| `total_occurrences` | `number`             | Total number of times the symbol appears across all files.         |
| `changes`           | `RenameFileChange[]` | Per-file change details (may be truncated based on max_files).     |
| `has_more_files`    | `boolean`            | True if the changes list was truncated due to max_files limit.     |

### RenameFileChange

| Field         | Type           | Description                                                          |
| :------------ | :------------- | :------------------------------------------------------------------- |
| `file_path`   | `Path`         | File path affected by the rename.                                    |
| `occurrences` | `number`       | Number of occurrences in this file.                                  |
| `diffs`       | `RenameDiff[]` | Detailed line-by-line diffs (only included if show_diffs=true). |

### RenameDiff

| Field      | Type     | Description                                    |
| :--------- | :------- | :--------------------------------------------- |
| `line`     | `number` | Line number (1-based) where the change occurs. |
| `original` | `string` | The text before the rename.                    |
| `modified` | `string` | The text after the rename.                     |

## Example Usage

### Workflow: Safe Two-Phase Rename

The recommended workflow is to **preview first**, verify the changes, then **execute**:

1. **Step 1: Preview** - Send a request with `mode: "preview"` (default)
2. **Step 2: Verify** - Agent reviews the summary
3. **Step 3: Execute** - Send the same request with `mode: "execute"`

### Scenario 1: Minimal Context Rename (Recommended for Agents)

Rename a method with minimal token usage - get a compact summary without detailed diffs.

#### Request (Preview with Minimal Context)

```json
{
  "locate": {
    "file_path": "src/client.py",
    "scope": {
      "symbol_path": ["APIClient", "fetch_data"]
    }
  },
  "new_name": "get_resource",
  "mode": "preview"
}
```

#### Response (Compact Summary)

```markdown
# Rename Preview: `fetch_data` → `get_resource`

**Status**: preview
**Scope**: Workspace-wide

## Summary
- **Files affected**: 2
- **Total occurrences**: 3

## Affected Files
- `src/client.py`: 1 occurrence(s)
- `src/main.py`: 2 occurrence(s)

---
> [!NOTE]
> This is a **preview only** - no changes have been made.
> To apply these changes, send the same request with `mode: "execute"`.
```

#### Request (Execute After Verification)

```json
{
  "locate": {
    "file_path": "src/client.py",
    "scope": {
      "symbol_path": ["APIClient", "fetch_data"]
    }
  },
  "new_name": "get_resource",
  "mode": "execute"
}
```

#### Response (Execution Confirmation)

```markdown
# Rename Preview: `fetch_data` → `get_resource`

**Status**: completed
**Scope**: Workspace-wide

## Summary
- **Files affected**: 2
- **Total occurrences**: 3

## Affected Files
- `src/client.py`: 1 occurrence(s)
- `src/main.py`: 2 occurrence(s)

---
> [!SUCCESS]
> Rename operation completed successfully.
> 3 occurrence(s) renamed across 2 file(s).
```

### Scenario 2: Preview with Detailed Diffs

When the agent needs to see exactly what will change, use `show_diffs: true`.

#### Request

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "find": "temp"
  },
  "new_name": "buffer",
  "mode": "preview",
  "show_diffs": true
}
```

#### Response

```markdown
# Rename Preview: `temp` → `buffer`

**Status**: preview
**Scope**: Workspace-wide

## Summary
- **Files affected**: 1
- **Total occurrences**: 5

## Affected Files
- `src/utils.py`: 5 occurrence(s)

## Detailed Changes

### `src/utils.py`
- Line 15:
  - `temp = []`
  + `buffer = []`
- Line 18:
  - `temp.append(item)`
  + `buffer.append(item)`
- Line 20:
  - `return temp`
  + `return buffer`
- Line 25:
  - `temp.clear()`
  + `buffer.clear()`
- Line 28:
  - `for item in temp:`
  + `for item in buffer:`

---
> [!NOTE]
> This is a **preview only** - no changes have been made.
> To apply these changes, send the same request with `mode: "execute"`.
```

### Scenario 3: Scoped Rename (Limit to Specific Files)

Rename only within a specific directory or file set for more control.

#### Request

```json
{
  "locate": {
    "file_path": "src/models.py",
    "scope": {
      "symbol_path": ["UserAccount"]
    }
  },
  "new_name": "UserProfile",
  "scope_filter": ["src/models.py", "src/auth.py"],
  "mode": "preview"
}
```

#### Response

```markdown
# Rename Preview: `UserAccount` → `UserProfile`

**Status**: preview
**Scope**: Limited to 2 file(s)/directory(ies)

## Summary
- **Files affected**: 2
- **Total occurrences**: 3

## Affected Files
- `src/models.py`: 1 occurrence(s)
- `src/auth.py`: 2 occurrence(s)

---
> [!NOTE]
> This is a **preview only** - no changes have been made.
> To apply these changes, send the same request with `mode: "execute"`.
```

### Scenario 4: Large Rename with Truncation

For very large renames, limit the preview to avoid excessive context usage.

#### Request

```json
{
  "locate": {
    "file_path": "src/models.py",
    "scope": {
      "symbol_path": ["User"]
    }
  },
  "new_name": "Account",
  "mode": "preview",
  "max_files": 5
}
```

#### Response

```markdown
# Rename Preview: `User` → `Account`

**Status**: preview
**Scope**: Workspace-wide

## Summary
- **Files affected**: 25 (showing 5/25)
- **Total occurrences**: 128

## Affected Files
- `src/models.py`: 15 occurrence(s)
- `src/auth.py`: 12 occurrence(s)
- `src/views.py`: 8 occurrence(s)
- `src/api.py`: 7 occurrence(s)
- `tests/test_models.py`: 6 occurrence(s)
- ... and 20 more file(s)

---
> [!NOTE]
> This is a **preview only** - no changes have been made.
> To apply these changes, send the same request with `mode: "execute"`.
```

## Security Features

1. **Preview by Default**: The `mode` parameter defaults to `"preview"`, ensuring agents must explicitly request execution
2. **Clear Status Communication**: Responses clearly indicate whether changes were made via the `status` field
3. **Scope Control**: The `scope_filter` allows limiting changes to specific files/directories
4. **Verification Support**: Compact summaries enable quick verification without excessive token usage
5. **Explicit Execution**: Changes only occur when `mode: "execute"` is explicitly set

## Best Practices for Agents

1. **Always Preview First**: Start with `mode: "preview"` to understand the impact
2. **Use Minimal Context**: Avoid `show_diffs: true` unless necessary to reduce token usage
3. **Limit Scope When Possible**: Use `scope_filter` for targeted renames
4. **Truncate Large Results**: Use `max_files` for very large rename operations
5. **Verify Before Execute**: Review the summary before sending `mode: "execute"`
