import { z } from "zod";

export const SymbolResponse = z.object({ "file_path": z.string(), "symbol_path": z.array(z.string()), "symbol_content": z.string() });

export const SymbolResponseTemplates = {
  "markdown": "### Symbol: `{{ symbol_path | join('.') }}` in `{{ file_path }}`\n\n```python\n{{ symbol_content }}\n```"
} as const;
