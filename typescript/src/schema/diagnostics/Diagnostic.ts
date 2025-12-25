import { z } from "zod";

export const Diagnostic = z.object({ "range": z.object({ "start": z.object({ "line": z.number().int(), "character": z.number().int() }), "end": z.object({ "line": z.number().int(), "character": z.number().int() }) }), "severity": z.enum(["Error","Warning","Information","Hint"]), "message": z.string(), "source": z.union([z.string(), z.null()]).default(null), "code": z.union([z.string(), z.number().int(), z.null()]).default(null) });
