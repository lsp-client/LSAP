from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from .abc import PaginatedRequest, PaginatedResponse
from .locate import LocateRequest
from .models import Location, SymbolDetailInfo


class ReferenceItem(BaseModel):
    location: Location
    code: str = Field(..., description="Surrounding code snippet")
    symbol: SymbolDetailInfo | None = Field(
        None, description="The symbol containing this reference"
    )


class ReferenceRequest(PaginatedRequest, LocateRequest):
    """
    Finds all references (usages) or concrete implementations of a symbol.

    Use this to see where a function, class, or variable is used across the codebase,
    or to find how an interface is implemented in subclasses.
    """

    mode: Literal["references", "implementations"] = "references"
    """Whether to find references or concrete implementations."""

    context_lines: int = 2
    """Number of lines around the match to include"""


markdown_template: Final = """
# {{ request.mode | capitalize }} Found

{% if total != nil -%}
Total {{ request.mode }}: {{ total }} | Showing: {{ items.size }}{% if max_items != nil %} (Offset: {{ start_index }}, Limit: {{ max_items }}){% endif %}
{%- endif %}

{% if items.size == 0 -%}
No {{ request.mode }} found.
{%- else -%}
{%- for item in items -%}
### {{ item.location.file_path }}:{{ item.location.range.start.line }}
{%- if item.symbol != nil %}
In `{{ item.symbol.path | join: "." }}` (`{{ item.symbol.kind }}`)
{%- endif %}

```{{ item.location.file_path.suffix | remove_first: "." }}
{{ item.code }}
```

{% endfor -%}

{% if has_more -%}
---
> [!TIP]
> More {{ request.mode }} available.
{%- if pagination_id != nil %}
> Use `pagination_id="{{ pagination_id }}"` to fetch the next page.
{%- else %}
> To see more, specify a `max_items` and use: `start_index={% assign step = max_items | default: items.size %}{{ start_index | plus: step }}`
{%- endif %}
{%- endif %}
{%- endif %}
"""


class ReferenceResponse(PaginatedResponse):
    request: ReferenceRequest
    items: list[ReferenceItem]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
