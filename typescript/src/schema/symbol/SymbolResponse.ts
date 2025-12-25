import { z } from "zod";

export const SymbolResponse = z.object({ "file_path": z.string(), "symbol_path": z.array(z.string()), "symbol_content": z.string() });

export const SymbolResponseTemplates = {
  "markdown": "\n### Symbol: `{{ symbol_path | join('.') }}` in `{{ file_path }}`\n\n```\n{{ symbol_content }}\n```\n"
} as const;
