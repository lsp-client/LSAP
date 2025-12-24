import { z } from "zod";

export const LocateResponse = z.object({ "file_path": z.string(), "position": z.object({ "line": z.number().int(), "character": z.number().int() }) });

export const LocateResponseTemplates = {
  "markdown": "Located `{{ file_path }}` at {{ position.line + 1 }}:{{ position.character + 1 }}"
} as const;
