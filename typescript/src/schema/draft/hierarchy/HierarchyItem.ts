import { z } from "zod";

export const HierarchyItem = z.object({ "name": z.string(), "kind": z.string(), "file_path": z.string(), "level": z.number().int(), "detail": z.union([z.string(), z.null()]).default(null), "is_cycle": z.boolean().default(false) }).describe("Represents an item in a flattened hierarchy tree for rendering.\n\nApplicable to any hierarchical relationship.");
