from pathlib import Path

import pytest
from pydantic import ValidationError

from lsap.schema.locate import Locate, SymbolScope
from lsap.schema.rename import RenameExecuteRequest, RenamePreviewRequest


def test_rename_preview_request_defaults():
    """Test that RenamePreviewRequest has correct default values"""
    req = RenamePreviewRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=["MyClass", "my_method"]),
        ),
        new_name="new_method",
    )

    assert req.new_name == "new_method"


def test_rename_execute_request_defaults():
    """Test that RenameExecuteRequest has correct default values"""
    req = RenameExecuteRequest(
        rename_id="test_id_123",
    )

    assert req.rename_id == "test_id_123"
    assert req.exclude_files == []


def test_rename_execute_request_with_exclusions():
    """Test RenameExecuteRequest with excluded files"""
    req = RenameExecuteRequest(
        rename_id="test_id_123",
        exclude_files=["tests/test_utils.py", "docs/example.py"],
    )

    assert len(req.exclude_files) == 2
    assert "tests/test_utils.py" in req.exclude_files


def test_rename_execute_requires_rename_id():
    """Test that execute mode requires rename_id"""
    with pytest.raises(ValidationError):
        RenameExecuteRequest(
            # Missing rename_id
        )


def test_path_traversal_validation_absolute():
    """Test that absolute paths are rejected"""
    with pytest.raises(ValidationError, match="must be relative"):
        RenameExecuteRequest(
            rename_id="test_id",
            exclude_files=["/etc/passwd"],
        )


def test_path_traversal_validation_dotdot():
    """Test that paths with .. are rejected"""
    with pytest.raises(ValidationError, match="must be relative"):
        RenameExecuteRequest(
            rename_id="test_id",
            exclude_files=["../../../etc/passwd"],
        )


def test_rename_execute_request_with_glob_patterns():
    """Test RenameExecuteRequest with glob patterns"""
    req = RenameExecuteRequest(
        rename_id="test_id_123",
        exclude_files=["tests/**/*.py", "**/test_*.py", "*.md"],
    )

    assert len(req.exclude_files) == 3
    assert "tests/**/*.py" in req.exclude_files
    assert "**/test_*.py" in req.exclude_files
    assert "*.md" in req.exclude_files
