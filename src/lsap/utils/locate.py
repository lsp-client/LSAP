"""Utility functions for locate string parsing and marker detection."""

from pathlib import Path
from typing import NamedTuple

from lsap.schema.locate import LineScope, Locate, SymbolScope


class MarkerPosition(NamedTuple):
    marker: str
    start_pos: int
    end_pos: int


def detect_marker(text: str) -> MarkerPosition | None:
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
            return MarkerPosition(
                marker=marker, start_pos=pos, end_pos=pos + len(marker)
            )
        elif count == 0:
            # This level doesn't exist, try next
            continue
        else:
            # Multiple occurrences, try higher nesting level
            continue

    return None


def parse_locate_string(locate_str: str) -> Locate:
    """
    Parse a locate string in the format: <file_path>:<scope>@<find>

    Format:
        - <file_path>:<scope>@<find> - Full format with scope and find
        - <file_path>:<scope> - Only file and scope
        - <file_path>@<find> - Only file and find
        - <file_path> - Only file (invalid, will raise error)

    Scope formats:
        - <line> - Single line number (e.g., "42")
        - <start>,<end> - Line range with comma (e.g., "10,20")
        - <start>-<end> - Line range with dash (e.g., "10-20")
        - <symbol_path> - Symbol path with dots (e.g., "MyClass.my_method")

    Examples:
        - "foo.py:42@return <|>result" - Line 42, find pattern
        - "foo.py:10,20@if <|>condition" - Line range 10-20, find pattern
        - "foo.py:MyClass.my_method@self.<|>" - Symbol scope, find pattern
        - "foo.py@self.<|>" - Whole file, find pattern
        - "foo.py:MyClass" - Symbol scope only
        - "foo.py:10-20" - Line range scope
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
        # Check if it's a line scope (numeric formats)
        if "," in scope_str:
            # Comma-separated line range: "10,20"
            start, end = scope_str.split(",", 1)
            scope = LineScope(line=(int(start), int(end)))
        elif "-" in scope_str and scope_str.replace("-", "").isdigit():
            # Dash-separated line range: "10-20"
            start, end = scope_str.split("-", 1)
            scope = LineScope(line=(int(start), int(end)))
        elif scope_str.isdigit():
            # Single line number: "42"
            scope = LineScope(line=int(scope_str))
        else:
            # Treat as symbol path
            symbol_path = scope_str.split(".")
            scope = SymbolScope(symbol_path=symbol_path)

    return Locate(file_path=Path(file_path_str), scope=scope, find=find)
