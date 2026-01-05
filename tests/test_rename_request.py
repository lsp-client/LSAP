from pathlib import Path

import pytest

from lsap_schema import Locate, RenameRequest, SymbolScope


def test_rename_request_defaults():
    """Test that RenameRequest has correct default values"""
    req = RenameRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
    )

    assert req.mode == "preview"
    assert req.show_diffs is False
    assert req.scope_filter is None
    assert req.max_files is None


def test_rename_request_preview_mode():
    """Test RenameRequest with preview mode"""
    req = RenameRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
        mode="preview",
    )

    assert req.mode == "preview"


def test_rename_request_execute_mode():
    """Test RenameRequest with execute mode"""
    req = RenameRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
        mode="execute",
    )

    assert req.mode == "execute"


def test_rename_request_with_diffs():
    """Test RenameRequest with show_diffs enabled"""
    req = RenameRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
        show_diffs=True,
    )

    assert req.show_diffs is True


def test_rename_request_with_scope_filter():
    """Test RenameRequest with scope_filter"""
    req = RenameRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
        scope_filter=[Path("src/"), Path("tests/")],
    )

    assert req.scope_filter == [Path("src/"), Path("tests/")]


def test_rename_request_with_max_files():
    """Test RenameRequest with max_files"""
    req = RenameRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
        max_files=10,
    )

    assert req.max_files == 10


def test_rename_request_max_files_validation():
    """Test that max_files must be >= 1"""
    with pytest.raises(Exception):  # Pydantic validation error
        RenameRequest(
            locate=Locate(
                file_path=Path("test.py"),
                scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
            ),
            new_name="new_method",
            max_files=0,
        )


def test_rename_request_full_configuration():
    """Test RenameRequest with all options"""
    req = RenameRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
        mode="execute",
        show_diffs=True,
        scope_filter=[Path("src/models.py"), Path("src/views.py")],
        max_files=5,
    )

    assert req.mode == "execute"
    assert req.show_diffs is True
    assert req.scope_filter == [Path("src/models.py"), Path("src/views.py")]
    assert req.max_files == 5
