from pathlib import Path

import pytest

from lsap_schema import (
    CallHierarchyItem,
    CallHierarchyNode,
    CallHierarchyResponse,
    CompletionItem,
    CompletionResponse,
    DefinitionResponse,
    Diagnostic,
    FileDiagnosticsResponse,
    DecoratedContentResponse,
    LocateResponse,
    Position,
    Range,
    ReferenceResponse,
    RenameDiff,
    RenameFileChange,
    RenameResponse,
    SymbolResponse,
    SymbolOutlineResponse,
    SymbolInfo,
    SymbolKind,
    TypeHierarchyItem,
    TypeHierarchyNode,
    TypeHierarchyResponse,
    WorkspaceSymbolItem,
    WorkspaceSymbolResponse,
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
        hover="Test Hover",
        code="def my_method(): pass",
    )
    rendered = resp.format()
    assert "MyClass.my_method" in rendered
    assert "Test Hover" in rendered
    assert "def my_method()" in rendered


def test_workspace_symbol_response_format():
    from lsap_schema.workspace_symbol import WorkspaceSymbolRequest

    req = WorkspaceSymbolRequest(query="test")
    resp = WorkspaceSymbolResponse(
        request=req,
        items=[
            WorkspaceSymbolItem(
                file_path=Path("test.py"),
                name="class MyClass",
                path=["MyClass"],
                kind=SymbolKind.Class,
                code="class MyClass: pass",
                hover="A test class",
            ),
            WorkspaceSymbolItem(
                file_path=Path("test.py"),
                name="my_method",
                path=["MyClass", "my_method"],
                kind=SymbolKind.Method,
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
    from lsap_schema.locate import LocateText

    item = ReferenceItem(
        file_path=Path("test.py"),
        line=10,
        code="test_content",
        symbol=SymbolInfo(
            file_path=Path("test.py"),
            name="test",
            path=["test"],
            kind=SymbolKind.Function,
        ),
    )
    req = ReferenceRequest(
        mode="references",
        locate=LocateText(
            file_path=Path("test.py"),
            line=10,
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
    from lsap_schema.locate import LocateText

    item = ReferenceItem(
        file_path=Path("test.py"),
        line=10,
        code="test_content",
        symbol=SymbolInfo(
            file_path=Path("test.py"),
            name="test",
            path=["test"],
            kind=SymbolKind.Function,
        ),
    )
    req = ReferenceRequest(
        mode="implementations",
        locate=LocateText(
            file_path=Path("test.py"),
            line=10,
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


def test_symbol_outline_response_format():
    resp = SymbolOutlineResponse(
        file_path=Path("test.py"),
        items=[
            SymbolInfo(
                file_path=Path("test.py"),
                name="class MyClass",
                path=["MyClass"],
                kind=SymbolKind.Class,
                code="class MyClass: pass",
                hover="A test class",
            ),
            SymbolInfo(
                file_path=Path("test.py"),
                name="my_method(arg1: int) -> None",
                path=["MyClass", "my_method"],
                kind=SymbolKind.Method,
            ),
        ],
    )
    rendered = resp.format()
    assert "class MyClass" in rendered
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
                diffs=[RenameDiff(line=0, original="old", modified="new")],
            )
        ],
    )
    rendered = resp.format()
    assert "old" in rendered
    assert "new" in rendered
    assert "test.py" in rendered


def test_decorated_content_response_format():
    resp = DecoratedContentResponse(
        file_path=Path("test.py"), decorated_content="x: int = 1 /* hint */"
    )
    rendered = resp.format()
    assert "test.py" in rendered
    assert "x: int = 1 /* hint */" in rendered


def test_call_hierarchy_response_format():
    node = CallHierarchyNode(
        id="1",
        name="root",
        kind="Function",
        file_path=Path("test.py"),
        range_start=Position(line=1, character=1),
    )
    item = CallHierarchyItem(
        name="caller", kind="Function", file_path=Path("test.py"), level=1
    )
    resp = CallHierarchyResponse(
        root=node,
        nodes={"1": node},
        edges_in={},
        edges_out={},
        calls_in=[item],
        calls_out=[],
        direction="both",
        depth=2,
    )
    rendered = resp.format()
    assert "root" in rendered
    assert "caller" in rendered


def test_type_hierarchy_response_format():
    node = TypeHierarchyNode(
        id="1",
        name="Base",
        kind="Class",
        file_path=Path("test.py"),
        range_start=Position(line=1, character=1),
    )
    item = TypeHierarchyItem(
        name="Sub", kind="Class", file_path=Path("test.py"), level=1
    )
    resp = TypeHierarchyResponse(
        root=node,
        nodes={"1": node},
        edges_up={},
        edges_down={},
        types_up=[],
        types_down=[item],
        direction="both",
        depth=2,
    )
    rendered = resp.format()
    assert "Base" in rendered
    assert "Sub" in rendered


def test_definition_response_format():
    from lsap_schema import DefinitionRequest, LocateText

    req = DefinitionRequest(
        mode="definition",
        locate=LocateText(file_path=Path("test.py"), line=1, find="test"),
    )
    resp = DefinitionResponse(
        request=req,
        items=[
            SymbolInfo(
                file_path=Path("test.py"),
                name="test",
                path=["test"],
                kind=SymbolKind.Function,
                code="test_content",
                hover="test_hover",
            )
        ],
    )
    rendered = resp.format()
    assert "Definition Result" in rendered
    assert "test_hover" in rendered
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
