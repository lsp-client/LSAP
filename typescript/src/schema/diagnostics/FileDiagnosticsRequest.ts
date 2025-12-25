import { z } from "zod";

export const FileDiagnosticsRequest = z.object({ "file_path": z.string(), "min_severity": z.enum(["Error","Warning","Information","Hint"]).default("Hint"), "limit": z.union([z.number().int(), z.null()]).default(null), "offset": z.number().int().default(0) }).describe("Retrieves diagnostics (errors, warnings, hints) for a specific file.\n\nUse this after making changes to verify code correctness or to identify\npotential issues and linting errors.");
