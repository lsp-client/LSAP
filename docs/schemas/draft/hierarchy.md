# Unified Hierarchy API

The Unified Hierarchy API provides a single, consistent interface for tracing both call relationships (who calls whom) and type relationships (inheritance hierarchies). This API consolidates the functionality previously split between the Call Hierarchy and Type Hierarchy APIs.

## Overview

The unified API supports:
- **Call Hierarchy**: Trace incoming calls (callers) and outgoing calls (callees) for functions/methods
- **Type Hierarchy**: Trace supertypes (parents/base classes) and subtypes (children/implementations) for classes/interfaces

Both hierarchy types share the same request/response structure, differing only by the `hierarchy_type` parameter.

## HierarchyRequest

| Field              | Type                                                          | Default   | Description                                                                                           |
| :----------------- | :------------------------------------------------------------ | :-------- | :---------------------------------------------------------------------------------------------------- |
| `locate`           | [`Locate`](locate.md)                                         | Required  | The symbol to trace the hierarchy for.                                                                |
| `hierarchy_type`   | `"call"` \| `"type"`                                          | Required  | Type of hierarchy: `"call"` for function calls, `"type"` for class inheritance.                       |
| `direction`        | `"incoming"` \| `"outgoing"` \| `"supertypes"` \| `"subtypes"` \| `"both"` | `"both"`  | Direction of the trace (see details below).                                                           |
| `depth`            | `number`                                                      | `2`       | Maximum number of hops/levels to trace.                                                               |
| `include_external` | `boolean`                                                     | `false`   | Whether to include external library references (only for call hierarchy).                             |

### Direction Parameter

The `direction` parameter behavior depends on `hierarchy_type`:

- **For call hierarchy** (`hierarchy_type: "call"`):
  - `"incoming"`: Find callers (who calls this?)
  - `"outgoing"`: Find callees (what does this call?)
  - `"both"`: Find both callers and callees

- **For type hierarchy** (`hierarchy_type: "type"`):
  - `"supertypes"`: Find parent classes/interfaces
  - `"subtypes"`: Find child classes/implementations
  - `"both"`: Find both parents and children

## HierarchyResponse

| Field            | Type                          | Description                                                                                |
| :--------------- | :---------------------------- | :----------------------------------------------------------------------------------------- |
| `hierarchy_type` | `"call"` \| `"type"`          | Type of hierarchy returned.                                                                |
| `root`           | `HierarchyNode`               | The starting node for the trace.                                                           |
| `nodes`          | `Map<string, HierarchyNode>`  | Map of node ID to node details for all nodes in the hierarchy.                             |
| `edges_in`       | `Map<string, HierarchyEdge[]>`| Incoming edges: for call hierarchy (callers), for type hierarchy (supertypes).             |
| `edges_out`      | `Map<string, HierarchyEdge[]>`| Outgoing edges: for call hierarchy (callees), for type hierarchy (subtypes).               |
| `items_in`       | `HierarchyItem[]`             | Flat list for tree rendering: incoming calls or supertypes.                                |
| `items_out`      | `HierarchyItem[]`             | Flat list for tree rendering: outgoing calls or subtypes.                                  |
| `direction`      | `string`                      | The direction that was used.                                                               |
| `depth`          | `number`                      | The depth that was used.                                                                   |

### HierarchyNode

| Field         | Type              | Description                                              |
| :------------ | :---------------- | :------------------------------------------------------- |
| `id`          | `string`          | Unique identifier for the node.                          |
| `name`        | `string`          | Name of the symbol (function, method, class, interface). |
| `kind`        | `string`          | Symbol kind (e.g., `Function`, `Method`, `Class`).       |
| `file_path`   | `string`          | Relative path to the file.                               |
| `range_start` | `Position`        | Start coordinates of the definition.                     |
| `detail`      | `string \| null`  | Optional detail (primarily used for type hierarchy).     |

### HierarchyItem

| Field       | Type              | Description                                            |
| :---------- | :---------------- | :----------------------------------------------------- |
| `name`      | `string`          | Name of the symbol.                                    |
| `kind`      | `string`          | Symbol kind (e.g., `Function`, `Class`).               |
| `file_path` | `string`          | Relative path to the file.                             |
| `level`     | `number`          | Nesting level in the hierarchy (0 = root).             |
| `detail`    | `string \| null`  | Optional detail (primarily used for type hierarchy).   |
| `is_cycle`  | `boolean`         | Whether this represents a recursive cycle.             |

### HierarchyEdge

| Field          | Type                              | Description                                                      |
| :------------- | :-------------------------------- | :--------------------------------------------------------------- |
| `from_node_id` | `string`                          | ID of the source node.                                           |
| `to_node_id`   | `string`                          | ID of the target node.                                           |
| `call_sites`   | `Position[] \| null`              | Exact positions where calls occur (for call hierarchy only).     |
| `relationship` | `"extends"` \| `"implements"` \| `null` | Type of relationship (for type hierarchy only).            |

## Example Usage

### Scenario 1: Call Hierarchy - Finding outgoing calls

Trace what functions a specific function calls.

#### Request

```json
{
  "locate": {
    "file_path": "src/app.py",
    "scope": {
      "symbol_path": ["start_server"]
    }
  },
  "hierarchy_type": "call",
  "direction": "outgoing",
  "depth": 2
}
```

#### Markdown Rendered for LLM

```markdown
# Call Hierarchy for `start_server` (Depth: 2, Direction: outgoing)

## Outgoing Calls (What does this call?)

### initialize_db
- **Kind**: `Function`
- **File**: `src/db.py`

#### connect_to_database
- **Kind**: `Function`
- **File**: `src/db.py`

### setup_routes
- **Kind**: `Function`
- **File**: `src/routes.py`

#### register_handlers
- **Kind**: `Function`
- **File**: `src/handlers.py`

### start_listening
- **Kind**: `Method`
- **File**: `src/app.py`

---
> [!NOTE]
> Tree is truncated at depth 2. Use `depth` parameter to explore further.
```

### Scenario 2: Call Hierarchy - Finding incoming calls

Trace which functions call a specific function.

#### Request

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "scope": {
      "symbol_path": ["validate_input"]
    }
  },
  "hierarchy_type": "call",
  "direction": "incoming",
  "depth": 3,
  "include_external": false
}
```

#### Markdown Rendered for LLM

```markdown
# Call Hierarchy for `validate_input` (Depth: 3, Direction: incoming)

## Incoming Calls (Who calls this?)

### handle_request
- **Kind**: `Function`
- **File**: `src/controllers.py`

#### router.dispatch
- **Kind**: `Method`
- **File**: `src/router.py`

##### app.run
- **Kind**: `Method`
- **File**: `src/app.py`

### process_form
- **Kind**: `Function`
- **File**: `src/forms.py`

---
> [!NOTE]
> Tree is truncated at depth 3. Use `depth` parameter to explore further.
```

### Scenario 3: Type Hierarchy - Finding subtypes

Trace which classes inherit from or implement a base class/interface.

#### Request

```json
{
  "locate": {
    "file_path": "src/models/base.py",
    "scope": {
      "symbol_path": ["BaseModel"]
    }
  },
  "hierarchy_type": "type",
  "direction": "subtypes",
  "depth": 2
}
```

#### Markdown Rendered for LLM

```markdown
# Type Hierarchy for `BaseModel` (Depth: 2, Direction: subtypes)

## Subtypes (Children/Implementations)

### User
- Kind: `Class`
- File: `src/models/user.py`

#### AdminUser
- Kind: `Class`
- File: `src/models/admin.py`

### Order
- Kind: `Class`
- File: `src/models/order.py`

#### PremiumOrder
- Kind: `Class`
- File: `src/models/premium.py`

### Product
- Kind: `Class`
- File: `src/models/product.py`

---
> [!NOTE]
> Tree is truncated at depth 2. Increase `depth` parameter to explore further if needed.
```

### Scenario 4: Type Hierarchy - Finding supertypes

Trace the inheritance chain of a class to its base classes.

#### Request

```json
{
  "locate": {
    "file_path": "src/models/admin.py",
    "scope": {
      "symbol_path": ["AdminUser"]
    }
  },
  "hierarchy_type": "type",
  "direction": "supertypes",
  "depth": 3
}
```

#### Markdown Rendered for LLM

```markdown
# Type Hierarchy for `AdminUser` (Depth: 3, Direction: supertypes)

## Supertypes (Parents/Base Classes)

### User
- Kind: `Class`
- File: `src/models/user.py`

#### BaseModel
- Kind: `Class`
- File: `src/models/base.py`

##### Serializable
- Kind: `Interface`
- File: `src/interfaces.py`

---
> [!NOTE]
> Tree is truncated at depth 3. Increase `depth` parameter to explore further if needed.
```

### Scenario 5: Exploring both directions

Useful for understanding a symbol's position in the hierarchy.

#### Request

```json
{
  "locate": {
    "file_path": "src/controllers/base.py",
    "scope": {
      "symbol_path": ["BaseController"]
    }
  },
  "hierarchy_type": "type",
  "direction": "both",
  "depth": 2
}
```

#### Markdown Rendered for LLM

```markdown
# Type Hierarchy for `BaseController` (Depth: 2, Direction: both)

## Supertypes (Parents/Base Classes)

### Controller
- Kind: `Interface`
- File: `src/interfaces.py`

## Subtypes (Children/Implementations)

### AuthController
- Kind: `Class`
- File: `src/controllers/auth.py`

#### AdminAuthController
- Kind: `Class`
- File: `src/controllers/admin_auth.py`

### DataController
- Kind: `Class`
- File: `src/controllers/data.py`

---
> [!NOTE]
> Tree is truncated at depth 2. Increase `depth` parameter to explore further if needed.
```

## Differences from Separate APIs

The Unified Hierarchy API consolidates the previous Call Hierarchy and Type Hierarchy APIs into a single, consistent interface:

### Key Improvements

1. **Single API Surface**: One request/response structure handles both call and type hierarchies
2. **Consistent Field Names**: Uses `edges_in`/`edges_out` and `items_in`/`items_out` for both hierarchy types
3. **Unified Node/Edge Models**: `HierarchyNode`, `HierarchyItem`, and `HierarchyEdge` work for both cases
4. **Flexible Edge Data**: `HierarchyEdge` supports both `call_sites` (for call hierarchy) and `relationship` (for type hierarchy)

### Field Mapping

| Unified API     | Call Hierarchy API | Type Hierarchy API |
| :-------------- | :----------------- | :----------------- |
| `items_in`      | `calls_in`         | `types_up`         |
| `items_out`     | `calls_out`        | `types_down`       |
| `edges_in`      | `edges_in`         | `edges_up`         |
| `edges_out`     | `edges_out`        | `edges_down`       |

### Comparison Table

| Feature                    | Call Hierarchy API | Type Hierarchy API | Unified Hierarchy API |
| :------------------------- | :----------------- | :----------------- | :-------------------- |
| Request class              | `CallHierarchyRequest` | `TypeHierarchyRequest` | `HierarchyRequest` |
| Response class             | `CallHierarchyResponse` | `TypeHierarchyResponse` | `HierarchyResponse` |
| Hierarchy type selection   | Implicit (separate API) | Implicit (separate API) | Explicit via `hierarchy_type` |
| Direction parameter        | `incoming`/`outgoing`/`both` | `supertypes`/`subtypes`/`both` | Both supported based on `hierarchy_type` |
| Edge data                  | `call_sites` only  | `relationship` only | Both via optional fields |
| Include external libraries | ✓                  | ✗                  | ✓ (call hierarchy only) |

## Migration Guide

### From Call Hierarchy API

**Before:**
```json
{
  "locate": { ... },
  "direction": "incoming",
  "depth": 2,
  "include_external": false
}
```

**After:**
```json
{
  "locate": { ... },
  "hierarchy_type": "call",
  "direction": "incoming",
  "depth": 2,
  "include_external": false
}
```

**Response field changes:**
- `response.calls_in` → `response.items_in`
- `response.calls_out` → `response.items_out`

### From Type Hierarchy API

**Before:**
```json
{
  "locate": { ... },
  "direction": "supertypes",
  "depth": 2
}
```

**After:**
```json
{
  "locate": { ... },
  "hierarchy_type": "type",
  "direction": "supertypes",
  "depth": 2
}
```

**Response field changes:**
- `response.types_up` → `response.items_in`
- `response.types_down` → `response.items_out`
- `response.edges_up` → `response.edges_in`
- `response.edges_down` → `response.edges_out`

### Backward Compatibility

The existing [Call Hierarchy API](call_hierarchy.md) and [Type Hierarchy API](type_hierarchy.md) remain available and are maintained for backward compatibility. They internally re-export types from the unified hierarchy API with appropriate aliases:

- `CallHierarchyNode` = `HierarchyNode`
- `TypeHierarchyNode` = `HierarchyNode`
- `CallEdge` = `HierarchyEdge`
- `TypeEdge` = `HierarchyEdge`

**Recommendation**: New implementations should use the Unified Hierarchy API (`HierarchyRequest`/`HierarchyResponse`) for consistency and future-proofing. The separate APIs will continue to work but may be deprecated in future versions.

## Best Practices

1. **Start with shallow depth**: Begin with `depth: 1` or `depth: 2` to avoid overwhelming results
2. **Use specific directions**: When you know what you're looking for, use `"incoming"`, `"outgoing"`, `"supertypes"`, or `"subtypes"` instead of `"both"`
3. **Check for cycles**: Monitor the `is_cycle` flag in `HierarchyItem` to detect recursive patterns
4. **Filter external calls**: For call hierarchies, set `include_external: false` unless you specifically need to trace into libraries
5. **Leverage edges**: Use `edges_in`/`edges_out` for graph-based navigation; use `items_in`/`items_out` for tree-based rendering

## Implementation Notes

- **Cycle Detection**: The API automatically detects recursive cycles (e.g., mutual recursion, circular inheritance) and marks them with `is_cycle: true`
- **Performance**: Deep hierarchies (depth > 5) may be computationally expensive; consider using pagination or multiple focused queries
- **Call Sites**: For call hierarchy, `call_sites` provides exact source locations where calls occur, enabling precise navigation
- **Type Relationships**: For type hierarchy, `relationship` distinguishes between `"extends"` (class inheritance) and `"implements"` (interface implementation)

## Related APIs

- [Call Hierarchy API](call_hierarchy.md) - Legacy call hierarchy API (backward compatible)
- [Type Hierarchy API](type_hierarchy.md) - Legacy type hierarchy API (backward compatible)
- [Relation API](relation.md) - Find call chains between two symbols
- [Implementation API](implementation.md) - Find implementations of interfaces/abstract methods

## Pending Issues

- **TBD**: Cross-language hierarchy tracing (e.g., TypeScript calling Python)
- **TBD**: Performance optimization for very deep or wide hierarchies (depth > 10, breadth > 1000 nodes)
- **TBD**: Support for multiple inheritance edge types in type hierarchy
