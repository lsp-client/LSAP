"""
# Locate API

The Locate API provides a unified way to specify a position or range in the codebase.
It is used as a base for many other requests like `SymbolRequest`, `ReferenceRequest`,
and `HierarchyRequest`.

## String Syntax

A concise string syntax is available: `<file_path>:<scope>@<find>`

### Scope formats

- `<line>`: Single line number (e.g., `"42"`)
- `<start>,<end>`: Line range with comma (e.g., `"10,20"`). Use `0` for `<end>` to mean till EOF (e.g., `"10,0"`)
- `<symbol_path>`: Symbol path with dots (e.g., `"MyClass.my_method"`)

### Examples

- `"foo.py@self.<|>"`
- `"foo.py:42@return <|>result"`
- `"foo.py:10,20@if <|>condition"`
- `"foo.py:MyClass.my_method@self.<|>"`
- `"foo.py:MyClass"`
"""

from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ._abc import Request, Response
from .models import Position, Range
from .types import SymbolPath


class LineScope(BaseModel):
    """Scope by line range"""

    start_line: int = Field(ge=1, description="Start line number (1-based, inclusive)")
    end_line: int = Field(
        description="End line number (1-based, exclusive). When set to 0, means till EOF."
    )


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

    Marker Detection:
        The marker is automatically detected using nested bracket notation:
        - <|> (single level)
        - <<|>> (double level) if <|> appears more than once
        ... and so on

        The marker with the deepest nesting level that appears exactly once
        is chosen as the position marker.

    Examples:
        # Symbol declaration
        Locate(file_path="foo.py", scope=SymbolScope(symbol_path=["MyClass"]))

        # Completion trigger point - basic marker
        Locate(file_path="foo.py", find="self.<|>")

        # When <|> exists in source, use deeper nesting
        Locate(file_path="foo.py", find="x = <|> + y <<|>> z")
        # Will use <<|>> as the position marker

        # Specific location in function
        Locate(
            file_path="foo.py",
            scope=SymbolScope(symbol_path=["process"]),
            find="return <|>result"
        )
    """

    file_path: Path

    scope: LineScope | SymbolScope | None = None
    """Narrow search to symbol body or line range"""

    find: str | None = None
    """Text pattern with marker for exact position; if no marker, positions at match start."""

    model_config = ConfigDict(
        json_schema_extra={
            "anyOf": [
                {"required": ["file_path", "scope"]},
                {"required": ["file_path", "find"]},
            ]
        }
    )

    @model_validator(mode="after")
    def check_valid_locate(self) -> Self:
        if self.scope is None and self.find is None:
            raise ValueError("Either scope or find must be provided")
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

    model_config = ConfigDict(
        json_schema_extra={
            "anyOf": [
                {"required": ["file_path", "scope"]},
                {"required": ["file_path", "find"]},
            ]
        }
    )

    @model_validator(mode="after")
    def check_valid_locate(self) -> Self:
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
    "Located `{{ file_path }}` at `{{ position.line }}:{{ position.character }}`"
)

markdown_range_template = (
    "Located `{{ file_path }}` range "
    "`{{ range.start.line }}:{{ range.start.character }}-"
    "{{ range.end.line }}:{{ range.end.character }}`"
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


__all__ = [
    "LineScope",
    "Locate",
    "LocateRange",
    "LocateRangeRequest",
    "LocateRangeResponse",
    "LocateRequest",
    "LocateResponse",
    "SymbolScope",
]
