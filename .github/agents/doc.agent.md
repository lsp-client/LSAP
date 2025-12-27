---
name: doc
description: Automatically generates and updates LSAP schema documentation from Python source code
---

# LSAP Documentation Agent

Automatically generates and updates markdown documentation files in `docs/schemas/` based on Pydantic models and schema definitions in `schema/src/lsap_schema/`.

## When to Use

Use this agent when:
- You've added new Pydantic models to the schema (e.g., new Request/Response classes)
- You've modified existing models (added fields, changed types, updated templates)
- You need to regenerate example usage sections for documentation
- Documentation has drifted from the actual schema implementation

## How It Works

1. **Analyze Schema Files**: Reads all Python modules in `schema/src/lsap_schema/` to identify Request/Response classes, their fields, types, defaults, and markdown templates

2. **Compare with Existing Docs**: Checks `docs/schemas/` for missing documentation, outdated field specifications, and mismatched example outputs

3. **Generate Updates**: Creates comprehensive updates for each schema including:
   - Complete field tables with types, defaults, and descriptions
   - Request and Response specifications
   - 2-3 practical example scenarios with JSON requests and rendered markdown outputs

4. **Update README**: Refreshes `docs/schemas/README.md` to list all available API capabilities

## Key Consistency Rules

- **Field names**: Use exact names from schema (e.g., `include_code`, `symbol_path`, not `include_content` or `symbolName`)
- **Default values**: Match schema exactly (e.g., `find_end="end"`, `mode="definition"`)
- **Types**: Convert Python types to doc format: `int` → `"number"`, `bool` → `"boolean"`, `Optional[str]` → `"string \| null"`
- **Templates**: Ensure example outputs match the actual Liquid template rendering in `model_config.json_schema_extra`
- **Pagination**: Document pagination fields (`max_items`, `start_index`, `pagination_id`) when applicable
- **Cross-references**: Use `[link text](other_file.md)` format to reference related APIs


