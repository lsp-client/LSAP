from functools import cached_property

from attrs import define, frozen
from lsprotocol.types import Range


@frozen
class SnippetResult:
    content: str
    range: Range


@define
class SnippetReader:
    """
    Utility for reading snippets from a string given a Range.
    """

    content: str

    @cached_property
    def _lines(self) -> list[str]:
        return self.content.splitlines(keepends=True)

    def read(self, read_range: Range) -> SnippetResult:
        """
        Reads a continuous range from the content.

        Args:
            range: The Range to read.

        Returns:
            A SnippetResult containing the text within the range and the range itself.
        """

        if not self._lines:
            return SnippetResult(content="", range=read_range)

        start_line = read_range.start.line
        start_char = read_range.start.character
        end_line = read_range.end.line
        end_char = read_range.end.character

        # Bound check for lines
        if start_line >= len(self._lines):
            return SnippetResult(content="", range=read_range)

        if start_line == end_line:
            snippet_text = self._lines[start_line][start_char:end_char]
        else:
            parts = []
            # Start line
            parts.append(self._lines[start_line][start_char:])
            # Intermediate lines
            for i in range(start_line + 1, min(end_line, len(self._lines))):
                parts.append(self._lines[i])
            # End line
            if end_line < len(self._lines):
                parts.append(self._lines[end_line][:end_char])
            snippet_text = "".join(parts)

        return SnippetResult(content=snippet_text, range=read_range)
