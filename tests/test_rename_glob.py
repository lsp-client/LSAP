"""Test glob pattern support in rename exclude_files."""

from pathlib import Path

import pytest
from lsprotocol.types import (
    OptionalVersionedTextDocumentIdentifier,
    TextDocumentEdit,
    TextEdit,
    WorkspaceEdit,
)
from lsprotocol.types import (
    Position as LSPPosition,
)
from lsprotocol.types import (
    Range as LSPRange,
)

from lsap.capability.rename import RenameExecuteCapability, RenamePreviewCapability
from lsap.schema.locate import Locate
from lsap.schema.rename import RenameExecuteRequest, RenamePreviewRequest

from .test_rename_e2e import E2ERenameClient


class GlobPatternRenameClient(E2ERenameClient):
    """Client that returns edits for multiple files with different paths."""

    async def request_rename_edits(
        self, file_path, position, new_name
    ) -> WorkspaceEdit:
        return WorkspaceEdit(
            document_changes=[
                TextDocumentEdit(
                    text_document=OptionalVersionedTextDocumentIdentifier(
                        uri=self.as_uri(Path("src/main.py"))
                    ),
                    edits=[
                        TextEdit(
                            range=LSPRange(
                                start=LSPPosition(0, 4), end=LSPPosition(0, 7)
                            ),
                            new_text=new_name,
                        )
                    ],
                ),
                TextDocumentEdit(
                    text_document=OptionalVersionedTextDocumentIdentifier(
                        uri=self.as_uri(Path("tests/test_main.py"))
                    ),
                    edits=[
                        TextEdit(
                            range=LSPRange(
                                start=LSPPosition(0, 0), end=LSPPosition(0, 3)
                            ),
                            new_text=new_name,
                        )
                    ],
                ),
                TextDocumentEdit(
                    text_document=OptionalVersionedTextDocumentIdentifier(
                        uri=self.as_uri(Path("tests/unit/test_utils.py"))
                    ),
                    edits=[
                        TextEdit(
                            range=LSPRange(
                                start=LSPPosition(0, 0), end=LSPPosition(0, 3)
                            ),
                            new_text=new_name,
                        )
                    ],
                ),
                TextDocumentEdit(
                    text_document=OptionalVersionedTextDocumentIdentifier(
                        uri=self.as_uri(Path("docs/example.py"))
                    ),
                    edits=[
                        TextEdit(
                            range=LSPRange(
                                start=LSPPosition(0, 0), end=LSPPosition(0, 3)
                            ),
                            new_text=new_name,
                        )
                    ],
                ),
            ]
        )


@pytest.mark.asyncio
async def test_exclude_with_wildcard_pattern(tmp_path: Path):
    """Test excluding files using wildcard patterns like tests/*.py."""
    # Setup files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    main_py = src_dir / "main.py"
    main_py.write_text("def foo(): pass")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    test_main = tests_dir / "test_main.py"
    test_main.write_text("foo()")

    unit_dir = tests_dir / "unit"
    unit_dir.mkdir()
    test_utils = unit_dir / "test_utils.py"
    test_utils.write_text("foo()")

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    example = docs_dir / "example.py"
    example.write_text("foo()")

    client = GlobPatternRenameClient(tmp_path)
    preview_cap = RenamePreviewCapability(client=client)  # type: ignore
    exec_cap = RenameExecuteCapability(client=client)  # type: ignore

    locate = Locate(file_path=Path("src/main.py"), find="foo")

    # Preview
    preview_resp = await preview_cap(
        RenamePreviewRequest(locate=locate, new_name="bar")
    )
    assert preview_resp is not None
    assert len(preview_resp.changes) == 4

    # Execute with glob pattern to exclude all test files
    exec_req = RenameExecuteRequest(
        rename_id=preview_resp.rename_id,
        exclude_files=["tests/*", "tests/**/*"],
    )
    await exec_cap(exec_req)

    # Verify: src/main.py and docs/example.py changed, test files NOT changed
    assert main_py.read_text() == "def bar(): pass"
    assert example.read_text() == "bar()"
    assert test_main.read_text() == "foo()"
    assert test_utils.read_text() == "foo()"


@pytest.mark.asyncio
async def test_exclude_with_filename_pattern(tmp_path: Path):
    """Test excluding files by filename pattern."""
    # Setup files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    main_py = src_dir / "main.py"
    main_py.write_text("def foo(): pass")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    test_main = tests_dir / "test_main.py"
    test_main.write_text("foo()")

    unit_dir = tests_dir / "unit"
    unit_dir.mkdir()
    test_utils = unit_dir / "test_utils.py"
    test_utils.write_text("foo()")

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    example = docs_dir / "example.py"
    example.write_text("foo()")

    client = GlobPatternRenameClient(tmp_path)
    preview_cap = RenamePreviewCapability(client=client)  # type: ignore
    exec_cap = RenameExecuteCapability(client=client)  # type: ignore

    locate = Locate(file_path=Path("src/main.py"), find="foo")

    # Preview
    preview_resp = await preview_cap(
        RenamePreviewRequest(locate=locate, new_name="bar")
    )
    assert preview_resp is not None

    # Execute with filename pattern to exclude all test_*.py files
    exec_req = RenameExecuteRequest(
        rename_id=preview_resp.rename_id,
        exclude_files=["test_*.py"],
    )
    await exec_cap(exec_req)

    # Verify: src/main.py and docs/example.py changed,
    # test_main.py and test_utils.py NOT changed
    assert main_py.read_text() == "def bar(): pass"
    assert example.read_text() == "bar()"
    assert test_main.read_text() == "foo()"
    assert test_utils.read_text() == "foo()"


@pytest.mark.asyncio
async def test_exclude_with_multiple_patterns(tmp_path: Path):
    """Test excluding files with multiple patterns."""
    # Setup files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    main_py = src_dir / "main.py"
    main_py.write_text("def foo(): pass")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    test_main = tests_dir / "test_main.py"
    test_main.write_text("foo()")

    unit_dir = tests_dir / "unit"
    unit_dir.mkdir()
    test_utils = unit_dir / "test_utils.py"
    test_utils.write_text("foo()")

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    example = docs_dir / "example.py"
    example.write_text("foo()")

    client = GlobPatternRenameClient(tmp_path)
    preview_cap = RenamePreviewCapability(client=client)  # type: ignore
    exec_cap = RenameExecuteCapability(client=client)  # type: ignore

    locate = Locate(file_path=Path("src/main.py"), find="foo")

    # Preview
    preview_resp = await preview_cap(
        RenamePreviewRequest(locate=locate, new_name="bar")
    )
    assert preview_resp is not None

    # Execute with multiple patterns
    exec_req = RenameExecuteRequest(
        rename_id=preview_resp.rename_id,
        exclude_files=["tests/*", "tests/**/*", "docs/*.py"],
    )
    await exec_cap(exec_req)

    # Verify: only src/main.py changed
    assert main_py.read_text() == "def bar(): pass"
    assert example.read_text() == "foo()"
    assert test_main.read_text() == "foo()"
    assert test_utils.read_text() == "foo()"
