import { z } from "zod";

export const InlayHintItem = z.object({ "label": z.string(), "kind": z.union([z.enum(["Type","Parameter"]), z.null()]).default(null), "position": z.string() });
