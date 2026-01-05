import { z } from "zod";

export const WorkspaceDiagnosticsRequest = z.object({ "max_items": z.union([z.number().int(), z.null()]).default(null), "start_index": z.number().int().default(0), "pagination_id": z.union([z.string(), z.null()]).default(null), "min_severity": z.enum(["Error","Warning","Information","Hint"]).default("Hint") }).describe("Retrieves diagnostics (errors, warnings, hints) across the entire workspace.\n\nUse this to get a high-level overview of project health and identify\nall existing issues.");
