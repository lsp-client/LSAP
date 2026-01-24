"""
# Diagnostics API

The Diagnostics API reports syntax errors, type mismatches, and other linting issues
found in a specific file or across the workspace.

## Example Usage

### Scenario 1: Getting all diagnostics for a file

Request:

```json
{
  "file_path": "src/buggy.py",
  "min_severity": "Hint"
}
```

### Scenario 2: Getting workspace-wide diagnostics

Request:

```json
{
  "min_severity": "Error",
  "max_items": 10
}
```
"""

from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from lsap.schema._abc import PaginatedRequest, PaginatedResponse
from lsap.schema.models import Range


class Diagnostic(BaseModel):
    range: Range
    severity: Literal["Error", "Warning", "Information", "Hint"]
    message: str
    source: str | None = None
    code: str | int | None = None


class FileDiagnosticsRequest(PaginatedRequest):
    """
    Retrieves diagnostics (errors, warnings, hints) for a specific file.

    Use this after making changes to verify code correctness or to identify
    potential issues and linting errors.
    """

    file_path: Path
    min_severity: Literal["Error", "Warning", "Information", "Hint"] = "Hint"
    """Minimum severity to include. Default to 'Hint' (all)."""


markdown_template: Final = """
# Diagnostics for `{{ file_path }}`
{% if total != nil -%}
Total issues: {{ total }} | Showing: {{ diagnostics.size }}{% if max_items != nil %} (Offset: {{ start_index }}, Limit: {{ max_items }}){% endif %}
{%- endif %}

{% if diagnostics.size == 0 -%}
No issues found.
{%- else -%}
| Line:Col | Severity | Message |
| :--- | :--- | :--- |
{%- for d in diagnostics %}
| `{{ d.range.start.line }}:{{ d.range.start.character }}` | {{ d.severity }} | {{ d.message }} |
{%- endfor %}

{% if has_more -%}
---
> [!TIP]
> More issues available.
> To see more, use: `pagination_id="{{ pagination_id }}"`, `start_index={{ start_index | plus: diagnostics.size }}`
{%- endif %}
{%- endif %}
"""


class FileDiagnosticsResponse(PaginatedResponse):
    file_path: Path
    diagnostics: list[Diagnostic]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


class WorkspaceDiagnosticItem(Diagnostic):
    file_path: Path


class WorkspaceDiagnosticsRequest(PaginatedRequest):
    """
    Retrieves diagnostics (errors, warnings, hints) across the entire workspace.

    Use this to get a high-level overview of project health and identify
    all existing issues.
    """

    min_severity: Literal["Error", "Warning", "Information", "Hint"] = "Hint"
    """Minimum severity to include. Default to 'Hint' (all)."""


workspace_markdown_template: Final = """
# Workspace Diagnostics
{% if total != nil -%}
Total issues: {{ total }} | Showing: {{ items.size }}{% if max_items != nil %} (Offset: {{ start_index }}, Limit: {{ max_items }}){% endif %}
{%- endif %}

{% if items.size == 0 -%}
No issues found in the workspace.
{%- else -%}
| File | Line:Col | Severity | Message |
| :--- | :--- | :--- | :--- |
{%- for item in items %}
| `{{ item.file_path }}` | `{{ item.range.start.line }}:{{ item.range.start.character }}` | {{ item.severity }} | {{ item.message }} |
{%- endfor %}

{% if has_more -%}
---
> [!TIP]
> More issues available.
> To see more, use: `pagination_id="{{ pagination_id }}"`, `start_index={{ start_index | plus: items.size }}`
{%- endif %}
{%- endif %}
"""


class WorkspaceDiagnosticsResponse(PaginatedResponse):
    items: list[WorkspaceDiagnosticItem]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": workspace_markdown_template,
        }
    )


__all__ = [
    "Diagnostic",
    "FileDiagnosticsRequest",
    "FileDiagnosticsResponse",
    "WorkspaceDiagnosticItem",
    "WorkspaceDiagnosticsRequest",
    "WorkspaceDiagnosticsResponse",
]
