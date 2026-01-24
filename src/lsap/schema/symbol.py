"""
# Symbol API

The Symbol API provides detailed information about a specific code symbol,
including its source code and documentation. It is the primary way for an
Agent to understand the implementation and usage of a function, class, or variable.

## Example Usage

### Scenario 1: Getting function documentation and implementation

Request:

```json
{
  "locate": {
    "file_path": "src/main.py",
    "scope": {
      "symbol_path": ["calculate_total"]
    }
  }
}
```

### Scenario 2: Getting class information

Request:

```json
{
  "locate": {
    "file_path": "src/models.py",
    "scope": {
      "symbol_path": ["User"]
    }
  }
}
```
"""

from typing import Final

from pydantic import ConfigDict

from ._abc import Response
from .locate import LocateRequest
from .models import CallHierarchy, SymbolCodeInfo


class SymbolRequest(LocateRequest):
    """
    Retrieves detailed information about a symbol at a specific location.

    Use this to get the documentation (hover) and source code implementation
    of a symbol to understand its purpose and usage.
    """


markdown_template: Final = """
# Symbol: `{{ info.path | join: "." }}` (`{{ info.kind }}`) at `{{ info.file_path }}`

{% if info.code != nil -%}
## Implementation
```{{ info.file_path.suffix | remove_first: "." }}
{{ info.code }}
```
{%- endif %}

{% if call_hierarchy != nil -%}
{% if call_hierarchy.incoming.size > 0 -%}
## Incoming Calls
{% for item in call_hierarchy.incoming -%}
- `{{ item.name }}` (`{{ item.kind }}`) at `{{ item.file_path }}:{{ item.range.start.line }}`
{% endfor -%}
{%- endif %}

{% if call_hierarchy.outgoing.size > 0 -%}
## Outgoing Calls
{% for item in call_hierarchy.outgoing -%}
- `{{ item.name }}` (`{{ item.kind }}`) at `{{ item.file_path }}:{{ item.range.start.line }}`
{% endfor -%}
{%- endif %}
{%- endif %}
"""


class SymbolResponse(Response):
    info: SymbolCodeInfo
    call_hierarchy: CallHierarchy | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


__all__ = [
    "SymbolRequest",
    "SymbolResponse",
]
