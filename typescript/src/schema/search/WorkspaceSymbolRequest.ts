import { z } from "zod";

export const WorkspaceSymbolRequest = z.object({ "query": z.string(), "limit": z.union([z.number().int(), z.null()]).default(null), "offset": z.number().int().default(0) }).describe("Searches for symbols across the entire workspace by name.\n\nUse this when you know the name of a symbol (or part of it) but don't know\nwhich file it is defined in.");
