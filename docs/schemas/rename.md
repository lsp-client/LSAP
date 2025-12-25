# Rename API (Refactoring)

The Rename API provides a safe, workspace-wide symbol renaming capability. It automates the task of updating all references to a symbol (variable, function, class, etc.) across multiple files.

## RenameRequest

Inherits from `LocateRequest`.

| Field      | Type                         | Default  | Description                           |
| :--------- | :--------------------------- | :------- | :------------------------------------ |
| `locate`   | `LocateText \| LocateSymbol` | Required | The location of the symbol to rename. |
| `new_name` | `string`                     | Required | The target name for the symbol.       |

## RenameResponse

LSAP focuses on providing a **Preview** of the changes to help the Agent verify the operation before continuing.

| Field               | Type                 | Description                          |
| :------------------ | :------------------- | :----------------------------------- |
| `old_name`          | `string`             | The original name of the symbol.     |
| `new_name`          | `string`             | The requested new name.              |
| `total_files`       | `number`             | Count of unique files affected.      |
| `total_occurrences` | `number`             | Total number of code points changed. |
| `changes`           | `RenameFileChange[]` | Detailed diffs for each file.        |

### RenameFileChange

Contains `file_path` and a list of `RenameDiff` objects (line number, original text, modified text).

## Example Usage

### Scenario: Renaming a method used across the project

#### Request

```json
{
  "locate": {
    "file_path": "src/client.py",
    "symbol_path": ["APIClient", "fetch_data"]
  },
  "new_name": "get_resource"
}
```

#### Markdown Rendered for LLM

```markdown
### Rename Preview: `fetch_data` -> `get_resource`

**Summary**: Affects 2 files and 3 occurrences.

#### File: `src/client.py`

- Line 10:
  - `def fetch_data(self, id):`
  * `def get_resource(self, id):`

#### File: `src/main.py`

- Line 42:
  - `data = client.fetch_data(1)`
  * `data = client.get_resource(1)`
- Line 50:
  - `logger.info("Fetched", client.fetch_data(2))`
  * `logger.info("Fetched", client.get_resource(2))`

---

> [!WARNING]
> **This is a permanent workspace-wide change.**
> Please verify the diffs above before proceeding with further edits.
```
