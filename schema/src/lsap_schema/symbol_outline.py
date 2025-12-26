from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from .abc import Request, Response
from .locate import Range


class SymbolOutlineItem(BaseModel):
    name: str
    kind: str
    range: Range
    level: int = 0
    symbol_content: str | None = None


class SymbolOutlineRequest(Request):
    """
    Retrieves a hierarchical outline of symbols within a file.

    Use this to understand the structure of a file (classes, methods, functions)
    and quickly navigate its contents.
    """

    file_path: Path
    display_code_for: list[str] = []


markdown_template: Final = """
# Symbol Outline for `{{ file_path }}`

{% for item in items -%}
{% for i in (1..item.level) %}  {% endfor %}- {{ item.name }} (`{{ item.kind }}`)
{%- if item.symbol_content != nil %}
{% assign content_depth = item.level | plus: 1 %}
{% assign indent_size = content_depth | times: 2 %}
{% for i in (1..content_depth) %}  {% endfor %}```{{ file_path.suffix | slice: 1, 10 }}
{{ item.symbol_content }}
{% for i in (1..content_depth) %}  {% endfor %}```
{%- endif %}
{%- endfor %}
"""


class SymbolOutlineResponse(Response):
    file_path: Path
    items: list[SymbolOutlineItem]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
