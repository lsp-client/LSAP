from pathlib import Path
import pytest
from lsprotocol.types import (
    DocumentSymbol,
    SymbolKind,
    Range,
    Position as LSPPosition,
    Location,
)
from lsap.protocol.reference import ReferenceCapability, ReferenceRequest
from lsap.protocol.locate import LocateText


class MockReferenceClient:
    def read_file(self, file_path: Path) -> str:
        return "class A:\n    def foo(self):\n        pass\n\na = A()\na.foo()"

    def from_uri(self, uri: str) -> Path:
        return Path(uri.replace("file://", ""))

    async def request_document_symbol_list(
        self, file_path: Path
    ) -> list[DocumentSymbol]:
        foo_symbol = DocumentSymbol(
            name="foo",
            kind=SymbolKind.Method,
            range=Range(
                start=LSPPosition(line=1, character=4),
                end=LSPPosition(line=2, character=12),
            ),
            selection_range=Range(
                start=LSPPosition(line=1, character=8),
                end=LSPPosition(line=1, character=11),
            ),
        )
        a_symbol = DocumentSymbol(
            name="A",
            kind=SymbolKind.Class,
            range=Range(
                start=LSPPosition(line=0, character=0),
                end=LSPPosition(line=2, character=12),
            ),
            selection_range=Range(
                start=LSPPosition(line=0, character=6),
                end=LSPPosition(line=0, character=7),
            ),
            children=[foo_symbol],
        )
        return [a_symbol]

    async def request_document_symbol_information_list(self, file_path: Path):
        return []

    async def request_references(
        self, file_path: Path, position: LSPPosition, include_declaration: bool
    ):
        return [
            Location(
                uri="file://test.py",
                range=Range(
                    start=LSPPosition(line=1, character=8),
                    end=LSPPosition(line=1, character=11),
                ),
            ),
            Location(
                uri="file://test.py",
                range=Range(
                    start=LSPPosition(line=5, character=2),
                    end=LSPPosition(line=5, character=5),
                ),
            ),
        ]


@pytest.mark.asyncio
async def test_reference():
    client = MockReferenceClient()
    capability = ReferenceCapability(client=client)  # type: ignore

    req = ReferenceRequest(
        locate=LocateText(file_path=Path("test.py"), line=1, find="foo")
    )

    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 2
    assert resp.items[0].symbol_path == ["A", "foo"]
    assert "def foo(self):" in resp.items[0].snippet
