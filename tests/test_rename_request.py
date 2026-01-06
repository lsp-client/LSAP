from pathlib import Path

import pytest
from pydantic import ValidationError

from lsap_schema import (
    Locate,
    RenamePreviewRequest,
    RenameExecuteRequest,
    SymbolScope,
)


def test_rename_preview_request_defaults():
    """Test that RenamePreviewRequest has correct default values"""
    req = RenamePreviewRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
    )

    assert req.mode == "preview"
    assert req.new_name == "new_method"


def test_rename_execute_request_defaults():
    """Test that RenameExecuteRequest has correct default values"""
    req = RenameExecuteRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
        rename_id="test_id_123",
    )

    assert req.mode == "execute"
    assert req.new_name == "new_method"
    assert req.rename_id == "test_id_123"
    assert req.exclude_files == []


def test_rename_execute_request_with_exclusions():
    """Test RenameExecuteRequest with excluded files"""
    req = RenameExecuteRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
        rename_id="test_id_123",
        exclude_files=[Path("tests/test_utils.py"), Path("docs/example.py")],
    )

    assert len(req.exclude_files) == 2
    assert Path("tests/test_utils.py") in req.exclude_files


def test_rename_execute_requires_rename_id():
    """Test that execute mode requires rename_id"""
    with pytest.raises(ValidationError):
        RenameExecuteRequest(
            locate=Locate(
                file_path=Path("test.py"),
                scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
            ),
            new_name="new_method",
        )


def test_path_traversal_validation_absolute():
    """Test that absolute paths are rejected"""
    with pytest.raises(ValidationError, match="must be relative"):
        RenameExecuteRequest(
            locate=Locate(
                file_path=Path("test.py"),
                scope=SymbolScope(symbol_path=["MyClass"]),
            ),
            new_name="new_method",
            rename_id="test_id",
            exclude_files=[Path("/etc/passwd")],
        )


def test_path_traversal_validation_dotdot():
    """Test that paths with .. are rejected"""
    with pytest.raises(ValidationError, match="must be relative"):
        RenameExecuteRequest(
            locate=Locate(
                file_path=Path("test.py"),
                scope=SymbolScope(symbol_path=["MyClass"]),
            ),
            new_name="new_method",
            rename_id="test_id",
            exclude_files=[Path("../../../etc/passwd")],
        )
