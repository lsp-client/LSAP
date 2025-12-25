import { z } from "zod";

export const RenameRequest = z.object({ "locate": z.union([z.object({ "file_path": z.string(), "line": z.union([z.number().int(), z.array(z.any()).min(2).max(2)]), "find": z.string(), "position": z.enum(["start","end"]).default("start") }), z.object({ "file_path": z.string(), "symbol_path": z.array(z.string()) }).describe("Locate by symbol path")]), "new_name": z.string() }).describe("Renames a symbol throughout the entire workspace.\n\nUse this to safely rename variables, functions, or classes across all files\nwhere they are referenced.");
