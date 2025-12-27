from typing import Final

from pydantic import ConfigDict

from .abc import Response
from .locate import LocateRequest
from .types import Range


class HoverRequest(LocateRequest):
    """
    Retrieves documentation or type information for a symbol at a specific location.

    Use this to quickly see the documentation, type signature, or other relevant
    information for a symbol without jumping to its definition.
    """


markdown_template: Final = """
# Hover Information

{{ contents }}
"""


class HoverResponse(Response):
    contents: str
    """The hover content, usually markdown."""

    range: Range | None = None
    """The range to which this hover applies."""

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
