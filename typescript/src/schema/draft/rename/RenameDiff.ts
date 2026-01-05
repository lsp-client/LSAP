import { z } from "zod";

export const RenameDiff = z.object({ "line": z.number().int(), "original": z.string(), "modified": z.string() });
