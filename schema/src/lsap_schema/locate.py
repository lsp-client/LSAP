from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from .abc import Request, Response
from .types import Position as Position, Range as Range, SymbolPath


class LocateBase(BaseModel):
    file_path: Path
    """Relative file path"""


class LocateText(LocateBase):
    line: int | tuple[int, int]
    """Line number or range (start, end)"""

    find: str
    """Text snippet to find"""

    find_end: Literal["start", "end"] = "end"
    """Which end of `find` should locate, default to 'end'"""


class LocateSymbol(LocateBase):
    """Locate by symbol path"""

    symbol_path: SymbolPath
    """Symbol hierarchy path, e.g., ["MyClass", "my_method"]"""


class LocateRequest(Request):
    """
    Base request for locating code positions.

    Use this when you need to specify a target location by either a text search or a symbol path.
    """

    locate: LocateText | LocateSymbol
    """Locate by text snippet or symbol path"""


markdown_template = (
    "Located `{{ file_path }}` at {{ position.line }}:{{ position.character }}"
)


class LocateResponse(Response):
    file_path: Path
    position: Position

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
