from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestHover,
)
from lsp_client.client.document_state import DocumentStateManager
from lsp_client.protocol import CapabilityClientProtocol
from lsp_client.protocol.lang import LanguageConfig
from lsp_client.utils.config import ConfigurationMap
from lsp_client.utils.workspace import DEFAULT_WORKSPACE_DIR, Workspace, WorkspaceFolder
from lsprotocol.types import DocumentSymbol, LanguageKind, SymbolKind
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import Range as LSPRange

from lsap.capability.outline import OutlineCapability
from lsap.schema.outline import OutlineRequest


class MockOutlineClient(
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
async def test_outline():
    client = MockOutlineClient()
    capability = OutlineCapability(client=client)  # type: ignore

    req = OutlineRequest(file_path=Path("test.py"))

    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 2

    assert resp.items[0].name == "A"
    assert len(resp.items[0].path) == 1

    assert resp.items[1].name == "foo"
    assert len(resp.items[1].path) == 2


@pytest.mark.asyncio
async def test_outline_top():
    client = MockOutlineClient()
    capability = OutlineCapability(client=client)  # type: ignore

    req = OutlineRequest(file_path=Path("test.py"), top=True)

    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 1

    assert resp.items[0].name == "A"
    assert len(resp.items[0].path) == 1


@pytest.mark.asyncio
async def test_outline_top_expansion():
    class MockModuleClient(MockOutlineClient):
        async def request_document_symbol_list(self, file_path) -> list[DocumentSymbol]:
            foo_symbol = DocumentSymbol(
                name="foo",
                kind=SymbolKind.Function,
                range=LSPRange(
                    start=LSPPosition(line=1, character=0),
                    end=LSPPosition(line=1, character=10),
                ),
                selection_range=LSPRange(
                    start=LSPPosition(line=1, character=4),
                    end=LSPPosition(line=1, character=7),
                ),
            )
            module_symbol = DocumentSymbol(
                name="mymodule",
                kind=SymbolKind.Module,
                range=LSPRange(
                    start=LSPPosition(line=0, character=0),
                    end=LSPPosition(line=2, character=0),
                ),
                selection_range=LSPRange(
                    start=LSPPosition(line=0, character=0),
                    end=LSPPosition(line=0, character=0),
                ),
                children=[foo_symbol],
            )
            return [module_symbol]

    client = MockModuleClient()
    capability = OutlineCapability(client=client)  # type: ignore

    req = OutlineRequest(file_path=Path("test.py"), top=True)

    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].name == "foo"
    assert resp.items[0].path == ["mymodule", "foo"]


@pytest.mark.asyncio
async def test_outline_filtering():
    class MockFilteringClient(MockOutlineClient):
        async def request_document_symbol_list(self, file_path) -> list[DocumentSymbol]:
            inner_var = DocumentSymbol(
                name="x",
                kind=SymbolKind.Variable,
                range=LSPRange(
                    start=LSPPosition(line=2, character=8),
                    end=LSPPosition(line=2, character=9),
                ),
                selection_range=LSPRange(
                    start=LSPPosition(line=2, character=8),
                    end=LSPPosition(line=2, character=9),
                ),
            )
            inner_func = DocumentSymbol(
                name="inner",
                kind=SymbolKind.Function,
                range=LSPRange(
                    start=LSPPosition(line=3, character=8),
                    end=LSPPosition(line=4, character=8),
                ),
                selection_range=LSPRange(
                    start=LSPPosition(line=3, character=12),
                    end=LSPPosition(line=3, character=17),
                ),
            )
            foo_symbol = DocumentSymbol(
                name="foo",
                kind=SymbolKind.Function,
                range=LSPRange(
                    start=LSPPosition(line=1, character=0),
                    end=LSPPosition(line=5, character=0),
                ),
                selection_range=LSPRange(
                    start=LSPPosition(line=1, character=4),
                    end=LSPPosition(line=1, character=7),
                ),
                children=[inner_var, inner_func],
            )
            return [foo_symbol]

    client = MockFilteringClient()
    capability = OutlineCapability(client=client)  # type: ignore

    req = OutlineRequest(file_path=Path("test.py"))

    resp = await capability(req)
    assert resp is not None
    # Should only contain 'foo', not 'x' or 'inner'
    assert len(resp.items) == 1
    assert resp.items[0].name == "foo"


@pytest.mark.asyncio
async def test_outline_nested_modules():
    class MockNestedModuleClient(MockOutlineClient):
        async def request_document_symbol_list(self, file_path) -> list[DocumentSymbol]:
            func_c = DocumentSymbol(
                name="C",
                kind=SymbolKind.Function,
                range=LSPRange(
                    start=LSPPosition(line=2, character=0),
                    end=LSPPosition(line=2, character=10),
                ),
                selection_range=LSPRange(
                    start=LSPPosition(line=2, character=4),
                    end=LSPPosition(line=2, character=5),
                ),
            )
            mod_b = DocumentSymbol(
                name="B",
                kind=SymbolKind.Module,
                range=LSPRange(
                    start=LSPPosition(line=1, character=0),
                    end=LSPPosition(line=3, character=0),
                ),
                selection_range=LSPRange(
                    start=LSPPosition(line=1, character=0),
                    end=LSPPosition(line=1, character=0),
                ),
                children=[func_c],
            )
            mod_a = DocumentSymbol(
                name="A",
                kind=SymbolKind.Module,
                range=LSPRange(
                    start=LSPPosition(line=0, character=0),
                    end=LSPPosition(line=4, character=0),
                ),
                selection_range=LSPRange(
                    start=LSPPosition(line=0, character=0),
                    end=LSPPosition(line=0, character=0),
                ),
                children=[mod_b],
            )
            return [mod_a]

    client = MockNestedModuleClient()
    capability = OutlineCapability(client=client)  # type: ignore

    req = OutlineRequest(file_path=Path("test.py"), top=True)

    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].name == "C"
    assert resp.items[0].path == ["A", "B", "C"]
