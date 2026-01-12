from pathlib import Path
from unittest.mock import MagicMock

import pytest
from lsp_client.capability.request import WithRequestDocumentSymbol, WithRequestHover
from lsprotocol.types import MarkupContent, MarkupKind
from lsprotocol.types import Position as LSPPosition

from lsap.capability.doc import DocCapability
from lsap.schema.doc import DocRequest
from lsap.schema.locate import LineScope, Locate


class MockDocClient(MagicMock):
    def __init__(self, *args, **kwargs):
        class MockProtocols(WithRequestHover, WithRequestDocumentSymbol):
            pass

        super().__init__(spec=MockProtocols, *args, **kwargs)

    def from_uri(self, uri: str) -> Path:
        return Path(uri.replace("file://", ""))

    async def request_hover(
        self, file_path: Path, position: LSPPosition
    ) -> MarkupContent | None:
        if "main.py" in str(file_path) and position.line == 0:
            return MarkupContent(
                kind=MarkupKind.Markdown,
                value="Hover content for foo",
            )
        return None

    async def read_file(self, file_path: Path) -> str:
        return "def foo():\n    pass"

    async def request_document_symbol_list(self, file_path: Path):
        return []


@pytest.mark.asyncio
async def test_doc():
    client = MockDocClient()
    capability = DocCapability(client=client)  # type: ignore

    req = DocRequest(
        locate=Locate(file_path=Path("main.py"), scope=LineScope(line=1), find="foo"),
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.content == "Hover content for foo"


@pytest.mark.asyncio
async def test_doc_not_found():
    client = MockDocClient()
    capability = DocCapability(client=client)  # type: ignore

    req = DocRequest(
        locate=Locate(file_path=Path("main.py"), scope=LineScope(line=1), find="bar"),
    )

    resp = await capability(req)
    assert resp is None
