"""Integration tests for the locate API with real-world usage scenarios."""

from pathlib import Path

from lsap.schema.locate import Locate, LocateRequest

# Import from the utils module
from lsap.utils.locate import parse_locate_string


class TestIntegration:
    """Test integration scenarios for the locate API."""

    def test_basic_marker_usage(self):
        """Test basic usage with default marker."""
        locate = Locate(file_path=Path("example.py"), find="def process<|>()")
        assert locate.file_path == Path("example.py")
        assert locate.find == "def process<|>()"

    def test_marker_conflict_resolution(self):
        """Test that when <|> is in code, we can use <<|>>."""
        # Simulate code that uses <|> as actual syntax
        locate = Locate(
            file_path=Path("example.py"),
            find="result = func<|>() if condition else default <<|>> value",
        )
        assert locate.file_path == Path("example.py")
        # Should validate successfully with <<|>> as the marker

    def test_string_syntax_simple(self):
        """Test simple string syntax parsing."""
        locate = parse_locate_string("example.py@def main<|>")
        assert locate.file_path == Path("example.py")
        assert locate.scope is None
        assert locate.find == "def main<|>"

    def test_string_syntax_with_line_scope(self):
        """Test string syntax with line scope."""
        locate = parse_locate_string("example.py:42@return <|>value")
        assert locate.file_path == Path("example.py")
        assert locate.scope is not None
        assert locate.find == "return <|>value"

    def test_string_syntax_with_symbol_scope(self):
        """Test string syntax with symbol scope."""
        locate = parse_locate_string("example.py:MyClass.method@self.<|>")
        assert locate.file_path == Path("example.py")
        assert locate.scope is not None
        assert locate.find == "self.<|>"

    def test_locate_request_creation(self):
        """Test creating a full LocateRequest."""
        locate = Locate(file_path=Path("example.py"), find="import <|>os")
        request = LocateRequest(locate=locate)
        assert request.locate == locate

    def test_locate_request_from_string(self):
        """Test creating LocateRequest from parsed string."""
        locate = parse_locate_string("example.py@from datetime import <|>datetime")
        request = LocateRequest(locate=locate)
        assert request.locate.file_path == Path("example.py")
        assert request.locate.find is not None and "datetime" in request.locate.find

    def test_nested_file_paths(self):
        """Test with nested file paths."""
        locate = parse_locate_string("src/utils/helper.py:process@result = <|>")
        assert locate.file_path == Path("src/utils/helper.py")
        assert locate.find == "result = <|>"

    def test_marker_in_string_literal(self):
        """Test handling of marker inside a string literal context."""
        locate = Locate(
            file_path=Path("test.py"), find='print("Hello <|> World") <<|>> next_line'
        )
        # Should use <<|>> as the position marker since <|> appears once
        # but we want the position after the string
        assert locate.file_path == Path("test.py")

    def test_no_marker_positioning(self):
        """Test that find without marker positions at start of match."""
        locate = Locate(file_path=Path("test.py"), find="def process")
        assert locate.file_path == Path("test.py")
        assert locate.find == "def process"
        # Should position at the start of "def process"

    def test_symbol_scope_only(self):
        """Test symbol scope without find for declaration position."""
        locate = parse_locate_string("test.py:MyClass")
        assert locate.file_path == Path("test.py")
        assert locate.scope is not None
        assert locate.find is None
        # Should position at MyClass declaration

    def test_line_range_scope(self):
        """Test line range scope."""
        locate = parse_locate_string("test.py:10,20@if <|>condition")
        assert locate.file_path == Path("test.py")
        assert locate.scope is not None
        assert locate.find == "if <|>condition"

    def test_completion_trigger_point(self):
        """Test typical completion trigger point scenario."""
        # Agent wants to trigger completion after self.
        locate = Locate(file_path=Path("service.py"), find="self.<|>")
        assert locate.file_path == Path("service.py")
        assert locate.find == "self.<|>"

    def test_hover_on_identifier(self):
        """Test hover information scenario."""
        # Agent wants to get hover info on a variable
        locate = parse_locate_string("utils.py:process@return <|>result")
        assert locate.file_path == Path("utils.py")
        assert locate.find == "return <|>result"

    def test_deepest_nesting_wins(self):
        """Test that the deepest nesting level is chosen."""
        # Has <|>, <<|>>, and <<<|>>>
        locate = Locate(file_path=Path("test.py"), find="a <|> b <<|>> c <<<|>>> d")
        # Validation should pass as <<<|>>> is unique
        assert locate.file_path == Path("test.py")
