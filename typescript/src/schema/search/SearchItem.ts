import { z } from "zod";

export const SearchItem = z.object({ "name": z.string(), "kind": z.enum(["file","module","namespace","package","class","method","property","field","constructor","enum","interface","function","variable","constant","string","number","boolean","array","object","key","null","enumMember","struct","event","operator","typeParameter"]), "file_path": z.string(), "line": z.union([z.number().int(), z.null()]).default(null), "container": z.union([z.string(), z.null()]).default(null) }).describe("Concise search result for quick discovery.");
