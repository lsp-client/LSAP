sync:
    uv sync --upgrade

# Export JSON schemas from Python
schema-json output:
    uv run -m lsap.schema -o {{output}}

# Generate Zod schemas from JSON schemas
schema-zod:
    cd typescript && bun run scripts/gen-zod.ts
