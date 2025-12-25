# Call Hierarchy API

The Call Hierarchy API allows tracing the relationships between functions, showing who calls whom. It supports both incoming (callers) and outgoing (callees) analysis.

## CallHierarchyRequest

Inherits from `LocateRequest`.

| Field              | Type                                 | Default  | Description                                          |
| :----------------- | :----------------------------------- | :------- | :--------------------------------------------------- |
| `direction`        | `"incoming" \| "outgoing" \| "both"` | `"both"` | Direction of the trace.                              |
| `depth`            | `number`                             | `2`      | Maximum number of hops to trace.                     |
| `include_external` | `boolean`                            | `false`  | Whether to include calls to/from external libraries. |

## CallHierarchyResponse

| Field       | Type                             | Description                                        |
| :---------- | :------------------------------- | :------------------------------------------------- |
| `root`      | `CallHierarchyNode`              | The starting node for the trace.                   |
| `nodes`     | `Map<string, CallHierarchyNode>` | Details of all types encountered in the hierarchy. |
| `edges_in`  | `Map<string, CallEdge[]>`        | Incoming edges for each node.                      |
| `edges_out` | `Map<string, CallEdge[]>`        | Outgoing edges for each node.                      |

### CallHierarchyNode

Contains `id`, `name`, `kind`, `file_path`, and `range_start`.

### CallEdge

Contains `from_node_id`, `to_node_id`, and `call_sites` (list of positions).

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

- **start_server** (`Function`) in `src/app.py`
  - **initialize_db** (`Function`) in `src/db.py`
  - **setup_routes** (`Function`) in `src/routes.py`
```
