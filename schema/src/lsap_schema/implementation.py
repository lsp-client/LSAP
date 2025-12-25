from typing import Final

from pydantic import BaseModel, ConfigDict

from .locate import LocateRequest
from .symbol import SymbolResponse


class ImplementationRequest(LocateRequest):
    """
    Finds concrete implementations of an abstract symbol or interface.

    Use this when you are at an interface or base class method and want to see
    how it is actually implemented in subclasses.
    """

    include_hover: bool = False
    """Whether to include documentation for each implementation. Default to False to save tokens."""

    include_content: bool = True
    """Whether to include the source code snippet for each implementation."""

    limit: int | None = None
    """Maximum number of implementations to return (default: None, returns all)"""

    offset: int = 0
    """Number of implementations to skip (default: 0)"""


markdown_template: Final = """
### Implementations Found

{% if total is not none -%}
**Total implementations**: {{ total }} | **Showing**: {{ items | length }}{% if limit %} (Offset: {{ offset }}, Limit: {{ limit }}){% endif %}
{%- endif %}

{% if not items -%}
No concrete implementations found.
{%- else -%}
{%- for item in items %}
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
> **More implementations available.**
> To see more, specify a `limit` and use: `offset={{ offset + (limit or items|length) }}`
{%- endif %}
{%- endif %}
"""


class ImplementationResponse(BaseModel):
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
