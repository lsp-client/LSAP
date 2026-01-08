from typing import Final

from pydantic import ConfigDict

from .abc import Response
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
