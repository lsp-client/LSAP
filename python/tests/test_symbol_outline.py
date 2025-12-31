from pathlib import Path

import pytest
from lsprotocol.types import (
    DocumentSymbol,
    Position as LSPPosition,
    Range as LSPRange,
    SymbolKind,
)

from lsap.symbol_outline import SymbolOutlineCapability
from lsap_schema.symbol_outline import SymbolOutlineRequest


class MockSymbolOutlineClient:
    async def read_file(self, file_path: Path) -> str:
        return "class A:\n    def foo(self):\n        pass"

    async def request_document_symbol_list(
        self, file_path: Path
    ) -> list[DocumentSymbol]:
        # class A
        foo_symbol = DocumentSymbol(
            name="foo",
            kind=SymbolKind.Method,
            range=LSPRange(
                start=LSPPosition(line=1, character=4),
                end=LSPPosition(line=2, character=12),
            ),
            selection_range=LSPRange(
                start=LSPPosition(line=1, character=8),
                end=LSPPosition(line=1, character=11),
            ),
        )
        a_symbol = DocumentSymbol(
            name="A",
            kind=SymbolKind.Class,
            range=LSPRange(
                start=LSPPosition(line=0, character=0),
                end=LSPPosition(line=2, character=12),
            ),
            selection_range=LSPRange(
                start=LSPPosition(line=0, character=6),
                end=LSPPosition(line=0, character=7),
            ),
            children=[foo_symbol],
        )
        return [a_symbol]

    async def request_hover(self, file_path: Path, position: LSPPosition):
        return None


@pytest.mark.asyncio
async def test_symbol_outline():
    client = MockSymbolOutlineClient()
    capability = SymbolOutlineCapability(client=client)  # type: ignore

    req = SymbolOutlineRequest(file_path=Path("test.py"))

    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 2

    assert resp.items[0].name == "A"
    assert len(resp.items[0].path) == 1

    assert resp.items[1].name == "foo"
    assert len(resp.items[1].path) == 2
