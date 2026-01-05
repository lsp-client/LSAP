sync:
    uv sync --upgrade

# Export JSON schemas from Python
schema-json output:
    cd schema && uv run -m lsap_schema -o {{output}}

# Generate Zod schemas from JSON schemas
schema-zod:
    cd typescript && bun run scripts/gen-zod.ts

# Run full codegen pipeline
codegen: (schema-json "../typescript/schemas") schema-zod
