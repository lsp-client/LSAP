import { z } from "zod";

export const CompletionResponse = z.object({ "items": z.array(z.object({ "label": z.string(), "kind": z.string(), "detail": z.union([z.string(), z.null()]).default(null), "documentation": z.union([z.string(), z.null()]).default(null), "insert_text": z.union([z.string(), z.null()]).default(null) })) });

export const CompletionResponseTemplates = {
  "markdown": "\n### Code Completion at the requested location\n\n{% if not items -%}\nNo completion suggestions found.\n{%- else -%}\n| Symbol | Kind | Detail |\n| :--- | :--- | :--- |\n{%- for item in items %}\n| `{{ item.label }}` | {{ item.kind }} | {{ item.detail or \"\" }} |\n{%- endfor %}\n\n{% if items[0].documentation %}\n#### Top Suggestion Detail: `{{ items[0].label }}`\n{{ items[0].documentation }}\n{% endif %}\n\n---\n> [!TIP]\n> Use these symbols to construct your next code edit. You can focus on a specific method to get more details.\n{%- endif %}\n"
} as const;
