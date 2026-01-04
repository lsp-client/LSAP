from pathlib import Path
from typing import Sequence

import pytest
from lsap_schema.search import SearchRequest
from lsprotocol.types import (
    Location,
    Position as LSPPosition,
    Range as LSPRange,
    SymbolKind as LSPSymbolKind,
    WorkspaceSymbol,
)

from lsap.search import SearchCapability


class MockSearchClient:
    def from_uri(self, uri: str) -> Path:
        return Path(uri.replace("file://", ""))

    async def request_workspace_symbol_list(
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


@pytest.mark.asyncio
async def test_search():
    client = MockSearchClient()
    capability = SearchCapability(client=client)  # type: ignore

    req = SearchRequest(query="foo")
    resp = await capability(req)

    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].name == "foo"
    assert resp.items[0].file_path == Path("/test.py")
    assert resp.items[0].line == 1


@pytest.mark.asyncio
async def test_search_empty():
    client = MockSearchClient()
    capability = SearchCapability(client=client)  # type: ignore

    req = SearchRequest(query="bar")
    resp = await capability(req)

    assert resp is not None
    assert len(resp.items) == 0
