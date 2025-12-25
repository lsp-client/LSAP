from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from .locate import Range


class WorkspaceSymbolItem(BaseModel):
    name: str
    kind: str
    file_path: Path
    range: Range
    container_name: str | None = None


class WorkspaceSymbolRequest(BaseModel):
    """
    Searches for symbols across the entire workspace by name.

    Use this when you know the name of a symbol (or part of it) but don't know
    which file it is defined in.
    """

    query: str
    limit: int | None = None
    """Maximum number of symbols to return (default: None, returns all)"""

    offset: int = 0
    """Number of symbols to skip (default: 0)"""


markdown_template: Final = """
### Workspace Symbols matching `{{ query }}`
{% if total is not none -%}
**Total found**: {{ total }} | **Showing**: {{ items | length }}{% if limit %} (Offset: {{ offset }}, Limit: {{ limit }}){% endif %}
{%- endif %}

{% if not items -%}
No symbols found matching the query.
{%- else -%}
{%- for item in items %}
- **{{ item.name }}** (`{{ item.kind }}`) in `{{ item.file_path }}` {% if item.container_name %}(in `{{ item.container_name }}`){% endif %}
{%- endfor %}

{% if has_more -%}
---
> [!TIP]
> **More results available.**
> To fetch the next page, specify a `limit` and use: `offset={{ offset + (limit or items|length) }}`
{%- endif %}
{%- endif %}
"""


class WorkspaceSymbolResponse(BaseModel):
    query: str
    items: list[WorkspaceSymbolItem]
    offset: int
    limit: int | None = None
    total: int | None = None
    has_more: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
