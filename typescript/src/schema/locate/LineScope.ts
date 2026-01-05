import { z } from "zod";

export const LineScope = z.object({ "line": z.union([z.number().int(), z.array(z.any()).min(2).max(2)]) }).describe("Scope by line range");
