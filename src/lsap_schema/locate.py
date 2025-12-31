"""Refer to [document](docs/locate_design.md) for locate design details."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, model_validator

from .abc import Request, Response
from .models import Position, Range
from .types import SymbolPath

HERE = "<HERE>"
"""Default marker token for exact position in find pattern"""


class LineScope(BaseModel):
    """Scope by line range"""

    line: int | tuple[int, int]
    """Line number or (start, end) range (1-based)"""


class SymbolScope(BaseModel):
    """Scope by symbol, also serves as declaration locator when find is omitted"""

    symbol_path: SymbolPath
    """Symbol hierarchy, e.g., ["MyClass", "my_method"]"""


class Locate(BaseModel):
    """
    Two-stage location: scope → find.

    Resolution rules:
        1. SymbolScope without find: symbol declaration position (for references, rename)
        2. With find containing marker: marker position
        3. With find only: start of matched text
        4. No scope + find: search entire file

    Examples:
        # Symbol declaration
        Locate(file_path="foo.py", scope=SymbolScope(symbol_path=["MyClass"]))

        # Completion trigger point
        Locate(file_path="foo.py", find="self.<HERE>")

        # When source contains "<HERE>", use custom marker
        Locate(file_path="foo.py", find="x = <|>value", marker="<|>")

        # Specific location in function
        Locate(
            file_path="foo.py",
            scope=SymbolScope(symbol_path=["process"]),
            find="return <HERE>result"
        )
    """

    file_path: Path

    scope: LineScope | SymbolScope | None = None
    """Optional: narrow search to symbol body or line range"""

    find: str | None = None
    """Text pattern with marker for exact position; if no marker, positions at match start."""

    marker: str = HERE
    """Position marker in find pattern. Change this if source contains the default '<HERE>'."""

    @model_validator(mode="after")
    def check_valid_locate(self):
        if self.scope is None and self.find is None:
            raise ValueError("Either scope or find must be provided")
        if self.find is not None:
            count = self.find.count(self.marker)
            if count > 1:
                raise ValueError(
                    f"Multiple markers not allowed, found {count} of '{self.marker}'"
                )
        return self


class LocateRange(BaseModel):
    """
    Locate a range.

    Examples:
        # Select symbol body
        LocateRange(file_path="foo.py", scope=SymbolScope(symbol_path=["MyClass"]))

        # Select specific text
        LocateRange(file_path="foo.py", find="if condition: return True")
    """

    file_path: Path

    scope: LineScope | SymbolScope | None = None
    """Scope defines the range; if symbol, uses symbol's full range"""

    find: str | None = None
    """Text to match; matched text becomes the range"""

    @model_validator(mode="after")
    def check_valid_locate(self):
        if self.scope is None and self.find is None:
            raise ValueError("Either scope or find must be provided")
        return self


class LocateRequest(Request):
    """Request to locate a code position."""

    locate: Locate


class LocateRangeRequest(Request):
    """Request to locate a code range."""

    locate: LocateRange


markdown_template = (
    "Located `{{ file_path }}` at {{ position.line }}:{{ position.character }}"
)

markdown_range_template = (
    "Located `{{ file_path }}` range "
    "{{ range.start.line }}:{{ range.start.character }}-"
    "{{ range.end.line }}:{{ range.end.character }}"
)


class LocateResponse(Response):
    file_path: Path
    position: Position

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


class LocateRangeResponse(Response):
    file_path: Path
    range: Range

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_range_template,
        }
    )
