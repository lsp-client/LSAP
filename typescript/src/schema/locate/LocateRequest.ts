import { z } from "zod";

export const LocateRequest = z.object({ "locate": z.union([z.object({ "file_path": z.string(), "line": z.union([z.number().int(), z.array(z.any()).min(2).max(2)]), "find": z.string(), "position": z.enum(["start","end"]).default("start") }), z.object({ "file_path": z.string(), "symbol_path": z.array(z.string()) }).describe("Locate by symbol path")]) }).describe("Base request for locating code positions.\n\nUse this when you need to specify a target location by either a text search or a symbol path.");
