from typing import Final

from pydantic import ConfigDict

from .abc import PaginatedRequest, PaginatedResponse
from .locate import LocateRequest
from .symbol import SymbolResponse


class ImplementationRequest(LocateRequest, PaginatedRequest):
    """
    Finds concrete implementations of an abstract symbol or interface.

    Use this when you are at an interface or base class method and want to see
    how it is actually implemented in subclasses.
    """

    include_hover: bool = False
    """Whether to include documentation for each implementation. Default to False to save tokens."""

    include_content: bool = True
    """Whether to include the source code snippet for each implementation."""


markdown_template: Final = """
### Implementations Found

{% if total != nil -%}
Total implementations: {{ total }} | Showing: {{ items.size }}{% if max_items != nil %} (Offset: {{ start_index }}, Limit: {{ max_items }}){% endif %}
{%- endif %}

{% if items.size == 0 -%}
No concrete implementations found.
{%- else -%}
{%- for item in items %}
- `{{ item.file_path }}` - `{{ item.symbol_path | join: "." }}`
{% if item.hover != nil -%}
  {{ item.hover | indent: 2 }}
{%- endif %}
{% if item.symbol_content != nil -%}
```python
{{ item.symbol_content }}
```
{%- endif %}
{%- endfor %}

{% if has_more -%}
---
> [!TIP]
> More implementations available.
{%- if pagination_id != nil %}
> Use `pagination_id="{{ pagination_id }}"` to fetch the next page.
{%- else %}
> To see more, specify a `max_items` and use: `start_index={% assign step = max_items | default: items.size %}{{ start_index | plus: step }}`
{%- endif %}
{%- endif %}
{%- endif %}
"""


class ImplementationResponse(PaginatedResponse):
    items: list[SymbolResponse]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
