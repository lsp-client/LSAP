import re
import textwrap
from bisect import bisect_right
from functools import cached_property

from attrs import define, frozen
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import Range as LSPRange


@frozen
class Snippet:
    """
    Result of a content read operation.
    """

    content: str
    """Full lines within the range, dedented and prefixed with line numbers."""

    exact_content: str
    """The exact text within the specified range."""

    range: LSPRange
    """The exact range of the snippet in the document."""


@define
class DocumentReader:
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

    @property
    def full_range(self) -> LSPRange:
        """
        The Range covering the entire document.
        """
        if not self._lines:
            return LSPRange(
                start=LSPPosition(line=0, character=0),
                end=LSPPosition(line=0, character=0),
            )

        last_line_idx = len(self._lines) - 1
        return LSPRange(
            start=LSPPosition(line=0, character=0),
            end=LSPPosition(
                line=last_line_idx, character=len(self._lines[last_line_idx])
            ),
        )

    def position_to_offset(self, position: LSPPosition) -> int:
        """
        Convert a Position to a character offset.
        """
        line_idx = max(0, min(position.line, len(self._line_starts) - 1))
        offset = self._line_starts[line_idx] + position.character
        return min(offset, self._line_starts[-1])

    def offset_to_position(self, start: LSPPosition, offset: int) -> LSPPosition:
        """
        Convert a relative offset from a start position to an absolute Position.
        """
        abs_offset = self._line_starts[start.line] + start.character + offset
        line_idx = bisect_right(self._line_starts, abs_offset) - 1
        line_idx = max(0, min(line_idx, len(self._lines) - 1))
        char_idx = abs_offset - self._line_starts[line_idx]
        return LSPPosition(line=line_idx, character=char_idx)

    def get_line(self, line_idx: int, *, keepends: bool = False) -> str | None:
        """
        Get a single line by index.
        """
        if 0 <= line_idx < len(self._lines):
            line = self._lines[line_idx]
            return line if keepends else line.rstrip("\r\n")
        return None

    def word_at(self, pos: LSPPosition) -> str | None:
        """
        Extract the word at the given position.
        """
        line = self.get_line(pos.line)
        if line is None:
            return None
        for match in re.finditer(r"\w+", line):
            if match.start() <= pos.character < match.end():
                return match.group()
        return None

    def get_text(self, read_range: LSPRange) -> str:
        """
        Get the exact text within the specified range.
        """
        if not self._lines:
            return ""

        start_line = read_range.start.line
        start_char = read_range.start.character
        end_line = min(read_range.end.line, len(self._lines))
        end_char = read_range.end.character

        if start_line >= len(self._lines):
            return ""

        start_offset = self._line_starts[start_line] + start_char
        end_offset = self._line_starts[end_line]
        if end_line < len(self._lines):
            end_offset = self._line_starts[end_line] + end_char

        end_offset = min(
            end_offset, self._line_starts[min(end_line + 1, len(self._lines))]
        )

        return self.document[start_offset:end_offset]

    def read(self, read_range: LSPRange) -> Snippet | None:
        if not self._lines:
            return None

        if read_range.start.line >= len(self._lines):
            return None

        exact_content = self.get_text(read_range)

        start_line = read_range.start.line
        end_char = read_range.end.character
        last_line_idx = (
            read_range.end.line
            if end_char > 0
            else max(start_line, read_range.end.line - 1)
        )
        raw_lines = self._lines[start_line : min(last_line_idx + 1, len(self._lines))]
        dedented_lines = textwrap.dedent("".join(raw_lines)).splitlines(keepends=True)

        numbered_lines = [
            f"{start_line + i + 1}| {line}" for i, line in enumerate(dedented_lines)
        ]
        content = "".join(numbered_lines)

        return Snippet(content=content, exact_content=exact_content, range=read_range)
