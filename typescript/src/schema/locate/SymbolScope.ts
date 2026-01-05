import { z } from "zod";

export const SymbolScope = z.object({ "symbol_path": z.array(z.string()) }).describe("Scope by symbol, also serves as declaration locator when find is omitted");
