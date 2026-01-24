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
| **Content** | Signature, Documentation, Usage Examples | Full Source Code, Implementation |
| **Goal** | Integration & Calling | Understanding Implementation |
| **Context** | External perspective | Internal perspective |

## Request Schema
- `locate`: The target symbol to inspect (supports `file_path`, `symbol_path`, `find`, etc.).
- `include_examples`: (Integer) Number of usage examples to include (0-20, default: 3).
- `include_signature`: (Boolean) Whether to include the symbol's signature (default: true).
- `include_doc`: (Boolean) Whether to include the symbol's documentation/hover content (default: true).
- `include_call_hierarchy`: (Boolean) Whether to include call hierarchy information (default: false).
- `include_external`: (Boolean) Whether to include examples from external libraries (default: false).
- `context_lines`: (Integer) Number of context lines around usage examples (0-10, default: 2).

## Response Schema
- `info`: Detailed information about the symbol (`SymbolDetailInfo` with name, kind, location, hover).
- `signature`: The formal signature of the symbol (e.g., function parameters and return types).
- `examples`: A list of usage examples showing how the symbol is used elsewhere, with code, location, context, and call pattern.
- `call_hierarchy`: Optional call hierarchy information showing incoming and outgoing calls.

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
  "include_examples": 2,
  "include_signature": true,
  "include_doc": true
}
```

**Response:**
```json
{
  "info": {
    "name": "verify_token",
    "kind": "function",
    "file_path": "src/utils/auth.py",
    "path": ["verify_token"],
    "range": { "start": { "line": 10, "character": 1 }, "end": { "line": 15, "character": 1 } },
    "hover": "Verifies a JWT token and returns the decoded payload.\n\n:param token: The JWT string to verify.\n:param secret: Optional secret override."
  },
  "signature": "def verify_token(token: str, secret: str = None) -> UserPayload",
  "examples": [
    {
      "code": "payload = verify_token(auth_header.split(' ')[1])",
      "location": {
        "file_path": "src/api/middleware.py",
        "range": { "start": { "line": 42, "character": 5 }, "end": { "line": 42, "character": 55 } }
      },
      "context": {
        "name": "authenticate",
        "kind": "function",
        "file_path": "src/api/middleware.py",
        "path": ["authenticate"]
      },
      "call_pattern": "verify_token(auth_header.split(' ')[1])"
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
