import { z } from "zod";

export const InlineValueRequest = z.object({ "file_path": z.string(), "range": z.object({ "start": z.object({ "line": z.number().int(), "character": z.number().int() }), "end": z.object({ "line": z.number().int(), "character": z.number().int() }) }) }).describe("Retrieves runtime or contextual values for variables in a range.\n\nUse this when debugging or inspecting code to see the actual values\nof variables at specific lines.");
