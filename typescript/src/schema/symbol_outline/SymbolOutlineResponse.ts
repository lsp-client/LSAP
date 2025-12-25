import { z } from "zod";

export const SymbolOutlineResponse = z.object({ "file_path": z.string(), "items": z.array(z.object({ "name": z.string(), "kind": z.string(), "range": z.object({ "start": z.object({ "line": z.number().int(), "character": z.number().int() }), "end": z.object({ "line": z.number().int(), "character": z.number().int() }) }), "children": z.array(z.any()).default([]), "symbol_content": z.union([z.string(), z.null()]).default(null) })) });

export const SymbolOutlineResponseTemplates = {
  "markdown": "\n### Symbol Outline for `{{ file_path }}`\n\n{%- macro render_item(item, depth=0) %}\n{{ \"  \" * depth }}- **{{ item.name }}** (`{{ item.kind }}`)\n{%- if item.symbol_content %}\n\n{{ \"  \" * (depth + 1) }}```{{ file_path.suffix[1:] if file_path.suffix else \"\" }}\n{{ item.symbol_content | indent(width=(depth + 1) * 2, first=True) }}\n{{ \"  \" * (depth + 1) }}```\n\n{%- endif %}\n{%- for child in item.children %}\n{{ render_item(child, depth + 1) }}\n{%- endfor %}\n{%- endmacro %}\n\n{%- for item in items %}\n{{ render_item(item) }}\n{%- endfor %}\n"
} as const;
