# LSAP Schema Documentation

This directory contains the specifications for the LLM-friendly LSP (Language Server Protocol) data models used in LSAP.

## Core Capabilities

- [**Locate**](locate.md): Resolve text snippets or symbol paths to exact file coordinates.
- [**Symbol**](symbol.md): Retrieve detailed information, documentation, and source code for specific symbols.
- [**Symbol Outline**](symbol_outline.md): Get a hierarchical overview of all symbols in a file.
- [**Workspace**](workspace.md): Global search for symbols across the entire project with pagination.
- [**Reference**](reference.md): Find all usages of a symbol in the project.
- [**Implementation**](implementation.md): Find concrete implementations of interfaces or abstract methods.
- [**Call Hierarchy**](call_hierarchy.md): Trace incoming and outgoing function call relationships.
- [**Type Hierarchy**](type_hierarchy.md): Explore inheritance relationships (supertypes and subtypes).
- [**Diagnostics**](diagnostics.md): Access linting issues and syntax errors.
- [**Inlay Hints & Inline Values**](inlay_hints.md): Read code with static hints and runtime values injected.

## Design Principles

1. **LLM Friendly**: All responses include a `markdown` template defined in the schema, allowing Agents to receive information in a format they can easily parse and reason about.
2. **Standardized Pagination**: Large result sets (Workspace, References, Diagnostics) support optional `limit` and `offset` parameters with proactive instructions for fetching the next page.
3. **Context Rich**: Where possible, related information is aggregated (e.g., Symbol responses include both documentation and source code) to reduce the number of round-trips an Agent needs to make.
