# Explore API

## Overview
The Explore API provides "what's around" information for a specific code element. It builds a relationship map of the symbol's neighborhood, including its siblings, dependencies, dependents, and hierarchical position. This API is designed to help Agents build a mental map of the code structure and discover related architectural context.

## When to Use
- **Building a mental map**: When an Agent first encounters a new class or module and needs to understand its role in the system.
- **Impact analysis**: When an Agent wants to see what other components depend on a specific class before making changes.
- **Discovering related code**: When an Agent is looking for similar implementations or helper classes in the same neighborhood.
- **Architectural context**: When an Agent needs to understand the "big picture" of how a component fits into the overall project structure.

## Key Differences from Hierarchy API
| Feature | Explore API | Hierarchy API |
|---------|-------------|---------------|
| **Scope** | Neighborhood & Relationships | Deep Tree Traversal |
| **Direction** | Multi-directional (Up, Down, Sideways) | Vertical (Parent/Child) |
| **Goal** | Contextual Mapping | Structural Navigation |
| **Content** | Siblings, Callers, Callees, Types | Call/Type Hierarchy Tree |

## Relationship Types
- **Siblings**: Other symbols defined in the same scope or file.
- **Dependencies**: Symbols that this symbol depends on.
- **Dependents**: Symbols that depend on this symbol.
- **Hierarchy**: Inheritance hierarchy (parents and children classes/interfaces).
- **Calls**: Call hierarchy information (incoming and outgoing calls).

## Request Schema
- `locate`: The target symbol to explore.
- `include`: (List of Strings) Which types of relationships to include. Options: `["siblings", "dependencies", "dependents", "hierarchy", "calls"]`. Default: `["siblings", "dependencies"]`.
- `max_items`: (Integer) Maximum number of items to return for each relationship type (1-50, default: 10).
- `resolve_info`: (Boolean) Whether to resolve detailed information for symbols (default: false).
- `include_external`: (Boolean) Whether to include external library symbols (default: false).

## Response Schema
- `target`: The symbol being explored (`SymbolInfo`).
- `siblings`: List of symbols defined in the same scope or file.
- `dependencies`: List of symbols that this symbol depends on.
- `dependents`: List of symbols that depend on this symbol.
- `hierarchy`: Optional inheritance hierarchy information with `parents` and `children`.
- `calls`: Optional call hierarchy information with `incoming` and `outgoing` calls.

## Example: Exploring a class
**Request:**
```json
{
  "locate": {
    "file_path": "src/models/user.py",
    "scope": {
      "symbol_path": ["User"]
    }
  },
  "include": ["hierarchy", "siblings", "calls"],
  "max_items": 10
}
```

**Response:**
```json
{
  "target": { 
    "name": "User", 
    "kind": "class",
    "file_path": "src/models/user.py",
    "path": ["User"]
  },
  "siblings": [
    { 
      "name": "UserRole", 
      "kind": "enum",
      "file_path": "src/models/user.py",
      "path": ["UserRole"]
    },
    { 
      "name": "AnonymousUser", 
      "kind": "class",
      "file_path": "src/models/user.py",
      "path": ["AnonymousUser"]
    }
  ],
  "hierarchy": {
    "parents": [
      {
        "name": "BaseModel",
        "kind": "class",
        "file_path": "src/models/base.py",
        "path": ["BaseModel"]
      }
    ],
    "children": [
      {
        "name": "AdminUser",
        "kind": "class",
        "file_path": "src/models/admin.py",
        "path": ["AdminUser"]
      }
    ]
  },
  "calls": {
    "incoming": [
      {
        "name": "authenticate",
        "kind": "function",
        "file_path": "src/services/auth.py",
        "range": { "start": { "line": 15, "character": 1 }, "end": { "line": 20, "character": 1 } }
      }
    ],
    "outgoing": []
  }
}
```

**Markdown Output:**
```markdown
# Explore: `User` (class)

## Siblings
- `UserRole` (enum)
- `AnonymousUser` (class)

## Hierarchy
### Parents
- `BaseModel` (class) in `src/models/base.py`

### Children
- `AdminUser` (class) in `src/models/admin.py`

## Call Hierarchy
### Incoming Calls
- `authenticate` (function) at `src/services/auth.py:15`
```

## See Also
- [Outline API](./outline.md)
- [Reference API](./reference.md)
