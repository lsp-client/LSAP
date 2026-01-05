import { z } from "zod";

export const WorkspaceSymbolResponse = z.object({ "query": z.string(), "items": z.array(z.object({ "name": z.string(), "kind": z.string(), "file_path": z.string(), "range": z.object({ "start": z.object({ "line": z.number().int(), "character": z.number().int() }), "end": z.object({ "line": z.number().int(), "character": z.number().int() }) }), "container_name": z.union([z.string(), z.null()]).default(null) })), "offset": z.number().int(), "limit": z.union([z.number().int(), z.null()]).default(null), "total": z.union([z.number().int(), z.null()]).default(null), "has_more": z.boolean().default(false) });

export const WorkspaceSymbolResponseTemplates = {
  "markdown": "\n### Workspace Symbols matching `{{ query }}`\n{% if total is not none -%}\n**Total found**: {{ total }} | **Showing**: {{ items | length }}{% if limit %} (Offset: {{ offset }}, Limit: {{ limit }}){% endif %}\n{%- endif %}\n\n{% if not items -%}\nNo symbols found matching the query.\n{%- else -%}\n{%- for item in items %}\n- **{{ item.name }}** (`{{ item.kind }}`) in `{{ item.file_path }}` {% if item.container_name %}(in `{{ item.container_name }}`){% endif %}\n{%- endfor %}\n\n{% if has_more -%}\n---\n> [!TIP]\n> **More results available.**\n> To fetch the next page, specify a `limit` and use: `offset={{ offset + (limit or items|length) }}`\n{%- endif %}\n{%- endif %}\n"
} as const;
