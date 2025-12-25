import { z } from "zod";

export const InlayHintRequest = z.object({ "file_path": z.string(), "range": z.union([z.object({ "start": z.object({ "line": z.number().int(), "character": z.number().int() }), "end": z.object({ "line": z.number().int(), "character": z.number().int() }) }), z.null()]).default(null) }).describe("Retrieves inline hints like parameter names or inferred types.\n\nUse this to get better context for code by seeing \"hidden\" details\nthat are normally provided by an IDE's visual overlay.");
