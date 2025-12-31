from typing import Final

from pydantic import ConfigDict

from .abc import Response
from .locate import LocateRequest
from .types import SymbolCodeInfo


class SymbolRequest(LocateRequest):
    """
    Retrieves detailed information about a symbol at a specific location.

    Use this to get the documentation (hover) and source code implementation
    of a symbol to understand its purpose and usage.
    """


markdown_template: Final = """
# Symbol: `{{ path | join: "." }}` (`{{ kind }}`) at `{{ file_path }}`

## Implementation
```{{ file_path.suffix | remove_first: "." }}
{{ code }}
```
"""


class SymbolResponse(SymbolCodeInfo, Response):
    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
