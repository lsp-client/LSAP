from pathlib import Path

import pytest
from lsprotocol.types import MarkupContent, MarkupKind
from lsprotocol.types import Position as LSPPosition

from lsap.capability.hover import HoverCapability
from lsap.schema.hover import HoverRequest
from lsap.schema.locate import LineScope, Locate


from unittest.mock import MagicMock
from lsp_client.capability.request import WithRequestHover, WithRequestDocumentSymbol


class MockHoverClient(MagicMock):
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
async def test_hover():
    client = MockHoverClient()
    capability = HoverCapability(client=client)  # type: ignore

    req = HoverRequest(
        locate=Locate(file_path=Path("main.py"), scope=LineScope(line=1), find="foo"),
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.content == "Hover content for foo"


@pytest.mark.asyncio
async def test_hover_not_found():
    client = MockHoverClient()
    capability = HoverCapability(client=client)  # type: ignore

    req = HoverRequest(
        locate=Locate(file_path=Path("main.py"), scope=LineScope(line=1), find="bar"),
    )

    resp = await capability(req)
    assert resp is None
