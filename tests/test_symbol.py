from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from lsp_client.capability.request import (
    WithRequestCallHierarchy,
    WithRequestDocumentSymbol,
    WithRequestHover,
)
from lsp_client.client.document_state import DocumentStateManager
from lsp_client.protocol import CapabilityClientProtocol
from lsp_client.protocol.lang import LanguageConfig
from lsp_client.utils.config import ConfigurationMap
from lsp_client.utils.types import AnyPath
from lsp_client.utils.workspace import DEFAULT_WORKSPACE_DIR, Workspace, WorkspaceFolder
from lsprotocol.types import (
    CallHierarchyIncomingCall,
    CallHierarchyOutgoingCall,
    DocumentSymbol,
    LanguageKind,
    SymbolKind,
)
from lsprotocol.types import (
    CallHierarchyItem as LSPCallHierarchyItem,
)
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import Range as LSPRange

from lsap.capability.symbol import SymbolCapability
from lsap.schema.locate import LineScope, Locate, SymbolScope
from lsap.schema.symbol import SymbolRequest
from lsap.schema.types import Symbol, SymbolPath


class MockSymbolClient(
    WithRequestCallHierarchy,
    WithRequestDocumentSymbol,
    WithRequestHover,
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
        return "class A:\n    def foo(self):\n        pass"

    async def write_file(self, uri: str, content: str) -> None:
        pass

    @asynccontextmanager
    async def open_files(self, *file_paths):
        yield

    async def request_hover(self, file_path, position):
        return None

    async def request_document_symbol_list(self, file_path) -> list[DocumentSymbol]:
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

    async def request_active_signature(self, file_path, position):
        return None

    async def request_call_hierarchy_incoming_call(
        self, file_path: AnyPath, position: LSPPosition
    ) -> list[CallHierarchyIncomingCall]:
        return [
            CallHierarchyIncomingCall(
                from_=LSPCallHierarchyItem(
                    name="caller",
                    kind=SymbolKind.Function,
                    uri="file:///caller.py",
                    range=LSPRange(
                        start=LSPPosition(line=4, character=0),
                        end=LSPPosition(line=4, character=10),
                    ),
                    selection_range=LSPRange(
                        start=LSPPosition(line=4, character=0),
                        end=LSPPosition(line=4, character=10),
                    ),
                ),
                from_ranges=[],
            )
        ]

    async def request_call_hierarchy_outgoing_call(
        self, file_path: AnyPath, position: LSPPosition
    ) -> list[CallHierarchyOutgoingCall]:
        return [
            CallHierarchyOutgoingCall(
                to=LSPCallHierarchyItem(
                    name="callee",
                    kind=SymbolKind.Function,
                    uri="file:///callee.py",
                    range=LSPRange(
                        start=LSPPosition(line=9, character=0),
                        end=LSPPosition(line=9, character=10),
                    ),
                    selection_range=LSPRange(
                        start=LSPPosition(line=9, character=0),
                        end=LSPPosition(line=9, character=10),
                    ),
                ),
                from_ranges=[],
            )
        ]


@pytest.mark.asyncio
async def test_symbol_call_hierarchy():
    client = MockSymbolClient()
    capability = SymbolCapability(client=client)  # type: ignore

    req = SymbolRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=SymbolPath([Symbol("A"), Symbol("foo")])),
        )
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.call_hierarchy is not None
    assert len(resp.call_hierarchy.incoming) == 1
    assert resp.call_hierarchy.incoming[0].name == "caller"
    assert resp.call_hierarchy.incoming[0].range.start.line == 5

    assert len(resp.call_hierarchy.outgoing) == 1
    assert resp.call_hierarchy.outgoing[0].name == "callee"
    assert resp.call_hierarchy.outgoing[0].range.start.line == 10


@pytest.mark.asyncio
async def test_symbol_from_path():
    client = MockSymbolClient()
    capability = SymbolCapability(client=client)  # type: ignore

    req = SymbolRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=SymbolScope(symbol_path=SymbolPath([Symbol("A"), Symbol("foo")])),
        )
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.info.path == ["A", "foo"]
    assert resp.info.code is not None
    assert "def foo(self):" in resp.info.code
    assert "pass" in resp.info.code


@pytest.mark.asyncio
async def test_symbol_from_text():
    client = MockSymbolClient()
    capability = SymbolCapability(client=client)  # type: ignore

    req = SymbolRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=LineScope(start_line=2, end_line=3),
            find="foo",
        )
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.info.path == ["A", "foo"]
    assert resp.info.code is not None
    assert "def foo(self):" in resp.info.code


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
    from lsap.utils.symbol import iter_symbols

    results = list(iter_symbols(symbols))
    assert len(results) == 2
    assert results[0][0] == ["A"]
    assert results[0][1].name == "A"
    assert results[1][0] == ["A", "foo"]
    assert results[1][1].name == "foo"
