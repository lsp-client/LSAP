from pathlib import Path
from typing import Sequence

import pytest
from lsprotocol.types import (
    Location,
    LocationUriOnly,
    WorkspaceSymbol,
)
from lsprotocol.types import (
    Position as LSPPosition,
)
from lsprotocol.types import (
    Range as LSPRange,
)
from lsprotocol.types import (
    SymbolKind as LSPSymbolKind,
)
from lsp_client.capability.request import WithRequestWorkspaceSymbol
from lsp_client.protocol.lang import LanguageConfig
from lsp_client.protocol import CapabilityClientProtocol
from lsp_client.client.document_state import DocumentStateManager
from lsp_client.utils.config import ConfigurationMap
from lsp_client.utils.workspace import Workspace, WorkspaceFolder, DEFAULT_WORKSPACE_DIR
from lsprotocol.types import LanguageKind
from lsap.capability.search import SearchCapability
from lsap.schema.models import SymbolKind
from lsap.schema.search import SearchRequest
from contextlib import asynccontextmanager


class MockSearchClient(
    WithRequestWorkspaceSymbol,
    CapabilityClientProtocol,
):
    def __init__(self):
        self._workspace = Workspace(
            {
                DEFAULT_WORKSPACE_DIR: WorkspaceFolder(
                    uri=Path.cwd().as_uri(),
                    name=DEFAULT_WORKSPACE_DIR,
                )
            }
        )
        self._config_map = ConfigurationMap()
        self._doc_state = DocumentStateManager()

    def from_uri(self, uri: str, *, relative: bool = True) -> Path:
        return Path(uri.replace("file://", ""))

    def get_workspace(self) -> Workspace:
        return self._workspace

    def get_config_map(self) -> ConfigurationMap:
        return self._config_map

    def get_document_state(self) -> DocumentStateManager:
        return self._doc_state

    @classmethod
    def get_language_config(cls):
        return LanguageConfig(
            kind=LanguageKind.Python,
            suffixes=["py"],
            project_files=["pyproject.toml"],
        )

    async def request(self, req, schema):
        return None

    async def notify(self, msg):
        pass

    async def read_file(self, file_path) -> str:
        return ""

    async def write_file(self, uri: str, content: str) -> None:
        pass

    @asynccontextmanager
    async def open_files(self, *file_paths):
        yield

    async def request_workspace_symbol_list(
        self, query: str, *, resolve: bool = False
    ) -> Sequence[WorkspaceSymbol]:
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


@pytest.mark.asyncio
async def test_search_resolve():
    class ResolveMockClient(MockSearchClient):
        async def request_workspace_symbol_list(
            self, query: str, *, resolve: bool = False
        ) -> Sequence[WorkspaceSymbol]:
            symbols = await super().request_workspace_symbol_list(
                query, resolve=resolve
            )
            if query == "uri_only":
                for s in symbols:
                    if s.name == "uri_only_sym":
                        # Give it a range
                        s.location = Location(
                            uri=s.location.uri,
                            range=LSPRange(
                                start=LSPPosition(line=10, character=0),
                                end=LSPPosition(line=10, character=5),
                            ),
                        )
            return symbols

    client = ResolveMockClient()
    capability = SearchCapability(client=client)  # type: ignore

    req = SearchRequest(query="uri_only")
    resp = await capability(req)

    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].name == "uri_only_sym"
    assert resp.items[0].line == 11  # 10 + 1
