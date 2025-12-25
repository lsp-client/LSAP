from typing import Final

from pydantic import ConfigDict

from .locate import LocateRequest
from .symbol import SymbolResponse


class DeclarationRequest(LocateRequest):
    """
    Finds the declaration site of a symbol.

    Use this when you need to find where a symbol is declared (e.g. in a header or interface).
    """

    include_hover: bool = True
    """Whether to include documentation for the declaration"""

    include_content: bool = True
    """Whether to include the source code of the declaration"""


class DefinitionRequest(LocateRequest):
    """
    Finds the definition/implementation site of a symbol.

    Use this when you need to jump to the actual source code where a function,
    class, or variable is defined.
    """

    include_hover: bool = True
    """Whether to include documentation for the definition"""

    include_content: bool = True
    """Whether to include the source code of the definition"""


class TypeDefinitionRequest(LocateRequest):
    """
    Finds the type definition of a symbol.

    Use this when you are at a variable and want to see the definition of its type/class.
    """

    include_hover: bool = True
    """Whether to include documentation for the type definition"""

    include_content: bool = True
    """Whether to include the source code of the type definition"""


markdown_template: Final = """
### Navigation Result

{% if hover != nil -%}
#### Documentation
{{ hover }}
{%- endif %}

{% if symbol_content != nil -%}
#### Implementation / Declaration
```python
{{ symbol_content }}
```
{%- endif %}
"""


class DefinitionResponse(SymbolResponse):
    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
