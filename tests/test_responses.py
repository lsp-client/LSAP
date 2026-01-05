from pathlib import Path

import pytest

from lsap_schema import (
    CompletionItem,
    CompletionResponse,
    DefinitionResponse,
    Diagnostic,
    FileDiagnosticsResponse,
    DecoratedContentResponse,
    HierarchyItem,
    HierarchyNode,
    HierarchyResponse,
    LocateResponse,
    Location,
    Position,
    Range,
    ReferenceResponse,
    RenameDiff,
    RenameFileChange,
    RenameResponse,
    OutlineResponse,
    SymbolCodeInfo,
    SymbolDetailInfo,
    SymbolKind,
    SearchItem,
    SearchResponse,
    WorkspaceDiagnosticItem,
    WorkspaceDiagnosticsResponse,
)


def test_completion_response_format():
    resp = CompletionResponse(
        items=[CompletionItem(label="test_label", kind="Method", detail="test_detail")],
        start_index=0,
        has_more=False,
    )
    rendered = resp.format()
    assert "test_label" in rendered
    assert "Method" in rendered
    assert "test_detail" in rendered


def test_locate_response_format():
    resp = LocateResponse(
        file_path=Path("test.py"), position=Position(line=1, character=2)
    )
    rendered = resp.format()
    assert "test.py" in rendered
    assert "1:2" in rendered


def test_symbol_response_format():
    resp = SymbolResponse(
        file_path=Path("test.py"),
        name="my_method",
        path=["MyClass", "my_method"],
        kind=SymbolKind.Method,
        code="def my_method(): pass",
    )
    rendered = resp.format()
    assert "MyClass.my_method" in rendered
    assert "def my_method()" in rendered


def test_workspace_symbol_response_format():
    from lsap_schema.search import SearchRequest

    req = SearchRequest(query="test")
    resp = SearchResponse(
        request=req,
        items=[
            SearchItem(
                file_path=Path("test.py"),
                name="class MyClass",
                kind=SymbolKind.Class,
                line=1,
            ),
            SearchItem(
                file_path=Path("test.py"),
                name="my_method",
                kind=SymbolKind.Method,
                line=5,
                container="MyClass",
            ),
        ],
        start_index=0,
        has_more=False,
    )
    rendered = resp.format()
    assert "test" in rendered
    assert "MyClass" in rendered
    assert "class" in rendered
    assert "test.py" in rendered


def test_reference_response_format():
    from lsap_schema.reference import ReferenceItem, ReferenceRequest
    from lsap_schema.locate import Locate, LineScope

    item = ReferenceItem(
        location=Location(
            file_path=Path("test.py"),
            range=Range(
                start=Position(line=10, character=1),
                end=Position(line=10, character=1),
            ),
        ),
        code="test_content",
        symbol=SymbolDetailInfo(
            file_path=Path("test.py"),
            name="test",
            path=["test"],
            kind=SymbolKind.Function,
            detail="detail",
            hover="hover",
        ),
    )
    req = ReferenceRequest(
        mode="references",
        locate=Locate(
            file_path=Path("test.py"),
            scope=LineScope(line=10),
            find="test",
        ),
    )
    resp = ReferenceResponse(request=req, items=[item], start_index=0, has_more=False)
    rendered = resp.format()
    assert "References Found" in rendered
    assert "test.py:10" in rendered
    assert "test_content" in rendered


def test_implementation_response_format():
    from lsap_schema.reference import ReferenceItem, ReferenceRequest
    from lsap_schema.locate import Locate, LineScope

    item = ReferenceItem(
        location=Location(
            file_path=Path("test.py"),
            range=Range(
                start=Position(line=10, character=1),
                end=Position(line=10, character=1),
            ),
        ),
        code="test_content",
        symbol=SymbolDetailInfo(
            file_path=Path("test.py"),
            name="test",
            path=["test"],
            kind=SymbolKind.Function,
            detail="detail",
            hover="hover",
        ),
    )
    req = ReferenceRequest(
        mode="implementations",
        locate=Locate(
            file_path=Path("test.py"),
            scope=LineScope(line=10),
            find="test",
        ),
    )
    resp = ReferenceResponse(request=req, items=[item], start_index=0, has_more=False)
    rendered = resp.format()
    assert "Implementations Found" in rendered
    assert "test.py:10" in rendered
    assert "test_content" in rendered


def test_diagnostics_response_format():
    resp = FileDiagnosticsResponse(
        file_path=Path("test.py"),
        diagnostics=[
            Diagnostic(
                range=Range(
                    start=Position(line=1, character=1),
                    end=Position(line=1, character=5),
                ),
                severity="Error",
                message="test error",
            )
        ],
        start_index=0,
        has_more=False,
    )
    rendered = resp.format()
    assert "test.py" in rendered
    assert "Error" in rendered
    assert "test error" in rendered


def test_outline_response_format():
    resp = OutlineResponse(
        file_path=Path("test.py"),
        items=[
            SymbolDetailInfo(
                file_path=Path("test.py"),
                name="class MyClass",
                path=["MyClass"],
                kind=SymbolKind.Class,
                detail="class",
                hover="A test class",
            ),
            SymbolDetailInfo(
                file_path=Path("test.py"),
                name="my_method(arg1: int) -> None",
                path=["MyClass", "my_method"],
                kind=SymbolKind.Method,
                detail="method",
                hover="documentation",
            ),
        ],
    )
    rendered = resp.format()
    assert "MyClass" in rendered
    assert "class" in rendered
    assert "A test class" in rendered
    assert "my_method" in rendered


def test_rename_response_format():
    resp = RenameResponse(
        old_name="old",
        new_name="new",
        total_files=1,
        total_occurrences=1,
        changes=[
            RenameFileChange(
                file_path=Path("test.py"),
                occurrences=1,
                diffs=[RenameDiff(line=0, original="old", modified="new")],
            )
        ],
    )
    rendered = resp.format()
    assert "old" in rendered
    assert "new" in rendered
    assert "test.py" in rendered
    assert "preview" in rendered.lower()


def test_rename_response_compact_format():
    resp = RenameResponse(
        old_name="fetch_data",
        new_name="get_resource",
        total_files=2,
        total_occurrences=5,
        changes=[
            RenameFileChange(
                file_path=Path("src/client.py"),
                occurrences=2,
                diffs=[],
            ),
            RenameFileChange(
                file_path=Path("src/main.py"),
                occurrences=3,
                diffs=[],
            ),
        ],
    )
    rendered = resp.format()
    assert "fetch_data" in rendered
    assert "get_resource" in rendered
    assert "2" in rendered  # total files
    assert "5" in rendered  # total occurrences
    assert "editor" in rendered.lower() or "IDE" in rendered


def test_rename_response_with_diffs():
    resp = RenameResponse(
        old_name="temp",
        new_name="buffer",
        total_files=1,
        total_occurrences=3,
        changes=[
            RenameFileChange(
                file_path=Path("utils.py"),
                occurrences=3,
                diffs=[
                    RenameDiff(line=10, original="temp = []", modified="buffer = []"),
                    RenameDiff(
                        line=15, original="temp.append(x)", modified="buffer.append(x)"
                    ),
                    RenameDiff(
                        line=20, original="return temp", modified="return buffer"
                    ),
                ],
            )
        ],
    )
    rendered = resp.format()
    assert "temp" in rendered
    assert "buffer" in rendered
    assert "Line 10" in rendered
    assert "temp = []" in rendered
    assert "buffer = []" in rendered


def test_rename_response_truncated():
    resp = RenameResponse(
        old_name="User",
        new_name="Account",
        total_files=10,
        total_occurrences=50,
        has_more_files=True,
        changes=[
            RenameFileChange(file_path=Path(f"file{i}.py"), occurrences=i + 1, diffs=[])
            for i in range(3)
        ],
    )
    rendered = resp.format()
    assert "User" in rendered
    assert "Account" in rendered
    assert "10" in rendered  # total files
    assert "50" in rendered  # total occurrences
    assert "showing 3/10" in rendered.lower() or "3/10" in rendered
    assert "User" in rendered
    assert "Account" in rendered
    assert "10" in rendered  # total files
    assert "50" in rendered  # total occurrences
    assert "showing 3/10" in rendered.lower() or "3/10" in rendered


def test_decorated_content_response_format():
    resp = DecoratedContentResponse(
        file_path=Path("test.py"), decorated_content="x: int = 1 /* hint */"
    )
    rendered = resp.format()
    assert "test.py" in rendered
    assert "x: int = 1 /* hint */" in rendered


def test_call_hierarchy_response_format():
    node = HierarchyNode(
        id="1",
        name="root",
        kind="Function",
        file_path=Path("test.py"),
        range_start=Position(line=1, character=1),
    )
    item = HierarchyItem(
        name="caller", kind="Function", file_path=Path("test.py"), level=1
    )
    resp = HierarchyResponse(
        hierarchy_type="call",
        root=node,
        nodes={"1": node},
        edges_incoming={},
        edges_outgoing={},
        items_incoming=[item],
        items_outgoing=[],
        direction="incoming",
        depth=2,
    )
    rendered = resp.format()
    assert "root" in rendered
    assert "caller" in rendered


def test_type_hierarchy_response_format():
    node = HierarchyNode(
        id="1",
        name="Base",
        kind="Class",
        file_path=Path("test.py"),
        range_start=Position(line=1, character=1),
    )
    item = HierarchyItem(name="Sub", kind="Class", file_path=Path("test.py"), level=1)
    resp = HierarchyResponse(
        hierarchy_type="type",
        root=node,
        nodes={"1": node},
        edges_incoming={},
        edges_outgoing={},
        items_incoming=[],
        items_outgoing=[item],
        direction="outgoing",
        depth=2,
    )
    rendered = resp.format()
    assert "Base" in rendered
    assert "Sub" in rendered


def test_definition_response_format():
    from lsap_schema import DefinitionRequest
    from lsap_schema.locate import Locate, LineScope

    req = DefinitionRequest(
        mode="definition",
        locate=Locate(file_path=Path("test.py"), scope=LineScope(line=1), find="test"),
    )
    resp = DefinitionResponse(
        request=req,
        items=[
            SymbolCodeInfo(
                file_path=Path("test.py"),
                name="test",
                path=["test"],
                kind=SymbolKind.Function,
                code="test_content",
            )
        ],
    )
    rendered = resp.format()
    assert "Definition Result" in rendered
    assert "test_content" in rendered

    req.mode = "type_definition"
    rendered = resp.format()
    assert "Type definition Result" in rendered


def test_workspace_diagnostics_response_format():
    resp = WorkspaceDiagnosticsResponse(
        items=[
            WorkspaceDiagnosticItem(
                file_path=Path("test.py"),
                range=Range(
                    start=Position(line=1, character=1),
                    end=Position(line=1, character=5),
                ),
                severity="Error",
                message="workspace error",
            )
        ],
        start_index=0,
        has_more=False,
    )
    rendered = resp.format()
    assert "Workspace Diagnostics" in rendered
    assert "test.py" in rendered
    assert "Error" in rendered
    assert "workspace error" in rendered


def test_format_invalid_template():
    resp = CompletionResponse(items=[], start_index=0)
    with pytest.raises(ValueError):
        resp.format(template_name="invalid")


def test_symbol_kind_conversion():
    """Test SymbolKind.from_lsp() conversion"""
    from lsprotocol.types import SymbolKind as LSPSymbolKind

    # Test various symbol kinds
    test_cases = [
        LSPSymbolKind.File,
        LSPSymbolKind.Module,
        LSPSymbolKind.Class,
        LSPSymbolKind.Method,
        LSPSymbolKind.Function,
        LSPSymbolKind.Variable,
        LSPSymbolKind.Interface,
        LSPSymbolKind.Enum,
    ]

    for lsp_kind in test_cases:
        result = SymbolKind.from_lsp(lsp_kind)
        # Verify the name matches
        assert result.name == lsp_kind.name
        # Verify it's the correct type
        assert isinstance(result, SymbolKind)
