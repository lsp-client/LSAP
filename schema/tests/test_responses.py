import pytest
from pathlib import Path
from lsap_schema.completion import CompletionResponse, CompletionItem
from lsap_schema.locate import LocateResponse, Position, Range
from lsap_schema.symbol import SymbolResponse, ParameterInfo
from lsap_schema.workspace import WorkspaceSymbolResponse, WorkspaceSymbolItem
from lsap_schema.reference import ReferenceResponse
from lsap_schema.implementation import ImplementationResponse
from lsap_schema.diagnostics import FileDiagnosticsResponse, Diagnostic
from lsap_schema.symbol_outline import SymbolOutlineResponse, SymbolOutlineItem
from lsap_schema.rename import RenameResponse, RenameFileChange, RenameDiff
from lsap_schema.inlay_hint import DecoratedContentResponse
from lsap_schema.call_hierarchy import (
    CallHierarchyResponse,
    CallHierarchyNode,
    CallHierarchyItem,
)
from lsap_schema.type_hierarchy import (
    TypeHierarchyResponse,
    TypeHierarchyNode,
    TypeHierarchyItem,
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
        symbol_path=["MyClass", "my_method"],
        hover="Test Hover",
        parameters=[ParameterInfo(name="p1", label="p1: int", documentation="doc")],
        symbol_content="def my_method(): pass",
    )
    rendered = resp.format()
    assert "MyClass.my_method" in rendered
    assert "Test Hover" in rendered
    assert "p1: int" in rendered
    assert "def my_method()" in rendered


def test_workspace_symbol_response_format():
    resp = WorkspaceSymbolResponse(
        query="test",
        items=[
            WorkspaceSymbolItem(
                name="test_sym",
                kind="Class",
                file_path=Path("test.py"),
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=0),
                ),
            )
        ],
        start_index=0,
        has_more=False,
    )
    rendered = resp.format()
    assert "test_sym" in rendered
    assert "Class" in rendered
    assert "test.py" in rendered


def test_reference_response_format():
    symbol_resp = SymbolResponse(
        file_path=Path("test.py"), symbol_path=["test"], symbol_content="test_content"
    )
    resp = ReferenceResponse(items=[symbol_resp], start_index=0, has_more=False)
    rendered = resp.format()
    assert "test.py" in rendered
    assert "test_content" in rendered


def test_implementation_response_format():
    symbol_resp = SymbolResponse(
        file_path=Path("test.py"), symbol_path=["test"], symbol_content="test_content"
    )
    resp = ImplementationResponse(items=[symbol_resp], start_index=0, has_more=False)
    rendered = resp.format()
    assert "test.py" in rendered
    assert "test_content" in rendered


def test_diagnostics_response_format():
    resp = FileDiagnosticsResponse(
        file_path=Path("test.py"),
        diagnostics=[
            Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=5),
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
            SymbolOutlineItem(
                name="MyClass",
                kind="Class",
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=10, character=0),
                ),
                level=0,
                symbol_content="class MyClass: pass",
            ),
            SymbolOutlineItem(
                name="my_method",
                kind="Method",
                range=Range(
                    start=Position(line=1, character=4),
                    end=Position(line=2, character=4),
                ),
                level=1,
            ),
        ],
    )
    rendered = resp.format()
    assert "MyClass" in rendered
    assert "Class" in rendered
    assert "class MyClass" in rendered
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
        range_start=Position(line=0, character=0),
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
        range_start=Position(line=0, character=0),
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


def test_format_invalid_template():
    resp = CompletionResponse(items=[], start_index=0)
    with pytest.raises(ValueError):
        resp.format(template_name="invalid")
