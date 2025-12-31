from typing import Final

from pydantic import ConfigDict

from .abc import Response, SymbolInfoRequest
from .locate import LocateRequest
from .types import SymbolInfo


class SymbolRequest(LocateRequest, SymbolInfoRequest):
    """
    Retrieves detailed information about a symbol at a specific location.

    Use this to get the documentation (hover) and source code implementation
    of a symbol to understand its purpose and usage.
    """

    include_hover: bool = False
    """Whether to include hover/documentation information"""

    include_code: bool = True
    """Whether to include the symbol's source code content"""


markdown_template: Final = """
# Symbol: `{{ path | join: "." }}` (`{{ kind }}`) at `{{ file_path }}`

{% if detail != nil -%}
## Detail
{{ detail }}
{%- endif %}

{% if hover != nil -%}
## Documentation
{{ hover }}
{%- endif %}

{% if code != nil -%}
## Implementation
```{{ file_path.suffix | remove_first: "." }}
{{ code }}
```
{%- endif %}
"""


class SymbolResponse(SymbolInfo, Response):
    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
