import { z } from "zod";

export const WorkspaceSymbolItem = z.object({ "name": z.string(), "kind": z.string(), "file_path": z.string(), "range": z.object({ "start": z.object({ "line": z.number().int(), "character": z.number().int() }), "end": z.object({ "line": z.number().int(), "character": z.number().int() }) }), "container_name": z.union([z.string(), z.null()]).default(null) });
