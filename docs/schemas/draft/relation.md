# Relation API

**Core Value**: Trace the call path between two symbols — answering "how does A reach B?"

This is a high-value query for:

- **Code Flow Understanding**: How does `handle_request` eventually call `db.query`?
- **Impact Analysis**: If I modify function X, which entry points are affected?
- **Architecture Validation**: Verify that module A never directly/indirectly calls module B

## RelationRequest

| Field       | Type                          | Default  | Description                              |
| :---------- | :---------------------------- | :------- | :--------------------------------------- |
| `source`    | [`Locate`](../locate.md)      | Required | The starting symbol for the path search. |
| `target`    | [`Locate`](../locate.md)      | Required | The ending symbol for the path search.   |
| `max_depth` | `number`                      | `10`     | Maximum search depth.                    |

## RelationResponse

| Field       | Type              | Description                                           |
| :---------- | :---------------- | :---------------------------------------------------- |
| `request`   | `RelationRequest` | The original request.                                 |
| `source`    | `ChainNode`       | The resolved source symbol.                           |
| `target`    | `ChainNode`       | The resolved target symbol.                           |
| `chains`    | `ChainNode[][]`   | All paths found. Each path is a sequence of nodes.    |

The maximum depth used for the search is available as `request.max_depth`, since the response includes the original `RelationRequest`.

### ChainNode

A lightweight symbol representation for path display:

| Field       | Type     | Description                        |
| :---------- | :------- | :--------------------------------- |
| `name`      | `string` | Symbol name (e.g., `get_user`)     |
| `kind`      | `string` | Symbol kind (e.g., `Function`)     |
| `file_path` | `Path`   | File containing the symbol         |
| `detail`    | `string` | Optional: signature or extra info  |

> **Design Note**: Unlike `HierarchyItem`, `ChainNode` has no `level` or `is_cycle` fields — the array index naturally represents position in the chain.

## Example

### How does `handle_request` reach `db.query`?

#### Request

```json
{
  "source": {
    "file_path": "src/controllers.py",
    "scope": { "symbol_path": ["handle_request"] }
  },
  "target": {
    "file_path": "src/db.py",
    "scope": { "symbol_path": ["query"] }
  },
  "max_depth": 5
}
```

#### Response (Markdown Rendered)

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

## Implementation

Orchestrates LSP `Call Hierarchy` requests:

1. **Resolve**: Use `textDocument/prepareCallHierarchy` to get `CallHierarchyItem` for both endpoints
2. **Search**: BFS via `callHierarchy/outgoingCalls` from source (optionally bidirectional with `incomingCalls` from target)
3. **Reconstruct**: Build paths when frontiers meet; filter by `max_depth`

## Design Decisions

| Decision | Rationale |
| :------- | :-------- |
| No pagination | `max_depth` bounds result size; path enumeration is typically small |
| `ChainNode` over `HierarchyItem` | Chains are linear; no tree semantics needed |
| Bidirectional search optional | Optimization for large graphs; not required for correctness |
