# Type Hierarchy API

The Type Hierarchy API allows exploring the inheritance relationships of a class or interface, providing both supertypes (parents) and subtypes (children/implementations).

## TypeHierarchyRequest

Inherits from `LocateRequest`.

| Field       | Type                                   | Default  | Description                        |
| :---------- | :------------------------------------- | :------- | :--------------------------------- |
| `direction` | `"supertypes" \| "subtypes" \| "both"` | `"both"` | Direction of the hierarchy trace.  |
| `depth`     | `number`                               | `2`      | Maximum number of levels to trace. |

## TypeHierarchyResponse

| Field        | Type                             | Description                                        |
| :----------- | :------------------------------- | :------------------------------------------------- |
| `root`       | `TypeHierarchyNode`              | The starting type for the trace.                   |
| `nodes`      | `Map<string, TypeHierarchyNode>` | Details of all types encountered in the hierarchy. |
| `edges_up`   | `Map<string, TypeEdge[]>`        | Edges leading to supertypes.                       |
| `edges_down` | `Map<string, TypeEdge[]>`        | Edges leading to subtypes.                         |

### TypeHierarchyNode

Contains `id`, `name`, `kind`, `file_path`, `range_start`, and optional `detail` (e.g., base class names).

### TypeEdge

Contains `from_node_id`, `to_node_id`, and `relationship` (`extends` or `implements`).

## Example Usage

### Request

```json
{
  "locate": {
    "file_path": "models.py",
    "symbol_path": ["BaseModel"]
  },
  "direction": "subtypes",
  "depth": 1
}
```

### Markdown Rendered for LLM

```markdown
### Type Hierarchy for `BaseModel` (Depth: 1, Direction: subtypes)

#### Subtypes (Children/Implementations)

- BaseModel (`Class`) in `models.py`
  - User (`Class`) in `user.py`
  - Order (`Class`) in `order.py`
```
