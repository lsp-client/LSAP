import { z } from "zod";

export const LocateText = z.object({ "file_path": z.string(), "line": z.union([z.number().int(), z.array(z.any()).min(2).max(2)]), "find": z.string(), "position": z.enum(["start","end"]).default("start") });
