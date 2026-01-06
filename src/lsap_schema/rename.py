from pathlib import Path
from typing import Annotated, Final, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    RootModel,
    field_validator,
)

from .abc import Response
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
    mode: Literal["preview"] = "preview"


class RenameExecuteRequest(LocateRequest):
    """
    Executes a rename operation, applying changes to the workspace.

    Must use a rename_id from a previous preview to ensure
    the same changes are applied. Supports excluding specific files.
    """

    locate: Locate
    new_name: str = Field(..., description="The new name for the symbol")
    mode: Literal["execute"] = "execute"

    rename_id: str = Field(
        ..., description="Required ID from a previous preview to apply"
    )
    exclude_files: list[Path] = Field(
        default_factory=list,
        description="List of file paths to exclude from the rename operation",
    )

    @field_validator("exclude_files")
    @classmethod
    def validate_paths(cls, v: list[Path]) -> list[Path]:
        """Validate that paths are relative and don't escape workspace"""
        for path in v:
            if path.is_absolute():
                raise ValueError(
                    f"Path must be relative to workspace, got absolute: {path}"
                )
            if ".." in path.parts:
                raise ValueError(
                    f"Path must be relative to workspace, contains '..': {path}"
                )
        return v


preview_template: Final = """
# Rename Preview: `{{ old_name }}` → `{{ new_name }}`

**ID**: `{{ rename_id }}`
**Summary**: Affects {{ total_files }} file{% if total_files != 1 %}s{% endif %} and {{ total_occurrences }} occurrence{% if total_occurrences != 1 %}s{% endif %}.

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
> To apply this rename, use `mode="execute"` with `rename_id="{{ rename_id }}"`.
> To exclude files, add `exclude_files=["path/to/exclude.py"]`.
{%- endif %}
"""

execute_template: Final = """
# Rename Applied: `{{ old_name }}` → `{{ new_name }}`

**Summary**: Modified {{ total_files }} file{% if total_files != 1 %}s{% endif %} with {{ total_occurrences }} occurrence{% if total_occurrences != 1 %}s{% endif %}.

{% assign num_changes = changes | size -%}
{% if num_changes == 0 -%}
No changes applied.
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
> [!NOTE]
> Rename completed successfully.{% assign num_excluded = request.exclude_files | size %}{% if num_excluded > 0 %} Excluded files: {% for f in request.exclude_files %}`{{ f }}`{% unless forloop.last %}, {% endunless %}{% endfor %}{% endif %}
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


RenameRequest = RootModel[
    Annotated[
        RenamePreviewRequest | RenameExecuteRequest,
        Discriminator("mode"),
    ]
]

RenameResponse = RootModel[
    Annotated[
        RenamePreviewResponse | RenameExecuteResponse,
        Discriminator("applied"),
    ]
]
