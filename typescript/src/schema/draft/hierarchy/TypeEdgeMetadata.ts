import { z } from "zod";

export const TypeEdgeMetadata = z.object({ "relationship": z.enum(["extends","implements"]) }).describe("Metadata specific to type inheritance relationships");
