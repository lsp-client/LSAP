"""Refer to [document](docs/locate_design.md) for locate design details."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from .abc import Request, Response
from .models import Position, Range
from .types import SymbolPath

HERE = "<HERE>"
"""Default marker token for exact position in find pattern"""


def detect_marker(text: str) -> tuple[str, int, int] | None:
    """
    Detect the marker in the text using nested bracket notation.
    
    Returns tuple of (marker, start_pos, end_pos) or None if no marker found.
    
    The marker detection uses the following priority:
    1. <|> (single level)
    2. <<|>> (double level)
    3. <<<|>>> (triple level)
    ... and so on
    
    The function selects the marker with the most nesting levels that appears
    exactly once in the text.
    """
    max_level = 10  # reasonable maximum nesting level
    
    for level in range(1, max_level + 1):
        marker = "<" * level + "|" + ">" * level
        count = text.count(marker)
        
        if count == 1:
            # Found a unique marker at this level
            pos = text.find(marker)
            return marker, pos, pos + len(marker)
        elif count == 0:
            # This level doesn't exist, try next
            continue
        else:
            # Multiple occurrences, try higher nesting level
            continue
    
    return None


def parse_locate_string(locate_str: str) -> "Locate":
    """
    Parse a locate string in the format: <file_path>:<scope>@<find>
    
    Format:
        - <file_path>:<scope>@<find> - Full format with scope and find
        - <file_path>:<scope> - Only file and scope
        - <file_path>@<find> - Only file and find
        - <file_path> - Only file (invalid, will raise error)
    
    Scope formats:
        - L<line> - Single line (e.g., "L42")
        - L<start>-<end> - Line range (e.g., "L10-20")
        - <symbol_path> - Symbol path with dots (e.g., "MyClass.my_method")
    
    Examples:
        - "foo.py:L42@return <|>result" - Line 42, find pattern
        - "foo.py:MyClass.my_method@self.<|>" - Symbol scope, find pattern
        - "foo.py@self.<|>" - Whole file, find pattern
        - "foo.py:MyClass" - Symbol scope only
        - "foo.py:L10-20" - Line range scope
    """
    # Split by @ first to separate find from file_path:scope
    if "@" in locate_str:
        path_scope, find = locate_str.rsplit("@", 1)
        find = find if find else None
    else:
        path_scope = locate_str
        find = None
    
    # Split by : to separate file_path from scope
    if ":" in path_scope:
        file_path_str, scope_str = path_scope.split(":", 1)
    else:
        file_path_str = path_scope
        scope_str = None
    
    # Parse scope
    scope = None
    if scope_str:
        # Check if it's a line scope
        if scope_str.startswith("L"):
            line_part = scope_str[1:]
            if "-" in line_part:
                start, end = line_part.split("-", 1)
                scope = LineScope(line=(int(start), int(end)))
            else:
                scope = LineScope(line=int(line_part))
        else:
            # Treat as symbol path
            symbol_path = scope_str.split(".")
            scope = SymbolScope(symbol_path=symbol_path)
    
    return Locate(
        file_path=Path(file_path_str),
        scope=scope,
        find=find
    )


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

    Marker Detection:
        The marker is automatically detected using nested bracket notation:
        - <|> (single level)
        - <<|>> (double level) if <|> appears more than once
        - <<<|>>> (triple level) if <<|>> appears more than once
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
    """Optional: narrow search to symbol body or line range"""

    find: str | None = None
    """Text pattern with marker for exact position; if no marker, positions at match start."""

    @model_validator(mode="after")
    def check_valid_locate(self):
        if self.scope is None and self.find is None:
            raise ValueError("Either scope or find must be provided")
        if self.find is not None:
            marker_info = detect_marker(self.find)
            if marker_info:
                marker, _, _ = marker_info
                # Check for multiple occurrences of the detected marker
                count = self.find.count(marker)
                if count > 1:
                    raise ValueError(
                        f"Multiple markers found: '{marker}' appears {count} times. "
                        f"Use a deeper nesting level like '<{'<' * (marker.count('<') + 1)}|{'>' * (marker.count('>') + 1)}>'."
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
