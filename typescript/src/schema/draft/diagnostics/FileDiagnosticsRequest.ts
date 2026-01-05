import { z } from "zod";

export const FileDiagnosticsRequest = z.object({ "max_items": z.union([z.number().int(), z.null()]).default(null), "start_index": z.number().int().default(0), "pagination_id": z.union([z.string(), z.null()]).default(null), "file_path": z.string(), "min_severity": z.enum(["Error","Warning","Information","Hint"]).default("Hint") }).describe("Retrieves diagnostics (errors, warnings, hints) for a specific file.\n\nUse this after making changes to verify code correctness or to identify\npotential issues and linting errors.");
