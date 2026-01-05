import { z } from "zod";

export const HoverResponse = z.object({ "content": z.string() });

export const HoverResponseTemplates = {
  "markdown": "\n# Hover Information\n\n{{ content }}\n"
} as const;
