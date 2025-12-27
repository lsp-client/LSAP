from pathlib import Path
import pytest
from lsprotocol.types import (
    DocumentSymbol,
    SymbolKind,
    Range as LSPRange,
    Position as LSPPosition,
)
from lsap.symbol import SymbolCapability
from lsap_schema.symbol import SymbolRequest
from lsap.locate import LocateText, LocateSymbol
from lsap_schema.abc import Symbol, SymbolPath


class MockSymbolClient:
    async def request_hover(self, file_path: Path, position: LSPPosition):
        return None

    def read_file(self, file_path: Path) -> str:
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


@pytest.mark.asyncio
async def test_symbol_from_path():
    client = MockSymbolClient()
    capability = SymbolCapability(client=client)  # type: ignore

    req = SymbolRequest(
        locate=LocateSymbol(
            file_path=Path("test.py"),
            symbol_path=SymbolPath([Symbol("A"), Symbol("foo")]),
        )
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.symbol_path == ["A", "foo"]
    assert resp.symbol_content is not None
    assert "def foo(self):" in resp.symbol_content
    assert "pass" in resp.symbol_content


@pytest.mark.asyncio
async def test_symbol_from_text():
    client = MockSymbolClient()
    capability = SymbolCapability(client=client)  # type: ignore

    req = SymbolRequest(
        locate=LocateText(file_path=Path("test.py"), line=1, find="foo")
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.symbol_path == ["A", "foo"]
    assert resp.symbol_content is not None
    assert "def foo(self):" in resp.symbol_content


def test_iter_symbols():
    foo_symbol = DocumentSymbol(
        name="foo",
        kind=SymbolKind.Method,
        range=LSPRange(
            start=LSPPosition(line=1, character=4),
            end=LSPPosition(line=1, character=10),
        ),
        selection_range=LSPRange(
            start=LSPPosition(line=1, character=4),
            end=LSPPosition(line=1, character=10),
        ),
    )
    a_symbol = DocumentSymbol(
        name="A",
        kind=SymbolKind.Class,
        range=LSPRange(
            start=LSPPosition(line=0, character=0),
            end=LSPPosition(line=2, character=0),
        ),
        selection_range=LSPRange(
            start=LSPPosition(line=0, character=0),
            end=LSPPosition(line=2, character=0),
        ),
        children=[foo_symbol],
    )

    symbols = [a_symbol]
    client = MockSymbolClient()
    capability = SymbolCapability(client=client)  # type: ignore

    results = list(capability.iter_symbols(symbols))
    assert len(results) == 2
    assert results[0][0] == ["A"]
    assert results[0][1].name == "A"
    assert results[1][0] == ["A", "foo"]
    assert results[1][1].name == "foo"
