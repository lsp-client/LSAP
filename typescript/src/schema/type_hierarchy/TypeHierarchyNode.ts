import { z } from "zod";

export const TypeHierarchyNode = z.object({ "id": z.string(), "name": z.string(), "kind": z.string(), "file_path": z.string(), "range_start": z.object({ "line": z.number().int(), "character": z.number().int() }), "detail": z.union([z.string(), z.null()]).default(null) });
