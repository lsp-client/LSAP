import { z } from "zod";

export const DecoratedContentResponse = z.object({ "file_path": z.string(), "decorated_content": z.string() });

export const DecoratedContentResponseTemplates = {
  "markdown": "\n### Code with Annotations: `{{ file_path }}`\n\n```python\n{{ decorated_content }}\n```\n\n---\n> [!NOTE]\n> Annotations like `/* :type */` or `/* param:= */` are injected for clarity.\n> Runtime values (if any) are shown as `// value: x=42`.\n"
} as const;
