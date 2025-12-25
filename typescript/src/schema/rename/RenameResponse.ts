import { z } from "zod";

export const RenameResponse = z.object({ "old_name": z.string(), "new_name": z.string(), "total_files": z.number().int(), "total_occurrences": z.number().int(), "changes": z.array(z.object({ "file_path": z.string(), "diffs": z.array(z.object({ "line": z.number().int(), "original": z.string(), "modified": z.string() })) })) });

export const RenameResponseTemplates = {
  "markdown": "\n### Rename Preview: `{{ old_name }}` -> `{{ new_name }}`\n\n**Summary**: Affects {{ total_files }} files and {{ total_occurrences }} occurrences.\n\n{% for file in changes -%}\n#### File: `{{ file.file_path }}`\n{%- for diff in file.diffs %}\n- Line {{ diff.line + 1 }}:\n  - `{{ diff.original }}`\n  + `{{ diff.modified }}`\n{%- endfor %}\n{% endfor %}\n\n---\n> [!WARNING]\n> **This is a permanent workspace-wide change.**\n> Please verify the diffs above before proceeding with further edits.\n"
} as const;
