import tempfile
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
from lsap.schema.outline import OutlineRequest, SymbolScope


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

    req = OutlineRequest(path=Path("test.py"), recursive=True)

    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 2

    assert resp.items[0].name == "A"
    assert len(resp.items[0].path) == 1

    assert resp.items[1].name == "foo"
    assert len(resp.items[1].path) == 2


@pytest.mark.asyncio
async def test_outline_non_recursive():
    client = MockOutlineClient()
    capability = OutlineCapability(client=client)  # type: ignore

    req = OutlineRequest(path=Path("test.py"), recursive=False)

    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 1

    assert resp.items[0].name == "A"
    assert len(resp.items[0].path) == 1


@pytest.mark.asyncio
async def test_outline_non_recursive_expansion():
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

    req = OutlineRequest(path=Path("test.py"), recursive=False)

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

    req = OutlineRequest(path=Path("test.py"))

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

    req = OutlineRequest(path=Path("test.py"), recursive=False)

    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].name == "C"
    assert resp.items[0].path == ["A", "B", "C"]


@pytest.mark.asyncio
async def test_outline_scope():
    client = MockOutlineClient()
    capability = OutlineCapability(client=client)  # type: ignore

    # Test successful scope with recursive=True (show nested symbols)
    req = OutlineRequest(
        path=Path("test.py"),
        scope=SymbolScope(symbol_path=["A"]),
        recursive=True,
    )
    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 2
    assert resp.items[0].name == "A"
    assert resp.items[1].name == "foo"

    # Test nested scope
    req = OutlineRequest(
        path=Path("test.py"),
        scope=SymbolScope(symbol_path=["A", "foo"]),
        recursive=True,
    )
    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].name == "foo"


@pytest.mark.asyncio
async def test_outline_scope_not_found():
    client = MockOutlineClient()
    capability = OutlineCapability(client=client)  # type: ignore

    req = OutlineRequest(
        path=Path("test.py"),
        scope=SymbolScope(symbol_path=["NonExistent"]),
    )
    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 0


@pytest.mark.asyncio
async def test_outline_scope_top():
    client = MockOutlineClient()
    capability = OutlineCapability(client=client)  # type: ignore

    # With scope and recursive=False, should only return the scoped symbol itself (if it's not a module)
    # or its direct children if it is a module.
    # In MockOutlineClient, A is a class, so it should return A.
    req = OutlineRequest(
        path=Path("test.py"),
        scope=SymbolScope(symbol_path=["A"]),
        recursive=False,
    )
    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].name == "A"


@pytest.mark.asyncio
async def test_outline_scope_top_module():
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

    # Scoped to the module with recursive=False should expand the module
    req = OutlineRequest(
        path=Path("test.py"),
        scope=SymbolScope(symbol_path=["mymodule"]),
        recursive=False,
    )
    resp = await capability(req)
    assert resp is not None
    assert len(resp.items) == 1
    assert resp.items[0].name == "foo"
    assert resp.items[0].path == ["mymodule", "foo"]


@pytest.mark.asyncio
async def test_outline_directory():
    class MockDirectoryClient(MockOutlineClient):
        def __init__(self, tmpdir):
            super().__init__()
            self.tmpdir = tmpdir
            self.file_symbols = {
                "file1.py": [
                    DocumentSymbol(
                        name="ClassA",
                        kind=SymbolKind.Class,
                        range=LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=1, character=0),
                        ),
                        selection_range=LSPRange(
                            start=LSPPosition(line=0, character=6),
                            end=LSPPosition(line=0, character=12),
                        ),
                    )
                ],
                "file2.py": [
                    DocumentSymbol(
                        name="func_b",
                        kind=SymbolKind.Function,
                        range=LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=1, character=0),
                        ),
                        selection_range=LSPRange(
                            start=LSPPosition(line=0, character=4),
                            end=LSPPosition(line=0, character=10),
                        ),
                    )
                ],
            }

        async def request_document_symbol_list(self, file_path) -> list[DocumentSymbol]:
            filename = file_path.name
            return self.file_symbols.get(filename, [])

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        (tmppath / "file1.py").write_text("class ClassA:\n    pass\n")
        (tmppath / "file2.py").write_text("def func_b():\n    pass\n")
        (tmppath / "README.md").write_text("# Not a code file")

        client = MockDirectoryClient(tmppath)
        capability = OutlineCapability(client=client)  # type: ignore

        req = OutlineRequest(path=tmppath)

        resp = await capability(req)
        assert resp is not None
        assert resp.path == tmppath
        assert resp.is_directory is True
        assert resp.total_files == 2
        assert resp.total_symbols == 2

        assert len(resp.files) == 2
        file_names = {group.file_path.name for group in resp.files}
        assert file_names == {"file1.py", "file2.py"}

        for group in resp.files:
            if group.file_path.name == "file1.py":
                assert len(group.symbols) == 1
                assert group.symbols[0].name == "ClassA"
            elif group.file_path.name == "file2.py":
                assert len(group.symbols) == 1
                assert group.symbols[0].name == "func_b"


@pytest.mark.asyncio
async def test_outline_directory_recursive():
    class MockDirectoryClient(MockOutlineClient):
        def __init__(self, tmpdir):
            super().__init__()
            self.tmpdir = tmpdir
            self.file_symbols = {
                "file1.py": [
                    DocumentSymbol(
                        name="ClassA",
                        kind=SymbolKind.Class,
                        range=LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=1, character=0),
                        ),
                        selection_range=LSPRange(
                            start=LSPPosition(line=0, character=6),
                            end=LSPPosition(line=0, character=12),
                        ),
                    )
                ],
                "file2.py": [
                    DocumentSymbol(
                        name="func_b",
                        kind=SymbolKind.Function,
                        range=LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=1, character=0),
                        ),
                        selection_range=LSPRange(
                            start=LSPPosition(line=0, character=4),
                            end=LSPPosition(line=0, character=10),
                        ),
                    )
                ],
                "nested.py": [
                    DocumentSymbol(
                        name="ClassC",
                        kind=SymbolKind.Class,
                        range=LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=1, character=0),
                        ),
                        selection_range=LSPRange(
                            start=LSPPosition(line=0, character=6),
                            end=LSPPosition(line=0, character=12),
                        ),
                    )
                ],
            }

        async def request_document_symbol_list(self, file_path) -> list[DocumentSymbol]:
            filename = file_path.name
            return self.file_symbols.get(filename, [])

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        (tmppath / "file1.py").write_text("class ClassA:\n    pass\n")
        (tmppath / "file2.py").write_text("def func_b():\n    pass\n")
        subdir = tmppath / "subdir"
        subdir.mkdir()
        (subdir / "nested.py").write_text("class ClassC:\n    pass\n")

        client = MockDirectoryClient(tmppath)
        capability = OutlineCapability(client=client)  # type: ignore

        # Test non-recursive (default) - should only find files in immediate directory
        req = OutlineRequest(path=tmppath, recursive=False)
        resp = await capability(req)
        assert resp is not None
        assert resp.path == tmppath
        assert resp.is_directory is True
        assert resp.total_files == 2
        assert resp.total_symbols == 2
        file_names = {group.file_path.name for group in resp.files}
        assert file_names == {"file1.py", "file2.py"}

        # Test recursive - should find files in subdirectories too
        req = OutlineRequest(path=tmppath, recursive=True)
        resp = await capability(req)
        assert resp is not None
        assert resp.path == tmppath
        assert resp.is_directory is True
        assert resp.total_files == 3
        assert resp.total_symbols == 3
        file_names = {group.file_path.name for group in resp.files}
        assert file_names == {"file1.py", "file2.py", "nested.py"}


@pytest.mark.asyncio
async def test_outline_directory_scope_validation():
    """Test that scope parameter raises ValueError with directory paths."""

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        (tmppath / "file1.py").write_text("class ClassA:\n    pass\n")

        client = MockOutlineClient()
        capability = OutlineCapability(client=client)  # type: ignore

        # Should raise ValueError when scope is provided with directory path
        with pytest.raises(
            ValueError, match="scope cannot be used with directory paths"
        ):
            req = OutlineRequest(
                path=tmppath,
                scope={"symbol_path": ["SomeClass"]},
            )
            await capability(req)


@pytest.mark.asyncio
async def test_outline_directory_excludes_non_code_files():
    """Test that non-code files like README.md are excluded from directory outline."""

    class MockDirectoryClient(MockOutlineClient):
        def __init__(self, tmpdir):
            super().__init__()
            self.tmpdir = tmpdir
            self.file_symbols = {
                "file1.py": [
                    DocumentSymbol(
                        name="ClassA",
                        kind=SymbolKind.Class,
                        range=LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=1, character=0),
                        ),
                        selection_range=LSPRange(
                            start=LSPPosition(line=0, character=6),
                            end=LSPPosition(line=0, character=12),
                        ),
                    )
                ],
            }

        async def request_document_symbol_list(self, file_path) -> list[DocumentSymbol]:
            filename = file_path.name
            return self.file_symbols.get(filename, [])

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        (tmppath / "file1.py").write_text("class ClassA:\n    pass\n")
        (tmppath / "README.md").write_text("# Not a code file")
        (tmppath / "data.json").write_text('{"key": "value"}')

        client = MockDirectoryClient(tmppath)
        capability = OutlineCapability(client=client)  # type: ignore

        req = OutlineRequest(path=tmppath)
        resp = await capability(req)

        assert resp is not None
        assert resp.is_directory is True
        assert resp.total_files == 1
        # Explicitly verify that only the Python file is included
        file_names = {group.file_path.name for group in resp.files}
        assert file_names == {"file1.py"}
        assert "README.md" not in file_names
        assert "data.json" not in file_names


@pytest.mark.asyncio
async def test_outline_with_glob_pattern():
    """Test outline with glob pattern to filter files."""

    class MockGlobClient(MockOutlineClient):
        def __init__(self, tmpdir):
            super().__init__()
            self.tmpdir = tmpdir
            self.file_symbols = {
                "test_one.py": [
                    DocumentSymbol(
                        name="TestOne",
                        kind=SymbolKind.Class,
                        range=LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=1, character=0),
                        ),
                        selection_range=LSPRange(
                            start=LSPPosition(line=0, character=6),
                            end=LSPPosition(line=0, character=13),
                        ),
                    )
                ],
                "test_two.py": [
                    DocumentSymbol(
                        name="TestTwo",
                        kind=SymbolKind.Class,
                        range=LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=1, character=0),
                        ),
                        selection_range=LSPRange(
                            start=LSPPosition(line=0, character=6),
                            end=LSPPosition(line=0, character=13),
                        ),
                    )
                ],
            }

        async def request_document_symbol_list(self, file_path) -> list[DocumentSymbol]:
            filename = file_path.name
            return self.file_symbols.get(filename, [])

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        (tmppath / "test_one.py").write_text("class TestOne:\n    pass\n")
        (tmppath / "test_two.py").write_text("class TestTwo:\n    pass\n")
        (tmppath / "main.py").write_text("def main():\n    pass\n")

        client = MockGlobClient(tmppath)
        capability = OutlineCapability(client=client)  # type: ignore

        # Test with glob pattern to only match test files
        req = OutlineRequest(path=tmppath, glob="test_*.py")
        resp = await capability(req)

        assert resp is not None
        assert resp.is_directory is True
        assert resp.total_files == 2
        file_names = {group.file_path.name for group in resp.files}
        assert file_names == {"test_one.py", "test_two.py"}
        assert "main.py" not in file_names


@pytest.mark.asyncio
async def test_outline_glob_without_path():
    """Test outline with glob pattern without explicit base path."""

    class MockGlobClient(MockOutlineClient):
        def __init__(self, tmpdir):
            super().__init__()
            self.tmpdir = tmpdir
            self.file_symbols = {
                "nested.py": [
                    DocumentSymbol(
                        name="NestedClass",
                        kind=SymbolKind.Class,
                        range=LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=1, character=0),
                        ),
                        selection_range=LSPRange(
                            start=LSPPosition(line=0, character=6),
                            end=LSPPosition(line=0, character=17),
                        ),
                    )
                ],
            }

        async def request_document_symbol_list(self, file_path) -> list[DocumentSymbol]:
            filename = file_path.name
            return self.file_symbols.get(filename, [])

    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        subdir = tmppath / "subdir"
        subdir.mkdir()
        (subdir / "nested.py").write_text("class NestedClass:\n    pass\n")

        # Change to tmpdir to test relative glob
        old_cwd = os.getcwd()
        try:
            os.chdir(tmppath)

            client = MockGlobClient(tmppath)
            capability = OutlineCapability(client=client)  # type: ignore

            # Test with glob pattern without base path
            req = OutlineRequest(glob="subdir/*.py")
            resp = await capability(req)

            assert resp is not None
            assert resp.is_directory is True
            assert resp.total_files == 1
            file_names = {group.file_path.name for group in resp.files}
            assert file_names == {"nested.py"}
        finally:
            os.chdir(old_cwd)


@pytest.mark.asyncio
async def test_outline_validation_errors():
    """Test validation errors in OutlineRequest."""

    # Test: neither path nor glob provided
    with pytest.raises(ValueError, match="Either path or glob must be provided"):
        OutlineRequest()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        (tmppath / "test.py").write_text("class Test:\n    pass\n")

        # Test: glob with file path
        with pytest.raises(
            ValueError, match="glob can only be used with directory paths"
        ):
            OutlineRequest(path=tmppath / "test.py", glob="*.py")

        # Test: scope with glob
        with pytest.raises(ValueError, match="scope cannot be used with glob patterns"):
            OutlineRequest(glob="*.py", scope=SymbolScope(symbol_path=["Test"]))
