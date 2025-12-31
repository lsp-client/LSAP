# LSAP: Language Server Agent Protocol

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Protocol Version](https://img.shields.io/badge/Protocol-v1.0.0--alpha-blue.svg)]()

LSAP is an open protocol that defines how AI coding agents interact with Language Servers. Each LSAP capability is designed to be exposed as an **agent tool** - the agent calls it via function calling, and receives Markdown output ready for reasoning.

```
┌──────────────┐    function call     ┌──────────────┐      LSP       ┌──────────────┐
│   AI Agent   │ ──────────────────►  │  LSAP Tool   │ ─────────────► │   Language   │
│              │ ◄──────────────────  │              │ ◄───────────── │   Server     │
└──────────────┘    markdown output   └──────────────┘                └──────────────┘
```

This repository contains the protocol specification and a Python reference implementation.

---

## How It Works

LSAP capabilities are exposed as tools that agents can call. For example, the `Symbol` capability:

**Tool Definition** (JSON Schema):

```json
{
  "name": "get_symbol",
  "description": "Get the source code and documentation of a symbol",
  "parameters": {
    "type": "object",
    "properties": {
      "file_path": { "type": "string" },
      "symbol_path": { "type": "array", "items": { "type": "string" } }
    }
  }
}
```

**Agent calls the tool**:

```json
{
  "name": "get_symbol",
  "arguments": {
    "file_path": "src/auth.py",
    "symbol_path": ["UserService", "authenticate"]
  }
}
```

**Tool returns Markdown** (directly usable by the agent):

````markdown
# Symbol: `UserService.authenticate` (`Method`) at `src/auth.py`

## Implementation

```python
def authenticate(self, username: str, password: str) -> Optional[User]:
    """Verify user credentials and return user if valid."""
    user = self.db.get_user(username)
    if user and user.check_password(password):
        return user
    return None
```
````

````

The agent receives structured, readable context without needing to parse JSON or understand LSP internals.

---

## Why Not Raw LSP?

Raw LSP requires `line:column` coordinates and returns fragmented JSON:

```python
# Agent would need to: read file → find line number → call LSP → parse response → format output
# This is error-prone and wastes tokens on coordinate calculation
````

LSAP lets agents reference code by **symbol names** and get **complete, formatted context** in one call.

| LSP                              | LSAP                                 |
| :------------------------------- | :----------------------------------- |
| `Position(line=42, character=8)` | `symbol_path: ["MyClass", "method"]` |
| Multiple round-trips             | Single request                       |
| Raw JSON for IDEs                | Markdown for LLMs                    |

---

## Capabilities (Agent Tools)

Each capability is a tool the agent can call:

### Stable

| Tool                   | What the agent gets                           | Spec                                   |
| :--------------------- | :-------------------------------------------- | :------------------------------------- |
| **get_symbol**         | Source code, signature, docstring of a symbol | [docs](docs/schemas/symbol.md)         |
| **get_symbol_outline** | List of all symbols in a file                 | [docs](docs/schemas/symbol_outline.md) |
| **get_references**     | All locations where a symbol is used          | [docs](docs/schemas/reference.md)      |
| **get_hover**          | Documentation/type info at a position         | [docs](docs/schemas/hover.md)          |
| **get_definition**     | Where a symbol is defined                     | [docs](docs/schemas/definition.md)     |
| **search_workspace**   | Find symbols by name across the project       | [docs](docs/schemas/workspace.md)      |

### Experimental

| Tool                   | Status | Spec                                         |
| :--------------------- | :----- | :------------------------------------------- |
| **get_call_hierarchy** | Beta   | [docs](docs/schemas/draft/call_hierarchy.md) |
| **get_type_hierarchy** | Beta   | [docs](docs/schemas/draft/type_hierarchy.md) |
| **get_diagnostics**    | Alpha  | [docs](docs/schemas/draft/diagnostics.md)    |
| **rename_symbol**      | Alpha  | [docs](docs/schemas/draft/rename.md)         |
| **get_inlay_hints**    | Alpha  | [docs](docs/schemas/draft/inlay_hints.md)    |
| **get_completions**    | Alpha  | [docs](docs/schemas/completion.md)           |

Full spec: [docs/schemas/README.md](docs/schemas/README.md)

---

## Locate: How Agents Reference Code

LSAP's `Locate` abstraction lets agents reference code without coordinates:

```json
// By symbol path - "get the authenticate method in UserService"
{"symbol_path": ["UserService", "authenticate"]}

// By text pattern - "find where we call self.db"
{"text": "self.db.<HERE>"}

// By scope - "lines 10-20 inside the main function"
{"scope": {"symbol_path": ["main"]}, "line": [10, 20]}
```

---

## Example: Agent Workflow

A coding agent reviewing a function might:

1. **Call `get_symbol`** to get the function's implementation
2. **Call `get_references`** to see how it's used
3. **Reason** over the Markdown output to identify issues

```
Agent: I need to review the handle_request function.

→ Tool call: get_symbol(file_path="api.py", symbol_path=["handle_request"])
← Returns: markdown with source code

→ Tool call: get_references(file_path="api.py", symbol_path=["handle_request"])
← Returns: markdown with all call sites

Agent: Based on the implementation and usage, I found a potential SQL injection...
```

The agent never deals with line numbers or JSON parsing - it receives context in a format it can directly reason over.

---

## Comparison with Other Approaches

|                    | Claude Code | Serena      | Cursor      | Aider | LSAP          |
| :----------------- | :---------- | :---------- | :---------- | :---- | :------------ |
| **Type**           | Proprietary | MCP server  | IDE feature | CLI   | Open protocol |
| **Position model** | Coordinates | Coordinates | Coordinates | Text  | Symbol paths  |
| **Output format**  | JSON        | Custom      | Internal    | Text  | Markdown      |
| **Cold start**     | Low         | High        | Low         | Low   | Low           |
| **Type precision** | Yes         | Yes         | No          | No    | Yes           |

LSAP is a protocol specification, not a product. The schema is open and can be implemented for any agent framework.

---

## Reference Implementation

This repo includes a Python implementation you can use directly or as a reference:

```bash
pip install lsap lsp-client
```

```python
from lsap.symbol import SymbolCapability
from lsap_schema import SymbolRequest
from lsp_client.clients.pyright import PyrightClient

async def main():
    async with PyrightClient() as client:
        symbol = SymbolCapability(client)

        response = await symbol(SymbolRequest(
            locate={
                "file_path": "src/main.py",
                "symbol_path": ["MyClass", "my_method"]
            }
        ))

        if response:
            print(response.markdown)
```

TypeScript schemas are also available:

```bash
npm install @lsap/schema
```

---

## Project Structure

```
LSAP/
├── src/lsap_schema/     # Protocol schema (Pydantic) - source of truth
├── python/src/lsap/     # Python reference implementation
├── typescript/          # TypeScript/Zod schemas (generated)
├── docs/schemas/        # Capability specifications
└── web/                 # Documentation viewer
```

Schema generation: `just codegen` (Python → JSON Schema → TypeScript)

---

## License

MIT - see [LICENSE](LICENSE)
