from pathlib import Path
from typing import Any, Sequence

import pytest
from lsap_schema.models import SymbolKind
from lsap_schema.search import SearchRequest
from lsprotocol.types import (
    Location,
    LocationUriOnly,
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
        elif query == "multi":
            return [
                WorkspaceSymbol(
                    name=f"sym{i}",
                    kind=LSPSymbolKind.Function,
                    location=Location(
                        uri=f"file:///test{i}.py",
                        range=LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=0, character=0),
                        ),
                    ),
                )
                for i in range(10)
            ]
        elif query == "kinds":
            return [
                WorkspaceSymbol(
                    name="func",
                    kind=LSPSymbolKind.Function,
                    location=Location(
                        uri="file:///1.py",
                        range=LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=0, character=0),
                        ),
                    ),
                ),
                WorkspaceSymbol(
                    name="cls",
                    kind=LSPSymbolKind.Class,
                    location=Location(
                        uri="file:///1.py",
                        range=LSPRange(
                            start=LSPPosition(line=1, character=0),
                            end=LSPPosition(line=1, character=0),
                        ),
                    ),
                ),
            ]
        elif query == "uri_only":
            return [
                WorkspaceSymbol(
                    name="uri_only_sym",
                    kind=LSPSymbolKind.Class,
                    location=LocationUriOnly(uri="file:///uri_only.py"),
                )
            ]
        return []

    def __getattr__(self, name: str) -> Any:
        return None


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


@pytest.mark.asyncio
async def test_search_kinds():
    client = MockSearchClient()
    capability = SearchCapability(client=client)  # type: ignore

    req = SearchRequest(query="kinds", kinds=[SymbolKind.Function])
    resp = await capability(req)

    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].name == "func"
    assert resp.items[0].kind == SymbolKind.Function


@pytest.mark.asyncio
async def test_search_pagination():
    client = MockSearchClient()
    capability = SearchCapability(client=client)  # type: ignore

    # First page
    req = SearchRequest(query="multi", max_items=2)
    resp = await capability(req)

    assert resp is not None
    assert len(resp.items) == 2
    assert resp.total == 10
    assert resp.has_more is True
    assert resp.pagination_id is not None

    # Second page
    req2 = SearchRequest(
        query="multi",
        max_items=2,
        start_index=2,
        pagination_id=resp.pagination_id,
    )
    resp2 = await capability(req2)

    assert resp2 is not None
    assert len(resp2.items) == 2
    assert resp2.items[0].name != resp.items[0].name
    assert resp2.total == 10


@pytest.mark.asyncio
async def test_search_uri_only():
    client = MockSearchClient()
    capability = SearchCapability(client=client)  # type: ignore

    req = SearchRequest(query="uri_only")
    resp = await capability(req)

    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].name == "uri_only_sym"
    assert resp.items[0].file_path == Path("/uri_only.py")
    assert resp.items[0].line is None
