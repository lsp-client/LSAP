import { z } from "zod";

export const SymbolResponse = z.object({ "file_path": z.string(), "symbol_path": z.array(z.string()), "symbol_content": z.union([z.string(), z.null()]).default(null), "hover": z.union([z.string(), z.null()]).default(null), "parameters": z.union([z.array(z.object({ "name": z.string(), "label": z.string(), "documentation": z.union([z.string(), z.null()]).default(null) })), z.null()]).default(null) });

export const SymbolResponseTemplates = {
  "markdown": "\n### Symbol: `{{ symbol_path | join('.') }}` in `{{ file_path }}`\n\n{% if hover -%}\n#### Overview\n{{ hover }}\n{%- endif %}\n\n{% if parameters -%}\n#### Parameters\n| Parameter | Description |\n| :--- | :--- |\n{%- for p in parameters %}\n| `{{ p.label }}` | {{ p.documentation or \"\" }} |\n{%- endfor %}\n{%- endif %}\n\n{% if symbol_content -%}\n#### Implementation\n```python\n{{ symbol_content }}\n```\n{%- endif %}\n"
} as const;
