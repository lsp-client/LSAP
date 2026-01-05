from pathlib import Path
from typing import Final

from pydantic import ConfigDict

from .abc import Request, Response
from .models import SymbolDetailInfo


class OutlineRequest(Request):
    """
    Retrieves a hierarchical outline of symbols within a file.

    Use this to understand the structure of a file (classes, methods, functions)
    and quickly navigate its contents.
    """

    file_path: Path


markdown_template: Final = """
# Outline for `{{ file_path }}`

{% for item in items -%}
{% assign level = item.path | size | plus: 1 -%}
{% for i in (1..level) %}#{% endfor %} {{ item.path | join: "." }} (`{{ item.kind }}`)
{% if item.detail != nil %}{{ item.detail }}{% endif %}
{% if item.hover != nil %}{{ item.hover | strip }}{% endif %}

{% endfor -%}
"""


class OutlineResponse(Response):
    file_path: Path
    items: list[SymbolDetailInfo]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
