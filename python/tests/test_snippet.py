from lsprotocol.types import Position, Range

from lsap.utils.content import SnippetReader


def test_read_single_line():
    content = "hello world\nsecond line"
    reader = SnippetReader(document=content)
    # Read "hello"
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=0, character=5)
    )
    result = reader.read(read_range)
    assert result is not None
    assert result.exact_content == "hello"
    assert result.content == "hello world\n"
    assert result.range == read_range


def test_read_multi_line():
    content = "line one\nline two\nline three"
    reader = SnippetReader(document=content)
    # Read from "one" to "two"
    read_range = Range(
        start=Position(line=0, character=5), end=Position(line=1, character=8)
    )
    result = reader.read(read_range)
    assert result is not None
    # "one\nline two"
    assert result.exact_content == "one\nline two"
    assert result.content == "line one\nline two\n"
    assert result.range == read_range


def test_read_empty_content():
    reader = SnippetReader(document="")
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=0, character=5)
    )
    result = reader.read(read_range)
    assert result is None


def test_read_out_of_bounds_line():
    content = "only one line"
    reader = SnippetReader(document=content)
    read_range = Range(
        start=Position(line=2, character=0), end=Position(line=2, character=5)
    )
    result = reader.read(read_range)
    assert result is None


def test_read_across_all_lines():
    content = "a\nb\nc"
    reader = SnippetReader(document=content)
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=2, character=1)
    )
    result = reader.read(read_range)
    assert result is not None
    assert result.exact_content == "a\nb\nc"
    assert result.content == "a\nb\nc"


def test_read_end_line_out_of_bounds():
    content = "line 0\nline 1"
    reader = SnippetReader(document=content)
    # End line 5 is out of bounds
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=5, character=0)
    )
    result = reader.read(read_range)
    assert result is not None
    assert result.exact_content == "line 0\nline 1"
    assert result.content == "line 0\nline 1"


def test_read_with_trailing_newline():
    content = "line 0\n"
    reader = SnippetReader(document=content)
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=1, character=0)
    )
    result = reader.read(read_range)
    assert result is not None
    assert result.exact_content == "line 0\n"
    assert result.content == "line 0\n"


def test_read_large_character_offset():
    content = "short"
    reader = SnippetReader(document=content)
    # character 100 is out of bounds for "short"
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=0, character=100)
    )
    result = reader.read(read_range)
    assert result is not None
    assert result.exact_content == "short"
    assert result.content == "short"


def test_read_dedent():
    content = "    def foo():\n        pass"
    reader = SnippetReader(document=content)
    read_range = Range(
        start=Position(line=1, character=8), end=Position(line=1, character=12)
    )
    result = reader.read(read_range)
    assert result is not None
    assert result.exact_content == "pass"
    assert result.content == "pass"
