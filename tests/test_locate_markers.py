"""Tests for the new marker detection and locate string parsing functionality."""

from pathlib import Path

import pytest

from lsap.schema.locate import (
    LineScope,
    Locate,
    SymbolScope,
)

# Import from the utils module
from lsap.utils.locate import detect_marker, parse_locate_string


class TestMarkerDetection:
    """Test the auto-detection of markers with nested brackets."""

    def test_detect_single_level_marker(self):
        """Test detection of <|> marker."""
        text = "self.<|>value"
        result = detect_marker(text)
        assert result is not None
        marker, start, end = result
        assert marker == "<|>"
        assert start == 5
        assert end == 8

    def test_detect_double_level_marker(self):
        """Test detection of <<|>> when <|> appears multiple times."""
        text = "x = <|> + y <<|>> z"
        result = detect_marker(text)
        assert result is not None
        marker, start, end = result
        assert marker == "<<|>>"
        assert start == 12
        assert end == 17

    def test_detect_triple_level_marker(self):
        """Test detection of <<<|>>> when <<|>> appears multiple times."""
        text = "a <<|>> b <<|>> c <<<|>>> d"
        result = detect_marker(text)
        assert result is not None
        marker, start, end = result
        assert marker == "<<<|>>>"
        assert start == 18
        assert end == 25

    def test_no_marker_found(self):
        """Test when no marker is present."""
        text = "just some regular text"
        result = detect_marker(text)
        assert result is None

    def test_multiple_same_level_markers(self):
        """Test that multiple markers of the same level returns None."""
        text = "x <|> y <|> z"
        # Since <|> appears twice, it should try higher levels
        result = detect_marker(text)
        assert result is None  # No unique marker found at any level

    def test_single_marker_with_surrounding_text(self):
        """Test marker detection with complex surrounding text."""
        text = "function(arg1, arg2)<|>.method()"
        result = detect_marker(text)
        assert result is not None
        marker, start, end = result
        assert marker == "<|>"
        assert text[start:end] == "<|>"


class TestLocateValidation:
    """Test the validation of Locate objects with auto-detected markers."""

    def test_valid_locate_with_marker(self):
        """Test valid Locate with a marker."""
        locate = Locate(file_path=Path("foo.py"), find="self.<|>value")
        assert locate.file_path == Path("foo.py")
        assert locate.find == "self.<|>value"

    def test_valid_locate_without_marker(self):
        """Test valid Locate without a marker."""
        locate = Locate(file_path=Path("foo.py"), find="def process")
        assert locate.file_path == Path("foo.py")
        assert locate.find == "def process"

    def test_invalid_multiple_markers_same_level(self):
        """Test that multiple markers of the same level are treated as no marker."""
        # When <|> appears multiple times and no higher level exists,
        # detect_marker returns None, so it's treated as a find without marker
        locate = Locate(file_path=Path("foo.py"), find="x <|> y <|> z")
        # This is valid - will position at the start of the matched text
        assert locate.file_path == Path("foo.py")
        assert locate.find == "x <|> y <|> z"

    def test_valid_multiple_different_levels(self):
        """Test valid Locate with markers at different nesting levels."""
        locate = Locate(file_path=Path("foo.py"), find="x = <|> + y <<|>> z")
        # Should use <<|>> as it's the unique marker
        assert locate.file_path == Path("foo.py")

    def test_invalid_no_scope_no_find(self):
        """Test that Locate without scope or find raises an error."""
        with pytest.raises(ValueError, match="Either scope or find must be provided"):
            Locate(file_path=Path("foo.py"))


class TestParseLocateString:
    """Test the parsing of locate string syntax."""

    def test_parse_file_and_find(self):
        """Test parsing file path with find pattern."""
        locate = parse_locate_string("foo.py@self.<|>")
        assert locate.file_path == Path("foo.py")
        assert locate.scope is None
        assert locate.find == "self.<|>"

    def test_parse_file_line_scope_and_find(self):
        """Test parsing with line scope and find pattern."""
        locate = parse_locate_string("foo.py:42@return <|>result")
        assert locate.file_path == Path("foo.py")
        assert isinstance(locate.scope, LineScope)
        assert locate.scope.start_line == 42
        assert locate.scope.end_line == 43
        assert locate.find == "return <|>result"

    def test_parse_file_line_range_and_find(self):
        """Test parsing with line range scope and find pattern."""
        locate = parse_locate_string("foo.py:10,20@if <|>condition")
        assert locate.file_path == Path("foo.py")
        assert isinstance(locate.scope, LineScope)
        assert locate.scope.start_line == 10
        assert locate.scope.end_line == 21
        assert locate.find == "if <|>condition"

    def test_parse_file_symbol_scope_and_find(self):
        """Test parsing with symbol scope and find pattern."""
        locate = parse_locate_string("foo.py:MyClass.my_method@self.<|>")
        assert locate.file_path == Path("foo.py")
        assert isinstance(locate.scope, SymbolScope)
        assert locate.scope.symbol_path == ["MyClass", "my_method"]
        assert locate.find == "self.<|>"

    def test_parse_file_and_symbol_scope_only(self):
        """Test parsing with only file and symbol scope."""
        locate = parse_locate_string("foo.py:MyClass")
        assert locate.file_path == Path("foo.py")
        assert isinstance(locate.scope, SymbolScope)
        assert locate.scope.symbol_path == ["MyClass"]
        assert locate.find is None

    def test_parse_file_and_line_scope_only(self):
        """Test parsing with only file and line scope."""
        locate = parse_locate_string("foo.py:42")
        assert locate.file_path == Path("foo.py")
        assert isinstance(locate.scope, LineScope)
        assert locate.scope.start_line == 42
        assert locate.scope.end_line == 43
        assert locate.find is None

    def test_parse_nested_path(self):
        """Test parsing with nested file path."""
        locate = parse_locate_string("src/utils/helper.py@process<|>")
        assert locate.file_path == Path("src/utils/helper.py")
        assert locate.scope is None
        assert locate.find == "process<|>"

    def test_parse_complex_symbol_path(self):
        """Test parsing with complex symbol path."""
        locate = parse_locate_string("foo.py:OuterClass.InnerClass.method@return <|>")
        assert locate.file_path == Path("foo.py")
        assert isinstance(locate.scope, SymbolScope)
        assert locate.scope.symbol_path == ["OuterClass", "InnerClass", "method"]
        assert locate.find == "return <|>"

    def test_parse_with_double_level_marker(self):
        """Test parsing with double-level marker."""
        locate = parse_locate_string("foo.py@x = <|> + y <<|>> z")
        assert locate.file_path == Path("foo.py")
        assert locate.find == "x = <|> + y <<|>> z"

    def test_parse_line_number_without_prefix(self):
        """Test parsing with line number without L prefix."""
        locate = parse_locate_string("foo.py:42@return <|>result")
        assert locate.file_path == Path("foo.py")
        assert isinstance(locate.scope, LineScope)
        assert locate.scope.start_line == 42
        assert locate.scope.end_line == 43
        assert locate.find == "return <|>result"

    def test_parse_line_range_with_comma(self):
        """Test parsing with line range using comma separator."""
        locate = parse_locate_string("foo.py:10,20@if <|>condition")
        assert locate.file_path == Path("foo.py")
        assert isinstance(locate.scope, LineScope)
        assert locate.scope.start_line == 10
        assert locate.scope.end_line == 21
        assert locate.find == "if <|>condition"

    def test_parse_line_number_only_no_find(self):
        """Test parsing with line number only, no find pattern."""
        locate = parse_locate_string("foo.py:123")
        assert locate.file_path == Path("foo.py")
        assert isinstance(locate.scope, LineScope)
        assert locate.scope.start_line == 123
        assert locate.scope.end_line == 124
        assert locate.find is None

    def test_parse_line_range_comma_no_find(self):
        """Test parsing with comma-separated line range, no find pattern."""
        locate = parse_locate_string("foo.py:12,14")
        assert locate.file_path == Path("foo.py")
        assert isinstance(locate.scope, LineScope)
        assert locate.scope.start_line == 12
        assert locate.scope.end_line == 15
        assert locate.find is None

    def test_parse_line_range_till_eof(self):
        """Test parsing with line range till EOF (end_line=0)."""
        locate = parse_locate_string("foo.py:10,0")
        assert locate.file_path == Path("foo.py")
        assert isinstance(locate.scope, LineScope)
        assert locate.scope.start_line == 10
        assert locate.scope.end_line == 0
        assert locate.find is None
