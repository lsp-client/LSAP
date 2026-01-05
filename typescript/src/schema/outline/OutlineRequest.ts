import { z } from "zod";

export const OutlineRequest = z.object({ "file_path": z.string() }).describe("Retrieves a hierarchical outline of symbols within a file.\n\nUse this to understand the structure of a file (classes, methods, functions)\nand quickly navigate its contents.");
