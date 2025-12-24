import textwrap
from bisect import bisect_right
from functools import cached_property

from attrs import define, frozen
from lsprotocol.types import Position, Range


@frozen
class Snippet:
    """
    Result of a content read operation.
    """

    content: str
    """Full lines within the range, dedented."""

    exact_content: str
    """The exact text within the specified range."""

    range: Range


@define
class SnippetReader:
    """
    Utility for reading snippets from a string given a Range.
    """

    document: str

    @cached_property
    def _lines(self) -> list[str]:
        return self.document.splitlines(keepends=True)

    @cached_property
    def _line_starts(self) -> list[int]:
        starts = [0]
        for line in self._lines:
            starts.append(starts[-1] + len(line))
        return starts

    def offset_to_position(self, start: Position, offset: int) -> Position:
        """
        Convert a relative offset from a start position to an absolute Position.
        """
        abs_offset = self._line_starts[start.line] + start.character + offset
        line_idx = bisect_right(self._line_starts, abs_offset) - 1
        line_idx = max(0, min(line_idx, len(self._lines) - 1))
        char_idx = abs_offset - self._line_starts[line_idx]
        return Position(line=line_idx, character=char_idx)

    def read(self, read_range: Range) -> Snippet | None:
        """
        Reads a continuous range from the content.

        Args:
            read_range: The Range to read.

        Returns:
            A Content object or None if the range is out of bounds.
        """

        if not self._lines:
            return

        start_line = read_range.start.line
        start_char = read_range.start.character
        end_line = min(read_range.end.line, len(self._lines))
        end_char = read_range.end.character

        if start_line >= len(self._lines):
            return

        start_offset = self._line_starts[start_line] + start_char
        # If end_line is at the end or beyond, cap it to the last offset
        end_offset = self._line_starts[end_line]
        if end_line < len(self._lines):
            end_offset = self._line_starts[end_line] + end_char

        # Ensure end_offset doesn't exceed next line's start or document end
        end_offset = min(
            end_offset, self._line_starts[min(end_line + 1, len(self._lines))]
        )

        exact_content = self.document[start_offset:end_offset]

        # Content: range line scope, dedented
        # If end_char is 0, the last line is excluded unless it's the start line.
        last_line_idx = (
            read_range.end.line
            if end_char > 0
            else max(start_line, read_range.end.line - 1)
        )
        lines = self._lines[start_line : min(last_line_idx + 1, len(self._lines))]
        content = textwrap.dedent("".join(lines))

        return Snippet(content=content, exact_content=exact_content, range=read_range)
