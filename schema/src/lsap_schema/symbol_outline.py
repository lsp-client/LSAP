from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from .locate import Range


class SymbolOutlineItem(BaseModel):
    name: str
    kind: str
    range: Range
    children: list["SymbolOutlineItem"] = []
    symbol_content: str | None = None


class SymbolOutlineRequest(BaseModel):
    """
    Retrieves a hierarchical outline of symbols within a file.

    Use this to understand the structure of a file (classes, methods, functions)
    and quickly navigate its contents.
    """

    file_path: Path
    display_code_for: list[str] = []


markdown_template: Final = """
### Symbol Outline for `{{ file_path }}`

{%- macro render_item(item, depth=0) %}
{{ "  " * depth }}- {{ item.name }} (`{{ item.kind }}`)
{%- if item.symbol_content %}

{{ "  " * (depth + 1) }}```{{ file_path.suffix[1:] if file_path.suffix else "" }}
{{ item.symbol_content | indent(width=(depth + 1) * 2, first=True) }}
{{ "  " * (depth + 1) }}```

{%- endif %}
{%- for child in item.children %}
{{ render_item(child, depth + 1) }}
{%- endfor %}
{%- endmacro %}

{%- for item in items %}
{{ render_item(item) }}
{%- endfor %}
"""


class SymbolOutlineResponse(BaseModel):
    file_path: Path
    items: list[SymbolOutlineItem]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
