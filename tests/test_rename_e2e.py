import os
from collections.abc import Sequence
from pathlib import Path
from lsp_client.utils.types import AnyPath

import pytest
from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestRename,
    WithRequestHover,
)
from lsp_client.protocol.lang import LanguageConfig
from lsp_client.protocol import CapabilityClientProtocol
from lsp_client.client.document_state import DocumentStateManager
from lsp_client.utils.config import ConfigurationMap
from lsp_client.utils.workspace import Workspace, WorkspaceFolder, DEFAULT_WORKSPACE_DIR
from lsp_client.utils.workspace_edit import (
    AnyTextEdit,
    get_edit_text,
)
from lsprotocol.types import (
    DocumentSymbol,
    OptionalVersionedTextDocumentIdentifier,
    SymbolKind,
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
from lsprotocol.types import LanguageKind

from lsap.capability.rename import RenameExecuteCapability, RenamePreviewCapability
from lsap.schema.locate import Locate, SymbolScope
from lsap.schema.rename import (
    RenameExecuteRequest,
    RenamePreviewRequest,
    RenamePreviewResponse,
)
from lsap.schema.types import Symbol, SymbolPath
from contextlib import asynccontextmanager


class E2ERenameClient(
    WithRequestDocumentSymbol,
    WithRequestRename,
    WithRequestHover,
    CapabilityClientProtocol,
):
    """A client that interacts with the real file system."""

    def __init__(self, root: Path):
        self.root = root
        self._workspace = Workspace(
            {
                DEFAULT_WORKSPACE_DIR: WorkspaceFolder(
                    uri=root.as_uri(),
                    name=DEFAULT_WORKSPACE_DIR,
                )
            }
        )
        self._config_map = ConfigurationMap()
        self._doc_state = DocumentStateManager()

    def as_uri(self, file_path: AnyPath) -> str:
        path = Path(file_path)
        abs_path = path if path.is_absolute() else self.root / path
        return abs_path.as_uri()

    def from_uri(self, uri: str, *, relative: bool = True) -> Path:
        # Simple URI to Path conversion for file://
        if not uri.startswith("file://"):
            raise ValueError(f"Unsupported URI: {uri}")

        # Remove file:// and handle both file:/// and file:// (Windows)
        path_str = uri[7:]
        if os.name == "nt" and path_str.startswith("/"):
            path_str = path_str[1:]

        path = Path(path_str)
        if relative and path.is_relative_to(self.root):
            return path.relative_to(self.root)
        return path

    def get_workspace(self) -> Workspace:
        return self._workspace

    def get_config_map(self) -> ConfigurationMap:
        return self._config_map

    def get_document_state(self) -> DocumentStateManager:
        return self._doc_state

    @classmethod
    def get_language_config(cls):
        return LanguageConfig(
            kind=LanguageKind.Python,
            suffixes=["py"],
            project_files=["pyproject.toml"],
        )

    async def request(self, req, schema):
        return None

    async def notify(self, msg):
        pass

    async def read_file(self, file_path: AnyPath) -> str:
        path = Path(file_path)
        abs_path = path if path.is_absolute() else self.root / path
        return abs_path.read_text()

    async def write_file(self, uri: str, content: str) -> None:
        path = self.from_uri(uri, relative=False)
        path.write_text(content)

    @asynccontextmanager
    async def open_files(self, *file_paths):
        yield

    async def request_document_symbol_list(self, file_path) -> list[DocumentSymbol]:
        # Return a simple symbol for "foo" at line 0
        return [
            DocumentSymbol(
                name="foo",
                kind=SymbolKind.Function,
                range=LSPRange(
                    start=LSPPosition(line=0, character=0),
                    end=LSPPosition(line=2, character=0),
                ),
                selection_range=LSPRange(
                    start=LSPPosition(line=0, character=4),
                    end=LSPPosition(line=0, character=7),
                ),
            )
        ]

    async def request_hover(self, file_path, position):
        return None

    async def request_prepare_rename(self, file_path, position) -> LSPRange | None:
        # Assume everything is fine for "foo" at (0, 4)
        return LSPRange(
            start=LSPPosition(line=0, character=4),
            end=LSPPosition(line=0, character=7),
        )

    async def request_rename_edits(
        self, file_path, position, new_name
    ) -> WorkspaceEdit | None:
        # Simulate what a server would return: rename foo to new_name in test.py
        uri = self.as_uri(file_path)
        return WorkspaceEdit(
            document_changes=[
                TextDocumentEdit(
                    text_document=OptionalVersionedTextDocumentIdentifier(uri=uri),
                    edits=[
                        TextEdit(
                            range=LSPRange(
                                start=LSPPosition(line=0, character=4),
                                end=LSPPosition(line=0, character=7),
                            ),
                            new_text=new_name,
                        )
                    ],
                )
            ]
        )

    async def apply_workspace_edit(self, edit: WorkspaceEdit) -> None:
        # Real application to disk
        if edit.document_changes:
            for change in edit.document_changes:
                if isinstance(change, TextDocumentEdit):
                    uri = change.text_document.uri
                    content = await self.read_file(self.from_uri(uri, relative=False))
                    # Simple application for tests
                    new_content = self._apply_edits(content, change.edits)
                    await self.write_file(uri, new_content)
        elif edit.changes:
            for uri, edits in edit.changes.items():
                content = await self.read_file(self.from_uri(uri, relative=False))
                new_content = self._apply_edits(content, edits)
                await self.write_file(uri, new_content)

    def _apply_edits(self, content: str, edits: Sequence[AnyTextEdit]) -> str:
        lines = content.splitlines(keepends=True)
        # Sort edits in reverse order
        sorted_edits = sorted(
            edits,
            key=lambda e: (e.range.start.line, e.range.start.character),
            reverse=True,
        )
        for edit in sorted_edits:
            start = edit.range.start
            end = edit.range.end
            new_text = get_edit_text(edit)

            if start.line == end.line:
                line = lines[start.line]
                lines[start.line] = (
                    line[: start.character] + new_text + line[end.character :]
                )
            else:
                # Basic multi-line support for tests
                start_line = lines[start.line]
                end_line = lines[end.line]
                new_start_line = (
                    start_line[: start.character] + new_text + end_line[end.character :]
                )
                lines[start.line] = new_start_line
                del lines[start.line + 1 : end.line + 1]

        return "".join(lines)


@pytest.mark.asyncio
async def test_rename_e2e_lifecycle(tmp_path: Path):
    # 1. Setup: Create a real file
    file_path = tmp_path / "test.py"
    file_path.write_text("def foo():\n    pass\n")

    client = E2ERenameClient(tmp_path)
    preview_cap = RenamePreviewCapability(client=client)  # type: ignore
    exec_cap = RenameExecuteCapability(client=client)  # type: ignore

    locate = Locate(
        file_path=Path("test.py"),
        scope=SymbolScope(symbol_path=SymbolPath([Symbol("foo")])),
    )

    # 2. Preview
    preview_req = RenamePreviewRequest(locate=locate, new_name="bar")
    preview_resp = await preview_cap(preview_req)

    assert preview_resp is not None
    assert isinstance(preview_resp, RenamePreviewResponse)
    rename_id = preview_resp.rename_id
    assert preview_resp.old_name == "foo"
    assert preview_resp.new_name == "bar"
    assert len(preview_resp.changes) == 1
    assert preview_resp.changes[0].diffs[0].original == "def foo():"
    assert preview_resp.changes[0].diffs[0].modified == "def bar():"

    # Verify file is NOT changed yet
    assert file_path.read_text() == "def foo():\n    pass\n"

    # 3. Execute
    exec_req = RenameExecuteRequest(rename_id=rename_id)
    exec_resp = await exec_cap(exec_req)

    assert exec_resp is not None
    # 4. Verify file IS changed on disk
    assert file_path.read_text() == "def bar():\n    pass\n"

    # 5. Verify execute response details
    assert exec_resp.old_name == "foo"
    assert exec_resp.new_name == "bar"
    assert exec_resp.total_files == 1


@pytest.mark.asyncio
async def test_rename_e2e_multiple_files(tmp_path: Path):
    # Setup two files
    f1 = tmp_path / "f1.py"
    f1.write_text("def foo(): pass")
    f2 = tmp_path / "f2.py"
    f2.write_text("foo()")

    class MultiFileClient(E2ERenameClient):
        async def request_rename_edits(
            self, file_path, position, new_name
        ) -> WorkspaceEdit:
            return WorkspaceEdit(
                document_changes=[
                    TextDocumentEdit(
                        text_document=OptionalVersionedTextDocumentIdentifier(
                            uri=self.as_uri(Path("f1.py"))
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
                            uri=self.as_uri(Path("f2.py"))
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

    client = MultiFileClient(tmp_path)
    preview_cap = RenamePreviewCapability(client=client)  # type: ignore
    exec_cap = RenameExecuteCapability(client=client)  # type: ignore

    locate = Locate(file_path=Path("f1.py"), find="foo")

    # Preview
    preview_resp = await preview_cap(
        RenamePreviewRequest(locate=locate, new_name="bar")
    )
    assert preview_resp is not None
    assert isinstance(preview_resp, RenamePreviewResponse)
    rename_id = preview_resp.rename_id
    assert len(preview_resp.changes) == 2

    # Execute with exclusion
    exec_req = RenameExecuteRequest(
        rename_id=rename_id,
        exclude_files=["f2.py"],
    )
    await exec_cap(exec_req)

    # Verify: f1 changed, f2 NOT changed
    assert f1.read_text() == "def bar(): pass"
    assert f2.read_text() == "foo()"


@pytest.mark.asyncio
async def test_rename_e2e_multiple_occurrences_single_file(tmp_path: Path):
    # Setup file with multiple occurrences
    f1 = tmp_path / "f1.py"
    f1.write_text("def foo():\n    foo()\n    print(foo)")

    class MultiOccurClient(E2ERenameClient):
        async def request_rename_edits(
            self, file_path, position, new_name
        ) -> WorkspaceEdit:
            uri = self.as_uri(file_path)
            return WorkspaceEdit(
                document_changes=[
                    TextDocumentEdit(
                        text_document=OptionalVersionedTextDocumentIdentifier(uri=uri),
                        edits=[
                            TextEdit(
                                range=LSPRange(LSPPosition(0, 4), LSPPosition(0, 7)),
                                new_text=new_name,
                            ),
                            TextEdit(
                                range=LSPRange(LSPPosition(1, 4), LSPPosition(1, 7)),
                                new_text=new_name,
                            ),
                            TextEdit(
                                range=LSPRange(LSPPosition(2, 10), LSPPosition(2, 13)),
                                new_text=new_name,
                            ),
                        ],
                    )
                ]
            )

    client = MultiOccurClient(tmp_path)
    preview_cap = RenamePreviewCapability(client=client)  # type: ignore
    exec_cap = RenameExecuteCapability(client=client)  # type: ignore

    locate = Locate(file_path=Path("f1.py"), find="foo")
    preview_resp = await preview_cap(
        RenamePreviewRequest(locate=locate, new_name="bar")
    )
    assert preview_resp is not None
    assert isinstance(preview_resp, RenamePreviewResponse)
    assert preview_resp.total_occurrences == 3

    await exec_cap(RenameExecuteRequest(rename_id=preview_resp.rename_id))
    assert f1.read_text() == "def bar():\n    bar()\n    print(bar)"


@pytest.mark.asyncio
async def test_rename_e2e_legacy_changes_format(tmp_path: Path):
    # Setup file
    f1 = tmp_path / "f1.py"
    f1.write_text("def foo(): pass")

    class LegacyClient(E2ERenameClient):
        async def request_rename_edits(
            self, file_path, position, new_name
        ) -> WorkspaceEdit:
            uri = self.as_uri(file_path)
            return WorkspaceEdit(
                changes={
                    uri: [
                        TextEdit(
                            range=LSPRange(LSPPosition(0, 4), LSPPosition(0, 7)),
                            new_text=new_name,
                        )
                    ]
                }
            )

    client = LegacyClient(tmp_path)
    preview_cap = RenamePreviewCapability(client=client)  # type: ignore
    exec_cap = RenameExecuteCapability(client=client)  # type: ignore

    locate = Locate(file_path=Path("f1.py"), find="foo")
    preview_resp = await preview_cap(
        RenamePreviewRequest(locate=locate, new_name="bar")
    )
    assert preview_resp is not None
    assert isinstance(preview_resp, RenamePreviewResponse)
    assert preview_resp.total_occurrences == 1

    await exec_cap(RenameExecuteRequest(rename_id=preview_resp.rename_id))
    assert f1.read_text() == "def bar(): pass"


@pytest.mark.asyncio
async def test_rename_e2e_no_op_rename(tmp_path: Path):
    f1 = tmp_path / "f1.py"
    f1.write_text("def foo(): pass")

    client = E2ERenameClient(tmp_path)
    preview_cap = RenamePreviewCapability(client=client)  # type: ignore
    exec_cap = RenameExecuteCapability(client=client)  # type: ignore

    locate = Locate(file_path=Path("f1.py"), find="foo")
    # Rename foo -> foo
    preview_resp = await preview_cap(
        RenamePreviewRequest(locate=locate, new_name="foo")
    )
    assert preview_resp is not None
    assert isinstance(preview_resp, RenamePreviewResponse)
    assert preview_resp.total_occurrences == 1
    assert preview_resp.changes[0].diffs[0].original == "def foo(): pass"
    assert preview_resp.changes[0].diffs[0].modified == "def foo(): pass"

    await exec_cap(RenameExecuteRequest(rename_id=preview_resp.rename_id))
    assert f1.read_text() == "def foo(): pass"


@pytest.mark.asyncio
async def test_rename_e2e_exclude_all(tmp_path: Path):
    f1 = tmp_path / "f1.py"
    f1.write_text("def foo(): pass")

    client = E2ERenameClient(tmp_path)
    preview_cap = RenamePreviewCapability(client=client)  # type: ignore
    exec_cap = RenameExecuteCapability(client=client)  # type: ignore

    locate = Locate(file_path=Path("f1.py"), find="foo")
    preview_resp = await preview_cap(
        RenamePreviewRequest(locate=locate, new_name="bar")
    )
    assert preview_resp is not None
    assert isinstance(preview_resp, RenamePreviewResponse)

    await exec_cap(
        RenameExecuteRequest(
            rename_id=preview_resp.rename_id,
            exclude_files=["f1.py"],
        )
    )
    # Should NOT have changed
    assert f1.read_text() == "def foo(): pass"
