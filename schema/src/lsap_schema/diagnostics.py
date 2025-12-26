from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from .abc import PaginatedRequest, PaginatedResponse
from .locate import Range


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
{%- for d in diagnostics %}
- {{ d.severity }}: {{ d.message }} (at line {{ d.range.start.line }}, col {{ d.range.start.character }})
{%- endfor %}

{% if has_more -%}
---
> [!TIP]
> More issues available.
{%- if pagination_id != nil %}
> Use `pagination_id="{{ pagination_id }}"` to fetch the next page.
{%- else %}
> To see the rest, specify a `max_items` and use: `start_index={% assign step = max_items | default: diagnostics.size %}{{ start_index | plus: step }}`
{%- endif %}
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
