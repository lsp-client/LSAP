"""
Functional tests for Relation API.

Tests the call chain discovery capability that answers "how does A reach B?"
"""

from pathlib import Path
from contextlib import asynccontextmanager

import pytest
from lsprotocol.types import (
    CallHierarchyIncomingCall,
    CallHierarchyItem,
    CallHierarchyOutgoingCall,
    CallHierarchyOutgoingCallsParams,
    DocumentSymbol,
    SymbolKind,
)
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import Range as LSPRange
from lsp_client.capability.request import (
    WithRequestCallHierarchy,
    WithRequestDocumentSymbol,
)
from lsp_client.client.document_state import DocumentStateManager
from lsp_client.protocol import CapabilityClientProtocol
from lsp_client.protocol.lang import LanguageConfig
from lsp_client.utils.config import ConfigurationMap
from lsp_client.utils.workspace import (
    DEFAULT_WORKSPACE_DIR,
    Workspace,
    WorkspaceFolder,
)
from lsprotocol.types import LanguageKind

from lsap.capability.relation import RelationCapability
from lsap.schema.locate import Locate, SymbolScope
from lsap.schema.relation import ChainNode, RelationRequest, RelationResponse


def test_chain_node_creation():
    """Test creating a ChainNode."""
    node = ChainNode(
        name="handle_request",
        kind="Function",
        file_path=Path("src/controllers.py"),
    )
    assert node.name == "handle_request"
    assert node.kind == "Function"
    assert node.file_path == Path("src/controllers.py")
    assert node.detail is None


def test_chain_node_with_detail():
    """Test creating a ChainNode with detail."""
    node = ChainNode(
        name="UserService.get_user",
        kind="Method",
        file_path=Path("src/services/user.py"),
        detail="(user_id: int) -> User",
    )
    assert node.name == "UserService.get_user"
    assert node.kind == "Method"
    assert node.detail == "(user_id: int) -> User"


def test_relation_request_creation():
    """Test creating a RelationRequest."""
    req = RelationRequest(
        source=Locate(
            file_path=Path("src/controllers.py"),
            scope=SymbolScope(symbol_path=["handle_request"]),
        ),
        target=Locate(
            file_path=Path("src/db.py"),
            scope=SymbolScope(symbol_path=["query"]),
        ),
    )
    assert req.source.file_path == Path("src/controllers.py")
    assert req.target.file_path == Path("src/db.py")
    assert req.max_depth == 10  # default


def test_relation_request_with_custom_max_depth():
    """Test creating a RelationRequest with custom max_depth."""
    req = RelationRequest(
        source=Locate(
            file_path=Path("src/controllers.py"),
            scope=SymbolScope(symbol_path=["handle_request"]),
        ),
        target=Locate(
            file_path=Path("src/db.py"),
            scope=SymbolScope(symbol_path=["query"]),
        ),
        max_depth=5,
    )
    assert req.max_depth == 5


def test_relation_response_with_single_chain():
    """Test RelationResponse with a single call chain."""
    source = ChainNode(
        name="handle_request",
        kind="Function",
        file_path=Path("src/controllers.py"),
    )
    target = ChainNode(
        name="query",
        kind="Function",
        file_path=Path("src/db.py"),
    )

    chain = [
        source,
        ChainNode(
            name="UserService.get_user",
            kind="Method",
            file_path=Path("src/services/user.py"),
        ),
        target,
    ]

    req = RelationRequest(
        source=Locate(
            file_path=Path("src/controllers.py"),
            scope=SymbolScope(symbol_path=["handle_request"]),
        ),
        target=Locate(
            file_path=Path("src/db.py"),
            scope=SymbolScope(symbol_path=["query"]),
        ),
    )

    resp = RelationResponse(
        request=req,
        source=source,
        target=target,
        chains=[chain],
    )

    assert len(resp.chains) == 1
    assert len(resp.chains[0]) == 3
    assert resp.chains[0][0].name == "handle_request"
    assert resp.chains[0][1].name == "UserService.get_user"
    assert resp.chains[0][2].name == "query"


def test_relation_response_with_multiple_chains():
    """Test RelationResponse with multiple call chains (example from docs)."""
    source = ChainNode(
        name="handle_request",
        kind="Function",
        file_path=Path("src/controllers.py"),
    )
    target = ChainNode(
        name="query",
        kind="Function",
        file_path=Path("src/db.py"),
    )

    # Chain 1: handle_request -> UserService.get_user -> db.query
    chain1 = [
        source,
        ChainNode(
            name="UserService.get_user",
            kind="Method",
            file_path=Path("src/services/user.py"),
        ),
        target,
    ]

    # Chain 2: handle_request -> AuthService.validate_token -> SessionManager.get_session -> db.query
    chain2 = [
        source,
        ChainNode(
            name="AuthService.validate_token",
            kind="Method",
            file_path=Path("src/services/auth.py"),
        ),
        ChainNode(
            name="SessionManager.get_session",
            kind="Method",
            file_path=Path("src/services/session.py"),
        ),
        target,
    ]

    req = RelationRequest(
        source=Locate(
            file_path=Path("src/controllers.py"),
            scope=SymbolScope(symbol_path=["handle_request"]),
        ),
        target=Locate(
            file_path=Path("src/db.py"),
            scope=SymbolScope(symbol_path=["query"]),
        ),
        max_depth=5,
    )

    resp = RelationResponse(
        request=req,
        source=source,
        target=target,
        chains=[chain1, chain2],
    )

    assert len(resp.chains) == 2
    assert len(resp.chains[0]) == 3
    assert len(resp.chains[1]) == 4
    assert resp.chains[0][1].name == "UserService.get_user"
    assert resp.chains[1][1].name == "AuthService.validate_token"
    assert resp.chains[1][2].name == "SessionManager.get_session"


def test_relation_response_with_no_chains():
    """Test RelationResponse when no connection found."""
    source = ChainNode(
        name="handle_request",
        kind="Function",
        file_path=Path("src/controllers.py"),
    )
    target = ChainNode(
        name="unrelated_function",
        kind="Function",
        file_path=Path("src/utils.py"),
    )

    req = RelationRequest(
        source=Locate(
            file_path=Path("src/controllers.py"),
            scope=SymbolScope(symbol_path=["handle_request"]),
        ),
        target=Locate(
            file_path=Path("src/utils.py"),
            scope=SymbolScope(symbol_path=["unrelated_function"]),
        ),
    )

    resp = RelationResponse(
        request=req,
        source=source,
        target=target,
        chains=[],
    )

    assert len(resp.chains) == 0


def test_relation_response_markdown_format_with_chains():
    """Test markdown formatting of RelationResponse with chains."""
    source = ChainNode(
        name="handle_request",
        kind="Function",
        file_path=Path("src/controllers.py"),
    )
    target = ChainNode(
        name="query",
        kind="Function",
        file_path=Path("src/db.py"),
    )

    chain = [
        source,
        ChainNode(
            name="UserService.get_user",
            kind="Method",
            file_path=Path("src/services/user.py"),
            detail="(user_id: int) -> User",
        ),
        target,
    ]

    req = RelationRequest(
        source=Locate(
            file_path=Path("src/controllers.py"),
            scope=SymbolScope(symbol_path=["handle_request"]),
        ),
        target=Locate(
            file_path=Path("src/db.py"),
            scope=SymbolScope(symbol_path=["query"]),
        ),
    )

    resp = RelationResponse(
        request=req,
        source=source,
        target=target,
        chains=[chain],
    )

    markdown = resp.format()

    # Check that markdown contains key elements
    assert "handle_request" in markdown
    assert "query" in markdown
    assert "Found 1 call chain(s)" in markdown
    assert "Chain 1" in markdown
    assert "UserService.get_user" in markdown
    assert "Method" in markdown
    assert "(user_id: int) -> User" in markdown


def test_relation_response_markdown_format_no_chains():
    """Test markdown formatting of RelationResponse with no chains."""
    source = ChainNode(
        name="handle_request",
        kind="Function",
        file_path=Path("src/controllers.py"),
    )
    target = ChainNode(
        name="unrelated_function",
        kind="Function",
        file_path=Path("src/utils.py"),
    )

    req = RelationRequest(
        source=Locate(
            file_path=Path("src/controllers.py"),
            scope=SymbolScope(symbol_path=["handle_request"]),
        ),
        target=Locate(
            file_path=Path("src/utils.py"),
            scope=SymbolScope(symbol_path=["unrelated_function"]),
        ),
        max_depth=5,
    )

    resp = RelationResponse(
        request=req,
        source=source,
        target=target,
        chains=[],
    )

    markdown = resp.format()

    # Check that markdown indicates no connection
    assert "handle_request" in markdown
    assert "unrelated_function" in markdown
    assert "No connection found" in markdown
    assert "within depth 5" in markdown


def test_chain_node_equality():
    """Test that ChainNodes with same data are equal."""
    node1 = ChainNode(
        name="foo",
        kind="Function",
        file_path=Path("test.py"),
        detail="detail",
    )
    node2 = ChainNode(
        name="foo",
        kind="Function",
        file_path=Path("test.py"),
        detail="detail",
    )
    assert node1 == node2


def test_relation_response_chain_order():
    """Test that chains preserve order."""
    source = ChainNode(
        name="a",
        kind="Function",
        file_path=Path("a.py"),
    )
    middle1 = ChainNode(
        name="b",
        kind="Function",
        file_path=Path("b.py"),
    )
    middle2 = ChainNode(
        name="c",
        kind="Function",
        file_path=Path("c.py"),
    )
    target = ChainNode(
        name="d",
        kind="Function",
        file_path=Path("d.py"),
    )

    chain = [source, middle1, middle2, target]

    req = RelationRequest(
        source=Locate(
            file_path=Path("a.py"),
            scope=SymbolScope(symbol_path=["a"]),
        ),
        target=Locate(
            file_path=Path("d.py"),
            scope=SymbolScope(symbol_path=["d"]),
        ),
    )

    resp = RelationResponse(
        request=req,
        source=source,
        target=target,
        chains=[chain],
    )

    # Verify order is preserved
    assert resp.chains[0][0].name == "a"
    assert resp.chains[0][1].name == "b"
    assert resp.chains[0][2].name == "c"
    assert resp.chains[0][3].name == "d"


def test_relation_request_with_nested_symbol_path():
    """Test RelationRequest with nested symbol paths."""
    req = RelationRequest(
        source=Locate(
            file_path=Path("src/services/user.py"),
            scope=SymbolScope(symbol_path=["UserService", "get_user"]),
        ),
        target=Locate(
            file_path=Path("src/db.py"),
            scope=SymbolScope(symbol_path=["Database", "query"]),
        ),
        max_depth=3,
    )

    assert req.source.scope.symbol_path == ["UserService", "get_user"]
    assert req.target.scope.symbol_path == ["Database", "query"]
    assert req.max_depth == 3


# ============================================================================
# Integration tests with mock LSP client
# ============================================================================


class MockRelationClient(
    WithRequestCallHierarchy, WithRequestDocumentSymbol, CapabilityClientProtocol
):
    """Mock client for testing RelationCapability with call hierarchy support."""

    def __init__(self, call_graph: dict[str, list[str]] | None = None):
        """
        Initialize mock client with a call graph.

        call_graph: Dictionary mapping symbol names to list of symbols they call.
                   Example: {"A": ["B", "C"], "B": ["D"]} means A calls B and C, B calls D.
        """
        self.call_graph = call_graph or {}
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
        return "# Mock file content"

    async def write_file(self, uri: str, content: str) -> None:
        pass

    @asynccontextmanager
    async def open_files(self, *file_paths):
        yield

    async def request_document_symbol_list(
        self, file_path: Path
    ) -> list[DocumentSymbol]:
        """Mock document symbol list - returns a single function symbol based on file name."""
        # Extract symbol name from file path (e.g., test_A.py -> A)
        name = file_path.stem.replace("test_", "")
        if name in self.call_graph or any(
            name in calls for calls in self.call_graph.values()
        ):
            return [
                DocumentSymbol(
                    name=name,
                    kind=SymbolKind.Function,
                    range=LSPRange(
                        start=LSPPosition(line=0, character=0),
                        end=LSPPosition(line=1, character=0),
                    ),
                    selection_range=LSPRange(
                        start=LSPPosition(line=0, character=4),
                        end=LSPPosition(line=0, character=4 + len(name)),
                    ),
                )
            ]
        return []

    async def request_document_symbol_information_list(self, file_path):
        return []

    def _make_call_hierarchy_item(self, name: str) -> CallHierarchyItem:
        """Create a mock CallHierarchyItem for a symbol name."""
        return CallHierarchyItem(
            name=name,
            kind=SymbolKind.Function,
            uri=f"file://test_{name}.py",
            range=LSPRange(
                start=LSPPosition(line=0, character=0),
                end=LSPPosition(line=1, character=0),
            ),
            selection_range=LSPRange(
                start=LSPPosition(line=0, character=4),
                end=LSPPosition(line=0, character=4 + len(name)),
            ),
        )

    async def prepare_call_hierarchy(
        self, file_path: Path, position: LSPPosition
    ) -> list[CallHierarchyItem] | None:
        """Mock prepare_call_hierarchy - returns item based on file path."""
        # Extract symbol name from file path (e.g., test_A.py -> A)
        name = file_path.stem.replace("test_", "")
        if name in self.call_graph or any(
            name in calls for calls in self.call_graph.values()
        ):
            return [self._make_call_hierarchy_item(name)]
        return None

    async def _request_call_hierarchy_outgoing_calls(
        self, params: CallHierarchyOutgoingCallsParams
    ) -> list[CallHierarchyOutgoingCall] | None:
        """Mock outgoing calls based on the call graph."""
        item_name = params.item.name
        if item_name not in self.call_graph:
            return []

        outgoing = []
        for target_name in self.call_graph[item_name]:
            target_item = self._make_call_hierarchy_item(target_name)
            outgoing.append(
                CallHierarchyOutgoingCall(
                    to=target_item,
                    from_ranges=[
                        LSPRange(
                            start=LSPPosition(line=0, character=0),
                            end=LSPPosition(line=0, character=1),
                        )
                    ],
                )
            )
        return outgoing


@pytest.mark.asyncio
async def test_relation_capability_single_path():
    """Test finding a single path between two symbols."""
    # Call graph: A -> B -> C
    call_graph = {"A": ["B"], "B": ["C"]}
    client = MockRelationClient(call_graph)
    capability = RelationCapability(client=client)  # type: ignore

    req = RelationRequest(
        source=Locate(
            file_path=Path("test_A.py"),
            scope=SymbolScope(symbol_path=["A"]),
        ),
        target=Locate(
            file_path=Path("test_C.py"),
            scope=SymbolScope(symbol_path=["C"]),
        ),
        max_depth=5,
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.source.name == "A"
    assert resp.target.name == "C"
    assert len(resp.chains) == 1
    assert len(resp.chains[0]) == 3  # A -> B -> C
    assert resp.chains[0][0].name == "A"
    assert resp.chains[0][1].name == "B"
    assert resp.chains[0][2].name == "C"


@pytest.mark.asyncio
async def test_relation_capability_multiple_paths():
    """Test finding multiple paths between two symbols."""
    # Call graph: A -> B -> D, A -> C -> D (two paths from A to D)
    call_graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"]}
    client = MockRelationClient(call_graph)
    capability = RelationCapability(client=client)  # type: ignore

    req = RelationRequest(
        source=Locate(
            file_path=Path("test_A.py"),
            scope=SymbolScope(symbol_path=["A"]),
        ),
        target=Locate(
            file_path=Path("test_D.py"),
            scope=SymbolScope(symbol_path=["D"]),
        ),
        max_depth=5,
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.source.name == "A"
    assert resp.target.name == "D"
    assert len(resp.chains) == 2  # Two paths: A->B->D and A->C->D

    # Both chains should start with A and end with D
    for chain in resp.chains:
        assert chain[0].name == "A"
        assert chain[-1].name == "D"
        assert len(chain) == 3  # A -> (B or C) -> D

    # Check that we have both paths
    middle_nodes = {chain[1].name for chain in resp.chains}
    assert middle_nodes == {"B", "C"}


@pytest.mark.asyncio
async def test_relation_capability_no_path():
    """Test when no path exists between source and target."""
    # Call graph: A -> B, C -> D (no connection from A to D)
    call_graph = {"A": ["B"], "C": ["D"]}
    client = MockRelationClient(call_graph)
    capability = RelationCapability(client=client)  # type: ignore

    req = RelationRequest(
        source=Locate(
            file_path=Path("test_A.py"),
            scope=SymbolScope(symbol_path=["A"]),
        ),
        target=Locate(
            file_path=Path("test_D.py"),
            scope=SymbolScope(symbol_path=["D"]),
        ),
        max_depth=5,
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.source.name == "A"
    assert resp.target.name == "D"
    assert len(resp.chains) == 0


@pytest.mark.asyncio
async def test_relation_capability_max_depth():
    """Test that max_depth is respected."""
    # Call graph: A -> B -> C -> D -> E (chain of 4 calls)
    call_graph = {"A": ["B"], "B": ["C"], "C": ["D"], "D": ["E"]}
    client = MockRelationClient(call_graph)
    capability = RelationCapability(client=client)  # type: ignore

    # With max_depth=3, we can reach D (3 hops: A->B, B->C, C->D)
    req = RelationRequest(
        source=Locate(
            file_path=Path("test_A.py"),
            scope=SymbolScope(symbol_path=["A"]),
        ),
        target=Locate(
            file_path=Path("test_C.py"),
            scope=SymbolScope(symbol_path=["C"]),
        ),
        max_depth=3,
    )

    resp = await capability(req)
    assert resp is not None
    assert len(resp.chains) == 1
    assert len(resp.chains[0]) == 3  # A -> B -> C

    # With max_depth=2, we can reach C (2 hops: A->B, B->C)
    req2 = RelationRequest(
        source=Locate(
            file_path=Path("test_A.py"),
            scope=SymbolScope(symbol_path=["A"]),
        ),
        target=Locate(
            file_path=Path("test_C.py"),
            scope=SymbolScope(symbol_path=["C"]),
        ),
        max_depth=2,
    )

    resp2 = await capability(req2)
    assert resp2 is not None
    assert len(resp2.chains) == 1

    # With max_depth=1, we cannot reach C (only B is reachable)
    req3 = RelationRequest(
        source=Locate(
            file_path=Path("test_A.py"),
            scope=SymbolScope(symbol_path=["A"]),
        ),
        target=Locate(
            file_path=Path("test_C.py"),
            scope=SymbolScope(symbol_path=["C"]),
        ),
        max_depth=1,
    )

    resp3 = await capability(req3)
    assert resp3 is not None
    assert len(resp3.chains) == 0  # Cannot reach C within max_depth=1


@pytest.mark.asyncio
async def test_relation_capability_cycle_detection():
    """Test that cycles are properly detected and don't cause infinite loops."""
    # Call graph with cycle: A -> B -> C -> B (cycle between B and C)
    # But there's also A -> B -> D (path without cycle)
    call_graph = {"A": ["B"], "B": ["C", "D"], "C": ["B"]}
    client = MockRelationClient(call_graph)
    capability = RelationCapability(client=client)  # type: ignore

    req = RelationRequest(
        source=Locate(
            file_path=Path("test_A.py"),
            scope=SymbolScope(symbol_path=["A"]),
        ),
        target=Locate(
            file_path=Path("test_D.py"),
            scope=SymbolScope(symbol_path=["D"]),
        ),
        max_depth=10,
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.source.name == "A"
    assert resp.target.name == "D"
    assert len(resp.chains) == 1  # Should find A -> B -> D
    assert len(resp.chains[0]) == 3
    assert resp.chains[0][0].name == "A"
    assert resp.chains[0][1].name == "B"
    assert resp.chains[0][2].name == "D"


@pytest.mark.asyncio
async def test_relation_capability_direct_call():
    """Test direct call (source directly calls target)."""
    # Call graph: A -> B (direct call)
    call_graph = {"A": ["B"]}
    client = MockRelationClient(call_graph)
    capability = RelationCapability(client=client)  # type: ignore

    req = RelationRequest(
        source=Locate(
            file_path=Path("test_A.py"),
            scope=SymbolScope(symbol_path=["A"]),
        ),
        target=Locate(
            file_path=Path("test_B.py"),
            scope=SymbolScope(symbol_path=["B"]),
        ),
        max_depth=5,
    )

    resp = await capability(req)
    assert resp is not None
    assert len(resp.chains) == 1
    assert len(resp.chains[0]) == 2  # Just A -> B
    assert resp.chains[0][0].name == "A"
    assert resp.chains[0][1].name == "B"


@pytest.mark.asyncio
async def test_relation_capability_different_path_lengths():
    """Test finding paths of different lengths."""
    # Call graph: A -> D (direct), A -> B -> D (2 hops), A -> C -> E -> D (3 hops)
    call_graph = {"A": ["B", "C", "D"], "B": ["D"], "C": ["E"], "E": ["D"]}
    client = MockRelationClient(call_graph)
    capability = RelationCapability(client=client)  # type: ignore

    req = RelationRequest(
        source=Locate(
            file_path=Path("test_A.py"),
            scope=SymbolScope(symbol_path=["A"]),
        ),
        target=Locate(
            file_path=Path("test_D.py"),
            scope=SymbolScope(symbol_path=["D"]),
        ),
        max_depth=5,
    )

    resp = await capability(req)
    assert resp is not None
    assert len(resp.chains) == 3  # Three paths of different lengths

    # Check path lengths
    path_lengths = sorted([len(chain) for chain in resp.chains])
    assert path_lengths == [2, 3, 4]  # Direct, 2-hop, and 3-hop paths
