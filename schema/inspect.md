# Inspect API

## Overview
The Inspect API provides "how to use" information for a specific symbol. While the Symbol API focuses on "what it is" (implementation details), the Inspect API is designed to help Agents understand how to correctly call or interact with a symbol by providing its signature, documentation, and real-world usage examples.

## When to Use
- **Learning to call an API**: When an Agent needs to know the parameters, types, and return values of a function.
- **Understanding usage patterns**: When an Agent wants to see how other parts of the codebase call a specific method to avoid common mistakes.
- **Contextual documentation**: When the Agent needs a high-level summary of a symbol's purpose without reading the entire implementation.

## Key Differences from Symbol API
| Feature | Inspect API | Symbol API |
|---------|-------------|------------|
| **Primary Focus** | How to use the symbol | What the symbol is/does |
| **Content** | Signature, Docstring, Usage Examples | Full Source Code, Implementation |
| **Goal** | Integration & Calling | Understanding Implementation |
| **Context** | External perspective | Internal perspective |

## Request Schema
- `locate`: The target symbol to inspect (supports `file_path`, `symbol_path`, `find`, etc.).
- `include_usage`: (Boolean) Whether to include real-world usage examples from the codebase.
- `max_usage_examples`: (Integer) Maximum number of usage examples to return.

## Response Schema
- `symbol`: Basic information about the symbol (name, kind, location).
- `signature`: The formal signature of the symbol (e.g., function parameters and return types).
- `documentation`: The docstring or comments associated with the symbol.
- `usages`: A list of code snippets showing how the symbol is used elsewhere.

## Example: Inspecting a function
**Request:**
```json
{
  "locate": {
    "file_path": "src/utils/auth.py",
    "scope": {
      "symbol_path": ["verify_token"]
    }
  },
  "include_usage": true,
  "max_usage_examples": 2
}
```

**Response:**
```json
{
  "symbol": {
    "name": "verify_token",
    "kind": "function",
    "location": { "uri": "file:///src/utils/auth.py", "range": { ... } }
  },
  "signature": "def verify_token(token: str, secret: str = None) -> UserPayload",
  "documentation": "Verifies a JWT token and returns the decoded payload.\n\n:param token: The JWT string to verify.\n:param secret: Optional secret override.",
  "usages": [
    {
      "file_path": "src/api/middleware.py",
      "line": 42,
      "code": "payload = verify_token(auth_header.split(' ')[1])"
    }
  ]
}
```

**Markdown Output:**
```markdown
# Inspect: `verify_token`

**Signature:** `def verify_token(token: str, secret: str = None) -> UserPayload`

---

Verifies a JWT token and returns the decoded payload.

:param token: The JWT string to verify.
:param secret: Optional secret override.

## Usage Examples

### src/api/middleware.py:42
```python
41 |     auth_header = request.headers.get('Authorization')
42 |     payload = verify_token(auth_header.split(' ')[1])
43 |     request.user = payload
```

## See Also
- [Symbol API](./symbol.md)
- [Reference API](./reference.md)
