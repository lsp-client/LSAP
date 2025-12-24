import { z } from "zod";

export const Position = z.object({ "line": z.number().int(), "character": z.number().int() });
