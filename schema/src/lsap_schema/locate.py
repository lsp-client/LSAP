from pathlib import Path
from typing import Literal, Self

from lsprotocol.types import Position as LSPPosition
from pydantic import BaseModel, ConfigDict, Field

from .abc import Request, Response, SymbolPath


class Position(BaseModel):
    """
    Represents a specific position in a file using line and character numbers.

    Note: Line and character are 1-based indices. 0-based indices are used in LSP, so conversion is needed when interfacing with LSP.
    """

    line: int = Field(ge=1)
    """1-based line number"""

    character: int = Field(ge=1)
    """1-based character (column) number"""

    @classmethod
    def from_lsp(cls, position: LSPPosition) -> Self:
        """Convert from LSP Position (0-based) to Position (1-based)"""
        return cls(line=position.line + 1, character=position.character + 1)

    def to_lsp(self) -> LSPPosition:
        return LSPPosition(line=self.line - 1, character=self.character - 1)


class Range(BaseModel):
    start: Position
    end: Position


class LocateText(BaseModel):
    file_path: Path
    """Relative file path"""

    line: int | tuple[int, int]
    """Line number or range (start, end)"""

    find: str
    """Text snippet to find"""

    find_end: Literal["start", "end"] = "start"
    """Which end of `find` should locate, default to 'start'"""


class LocateSymbol(BaseModel):
    """Locate by symbol path"""

    file_path: Path
    """Relative file path"""

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
