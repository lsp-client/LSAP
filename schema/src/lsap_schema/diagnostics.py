from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from .locate import Range


class Diagnostic(BaseModel):
    range: Range
    severity: Literal["Error", "Warning", "Information", "Hint"]
    message: str
    source: str | None = None
    code: str | int | None = None


class FileDiagnosticsRequest(BaseModel):
    """
    Retrieves diagnostics (errors, warnings, hints) for a specific file.

    Use this after making changes to verify code correctness or to identify
    potential issues and linting errors.
    """

    file_path: Path
    min_severity: Literal["Error", "Warning", "Information", "Hint"] = "Hint"
    """Minimum severity to include. Default to 'Hint' (all)."""

    limit: int | None = None
    """Maximum number of diagnostics to return (default: None, returns all)"""

    offset: int = 0
    """Number of diagnostics to skip (default: 0)"""


markdown_template: Final = """
### Diagnostics for `{{ file_path }}`
{% if total is not none -%}
Total issues: {{ total }} | Showing: {{ diagnostics | length }}{% if limit %} (Offset: {{ offset }}, Limit: {{ limit }}){% endif %}
{%- endif %}

{% if not diagnostics -%}
No issues found.
{%- else -%}
{%- for d in diagnostics %}
- {{ d.severity }}: {{ d.message }} (at line {{ d.range.start.line + 1 }}, col {{ d.range.start.character + 1 }})
{%- endfor %}

{% if has_more -%}
---
> [!TIP]
> More issues available.
> To see the rest, specify a `limit` and use: `offset={{ offset + (limit or diagnostics|length) }}`
{%- endif %}
{%- endif %}
"""


class FileDiagnosticsResponse(BaseModel):
    file_path: Path
    diagnostics: list[Diagnostic]
    offset: int
    limit: int | None = None
    total: int | None = None
    has_more: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
