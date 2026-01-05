# Rename API (Refactoring)

The Rename API provides a workspace-wide symbol renaming preview capability. It returns a preview of all changes that would be made by renaming a symbol (variable, function, class, etc.) across multiple files.

## Design Philosophy

This API is designed with **agent-friendliness** and **minimal context usage** in mind:

1. **Preview-Only**: Returns a preview of changes; actual execution is handled by the client (editor/IDE)
2. **Minimal Context by Default**: Returns compact summaries, detailed diffs only on request
3. **Workspace-Wide**: LSP rename is always workspace-wide, covering all references
4. **Agent-Optimized Output**: Structured format optimized for LLM understanding

## RenameRequest

| Field           | Type                  | Default | Description                                                    |
| :-------------- | :-------------------- | :------ | :------------------------------------------------------------- |
| `locate`        | [`Locate`](locate.md) | Required | The location of the symbol to rename.                          |
| `new_name`      | `string`              | Required | The target name for the symbol.                                |
| `show_diffs`    | `boolean`             | `false` | Include detailed line-by-line diffs (increases context usage). |
| `max_items`     | `number?`             | `100`   | Maximum number of files to show in preview.                    |
| `start_index`   | `number`              | `0`     | Number of files to skip.                                       |
| `pagination_id` | `string?`             | `null`  | Token to retrieve the next page of results.                    |

## RenameResponse

| Field               | Type                 | Description                                                     |
| :------------------ | :------------------- | :-------------------------------------------------------------- |
| `old_name`          | `string`             | The original symbol name.                                       |
| `new_name`          | `string`             | The new symbol name.                                            |
| `total`             | `number`             | Total number of files that contain the symbol.                  |
| `start_index`       | `number`             | Number of files skipped.                                        |
| `has_more`          | `boolean`            | True if more files are available.                               |
| `total_occurrences` | `number`             | Total number of times the symbol appears across all files.      |
| `changes`           | `RenameFileChange[]` | Per-file change details (may be truncated based on `max_items`). |
| `pagination_id`     | `string?`            | Token for next page.                                            |

### RenameFileChange

| Field         | Type           | Description                                                     |
| :------------ | :------------- | :-------------------------------------------------------------- |
| `file_path`   | `Path`         | File path affected by the rename.                               |
| `occurrences` | `number`       | Number of occurrences in this file.                             |
| `diffs`       | `RenameDiff[]` | Detailed line-by-line diffs (only included if show_diffs=true). |

### RenameDiff

| Field      | Type     | Description                                    |
| :--------- | :------- | :--------------------------------------------- |
| `line`     | `number` | Line number (1-based) where the change occurs. |
| `original` | `string` | The text before the rename.                    |
| `modified` | `string` | The text after the rename.                     |

## Example Usage

### Scenario 1: Minimal Context Rename (Recommended for Agents)

Get a compact summary of rename impact without detailed diffs to minimize token usage.

#### Request

```json
{
  "locate": {
    "file_path": "src/client.py",
    "scope": {
      "symbol_path": ["APIClient", "fetch_data"]
    }
  },
  "new_name": "get_resource"
}
```

#### Response (Compact Summary)

```markdown
# Rename Preview: `fetch_data` → `get_resource`

## Summary
- **Files affected**: 2
- **Total occurrences**: 3

## Affected Files
- `src/client.py`: 1 occurrence(s)
- `src/main.py`: 2 occurrence(s)

---
> [!NOTE]
> This is a preview of changes. The actual rename operation will be executed by your editor/IDE.
> Review the changes above before applying them.
```

### Scenario 2: Detailed Preview with Diffs

When you need to see exactly what will change, use `show_diffs: true`.

#### Request

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "find": "temp"
  },
  "new_name": "buffer",
  "show_diffs": true
}
```

#### Response

```markdown
# Rename Preview: `temp` → `buffer`

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
> This is a preview of changes. The actual rename operation will be executed by your editor/IDE.
> Review the changes above before applying them.
```

### Scenario 3: Large Rename with Pagination

For very large renames, use pagination to review the impact in chunks.

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
  "max_items": 5
}
```

#### Response

```markdown
# Rename Preview: `User` → `Account`

## Summary
- **Files affected**: 25 (showing 5/25)
- **Total occurrences**: 128

## Affected Files
- `src/models.py`: 15 occurrence(s)
- `src/auth.py`: 12 occurrence(s)
- `src/views.py`: 8 occurrence(s)
- `src/api.py`: 7 occurrence(s)
- `tests/test_models.py`: 6 occurrence(s)
- ... and more file(s) available.

---
> [!TIP]
> More changes available. To see more, use: `start_index=5`

---
> [!NOTE]
> This is a preview of changes. The actual rename operation will be executed by your editor/IDE.
> Review the changes above before applying them.
```

## Implementation Notes

### LSP Integration

This API is built on top of LSP's `textDocument/rename` capability:

1. The request is translated to LSP `RenameParams` with the located position and new name
2. LSP returns a `WorkspaceEdit` containing all affected files and their text edits
3. LSAP transforms this into an agent-friendly format with summaries and optional diffs
4. The client (editor/IDE) is responsible for applying the actual changes

### Workspace-Wide Behavior

LSP rename is always workspace-wide by design. It will find and include **all** references to the symbol across **all** files in the workspace. There is no way to limit the scope through the LSP protocol.

### Preview Generation

The preview is generated from the LSP `WorkspaceEdit`:
- The `WorkspaceEdit` contains all text edits across all affected files
- By default (`show_diffs: false`), only file paths and occurrence counts are extracted
- With `show_diffs: true`, detailed line-by-line diffs are generated from the text edits
- The `max_items` and `start_index` parameters control pagination of the file list

**Note**: The same `WorkspaceEdit` can be used by the client to apply the changes. LSAP's role is to transform it into an agent-readable preview format.

## Best Practices for Agents

1. **Start with Compact Mode**: Use default settings (no `show_diffs`) to get a quick overview
2. **Verify Impact**: Review the file list and occurrence count before applying
3. **Use Diffs for Complex Cases**: Enable `show_diffs: true` only when you need to verify specific changes
4. **Handle Large Renames**: Use `max_files` to get a representative sample for very large refactorings
5. **Let the Client Execute**: Remember that LSAP only provides the preview; the client handles execution
