# Rename API (Refactoring)

The Rename API provides a safe, workspace-wide symbol renaming capability. It automates the task of updating all references to a symbol (variable, function, class, etc.) across multiple files.

## RenameRequest

| Field      | Type                | Default  | Description                           |
| :--------- | :------------------ | :------- | :------------------------------------ |
| `locate`   | [`Locate`](locate.md) | Required | The location of the symbol to rename. |
| `new_name` | `string`            | Required | The target name for the symbol.       |

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

| Field       | Type           | Description                             |
| :---------- | :------------- | :-------------------------------------- |
| `file_path` | `string`       | Relative path to the modified file.     |
| `diffs`     | `RenameDiff[]` | List of text replacements in this file. |

### RenameDiff

| Field      | Type     | Description                          |
| :--------- | :------- | :----------------------------------- |
| `line`     | `number` | Line number (1-based) where the change occurs. |
| `original` | `string` | The text before the rename.          |
| `modified` | `string` | The text after the rename.           |

## Example Usage

### Scenario 1: Renaming a method used across the project

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

#### Markdown Rendered for LLM

```markdown
# Rename Preview: `fetch_data` -> `get_resource`

Summary: Affects 2 files and 3 occurrences.

## File: `src/client.py`

- Line 10:
  - `def fetch_data(self, id):`
  + `def get_resource(self, id):`

## File: `src/main.py`

- Line 42:
  - `data = client.fetch_data(1)`
  + `data = client.get_resource(1)`
- Line 50:
  - `logger.info("Fetched", client.fetch_data(2))`
  + `logger.info("Fetched", client.get_resource(2))`

---

> [!WARNING]
> This is a permanent workspace-wide change.
> Please verify the diffs above before proceeding with further edits.
```

### Scenario 2: Renaming a variable within a function

#### Request

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "find": "temp"
  },
  "new_name": "buffer"
}
```

#### Markdown Rendered for LLM

```markdown
# Rename Preview: `temp` -> `buffer`

Summary: Affects 1 file and 5 occurrences.

## File: `src/utils.py`

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

> [!WARNING]
> This is a permanent workspace-wide change.
> Please verify the diffs above before proceeding with further edits.
```

### Scenario 3: Renaming a class with many usages

#### Request

```json
{
  "locate": {
    "file_path": "src/models.py",
    "scope": {
      "symbol_path": ["UserAccount"]
    }
  },
  "new_name": "UserProfile"
}
```

#### Markdown Rendered for LLM

```markdown
# Rename Preview: `UserAccount` -> `UserProfile`

Summary: Affects 5 files and 12 occurrences.

## File: `src/models.py`

- Line 10:
  - `class UserAccount:`
  + `class UserProfile:`

## File: `src/auth.py`

- Line 5:
  - `from .models import UserAccount`
  + `from .models import UserProfile`
- Line 15:
  - `user = UserAccount(...)`
  + `user = UserProfile(...)`

## File: `src/views.py`

- Line 20:
  - `def get_user_account(request):`
  + `def get_user_profile(request):`
- Line 22:
  - `account = UserAccount.objects.get(...)`
  + `account = UserProfile.objects.get(...)`

## File: `tests/test_models.py`

- Line 10:
  - `def test_user_account_creation():`
  + `def test_user_profile_creation():`
- Line 12:
  - `account = UserAccount(...)`
  + `account = UserProfile(...)`

## File: `docs/api.md`

- Line 5:
  - `### UserAccount Endpoints`
  + `### UserProfile Endpoints`
- Line 10:
  - `Creates a new UserAccount instance.`
  + `Creates a new UserProfile instance.`

---

> [!WARNING]
> This is a permanent workspace-wide change.
> Please verify the diffs above before proceeding with further edits.
```

## Pending Issues

- **TBD**: Handling of dynamic references (e.g., `getattr`, reflection) and safe rollback mechanisms.
