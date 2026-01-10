# Hierarchy APIs

Two separate APIs for tracing hierarchical relationships in code.

---

## Call Hierarchy API

The Call Hierarchy API traces function/method call relationships.

### CallHierarchyRequest

| Field              | Type                                     | Default  | Description                        |
| :----------------- | :--------------------------------------- | :------- | :--------------------------------- |
| `locate`           | [`Locate`](../locate.md)                 | Required | The function/method to trace from. |
| `direction`        | `"incoming"` \| `"outgoing"` \| `"both"` | `"both"` | Traversal direction.               |
| `depth`            | `number`                                 | `2`      | Maximum traversal depth.           |
| `include_external` | `boolean`                                | `false`  | Include external library calls.    |

### CallHierarchyResponse

| Field            | Type                               | Description                 |
| :--------------- | :--------------------------------- | :-------------------------- |
| `root`           | `HierarchyNode`                    | The starting symbol.        |
| `nodes`          | `Map<string, HierarchyNode>`       | All nodes in the graph.     |
| `edges_incoming` | `Map<string, CallHierarchyEdge[]>` | Caller edges.               |
| `edges_outgoing` | `Map<string, CallHierarchyEdge[]>` | Callee edges.               |
| `items_incoming` | `HierarchyItem[]`                  | Flattened caller tree.      |
| `items_outgoing` | `HierarchyItem[]`                  | Flattened callee tree.      |
| `direction`      | `string`                           | The direction used.         |
| `depth`          | `number`                           | The depth used.             |

### Example Usage

#### Request

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "scope": { "symbol_path": ["process_data"] }
  },
  "direction": "both",
  "depth": 2
}
```

#### Markdown Rendered for LLM

````markdown
# Call Hierarchy: `process_data`

Root: `process_data` (`Function`) at `src/utils.py`
Detail: Process and transform input data

## Callers (incoming)

### `main`
main -> process_data
- Kind: `Function`
- File: `src/main.py`
- Detail: Application entry point

#### `cli_handler`
cli_handler -> main -> process_data
- Kind: `Function`
- File: `src/cli.py`
- Detail: CLI argument handler

### `batch_runner`
batch_runner -> process_data
- Kind: `Function`
- File: `src/batch.py`
- Detail: Batch processing entry

## Callees (outgoing)

### `validate`
process_data -> validate
- Kind: `Function`
- File: `src/validation.py`
- Detail: Validate input format

#### `check_schema`
process_data -> validate -> check_schema
- Kind: `Function`
- File: `src/validation.py`
- Detail: Check JSON schema

### `transform`
process_data -> transform
- Kind: `Function`
- File: `src/transform.py`
- Detail: Transform data format
````

---

## Type Hierarchy API

The Type Hierarchy API traces class/interface inheritance relationships.

### TypeHierarchyRequest

| Field       | Type                                       | Default  | Description                        |
| :---------- | :----------------------------------------- | :------- | :--------------------------------- |
| `locate`    | [`Locate`](../locate.md)                   | Required | The class/interface to trace from. |
| `direction` | `"supertypes"` \| `"subtypes"` \| `"both"` | `"both"` | Traversal direction.               |
| `depth`     | `number`                                   | `2`      | Maximum traversal depth.           |

### TypeHierarchyResponse

| Field              | Type                               | Description                 |
| :----------------- | :--------------------------------- | :-------------------------- |
| `root`             | `HierarchyNode`                    | The starting symbol.        |
| `nodes`            | `Map<string, HierarchyNode>`       | All nodes in the graph.     |
| `edges_supertypes` | `Map<string, TypeHierarchyEdge[]>` | Parent edges.               |
| `edges_subtypes`   | `Map<string, TypeHierarchyEdge[]>` | Child edges.                |
| `items_supertypes` | `HierarchyItem[]`                  | Flattened supertype tree.   |
| `items_subtypes`   | `HierarchyItem[]`                  | Flattened subtype tree.     |
| `direction`        | `string`                           | The direction used.         |
| `depth`            | `number`                           | The depth used.             |

### Example Usage

#### Request

```json
{
  "locate": {
    "file_path": "src/models.py",
    "scope": { "symbol_path": ["UserModel"] }
  },
  "direction": "both",
  "depth": 2
}
```

#### Markdown Rendered for LLM

````markdown
# Type Hierarchy: `UserModel`

Root: `UserModel` (`Class`) at `src/models.py`
Detail: User data model with validation

## Supertypes (parents)

### `BaseModel`
UserModel <- BaseModel
- Kind: `Class`
- File: `src/base.py`
- Detail: Base model with serialization

#### `object`
UserModel <- BaseModel <- object
- Kind: `Class`
- File: `builtins`

### `Serializable`
UserModel <- Serializable
- Kind: `Interface`
- File: `src/interfaces.py`
- Detail: JSON serialization interface

## Subtypes (children)

### `AdminUser`
UserModel -> AdminUser
- Kind: `Class`
- File: `src/admin.py`
- Detail: Admin user with elevated permissions

### `GuestUser`
UserModel -> GuestUser
- Kind: `Class`
- File: `src/guest.py`
- Detail: Guest user with limited access

#### `AnonymousUser`
UserModel -> GuestUser -> AnonymousUser
- Kind: `Class`
- File: `src/guest.py`
- Detail: Unauthenticated user
````

---

## Shared Models

### HierarchyNode

| Field         | Type             | Description      |
| :------------ | :--------------- | :--------------- |
| `id`          | `string`         | Unique ID.       |
| `name`        | `string`         | Symbol name.     |
| `kind`        | `string`         | Symbol kind.     |
| `file_path`   | `string`         | File path.       |
| `range_start` | `Position`       | Start position.  |
| `detail`      | `string \| null` | Optional detail. |

### HierarchyItem

| Field       | Type             | Description                                       |
| :---------- | :--------------- | :------------------------------------------------ |
| `name`      | `string`         | Symbol name.                                      |
| `kind`      | `string`         | Symbol kind.                                      |
| `file_path` | `string`         | File path.                                        |
| `level`     | `number`         | Depth level (1 = direct child of root).           |
| `chain`     | `string[]`       | Full path from this node to root.                 |
| `detail`    | `string \| null` | Optional detail.                                  |
| `is_cycle`  | `boolean`        | Whether this node creates a cycle.                |

### CallHierarchyEdge

| Field          | Type         | Description                      |
| :------------- | :----------- | :------------------------------- |
| `from_node_id` | `string`     | ID of the caller.                |
| `to_node_id`   | `string`     | ID of the callee.                |
| `call_sites`   | `CallSite[]` | Positions where the call occurs. |

### CallSite

| Field      | Type             | Description           |
| :--------- | :--------------- | :-------------------- |
| `position` | `Position`       | Position of the call. |
| `snippet`  | `string \| null` | Optional code snippet.|

### TypeHierarchyEdge

| Field          | Type           | Description                        |
| :------------- | :------------- | :--------------------------------- |
| `from_node_id` | `string`       | ID of the child class.             |
| `to_node_id`   | `string`       | ID of the parent class.            |
| `relation`     | `TypeRelation` | The inheritance relationship type. |

### TypeRelation

| Field  | Type                          | Description           |
| :----- | :---------------------------- | :-------------------- |
| `kind` | `"extends"` \| `"implements"` | Extends or implements.|
