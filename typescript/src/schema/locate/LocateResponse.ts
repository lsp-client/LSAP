import { z } from "zod";

export const LocateResponse = z.object({ "file_path": z.string(), "position": z.object({ "line": z.number().int().gte(1), "character": z.number().int().gte(1) }).describe("Represents a specific position in a file using line and character numbers.\n\nNote: Line and character are 1-based indices. 0-based indices are used in LSP, so conversion is needed when interfacing with LSP.") });

export const LocateResponseTemplates = {
  "markdown": "Located `{{ file_path }}` at {{ position.line }}:{{ position.character }}"
} as const;
