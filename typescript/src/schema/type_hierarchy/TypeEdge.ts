import { z } from "zod";

export const TypeEdge = z.object({ "from_node_id": z.string(), "to_node_id": z.string(), "relationship": z.enum(["extends","implements"]) });
