import { z } from "zod";

export const CallGraphRequest = z.object({ "locate": z.union([z.object({ "file_path": z.string(), "line": z.union([z.number().int(), z.array(z.any()).min(2).max(2)]), "find": z.string(), "position": z.enum(["start","end"]).default("start") }), z.object({ "file_path": z.string(), "symbol_path": z.array(z.string()) }).describe("Locate by symbol path")]), "direction": z.enum(["incoming","outgoing","both"]).default("both"), "depth": z.number().int().default(2), "include_external": z.boolean().default(false) });
