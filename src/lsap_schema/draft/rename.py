from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from lsap_schema.abc import Response
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


class RenameRequest(LocateRequest):
    """
    Preview or execute a safe, workspace-wide symbol rename.

    This API operates in two modes for safety:
    1. Preview (mode="preview", default): Returns a summary without making changes
    2. Execute (mode="execute"): Actually performs the rename operation

    The preview mode provides minimal context by default to reduce token usage.
    Use show_diffs=true to see detailed line-by-line changes.

    Scope can be limited to specific files or directories using the scope_filter.
    """

    new_name: str
    """The new name to apply to the symbol"""

    mode: Literal["preview", "execute"] = "preview"
    """Operation mode: 'preview' (default, safe) or 'execute' (applies changes)"""

    show_diffs: bool = False
    """Include detailed line diffs in preview (increases context usage)"""

    scope_filter: list[Path] | None = None
    """Optional: Limit rename to specific files/directories. If None, applies workspace-wide."""

    max_files: int | None = Field(default=None, ge=1)
    """Optional: Maximum number of files to show in preview (for large renames)"""


preview_template: Final = """
# Rename Preview: `{{ old_name }}` → `{{ new_name }}`

**Status**: {{ status }}
**Scope**: {{ scope_description }}

## Summary
- **Files affected**: {{ total_files }}{% if has_more_files %} (showing {{ changes | size }}/{{ total_files }}){% endif %}
- **Total occurrences**: {{ total_occurrences }}

## Affected Files
{%- for file in changes %}
- `{{ file.file_path }}`: {{ file.occurrences }} occurrence(s)
{%- endfor %}
{%- if has_more_files %}
- ... and {{ total_files | minus: changes | size }} more file(s)
{%- endif %}

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

---
{%- if status == "preview" %}
> [!NOTE]
> This is a **preview only** - no changes have been made.
> To apply these changes, send the same request with `mode: "execute"`.
{%- else %}
> [!SUCCESS]
> Rename operation completed successfully.
> {{ total_occurrences }} occurrence(s) renamed across {{ total_files }} file(s).
{%- endif %}
"""


class RenameResponse(Response):
    old_name: str
    """The original symbol name that was (or will be) renamed"""

    new_name: str
    """The new symbol name"""

    status: Literal["preview", "completed"]
    """Operation status: 'preview' (no changes made) or 'completed' (changes applied)"""

    scope_description: str
    """Human-readable description of the rename scope"""

    total_files: int
    """Total number of files that contain the symbol"""

    total_occurrences: int
    """Total number of times the symbol appears across all files"""

    changes: list[RenameFileChange]
    """Per-file change details (may be truncated based on max_files)"""

    has_more_files: bool = False
    """True if the changes list was truncated due to max_files limit"""

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": preview_template,
        }
    )
