from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from ..abc import SymbolPath


class Position(BaseModel):
    line: int
    character: int


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

    position: Literal["start", "end"] = "start"
    """Position in the snippet to locate, default to 'start'"""


class LocateSymbol(BaseModel):
    """Locate by symbol path"""

    file_path: Path
    """Relative file path"""

    symbol_path: SymbolPath
    """Symbol hierarchy path, e.g., ["MyClass", "my_method"]"""


class LocateRequest(BaseModel):
    locate: LocateText | LocateSymbol


class LocateResponse(BaseModel):
    file_path: Path
    position: Position

    model_config = ConfigDict(
        json_schema_extra={
            "lsap_templates": {
                "markdown": "Located `{{ file_path }}` at {{ position.line + 1 }}:{{ position.character + 1 }}"
            }
        }
    )
