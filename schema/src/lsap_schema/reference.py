from typing import Final, Literal

from pydantic import ConfigDict

from .abc import PaginatedRequest, PaginatedResponse
from .locate import LocateRequest
from .symbol import SymbolResponse


class ReferenceRequest(LocateRequest, PaginatedRequest):
    """
    Finds all references (usages) or concrete implementations of a symbol.

    Use this to see where a function, class, or variable is used across the codebase,
    or to find how an interface is implemented in subclasses.
    """

    mode: Literal["references", "implementations"] = "references"
    """Whether to find references or concrete implementations."""

    include_hover: bool = True
    """Whether to include documentation for each item."""

    include_content: bool = False
    """Whether to include the source code snippet for each item."""


markdown_template: Final = """
# {{ mode | capitalize }} Found

{% if total != nil -%}
Total {{ mode }}: {{ total }} | Showing: {{ items.size }}{% if max_items != nil %} (Offset: {{ start_index }}, Limit: {{ max_items }}){% endif %}
{%- endif %}

{% if items.size == 0 -%}
No {{ mode }} found.
{%- else -%}
{%- for item in items %}
- `{{ item.file_path }}` - `{{ item.symbol_path | join: "." }}`
{% if item.hover != nil -%}
  {{ item.hover | indent: 2 }}
{%- endif %}
{% if item.symbol_content != nil -%}
```
{{ item.symbol_content }}
```
{%- endif %}
{%- endfor %}

{% if has_more -%}
---
> [!TIP]
> More {{ mode }} available.
{%- if pagination_id != nil %}
> Use `pagination_id="{{ pagination_id }}"` to fetch the next page.
{%- else %}
> To see more, specify a `max_items` and use: `start_index={% assign step = max_items | default: items.size %}{{ start_index | plus: step }}`
{%- endif %}
{%- endif %}
{%- endif %}
"""


class ReferenceResponse(PaginatedResponse):
    mode: Literal["references", "implementations"] = "references"
    """The mode used for this response."""

    items: list[SymbolResponse]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
