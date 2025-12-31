from pathlib import Path

import pytest
from lsap_schema.draft.completion import CompletionRequest
from lsap_schema.locate import LineScope, Locate
from lsprotocol.types import (
    CompletionItem as LSPCompletionItem,
    CompletionItemKind,
    Position as LSPPosition,
)

from lsap.draft.completion import CompletionCapability


class MockCompletionClient:
    def from_uri(self, uri: str) -> Path:
        return Path(uri.replace("file://", ""))

    async def request_completion(
        self, file_path: Path, position: LSPPosition, resolve: bool = False
    ) -> list[LSPCompletionItem] | None:
        if "test.py" in str(file_path) and position.line == 0:
            return [
                LSPCompletionItem(
                    label="hello",
                    kind=CompletionItemKind.Function,
                    detail="detail",
                    documentation="doc",
                )
            ]
        return []

    async def read_file(self, file_path: Path) -> str:
        return "h\n"

    async def request_document_symbol_list(self, file_path: Path):
        return []


@pytest.mark.asyncio
async def test_completion():
    client = MockCompletionClient()
    capability = CompletionCapability(client=client)  # type: ignore

    req = CompletionRequest(
        locate=Locate(file_path=Path("test.py"), scope=LineScope(line=1), find="h"),
    )

    resp = await capability(req)

    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].label == "hello"
    assert resp.items[0].kind == "Function"
    assert resp.items[0].detail == "detail"
    assert resp.items[0].documentation == "doc"
