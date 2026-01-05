from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from lsap_schema.abc import PaginatedRequest, PaginatedResponse
from lsap_schema.locate import LocateRequest


class RenameDiff(BaseModel):
    line: int
    """Line number (1-based)"""

    original: str
    """Line content before rename"""

    modified: str
    """Line content after rename (preview)"""


class RenameFileChange(BaseModel):
    file_path: Path
    """File path affected by the rename"""

    occurrences: int
    """Number of occurrences in this file"""

    diffs: list[RenameDiff] = Field(default_factory=list)
    """Detailed line-by-line diffs (only included if show_diffs=true)"""


class RenameRequest(PaginatedRequest, LocateRequest):
    """
    Previews a workspace-wide symbol rename operation.

    This API returns a preview of all changes that would be made by renaming
    the specified symbol. The preview is generated from LSP's WorkspaceEdit,
    which contains all the text edits needed for the rename. The actual
    execution of changes is handled by the client (editor/IDE) using the
    same WorkspaceEdit.

    By default, returns a compact summary to minimize token usage.
    Use show_diffs=true to see detailed line-by-line changes extracted
    from the WorkspaceEdit.

    Note: LSP rename is always workspace-wide. All references to the symbol
    across all files will be included in the preview.
    """

    new_name: str
    """The new name to apply to the symbol"""

    show_diffs: bool = False
    """Include detailed line diffs in preview (increases context usage)"""

    max_items: int | None = Field(default=100, ge=1)
    """Maximum number of files to show in preview (for large renames)"""


preview_template: Final = """
# Rename Preview: `{{ old_name }}` → `{{ new_name }}`

## Summary
- **Files affected**: {{ total }}{% if has_more or start_index > 0 %} (showing {{ changes | size }}/{{ total }}){% endif %}
- **Total occurrences**: {{ total_occurrences }}

## Affected Files
{%- for file in changes %}
- `{{ file.file_path }}`: {{ file.occurrences }} occurrence(s)
{%- endfor %}
{%- if has_more %}
- ... and more file(s) available.
{%- endif %}

{%- if changes.size > 0 -%}
{%- assign first_file = changes[0] -%}
{%- if first_file.diffs.size > 0 %}

## Detailed Changes
{%- for file in changes %}

### `{{ file.file_path }}`
{%- for diff in file.diffs %}
- Line {{ diff.line }}:
  - `{{ diff.original }}`
  + `{{ diff.modified }}`
{%- endfor %}
{%- endfor %}
{%- endif %}
{%- endif %}

{%- if has_more %}

---
> [!TIP]
> More changes available. To see more, use: `start_index={{ start_index | plus: max_items }}`
{%- endif %}

---
> [!NOTE]
> This is a preview of changes. The actual rename operation will be executed by your editor/IDE.
> Review the changes above before applying them.
"""


class RenameResponse(PaginatedResponse):
    old_name: str
    """The original symbol name"""

    new_name: str
    """The new symbol name"""

    total_occurrences: int
    """Total number of times the symbol appears across all files"""

    changes: list[RenameFileChange]
    """Per-file change details (may be truncated based on max_items limit)"""

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": preview_template,
        }
    )
