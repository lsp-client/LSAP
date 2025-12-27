# Type Hierarchy API

The Type Hierarchy API allows exploring the inheritance relationships of a class or interface, providing both supertypes (parents) and subtypes (children/implementations).

## TypeHierarchyRequest

| Field       | Type                                                     | Default  | Description                            |
| :---------- | :------------------------------------------------------- | :------- | :------------------------------------- |
| `locate`    | [`LocateText`](locate.md) \| [`LocateSymbol`](locate.md) | Required | The symbol to trace the hierarchy for. |
| `direction` | `"supertypes" \| "subtypes" \| "both"`                   | `"both"` | Direction of the hierarchy trace.      |
| `depth`     | `number`                                                 | `2`      | Maximum number of levels to trace.     |

## TypeHierarchyResponse

| Field        | Type                             | Description                                        |
| :----------- | :------------------------------- | :------------------------------------------------- |
| `root`       | `TypeHierarchyNode`              | The starting type for the trace.                   |
| `nodes`      | `Map<string, TypeHierarchyNode>` | Details of all types encountered in the hierarchy. |
| `edges_up`   | `Map<string, TypeEdge[]>`        | Edges leading to supertypes.                       |
| `edges_down` | `Map<string, TypeEdge[]>`        | Edges leading to subtypes.                         |

### TypeHierarchyNode

| Field         | Type             | Description                               |
| :------------ | :--------------- | :---------------------------------------- |
| `id`          | `string`         | Unique identifier for the node.           |
| `name`        | `string`         | Name of the type.                         |
| `kind`        | `string`         | Symbol kind (e.g., `Class`, `Interface`). |
| `file_path`   | `string`         | Relative path to the file.                |
| `range_start` | `Position`       | Start coordinates of the definition.      |
| `detail`      | `string \| null` | Optional detail (e.g., base class names). |

### TypeEdge

| Field          | Type                        | Description                   |
| :------------- | :-------------------------- | :---------------------------- |
| `from_node_id` | `string`                    | ID of the child/derived node. |
| `to_node_id`   | `string`                    | ID of the parent/base node.   |
| `relationship` | `"extends" \| "implements"` | Type of inheritance.          |

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
# Type Hierarchy for `BaseModel` (Depth: 1, Direction: subtypes)

## Subtypes (Children/Implementations)

- BaseModel (`Class`) in `models.py`
  - User (`Class`) in `user.py`
  - Order (`Class`) in `order.py`

---

> [!NOTE]
> Tree is truncated at depth 1. Increase `depth` parameter to explore further if needed.
```
