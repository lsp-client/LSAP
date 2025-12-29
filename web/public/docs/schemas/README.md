# LSAP Schema Documentation

This directory contains the specifications for the LLM-friendly LSP (Language Server Protocol) data models used in LSAP.

## Core Capabilities

- [**Locate**](locate.md): Resolve text snippets or symbol paths to exact file coordinates.
- [**Symbol**](symbol.md): Retrieve detailed information, documentation, and source code for specific symbols.
- [**Symbol Outline**](symbol_outline.md): Get a hierarchical overview of all symbols in a file.
- [**Definition**](definition.md): Navigate from a symbol usage to its declaration or definition.
- [**Hover**](hover.md): Quick access to documentation and type information at a specific location.
- [**Workspace**](workspace.md): Global search for symbols across the entire project with pagination.
- [**Completion**](completion.md): Get code completion suggestions at a specific position.
- [**Reference**](reference.md): Find all usages of a symbol in the project.
- [**Implementation**](implementation.md): Find concrete implementations of interfaces or abstract methods.
- [**Call Hierarchy**](call_hierarchy.md): Trace incoming and outgoing function call relationships.
- [**Type Hierarchy**](type_hierarchy.md): Explore inheritance relationships (supertypes and subtypes).
- [**Diagnostics**](diagnostics.md): Access linting issues and syntax errors.
- [**Rename**](rename.md): Preview and execute safe workspace-wide symbol renaming.
- [**Inlay Hints & Inline Values**](inlay_hints.md): Read code with static hints and runtime values injected.

## Design Principles

1. **LLM Friendly**: All responses include a `markdown` template defined in the schema, allowing Agents to receive information in a format they can easily parse and reason about.
2. **Standardized Pagination**: Large result sets (Workspace, References, Diagnostics) support optional `max_items` and `start_index` parameters with optional `pagination_id` tokens, and include proactive instructions for fetching the next page.

### PaginatedRequest

| Field           | Type             | Default | Description                                 |
| :-------------- | :--------------- | :------ | :------------------------------------------ |
| `max_items`     | `number \| null` | `null`  | Maximum number of results to return.        |
| `start_index`   | `number`         | `0`     | Number of results to skip for pagination.   |
| `pagination_id` | `string \| null` | `null`  | Token to retrieve the next page of results. |

### PaginatedResponse

| Field           | Type      | Description                                   |
| :-------------- | :-------- | :-------------------------------------------- |
| `start_index`   | `number`  | Offset of the current page.                   |
| `max_items`     | `number?` | Number of items per page (if specified).      |
| `total`         | `number?` | Total number of matches found (if available). |
| `has_more`      | `boolean` | Whether more results are available.           |
| `pagination_id` | `string?` | Token for retrieving the next page.           |

3. **Context Rich**: Where possible, related information is aggregated (e.g., Symbol responses include both documentation and source code) to reduce the number of round-trips an Agent needs to make.
