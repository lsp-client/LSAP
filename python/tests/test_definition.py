from pathlib import Path
from typing import Sequence

import pytest
from lsap_schema.definition import DefinitionRequest
from lsap_schema.locate import LocateText
from lsprotocol.types import DocumentSymbol, Location, SymbolKind
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import Range as LSPRange

from lsap.definition import DefinitionCapability


class MockDefinitionClient:
    def from_uri(self, uri: str) -> Path:
        return Path(uri.replace("file://", ""))

    async def request_definition(
        self, file_path: Path, position: LSPPosition
    ) -> Location | Sequence[Location] | None:
        if "main.py" in str(file_path):
            return Location(
                uri="file:///lib.py",
                range=LSPRange(
                    start=LSPPosition(line=0, character=4),
                    end=LSPPosition(line=0, character=7),
                ),
            )
        return None

    async def request_declaration(self, file_path: Path, position: LSPPosition):
        return None

    async def request_type_definition(self, file_path: Path, position: LSPPosition):
        return None

    async def request_hover(self, file_path: Path, position: LSPPosition):
        return None

    async def read_file(self, file_path: Path) -> str:
        if "lib.py" in str(file_path):
            return "def foo():\n    pass"
        return "import lib\nlib.foo()"

    async def request_document_symbol_list(
        self, file_path: Path
    ) -> list[DocumentSymbol]:
        if "lib.py" in str(file_path):
            return [
                DocumentSymbol(
                    name="foo",
                    kind=SymbolKind.Function,
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


@pytest.mark.asyncio
async def test_definition():
    client = MockDefinitionClient()
    capability = DefinitionCapability(client=client)  # type: ignore

    req = DefinitionRequest(
        locate=LocateText(file_path=Path("main.py"), line=1, find="foo"),
        mode="definition",
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.file_path == Path("/lib.py")
    assert resp.name == "foo"
    assert resp.path == ["foo"]
    assert resp.code is not None
    assert "def foo():" in resp.code
