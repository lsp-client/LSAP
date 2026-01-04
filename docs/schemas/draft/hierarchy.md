# Unified Hierarchy API

The Unified Hierarchy API provides a single, consistent interface for tracing hierarchical relationships in code. It traces two types of hierarchies:

- **Call Hierarchy**: Function/method call relationships (who calls whom)
- **Type Hierarchy**: Class/interface inheritance relationships (parent-child)

Both hierarchies are modeled as **directed graph traversal** with generic "incoming"/"outgoing" direction terminology.

## HierarchyRequest

Traces hierarchical relationships starting from a symbol.

| Field              | Type                                     | Default  | Description                                     |
| :----------------- | :--------------------------------------- | :------- | :---------------------------------------------- |
| `locate`           | [`Locate`](../locate.md)                 | Required | The symbol to start tracing from.               |
| `hierarchy_type`   | `"call"` \| `"type"`                     | Required | Type of hierarchy to trace.                     |
| `direction`        | `"incoming"` \| `"outgoing"` \| `"both"` | `"both"` | Graph traversal direction.                      |
| `depth`            | `number`                                 | `2`      | Maximum traversal depth (number of hops).       |
| `include_external` | `boolean`                                | `false`  | Whether to include external library references. |

### Direction Parameter

Direction uses **generic graph terminology**, not hierarchy-specific terms:

- `"incoming"`: Trace predecessors in the graph
  - For call hierarchy: find **callers** (who calls this function?)
  - For type hierarchy: find **parent classes/interfaces** (what does this inherit from?)

- `"outgoing"`: Trace successors in the graph
  - For call hierarchy: find **callees** (what does this function call?)
  - For type hierarchy: find **child classes** (what inherits from this?)

- `"both"`: Trace both directions

### Usage Examples

**Example 1: Find who calls a function**

```python
HierarchyRequest(
    hierarchy_type="call",
    locate=Locate(
        file_path="src/main.py",
        scope=LineScope(line=10),
        find="process_data"
    ),
    direction="incoming",  # Find callers
    depth=2
)
```

**Example 2: Find what a function calls**

```python
HierarchyRequest(
    hierarchy_type="call",
    locate=Locate(
        file_path="src/main.py",
        scope=LineScope(line=10),
        find="process_data"
    ),
    direction="outgoing",  # Find callees
    depth=2
)
```

**Example 3: Find parent classes**

```python
HierarchyRequest(
    hierarchy_type="type",
    locate=Locate(
        file_path="src/models.py",
        scope=LineScope(line=5),
        find="UserModel"
    ),
    direction="incoming",  # Find parents
    depth=2
)
```

**Example 4: Find child classes**

```python
HierarchyRequest(
    hierarchy_type="type",
    locate=Locate(
        file_path="src/models.py",
        scope=LineScope(line=5),
        find="BaseModel"
    ),
    direction="outgoing",  # Find children
    depth=2
)
```

## HierarchyResponse

Contains the hierarchy graph and flattened tree for rendering.

| Field            | Type                           | Description                                                  |
| :--------------- | :----------------------------- | :----------------------------------------------------------- |
| `hierarchy_type` | `"call"` \| `"type"`           | Type of hierarchy returned.                                  |
| `root`           | `HierarchyNode`                | The starting node.                                           |
| `nodes`          | `Map<string, HierarchyNode>`   | All nodes in the hierarchy graph.                            |
| `edges_incoming` | `Map<string, HierarchyEdge[]>` | Incoming edges for each node (predecessors).                 |
| `edges_outgoing` | `Map<string, HierarchyEdge[]>` | Outgoing edges for each node (successors).                   |
| `items_incoming` | `HierarchyItem[]`              | Flattened list of incoming relationships for tree rendering. |
| `items_outgoing` | `HierarchyItem[]`              | Flattened list of outgoing relationships for tree rendering. |
| `direction`      | `string`                       | The direction that was used.                                 |
| `depth`          | `number`                       | The depth that was used.                                     |

### HierarchyNode

Represents a symbol in the hierarchy graph.

| Field         | Type             | Description                              |
| :------------ | :--------------- | :--------------------------------------- |
| `id`          | `string`         | Unique identifier for the node.          |
| `name`        | `string`         | Name of the symbol.                      |
| `kind`        | `string`         | Symbol kind (e.g., `Function`, `Class`). |
| `file_path`   | `string`         | Path to the file.                        |
| `range_start` | `Position`       | Start position of the symbol definition. |
| `detail`      | `string \| null` | Optional detail about the symbol.        |

### HierarchyItem

Represents an item in the flattened hierarchy tree for rendering.

| Field       | Type             | Description                           |
| :---------- | :--------------- | :------------------------------------ |
| `name`      | `string`         | Name of the symbol.                   |
| `kind`      | `string`         | Symbol kind.                          |
| `file_path` | `string`         | Path to the file.                     |
| `level`     | `number`         | Nesting level in the tree (0 = root). |
| `detail`    | `string \| null` | Optional detail.                      |
| `is_cycle`  | `boolean`        | Whether this represents a cycle.      |

### HierarchyEdge

Represents a directed edge in the hierarchy graph.

The `metadata` field contains hierarchy-specific information:

| Field          | Type                                           | Description                       |
| :------------- | :--------------------------------------------- | :-------------------------------- |
| `from_node_id` | `string`                                       | ID of the source node.            |
| `to_node_id`   | `string`                                       | ID of the target node.            |
| `metadata`     | `CallEdgeMetadata \| TypeEdgeMetadata \| null` | Hierarchy-specific edge metadata. |

**CallEdgeMetadata** (for call hierarchy):

- `call_sites`: `Position[]` - Exact positions where the call occurs

**TypeEdgeMetadata** (for type hierarchy):

- `relationship`: `"extends" \| "implements"` - Type of inheritance relationship

## Output Format

The response includes a markdown template that adapts to the hierarchy type:

```markdown
# process_data Hierarchy (call, depth: 2)

## Incoming

### main

- Kind: `Function`
- File: `src/main.py`

## Outgoing

### validate_input

- Kind: `Function`
- File: `src/utils.py`
```

## Design Principles

The API is designed around these principles:

1. **Graph abstraction**: Both hierarchies are directed graphs with generic "incoming"/"outgoing" terminology
2. **Polymorphic metadata**: Edge metadata uses Union types, not conditional null fields
3. **Consistent naming**: Same field names for both hierarchy types (`edges_incoming`/`edges_outgoing`, `items_incoming`/`items_outgoing`)
4. **Semantic control**: `hierarchy_type` parameter controls interpretation, not structure

## Related APIs

- [`Locate`](../locate.md) - For specifying symbol location
- [`Reference`](../reference.md) - For finding all references to a symbol
- [`Symbol`](../symbol.md) - For inspecting symbol details
