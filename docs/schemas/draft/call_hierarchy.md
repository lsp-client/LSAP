# Call Hierarchy API

The Call Hierarchy API allows tracing the relationships between functions, showing who calls whom. It supports both incoming (callers) and outgoing (callees) analysis.

## CallHierarchyRequest

| Field              | Type                        | Default   | Description                                          |
| :----------------- | :-------------------------- | :-------- | :--------------------------------------------------- |
| `locate`           | [`Locate`](locate.md)       | Required  | The symbol to trace callers/callees for.             |
| `direction`        | `"incoming"` \| `"outgoing"` \| `"both"` | `"both"` | Direction of the trace.                              |
| `depth`            | `number`                    | `2`       | Maximum number of hops to trace.                     |
| `include_external` | `boolean`                   | `false`   | Whether to include calls to/from external libraries. |

## CallHierarchyResponse

| Field       | Type                             | Description                                        |
| :---------- | :------------------------------- | :------------------------------------------------- |
| `root`      | `CallHierarchyNode`              | The starting node for the trace.                   |
| `nodes`     | `Map<string, CallHierarchyNode>` | Details of all types encountered in the hierarchy. |
| `edges_in`  | `Map<string, CallEdge[]>`        | Incoming edges for each node.                      |
| `edges_out` | `Map<string, CallEdge[]>`        | Outgoing edges for each node.                      |
| `calls_in`  | `CallHierarchyItem[]`            | Flat list of incoming calls for tree rendering.    |
| `calls_out` | `CallHierarchyItem[]`            | Flat list of outgoing calls for tree rendering.    |
| `direction` | `string`                         | The direction that was used.                       |
| `depth`     | `number`                         | The depth that was used.                           |

### CallHierarchyNode

| Field         | Type       | Description                               |
| :------------ | :--------- | :---------------------------------------- |
| `id`          | `string`   | Unique identifier for the node.           |
| `name`        | `string`   | Name of the function.                     |
| `kind`        | `string`   | Symbol kind (e.g., `Function`, `Method`). |
| `file_path`   | `string`   | Relative path to the file.                |
| `range_start` | `Position` | Start coordinates of the definition.      |

### CallHierarchyItem

| Field       | Type       | Description                                            |
| :---------- | :--------- | :----------------------------------------------------- |
| `name`      | `string`   | Name of the function.                                  |
| `kind`      | `string`   | Symbol kind (e.g., `Function`, `Method`).              |
| `file_path` | `string`   | Relative path to the file.                             |
| `level`     | `number`   | Nesting level in the hierarchy.                        |
| `is_cycle`  | `boolean`  | Whether this represents a recursive cycle.             |

### CallEdge

| Field          | Type         | Description                              |
| :------------- | :----------- | :--------------------------------------- |
| `from_node_id` | `string`     | ID of the calling node.                  |
| `to_node_id`   | `string`     | ID of the called node.                   |
| `call_sites`   | `Position[]` | List of positions where the call occurs. |

## Example Usage

### Scenario 1: Finding outgoing calls (what does this function call?)

#### Request

```json
{
  "locate": {
    "file_path": "src/app.py",
    "scope": {
      "symbol_path": ["start_server"]
    }
  },
  "direction": "outgoing",
  "depth": 1
}
```

#### Markdown Rendered for LLM

```markdown
# Call Hierarchy for `start_server` (Depth: 1, Direction: outgoing)

## Outgoing Calls (What does this call?)
- initialize_db (`Function`) in `src/db.py`
- setup_routes (`Function`) in `src/routes.py`
- start_listening (`Method`) in `src/app.py`

---

> [!NOTE]
> Tree is truncated at depth 1. Use `depth` parameter to explore further.
```

### Scenario 2: Finding incoming calls (what calls this function?)

#### Request

```json
{
  "locate": {
    "file_path": "src/db.py",
    "scope": {
      "symbol_path": ["initialize_db"]
    }
  },
  "direction": "incoming",
  "depth": 2
}
```

#### Markdown Rendered for LLM

```markdown
# Call Hierarchy for `initialize_db` (Depth: 2, Direction: incoming)

## Incoming Calls (Who calls this?)
- start_server (`Function`) in `src/app.py`
  - main (`Function`) in `src/main.py`
- run_tests (`Function`) in `tests/setup.py`

---

> [!NOTE]
> Tree is truncated at depth 2. Use `depth` parameter to explore further.
```

### Scenario 3: Exploring both directions with deeper depth

#### Request

```json
{
  "locate": {
    "file_path": "src/controllers.py",
    "scope": {
      "symbol_path": ["handle_request"]
    }
  },
  "direction": "both",
  "depth": 3,
  "include_external": false
}
```

#### Markdown Rendered for LLM

```markdown
# Call Hierarchy for `handle_request` (Depth: 3, Direction: both)

## Incoming Calls (Who calls this?)
- router.dispatch (`Method`) in `src/router.py`
  - app.run (`Method`) in `src/app.py`

## Outgoing Calls (What does this call?)
- validate_input (`Function`) in `src/utils.py`
  - is_valid_email (`Function`) in `src/validators.py`
  - sanitize_string (`Function`) in `src/sanitizer.py`
- process_data (`Method`) in `src/controllers.py`

---

> [!NOTE]
> Tree is truncated at depth 3. Use `depth` parameter to explore further.
```
