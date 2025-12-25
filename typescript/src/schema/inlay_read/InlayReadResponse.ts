import { z } from "zod";

export const InlayReadResponse = z.object({ "content": z.string() });

export const InlayReadResponseTemplates = {
  "markdown": "{{ content }}"
} as const;
