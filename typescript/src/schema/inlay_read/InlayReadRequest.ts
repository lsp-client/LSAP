import { z } from "zod";

export const InlayReadRequest = z.object({ "file_path": z.string(), "range": z.union([z.object({ "start": z.object({ "line": z.number().int(), "character": z.number().int() }), "end": z.object({ "line": z.number().int(), "character": z.number().int() }) }), z.null()]).default(null) });
