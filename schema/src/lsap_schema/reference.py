from typing import Final

from pydantic import ConfigDict

from .abc import PaginatedRequest, PaginatedResponse
from .locate import LocateRequest
from .symbol import SymbolResponse


class ReferenceRequest(LocateRequest, PaginatedRequest):
    """
    Finds all references (usages) of a symbol.

    Use this to see where a function, class, or variable is used across the codebase,
    which is essential for refactoring or understanding the impact of a change.
    """

    include_hover: bool = False
    """Whether to include hover/documentation for each reference. Default to False to save tokens."""

    include_content: bool = True
    """Whether to include the source code snippet for each reference."""


markdown_template: Final = """
### References Found

{% if total != nil -%}
Total references: {{ total }} | Showing: {{ items.size }}{% if max_items != nil %} (Offset: {{ start_index }}, Limit: {{ max_items }}){% endif %}
{%- endif %}

{% for item in items -%}
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
> More references available.
{%- if pagination_id != nil %}
> Use `pagination_id="{{ pagination_id }}"` to fetch the next page.
{%- else %}
> To see more, specify a `max_items` and use: `start_index={% assign step = max_items | default: items.size %}{{ start_index | plus: step }}`
{%- endif %}
{%- endif %}
"""


class ReferenceResponse(PaginatedResponse):
    items: list[SymbolResponse]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
