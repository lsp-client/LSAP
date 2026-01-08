from typing import Final

from pydantic import ConfigDict

from .abc import Response
from .locate import LocateRequest


class HoverRequest(LocateRequest):
    """
    Retrieves documentation or type information for a symbol at a specific location.

    Use this to quickly see the documentation, type signature, or other relevant
    information for a symbol without jumping to its definition.
    """


markdown_template: Final = """
# Hover Information

{{ content }}
"""


class HoverResponse(Response):
    content: str
    """The hover content, usually markdown."""

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
