from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class LocateText(BaseModel):
    file_path: Path
    """
    Relative file path
    """

    line: int | tuple[int, int]
    """
    line number or line range (start_line, end_line)
    """

    find: str
    """
    text snippet to find
    """

    position: Literal["start", "end"] = "start"
    """
    position in the snippet to locate, default to "start"
    """


class LocateSymbol(BaseModel):
    file_path: Path
    """
    Relative file path
    """

    symbol_path: list[str]
    """
    symbol hierarchy path, e.g., ["MyClass", "my_method"]
    """


class Locate(BaseModel):
    locate: LocateText | LocateSymbol
    """
    Locate a specific text position in the file.
    """
