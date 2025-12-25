import { z } from "zod";

export const SymbolOutlineResponse = z.object({ "file_path": z.string(), "items": z.array(z.object({ "name": z.string(), "kind": z.string(), "range": z.object({ "start": z.object({ "line": z.number().int(), "character": z.number().int() }), "end": z.object({ "line": z.number().int(), "character": z.number().int() }) }), "children": z.array(z.any()).default([]) })) });

export const SymbolOutlineResponseTemplates = {
  "markdown": "\n### Symbol Outline for `{{ file_path }}`\n\n{%- macro render_item(item, depth=0) %}\n{{ \"  \" * depth }}- **{{ item.name }}** (`{{ item.kind }}`)\n{%- for child in item.children %}\n{{ render_item(child, depth + 1) }}\n{%- endfor %}\n{%- endmacro %}\n\n{%- for item in items %}\n{{ render_item(item) }}\n{%- endfor %}\n"
} as const;
