import { z } from "zod";

export const ReferenceResponse = z.object({ "items": z.array(z.object({ "file_path": z.string(), "symbol_path": z.array(z.string()), "symbol_content": z.string() })) });

export const ReferenceResponseTemplates = {
  "markdown": "{% for item in items -%}\n- `{{ item.file_path }}` - `{{ item.symbol_path | join('.') }}`\n```python\n{{ item.symbol_content }}\n```\n{% if not loop.last %}\n{% endif %}\n{%- endfor %}"
} as const;
