from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from ..abc import Response
from ..locate import LocateRequest


class RenameDiff(BaseModel):
    line: int
    """Line number (1-based)"""
    original: str
    """Line content before rename"""

    modified: str
    """Line content after rename (preview)"""


class RenameFileChange(BaseModel):
    file_path: Path
    diffs: list[RenameDiff]


class RenameRequest(LocateRequest):
    """
    Renames a symbol throughout the entire workspace.

    Use this to safely rename variables, functions, or classes across all files
    where they are referenced.
    """

    new_name: str
    """The new name to apply to the symbol"""


markdown_template: Final = """
# Rename Preview: `{{ old_name }}` -> `{{ new_name }}`

Summary: Affects {{ total_files }} files and {{ total_occurrences }} occurrences.

{% for file in changes -%}
## File: `{{ file.file_path }}`
{%- for diff in file.diffs %}
- Line {{ diff.line }}:
  - `{{ diff.original }}`
  + `{{ diff.modified }}`
{%- endfor %}
{% endfor %}

---
> [!WARNING]
> This is a permanent workspace-wide change.
> Please verify the diffs above before proceeding with further edits.
"""


class RenameResponse(Response):
    old_name: str
    new_name: str
    total_files: int
    total_occurrences: int
    changes: list[RenameFileChange]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
