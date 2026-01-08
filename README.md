# LSAP: Language Server Agent Protocol

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Protocol Version](https://img.shields.io/badge/Protocol-v1.0.0--alpha-blue.svg)]()

**LSAP (Language Server Agent Protocol)** transforms low-level LSP capabilities into high-level, **Agent-Native** cognitive tools, empowering Coding Agents with **Repository-Scale Intelligence**.

As an **Orchestration Layer**, LSAP composes atomic LSP operations into semantic interfaces. This aligns with Agent cognitive logic, allowing them to focus on high-level "intent realization" rather than tedious "editor operations."

## Core Concept: Atomic Capabilities vs. Cognitive Capabilities

The core difference of LSAP lies in how it defines "capabilities." LSP is designed for editors, providing **Atomic** operations; whereas LSAP is designed for Agents, providing **Cognitive** capabilities.

- **LSP (Editor Perspective - Atomic)**:
  - Editors require very low-level instructions: `textDocument/definition` (jump), `textDocument/hover` (hover), `textDocument/documentSymbol` (outline).
  - **The Agent's Dilemma**: If an Agent uses LSP directly, it needs to execute a dozen interactions sequentially like a script (open file -> calculate offset -> request definition -> parse URI -> read file -> extract snippet) just to get a useful context.
- **LSAP (Agent Perspective - Cognitive)**:
  - LSAP encapsulates the complex chain of atomic operations above into a single semantic instruction.
  - **Example**: A single request to "Find all references" triggers background execution of symbol localization, reference search, and context extraction, returning a consolidated **Markdown Report**.

```mermaid
sequenceDiagram
    participant Agent as 🤖 Agent
    participant LSAP as 🧠 LSAP Layer
    participant LSP as 🔧 Language Server

    Note left of Agent: Goal: Find all references of "User"

    Agent->>LSAP: 1. Semantic Request (Locate + References)

    rect rgb(245, 245, 245)
        Note right of LSAP: ⚡️ Auto Orchestration
        LSAP->>LSAP: Parse Semantic Anchor (Fuzzy Match)
        LSAP->>LSP: textDocument/hover (Confirm Symbol Info)
        LSAP->>LSP: textDocument/references (Get Reference List)
        LSP-->>LSAP: Return List<Location>

        loop For each reference point
            LSAP->>LSP: textDocument/documentSymbol (Identify Function/Class)
            LSAP->>LSAP: Read Surrounding Code (Context Lines)
        end
    end

    LSAP-->>Agent: 2. Structured Markdown (Callers + Code Context)
```

## Interaction Example

LSAP's interaction design strictly follows the **Markdown-First** principle: input expresses intent, and output provides refined knowledge.

### Request: Semantic Search (Demonstrating Composed Capabilities)

The Agent only needs to issue a high-level command without worrying about underlying row/column calculations or file reading:

```jsonc
// Intent: Find all usages of 'DateUtil.format_date' to refactor it
{
  "locate": {
    "file_path": "src/utils.py",
    // we can find the def ...
    "find": "def format_date<|>", // use `<|>` to identify the exact position
    // ... or we can use locate
    "locate": "DateUtil.format_date", // use hierarchical path to identify symbol
  },
  "mode": "references",
  "max_items": 10,
}
```

### Response: Structured Knowledge

LSAP aggregates the results of `references` (locations), `documentSymbol` (caller context), and `read` (code snippets):

````markdown
# References Found

Total references: 45 | Showing: 2

### `src/ui/header.py`:28

In `Header.render` (`Method`)

```python
formatted = format_date(user.last_login)
```

### `src/api/views.py`:42

In `UserDetail.get` (`Method`)

```python
return {"date": format_date(obj.created_at)}
```
````

## I'm Not Convinced...

### "LSAP Just Replicates LSP—What's Special?"

While LSP provides **atomic operations**, LSAP offers **composed capabilities**.

For instance, the **[Relation API](docs/schemas/draft/relation.md)** finds call paths between functions in a single request (handling traversal, cycles, and formatting), a task requiring complex orchestration in raw LSP. Similarly, the **[Unified Hierarchy API](docs/schemas/draft/hierarchy.md)** delivers unified graph representations optimized for agents.

LSAP centralizes these patterns, preventing agents from wasting tokens on orchestration and enabling advanced capabilities like architectural and impact analysis.

### "This Adds Complexity"

LSAP **centralizes** complexity. Instead of every Agent reimplementing LSP orchestration logic, LSAP provides a shared, optimized layer for these common patterns.

## Project Structure

- [`docs/`](docs/): Core protocol definitions and Schema documentation.
- [`python/`](python/): Python SDK reference implementation.
- [`typescript/`](typescript/): TypeScript type definitions and utility library.
- [`web/`](web/): Protocol documentation site.

## Alternatives

### Claude Code

Claude Code have native LSP supports now - Well [they don't](https://www.reddit.com/r/ClaudeAI/comments/1q6q9my/claudecode_v210_just_dropped/)

### Serena

[serena](https://github.com/oraios/serena) is a powerful coding agent toolkit providing semantic retrieval and editing capabilities.

### Other Projects

- [claude-code-lsps](https://github.com/Piebald-AI/claude-code-lsps)
- [cclsp](https://github.com/ktnyt/cclsp)
- [mcpls](https://github.com/bug-ops/mcpls)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on development workflows and design principles.

## License

[MIT](LICENSE)
