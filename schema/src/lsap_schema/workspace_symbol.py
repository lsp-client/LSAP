from typing import Final

from pydantic import ConfigDict

from .abc import PaginatedRequest, PaginatedResponse
from .types import SymbolDetailInfo


class WorkspaceSymbolItem(SymbolDetailInfo):
    container_name: str | None = None


class WorkspaceSymbolRequest(PaginatedRequest):
    """
    Searches for symbols across the entire workspace by name.

    Use this when you know the name of a symbol (or part of it) but don't know
    which file it is defined in.
    """

    query: str
    """The symbol name to search for."""


markdown_template: Final = """
# Workspace Symbols matching `{{ request.query }}`
{% if total != nil -%}
Total found: {{ total }} | Showing: {{ items.size }}{% if max_items != nil %} (Offset: {{ start_index }}, Limit: {{ max_items }}){% endif %}
{%- endif %}

{% if items.size == 0 -%}
No symbols found matching the query.
{%- else -%}
{%- for item in items %}
### {{ item.name }} (`{{ item.kind }}`)
- Location: `{{ item.file_path }}` {% if item.container_name != nil %}(in `{{ item.container_name }}`){% endif %}
- Detail: {{ item.detail }}

{{ item.hover }}
{%- endfor %}

{% if has_more -%}
---
> [!TIP]
> More results available.
{%- if pagination_id != nil %}
> Use `pagination_id="{{ pagination_id }}"` to fetch the next page.
{%- else %}
> To fetch the next page, specify a `max_items` and use: `start_index={% assign step = max_items | default: items.size %}{{ start_index | plus: step }}`
{%- endif %}
{%- endif %}
{%- endif %}
"""


class WorkspaceSymbolResponse(PaginatedResponse):
    request: WorkspaceSymbolRequest

    items: list[WorkspaceSymbolItem]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
