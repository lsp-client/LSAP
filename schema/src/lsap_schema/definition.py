from typing import Final, Literal

from pydantic import ConfigDict

from .locate import LocateRequest
from .symbol import SymbolResponse


class DefinitionRequest(LocateRequest):
    """
    Finds the definition, declaration, or type definition of a symbol.

    Use this to jump to the actual source code where a symbol is defined,
    its declaration site, or the definition of its type/class.
    """

    mode: Literal["definition", "declaration", "type_definition"] = "definition"
    """The type of location to find."""

    include_hover: bool = True
    """Whether to include documentation for the result."""

    include_content: bool = True
    """Whether to include the source code of the result."""


markdown_template: Final = """
# {{ mode | replace: "_", " " | capitalize }} Result

{% if hover != nil -%}
## Documentation
{{ hover }}
{%- endif %}

{% if symbol_content != nil -%}
## Content
```
{{ symbol_content }}
```
{%- endif %}
"""


class DefinitionResponse(SymbolResponse):
    mode: Literal["definition", "declaration", "type_definition"] = "definition"
    """The mode used for this response."""

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
