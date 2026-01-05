import { z } from "zod";

export const InlineValueItem = z.object({ "line": z.number().int(), "text": z.string() });
