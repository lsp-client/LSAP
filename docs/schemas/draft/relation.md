# Relation API

The Relation API allows finding all call chains (paths) that connect two specific symbols. This is useful for understanding how one part of the system interacts with another, validating architectural dependencies, or impact analysis.

It leverages the [Call Hierarchy API](call_hierarchy.md) to trace paths.

## RelationRequest

| Field       | Type                  | Default  | Description                                |
| :---------- | :-------------------- | :------- | :----------------------------------------- |
| `source`    | [`Locate`](locate.md) | Required | The starting symbol for the path search.   |
| `target`    | [`Locate`](locate.md) | Required | The ending symbol for the path search.     |
| `max_depth` | `number`              | `10`     | Maximum depth to search for connections.   |

## RelationResponse

| Field       | Type                    | Description                                                                 |
| :---------- | :---------------------- | :-------------------------------------------------------------------------- |
| `source`    | `CallHierarchyItem`     | The resolved source symbol.                                                 |
| `target`    | `CallHierarchyItem`     | The resolved target symbol.                                                 |
| `chains`    | `CallHierarchyItem[][]` | List of paths connecting source to target. Each path is a sequence of items.|
| `max_depth` | `number`                | The maximum depth used for the search.                                      |

## Example Usage

### Scenario 1: How does `handle_request` reach `db.query`?

#### Request

```json
{
  "source": {
    "file_path": "src/controllers.py",
    "scope": {
      "symbol_path": ["handle_request"]
    }
  },
  "target": {
    "file_path": "src/db.py",
    "scope": {
      "symbol_path": ["query"]
    }
  },
  "max_depth": 5
}
```

#### Markdown Rendered for LLM

```markdown
# Relation: `handle_request` → `query`

Found 2 call chain(s):

### Chain 1
1. **handle_request** (`Function`) - `src/controllers.py`
2. **UserService.get_user** (`Method`) - `src/services/user.py`
3. **db.query** (`Function`) - `src/db.py`

### Chain 2
1. **handle_request** (`Function`) - `src/controllers.py`
2. **AuthService.validate_token** (`Method`) - `src/services/auth.py`
3. **SessionManager.get_session** (`Method`) - `src/services/session.py`
4. **db.query** (`Function`) - `src/db.py`
```
