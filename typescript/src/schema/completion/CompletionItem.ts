import { z } from "zod";

export const CompletionItem = z.object({ "label": z.string(), "kind": z.string(), "detail": z.union([z.string(), z.null()]).default(null), "documentation": z.union([z.string(), z.null()]).default(null), "insert_text": z.union([z.string(), z.null()]).default(null) });
