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
- **Hierarchy**: The parent/child relationship (e.g., class members, module contents).
- **Calls**: Outgoing calls (dependencies) and incoming calls (dependents).
- **Types**: Type relationships (e.g., base classes, interface implementations).
- **Siblings**: Other symbols defined in the same scope or file.

## Request Schema
- `locate`: The target symbol to explore.
- `depth`: (Integer) How many levels of relationships to traverse (default: 1).
- `relationship_types`: (List of Strings) Which types of relationships to include (e.g., `["calls", "hierarchy", "siblings"]`).

## Response Schema
- `center`: The symbol at the center of the exploration.
- `relationships`: A structured map of related symbols grouped by relationship type.
- `summary`: A high-level description of the symbol's neighborhood.

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
  "relationship_types": ["hierarchy", "siblings", "calls"],
  "depth": 1
}
```

**Response:**
```json
{
  "center": { "name": "User", "kind": "class" },
  "relationships": {
    "hierarchy": [
      { "name": "User.validate", "kind": "method" },
      { "name": "User.save", "kind": "method" }
    ],
    "siblings": [
      { "name": "UserRole", "kind": "enum" },
      { "name": "AnonymousUser", "kind": "class" }
    ],
    "dependents": [
      { "name": "AuthService", "kind": "class", "file": "src/services/auth.py" }
    ]
  }
}
```

**Markdown Output:**
```markdown
# Explore: `User` (class)

`User` is a central model in `src/models/user.py`, primarily used by `AuthService`.

## Hierarchy (Members)
- `validate` (method)
- `save` (method)

## Siblings (In same file)
- `UserRole` (enum)
- `AnonymousUser` (class)

## Dependents (Used by)
- `AuthService` (src/services/auth.py)
```

## See Also
- [Outline API](./outline.md)
- [Reference API](./reference.md)
