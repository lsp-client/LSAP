import { z } from "zod";

export const ParameterInfo = z.object({ "name": z.string(), "label": z.string(), "documentation": z.union([z.string(), z.null()]).default(null) });
