from lsprotocol.types import Position, Range

from lsap.utils.snippet import SnippetReader


def test_read_single_line():
    content = "hello world\nsecond line"
    reader = SnippetReader(content=content)
    # Read "hello"
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=0, character=5)
    )
    result = reader.read(read_range)
    assert result.content == "hello"
    assert result.range == read_range


def test_read_multi_line():
    content = "line one\nline two\nline three"
    reader = SnippetReader(content=content)
    # Read from "one" to "two"
    read_range = Range(
        start=Position(line=0, character=5), end=Position(line=1, character=8)
    )
    result = reader.read(read_range)
    # "one\nline two"
    assert result.content == "one\nline two"
    assert result.range == read_range


def test_read_empty_content():
    reader = SnippetReader(content="")
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=0, character=5)
    )
    result = reader.read(read_range)
    assert result.content == ""


def test_read_out_of_bounds_line():
    content = "only one line"
    reader = SnippetReader(content=content)
    read_range = Range(
        start=Position(line=2, character=0), end=Position(line=2, character=5)
    )
    result = reader.read(read_range)
    assert result.content == ""


def test_read_across_all_lines():
    content = "a\nb\nc"
    reader = SnippetReader(content=content)
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=2, character=1)
    )
    result = reader.read(read_range)
    assert result.content == "a\nb\nc"


def test_read_end_line_out_of_bounds():
    content = "line 0\nline 1"
    reader = SnippetReader(content=content)
    # End line 5 is out of bounds
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=5, character=0)
    )
    result = reader.read(read_range)
    assert result.content == "line 0\nline 1"


def test_read_with_trailing_newline():
    content = "line 0\n"
    reader = SnippetReader(content=content)
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=1, character=0)
    )
    result = reader.read(read_range)
    assert result.content == "line 0\n"


def test_read_large_character_offset():
    content = "short"
    reader = SnippetReader(content=content)
    # character 100 is out of bounds for "short"
    read_range = Range(
        start=Position(line=0, character=0), end=Position(line=0, character=100)
    )
    result = reader.read(read_range)
    assert result.content == "short"
