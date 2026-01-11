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
from .models import SymbolCodeInfo


class SymbolRequest(LocateRequest):
    """
    Retrieves detailed information about a symbol at a specific location.

    Use this to get the documentation (hover) and source code implementation
    of a symbol to understand its purpose and usage.
    """


markdown_template: Final = """
# Symbol: `{{ path | join: "." }}` (`{{ kind }}`) at `{{ file_path }}`

{% if code != nil -%}
## Implementation
```{{ file_path.suffix | remove_first: "." }}
{{ code }}
```
{%- endif %}
"""


class SymbolResponse(SymbolCodeInfo, Response):
    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


__all__ = [
    "SymbolRequest",
    "SymbolResponse",
]
