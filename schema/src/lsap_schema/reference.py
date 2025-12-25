from typing import Final

from pydantic import BaseModel, ConfigDict

from .locate import LocateRequest
from .symbol import SymbolResponse


class ReferenceRequest(LocateRequest):
    """
    Finds all references (usages) of a symbol.

    Use this to see where a function, class, or variable is used across the codebase,
    which is essential for refactoring or understanding the impact of a change.
    """

    include_hover: bool = False
    """Whether to include hover/documentation for each reference. Default to False to save tokens."""

    include_content: bool = True
    """Whether to include the source code snippet for each reference."""

    limit: int | None = None
    """Maximum number of references to return (default: None, returns all)"""

    offset: int = 0
    """Number of references to skip (default: 0)"""


markdown_template: Final = """
### References Found

{% if total is not none -%}
**Total references**: {{ total }} | **Showing**: {{ items | length }}{% if limit %} (Offset: {{ offset }}, Limit: {{ limit }}){% endif %}
{%- endif %}

{% for item in items -%}
- `{{ item.file_path }}` - `{{ item.symbol_path | join('.') }}`
{% if item.hover -%}
  {{ item.hover | indent(2) }}
{%- endif %}
{% if item.symbol_content -%}
```python
{{ item.symbol_content }}
```
{%- endif %}
{%- endfor %}

{% if has_more -%}
---
> [!TIP]
> **More references available.**
> To see more, specify a `limit` and use: `offset={{ offset + (limit or items|length) }}`
{%- endif %}
"""


class ReferenceResponse(BaseModel):
    items: list[SymbolResponse]
    offset: int
    limit: int | None = None
    total: int | None = None
    has_more: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
