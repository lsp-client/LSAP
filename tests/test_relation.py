"""
Functional tests for Relation API.

Tests the call chain discovery capability that answers "how does A reach B?"
"""

from pathlib import Path

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
