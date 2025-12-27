from typing import Final, Literal

from pydantic import ConfigDict

from .abc import Response, SymbolInfoRequest
from .locate import LocateRequest
from .types import SymbolInfo


class DefinitionRequest(LocateRequest, SymbolInfoRequest):
    """
    Finds the definition, declaration, or type definition of a symbol.

    Use this to jump to the actual source code where a symbol is defined,
    its declaration site, or the definition of its type/class.
    """

    mode: Literal["definition", "declaration", "type_definition"] = "definition"
    """The type of location to find."""


markdown_template: Final = """
# {{ request.mode | replace: "_", " " | capitalize }} Result

### `{{ file_path }}`: {{ path | join: "." }} (`{{ kind }}`)

{% if detail -%}
{{ detail }}
{%- endif %}

{% if hover != nil -%}
## Documentation
{{ hover }}
{%- endif %}

{% if code != nil -%}
## Content
```{{ file_path.suffix | remove_first: "." }}
{{ code }}
```
{%- endif %}
"""


class DefinitionResponse(SymbolInfo, Response):
    request: DefinitionRequest

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
