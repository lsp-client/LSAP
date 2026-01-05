import { z } from "zod";

export const PaginatedRequest = z.object({ "max_items": z.union([z.number().int(), z.null()]).default(null), "start_index": z.number().int().default(0), "pagination_id": z.union([z.string(), z.null()]).default(null) }).describe("Base request for paginated results.");
