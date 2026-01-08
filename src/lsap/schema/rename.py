from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

from .abc import Request, Response
from .locate import Locate, LocateRequest


class RenameDiff(BaseModel):
    """Line-level change showing before and after rename."""

    line: int = Field(..., ge=1, description="1-based line number")
    original: str = Field(..., description="Original line content before rename")
    modified: str = Field(..., description="Modified line content after rename")


class RenameFileChange(BaseModel):
    """Changes within a single file."""

    file_path: Path
    diffs: list[RenameDiff]


class RenamePreviewRequest(LocateRequest):
    """
    Previews a rename operation without applying changes.

    Returns a rename_id that can be used to execute the rename later,
    along with a preview of all affected files and line changes.
    """

    locate: Locate
    new_name: str = Field(..., description="The new name for the symbol")


class RenameExecuteRequest(Request):
    """
    Executes a rename operation, applying changes to the workspace.

    Must use a rename_id from a previous preview to ensure
    the same changes are applied. Supports excluding specific files or glob patterns.
    """

    rename_id: str = Field(
        ..., description="Required ID from a previous preview to apply"
    )
    exclude_files: list[str] = Field(
        default_factory=list,
        description="List of file paths or glob patterns to exclude from the rename operation",
    )

    @field_validator("exclude_files")
    @classmethod
    def validate_patterns(cls, v: list[str]) -> list[str]:
        """Validate that patterns are relative and don't escape workspace"""
        for pattern in v:
            # Check if absolute path
            if Path(pattern).is_absolute():
                raise ValueError(
                    f"Pattern must be relative to workspace, got absolute: {pattern}"
                )
            # Check for parent directory references
            if ".." in Path(pattern).parts:
                raise ValueError(
                    f"Pattern must be relative to workspace, contains '..': {pattern}"
                )
        return v


preview_template: Final = """
# Rename Preview: `{{ old_name }}` → `{{ new_name }}`

ID: `{{ rename_id }}`
Summary: Affects {{ total_files }} files and {{ total_occurrences }} occurrences.

{% assign num_changes = changes | size -%}
{% if num_changes == 0 -%}
No changes to preview.
{%- else -%}
{%- for file in changes %}
## `{{ file.file_path }}`
{% for diff in file.diffs %}
Line {{ diff.line }}:
```diff
- {{ diff.original }}
+ {{ diff.modified }}
```
{% endfor %}
{% endfor -%}
---
> [!TIP]
> To apply this rename, use `rename_execute` with `rename_id="{{ rename_id }}"`.
> To exclude files, add `exclude_files=["path/to/exclude.py"]` or use glob patterns like `exclude_files=["tests/**/*.py", "**/*_test.py"]`.
{%- endif %}
"""


class RenamePreviewResponse(Response):
    request: RenamePreviewRequest
    rename_id: str = Field(..., description="Unique ID for this preview")
    old_name: str
    new_name: str
    total_files: int
    total_occurrences: int
    changes: list[RenameFileChange]
    applied: Literal[False] = False

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": preview_template,
        }
    )


execute_template: Final = """
# Rename Applied: `{{ old_name }}` → `{{ new_name }}`

Summary: Modified {{ total_files }} files with {{ total_occurrences }} occurrences.

{% assign num_changes = changes | size -%}
{% if num_changes > 0 -%}
{%- for file in changes %}
- `{{ file.file_path }}`: {{ file.diffs | size }} occurrences
{%- endfor %}
{%- endif %}
---
> [!NOTE]
> Rename completed successfully.{% assign num_excluded = request.exclude_files | size %}{% if num_excluded > 0 %} Excluded files: {% for f in request.exclude_files %}`{{ f }}`{% unless forloop.last %}, {% endunless %}{% endfor %}.
> [!IMPORTANT]
> You must manually rename the symbol in the excluded files to maintain consistency.{% endif %}
"""


class RenameExecuteResponse(Response):
    request: RenameExecuteRequest
    old_name: str
    new_name: str
    total_files: int
    total_occurrences: int
    changes: list[RenameFileChange]
    applied: Literal[True] = True

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": execute_template,
        }
    )


type RenameResponse = RootModel[RenamePreviewResponse | RenameExecuteResponse]
