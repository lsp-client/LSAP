from pathlib import Path
from typing import Sequence

import pytest
from lsap_schema.workspace_symbol import WorkspaceSymbolRequest
from lsprotocol.types import (
    DocumentSymbol,
    Location,
    Position as LSPPosition,
    Range as LSPRange,
    SymbolKind as LSPSymbolKind,
    WorkspaceSymbol,
)

from lsap.workspace_symbol import WorkspaceSymbolCapability


class MockWorkspaceSymbolClient:
    def from_uri(self, uri: str) -> Path:
        return Path(uri.replace("file://", ""))

    async def request_workspace_symbol(
        self, query: str
    ) -> Sequence[WorkspaceSymbol] | None:
        if query == "foo":
            return [
                WorkspaceSymbol(
                    name="foo",
                    kind=LSPSymbolKind.Function,
                    location=Location(
                        uri="file:///test.py",
                        range=LSPRange(
                            start=LSPPosition(line=0, character=4),
                            end=LSPPosition(line=0, character=7),
                        ),
                    ),
                )
            ]
        return []

    async def request_document_symbol_list(
        self, file_path: Path
    ) -> list[DocumentSymbol]:
        if "test.py" in str(file_path):
            return [
                DocumentSymbol(
                    name="foo",
                    kind=LSPSymbolKind.Function,
                    range=LSPRange(
                        start=LSPPosition(line=0, character=0),
                        end=LSPPosition(line=1, character=8),
                    ),
                    selection_range=LSPRange(
                        start=LSPPosition(line=0, character=4),
                        end=LSPPosition(line=0, character=7),
                    ),
                )
            ]
        return []

    async def read_file(self, file_path: Path) -> str:
        return "def foo():\n    pass"

    async def request_hover(self, file_path: Path, position: LSPPosition):
        return None


@pytest.mark.asyncio
async def test_workspace_symbol():
    client = MockWorkspaceSymbolClient()
    capability = WorkspaceSymbolCapability(client=client)  # type: ignore

    req = WorkspaceSymbolRequest(query="foo")
    resp = await capability(req)

    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].name == "foo"
    assert resp.items[0].file_path == Path("/test.py")
    assert resp.items[0].path == ["foo"]


@pytest.mark.asyncio
async def test_workspace_symbol_empty():
    client = MockWorkspaceSymbolClient()
    capability = WorkspaceSymbolCapability(client=client)  # type: ignore

    req = WorkspaceSymbolRequest(query="bar")
    resp = await capability(req)

    assert resp is not None
    assert len(resp.items) == 0
