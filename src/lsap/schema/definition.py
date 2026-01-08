from typing import Final, Literal

from pydantic import ConfigDict

from .abc import Response
from .locate import LocateRequest
from .models import SymbolCodeInfo


class DefinitionRequest(LocateRequest):
    """
    Finds the definition, declaration, or type definition of a symbol.

    Use this to jump to the actual source code where a symbol is defined,
    its declaration site, or the definition of its type/class.
    """

    mode: Literal["definition", "declaration", "type_definition"] = "definition"
    """The type of location to find."""


markdown_template: Final = """
# {{ request.mode | replace: "_", " " | capitalize }} Result

{% if items.size == 0 -%}
No {{ request.mode | replace: "_", " " }} found.
{%- else -%}
{%- for item in items -%}
## `{{ item.file_path }}`: {{ item.path | join: "." }} (`{{ item.kind }}`)

{% if item.code != nil -%}
### Content
```{{ item.file_path.suffix | remove_first: "." }}
{{ item.code }}
```
{%- endif %}

{% endfor -%}
{%- endif %}
"""


class DefinitionResponse(Response):
    request: DefinitionRequest
    items: list[SymbolCodeInfo]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
