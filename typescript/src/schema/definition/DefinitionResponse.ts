import { z } from "zod";

export const DefinitionResponse = z.object({ "file_path": z.string(), "symbol_path": z.array(z.string()), "symbol_content": z.union([z.string(), z.null()]).default(null), "hover": z.union([z.string(), z.null()]).default(null), "parameters": z.union([z.array(z.object({ "name": z.string(), "label": z.string(), "documentation": z.union([z.string(), z.null()]).default(null) })), z.null()]).default(null) });

export const DefinitionResponseTemplates = {
  "markdown": "\n### Navigation Result\n\n{% if hover -%}\n#### Documentation\n{{ hover }}\n{%- endif %}\n\n{% if symbol_content -%}\n#### Implementation / Declaration\n```python\n{{ symbol_content }}\n```\n{%- endif %}\n"
} as const;
