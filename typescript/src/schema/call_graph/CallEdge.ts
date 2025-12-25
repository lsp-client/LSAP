import { z } from "zod";

export const CallEdge = z.object({ "from_node_id": z.string(), "to_node_id": z.string(), "call_sites": z.array(z.object({ "line": z.number().int(), "character": z.number().int() })) });
