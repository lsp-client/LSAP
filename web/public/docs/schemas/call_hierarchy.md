# Call Hierarchy API

The Call Hierarchy API allows tracing the relationships between functions, showing who calls whom. It supports both incoming (callers) and outgoing (callees) analysis.

## CallHierarchyRequest

| Field              | Type                                                     | Default  | Description                                          |
| :----------------- | :------------------------------------------------------- | :------- | :--------------------------------------------------- |
| `locate`           | [`LocateText`](locate.md) \| [`LocateSymbol`](locate.md) | Required | The symbol to trace callers/callees for.             |
| `direction`        | `"incoming" \| "outgoing" \| "both"`                     | `"both"` | Direction of the trace.                              |
| `depth`            | `number`                                                 | `2`      | Maximum number of hops to trace.                     |
| `include_external` | `boolean`                                                | `false`  | Whether to include calls to/from external libraries. |

## CallHierarchyResponse

| Field       | Type                             | Description                                        |
| :---------- | :------------------------------- | :------------------------------------------------- |
| `root`      | `CallHierarchyNode`              | The starting node for the trace.                   |
| `nodes`     | `Map<string, CallHierarchyNode>` | Details of all types encountered in the hierarchy. |
| `edges_in`  | `Map<string, CallEdge[]>`        | Incoming edges for each node.                      |
| `edges_out` | `Map<string, CallEdge[]>`        | Outgoing edges for each node.                      |

### CallHierarchyNode

| Field         | Type       | Description                               |
| :------------ | :--------- | :---------------------------------------- |
| `id`          | `string`   | Unique identifier for the node.           |
| `name`        | `string`   | Name of the function.                     |
| `kind`        | `string`   | Symbol kind (e.g., `Function`, `Method`). |
| `file_path`   | `string`   | Relative path to the file.                |
| `range_start` | `Position` | Start coordinates of the definition.      |

### CallEdge

| Field          | Type         | Description                              |
| :------------- | :----------- | :--------------------------------------- |
| `from_node_id` | `string`     | ID of the calling node.                  |
| `to_node_id`   | `string`     | ID of the called node.                   |
| `call_sites`   | `Position[]` | List of positions where the call occurs. |

## Example Usage

### Request

```json
{
  "locate": {
    "file_path": "src/app.py",
    "symbol_path": ["start_server"]
  },
  "direction": "outgoing",
  "depth": 1
}
```

### Markdown Rendered for LLM

```markdown
### Call Hierarchy for `start_server` (Depth: 1, Direction: outgoing)

#### Outgoing Calls (What does this call?)

- initialize_db (`Function`) in `src/db.py`
- setup_routes (`Function`) in `src/routes.py`

---

> [!NOTE]
> Tree is truncated at depth 1. Use `depth` parameter to explore further.
```
