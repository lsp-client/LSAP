"""
# Reference API

The Reference API finds all locations where a specific symbol is used across the codebase.

## Example Usage

### Scenario 1: Finding all references of a function

Request:

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "scope": {
      "symbol_path": ["format_date"]
    }
  },
  "max_items": 10
}
```

### Scenario 2: Finding all implementations of an interface method

Request:

```json
{
  "locate": {
    "file_path": "src/base.py",
    "scope": {
      "symbol_path": ["DatabaseConnection", "connect"]
    }
  },
  "mode": "implementations",
  "max_items": 5
}
```

### Scenario 3: Finding all classes that implement an interface

Request:

```json
{
  "locate": {
    "file_path": "src/interfaces.py",
    "scope": {
      "symbol_path": ["IRepository"]
    }
  },
  "mode": "implementations",
  "max_items": 5
}
```
"""

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from ._abc import PaginatedRequest, PaginatedResponse
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
### `{{ item.location.file_path }}:{{ item.location.range.start.line }}`
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
> To see more, use: `pagination_id="{{ pagination_id }}"`, `start_index={{ start_index | plus: items.size }}`
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


__all__ = [
    "ReferenceItem",
    "ReferenceRequest",
    "ReferenceResponse",
]
