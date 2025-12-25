import { z } from "zod";

export const RenameFileChange = z.object({ "file_path": z.string(), "diffs": z.array(z.object({ "line": z.number().int(), "original": z.string(), "modified": z.string() })) });
