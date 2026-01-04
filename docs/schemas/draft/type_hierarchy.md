# Type Hierarchy API

The Type Hierarchy API allows exploring the inheritance relationships of a class or interface, providing both supertypes (parents) and subtypes (children/implementations).

## TypeHierarchyRequest

| Field       | Type                        | Default  | Description                            |
| :---------- | :-------------------------- | :------- | :------------------------------------- |
| `locate`    | [`Locate`](locate.md)       | Required | The symbol to trace the hierarchy for. |
| `direction` | `"supertypes"` \| `"subtypes"` \| `"both"` | `"both"` | Direction of the hierarchy trace.      |
| `depth`     | `number`                    | `2`      | Maximum number of levels to trace.     |

## TypeHierarchyResponse

| Field        | Type                             | Description                                        |
| :----------- | :------------------------------- | :------------------------------------------------- |
| `root`       | `TypeHierarchyNode`              | The starting type for the trace.                   |
| `nodes`      | `Map<string, TypeHierarchyNode>` | Details of all types encountered in the hierarchy. |
| `edges_up`   | `Map<string, TypeEdge[]>`        | Edges leading to supertypes.                       |
| `edges_down` | `Map<string, TypeEdge[]>`        | Edges leading to subtypes.                         |
| `types_up`   | `TypeHierarchyItem[]`            | Flat list of supertypes for tree rendering.        |
| `types_down` | `TypeHierarchyItem[]`            | Flat list of subtypes for tree rendering.          |
| `direction`  | `string`                         | The direction that was used.                       |
| `depth`      | `number`                         | The depth that was used.                           |

### TypeHierarchyNode

| Field         | Type             | Description                               |
| :------------ | :--------------- | :---------------------------------------- |
| `id`          | `string`         | Unique identifier for the node.           |
| `name`        | `string`         | Name of the type.                         |
| `kind`        | `string`         | Symbol kind (e.g., `Class`, `Interface`). |
| `file_path`   | `string`         | Relative path to the file.                |
| `range_start` | `Position`       | Start coordinates of the definition.      |
| `detail`      | `string \| null` | Optional detail (e.g., base class names). |

### TypeHierarchyItem

| Field       | Type              | Description                                            |
| :---------- | :---------------- | :----------------------------------------------------- |
| `name`      | `string`          | Name of the type.                                      |
| `kind`      | `string`          | Symbol kind (e.g., `Class`, `Interface`).              |
| `file_path` | `string`          | Relative path to the file.                             |
| `level`     | `number`          | Nesting level in the hierarchy.                        |
| `detail`    | `string \| null`  | Optional detail (e.g., base class names).              |
| `is_cycle`  | `boolean`         | Whether this represents a recursive cycle.             |

### TypeEdge

| Field          | Type                              | Description                   |
| :------------- | :-------------------------------- | :---------------------------- |
| `from_node_id` | `string`                          | ID of the child/derived node. |
| `to_node_id`   | `string`                          | ID of the parent/base node.   |
| `relationship` | `"extends"` \| `"implements"`     | Type of inheritance.          |

## Example Usage

### Scenario 1: Finding all subclasses (subtypes)

#### Request

```json
{
  "locate": {
    "file_path": "models.py",
    "scope": {
      "symbol_path": ["BaseModel"]
    }
  },
  "direction": "subtypes",
  "depth": 1
}
```

#### Markdown Rendered for LLM

```markdown
# Type Hierarchy for `BaseModel` (Depth: 1, Direction: subtypes)

## Subtypes (Children/Implementations)
  - User (`Class`) in `src/models/user.py`
  - Order (`Class`) in `src/models/order.py`
  - Product (`Class`) in `src/models/product.py`

---

> [!NOTE]
> Tree is truncated at depth 1. Increase `depth` parameter to explore further if needed.
```

### Scenario 2: Finding parent classes (supertypes)

#### Request

```json
{
  "locate": {
    "file_path": "src/models/user.py",
    "scope": {
      "symbol_path": ["User"]
    }
  },
  "direction": "supertypes",
  "depth": 2
}
```

#### Markdown Rendered for LLM

```markdown
# Type Hierarchy for `User` (Depth: 2, Direction: supertypes)

## Supertypes (Parents/Base Classes)
  - BaseModel (`Class`) in `src/models/base.py`
  - Serializable (`Interface`) in `src/interfaces.py`

---

> [!NOTE]
> Tree is truncated at depth 2. Increase `depth` parameter to explore further if needed.
```

## Pending Issues

- **TBD**: Handling of multiple inheritance and integration with external types not defined in the workspace.


#### Markdown Rendered for LLM

```markdown
# Type Hierarchy for `AuthController` (Depth: 2, Direction: both)

## Supertypes (Parents/Base Classes)
  - BaseController (`Class`) in `src/controllers/base.py`

## Subtypes (Children/Implementations)
  - AdminAuthController (`Class`) in `src/controllers/admin.py`

---

> [!NOTE]
> Tree is truncated at depth 2. Increase `depth` parameter to explore further if needed.
```
