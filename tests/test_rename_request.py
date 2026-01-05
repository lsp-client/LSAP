from pathlib import Path

import pytest
from pydantic import ValidationError

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

    assert req.show_diffs is False
    assert req.max_items == 100


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


def test_rename_request_with_max_items():
    """Test RenameRequest with max_items"""
    req = RenameRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
        max_items=10,
    )

    assert req.max_items == 10


def test_rename_request_max_items_validation():
    """Test that max_items must be >= 1"""
    with pytest.raises(ValidationError):
        RenameRequest(
            locate=Locate(
                file_path=Path("test.py"),
                scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
            ),
            new_name="new_method",
            max_items=0,
        )


def test_rename_request_full_configuration():
    """Test RenameRequest with all options"""
    req = RenameRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
        show_diffs=True,
        max_items=5,
        start_index=10,
    )

    assert req.show_diffs is True
    assert req.max_items == 5
    assert req.start_index == 10
