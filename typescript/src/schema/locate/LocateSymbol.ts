import { z } from "zod";

export const LocateSymbol = z.object({ "file_path": z.string(), "symbol_path": z.array(z.string()) }).describe("Locate by symbol path");
