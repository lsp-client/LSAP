from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from .locate import Range


class SymbolOutlineItem(BaseModel):
    name: str
    kind: str
    range: Range
    children: list["SymbolOutlineItem"] = []


class SymbolOutlineRequest(BaseModel):
    """
    Retrieves a hierarchical outline of symbols within a file.

    Use this to understand the structure of a file (classes, methods, functions)
    and quickly navigate its contents.
    """

    file_path: Path


markdown_template: Final = """
### Symbol Outline for `{{ file_path }}`

{%- macro render_item(item, depth=0) %}
{{ "  " * depth }}- **{{ item.name }}** (`{{ item.kind }}`)
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
