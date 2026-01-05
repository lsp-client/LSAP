import { z } from "zod";

export const RenameFileChange = z.object({ "file_path": z.string(), "occurrences": z.number().int(), "diffs": z.array(z.object({ "line": z.number().int(), "original": z.string(), "modified": z.string() })).optional() });
