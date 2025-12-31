from pathlib import Path
import pytest
from lsprotocol.types import (
    DocumentSymbol,
    SymbolKind,
    Range as LSPRange,
    Position as LSPPosition,
    Location,
)
from lsap.reference import ReferenceCapability
from lsap_schema.reference import ReferenceRequest
from lsap_schema.locate import LineScope, Locate


class MockReferenceClient:
    async def read_file(self, file_path: Path) -> str:
        return "class A:\n    def foo(self):\n        pass\n\na = A()\na.foo()"

    async def request_hover(self, file_path: Path, position: LSPPosition):
        return None

    def from_uri(self, uri: str) -> Path:
        return Path(uri.replace("file://", ""))

    async def request_document_symbol_list(
        self, file_path: Path
    ) -> list[DocumentSymbol]:
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

    async def request_document_symbol_information_list(self, file_path: Path):
        return []

    async def request_references(
        self, file_path: Path, position: LSPPosition, include_declaration: bool
    ):
        return [
            Location(
                uri="file://test.py",
                range=LSPRange(
                    start=LSPPosition(line=1, character=8),
                    end=LSPPosition(line=1, character=11),
                ),
            ),
            Location(
                uri="file://test.py",
                range=LSPRange(
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
        locate=Locate(file_path=Path("test.py"), scope=LineScope(line=2), find="foo")
    )

    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 2
    assert resp.items[0].symbol is not None
    assert resp.items[0].symbol.path == ["A", "foo"]
    assert resp.items[0].code is not None
    assert "def foo(self):" in resp.items[0].code


@pytest.mark.asyncio
async def test_reference_pagination():
    client = MockReferenceClient()
    capability = ReferenceCapability(client=client)  # type: ignore

    # First page
    req1 = ReferenceRequest(
        locate=Locate(file_path=Path("test.py"), scope=LineScope(line=2), find="foo"),
        max_items=1,
    )
    resp1 = await capability(req1)
    assert resp1 is not None
    assert len(resp1.items) == 1
    assert resp1.pagination_id is not None
    assert resp1.has_more is True

    # Second page
    req2 = ReferenceRequest(
        locate=Locate(file_path=Path("test.py"), scope=LineScope(line=2), find="foo"),
        pagination_id=resp1.pagination_id,
        start_index=1,
        max_items=1,
    )
    resp2 = await capability(req2)
    assert resp2 is not None
    assert len(resp2.items) == 1
    assert resp2.has_more is False
    assert resp2.pagination_id is None
