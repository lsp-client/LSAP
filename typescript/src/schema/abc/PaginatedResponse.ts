import { z } from "zod";

export const PaginatedResponse = z.object({ "start_index": z.number().int(), "max_items": z.union([z.number().int(), z.null()]).default(null), "total": z.union([z.number().int(), z.null()]).default(null), "has_more": z.boolean().default(false), "pagination_id": z.union([z.string(), z.null()]).default(null) });
