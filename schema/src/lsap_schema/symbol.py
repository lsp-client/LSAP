from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from .abc import Response, SymbolPath
from .locate import LocateRequest


class ParameterInfo(BaseModel):
    name: str
    label: str
    """The full label of the parameter (e.g., 'timeout: int = 10')"""

    documentation: str | None = None
    """Markdown documentation for this specific parameter"""


class SymbolRequest(LocateRequest):
    """
    Retrieves detailed information about a symbol at a specific location.

    Use this to get the documentation (hover) and source code implementation
    of a symbol to understand its purpose and usage.
    """

    include_hover: bool = True
    """Whether to include hover/documentation information"""

    include_content: bool = True
    """Whether to include the symbol's source code content"""


markdown_template: Final = """
# Symbol: `{{ symbol_path | join: "." }}` in `{{ file_path }}`

{% if hover -%}
## Overview
{{ hover }}
{%- endif %}

{% if parameters.size > 0 -%}
## Parameters
| Parameter | Description |
| :--- | :--- |
{%- for p in parameters %}
| `{{ p.label }}` | {{ p.documentation | default: "" }} |
{%- endfor %}
{%- endif %}

{% if symbol_content -%}
## Implementation
```
{{ symbol_content }}
```
{%- endif %}
"""


class SymbolResponse(Response):
    file_path: Path
    symbol_path: SymbolPath
    symbol_content: str | None = None
    hover: str | None = None
    """Markdown formatted hover/documentation information"""

    parameters: list[ParameterInfo] | None = None
    """Structured parameter information (Signature Help)"""

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
