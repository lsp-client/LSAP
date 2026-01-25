from pathlib import Path

import pytest
from pydantic import ValidationError

from lsap.schema.draft.explore import ExploreRequest, ExploreResponse, HierarchyInfo
from lsap.schema.locate import Locate
from lsap.schema.models import (
    CallHierarchy,
    CallHierarchyItem,
    Position,
    Range,
    SymbolInfo,
    SymbolKind,
)


def test_explore_request_defaults():
    """Test ExploreRequest default values."""
    req = ExploreRequest(locate=Locate(file_path=Path("test.py"), find="MyClass"))
    assert req.include == ["siblings", "dependencies"]
    assert req.max_items == 10
    assert req.resolve_info is False
    assert req.include_external is False


def test_explore_request_validation():
    """Test ExploreRequest field validation."""
    # Test max_items range (1-50)
    with pytest.raises(ValidationError):
        ExploreRequest(
            locate=Locate(file_path=Path("test.py"), find="MyClass"), max_items=0
        )
    with pytest.raises(ValidationError):
        ExploreRequest(
            locate=Locate(file_path=Path("test.py"), find="MyClass"), max_items=51
        )


def test_hierarchy_info_model():
    """Test HierarchyInfo model with parents and children."""
    parent = SymbolInfo(
        name="Base",
        kind=SymbolKind.Class,
        file_path=Path("base.py"),
        range=Range(
            start=Position(line=1, character=1), end=Position(line=10, character=1)
        ),
        path=["Base"],
    )
    child = SymbolInfo(
        name="Sub",
        kind=SymbolKind.Class,
        file_path=Path("sub.py"),
        range=Range(
            start=Position(line=1, character=1), end=Position(line=10, character=1)
        ),
        path=["Sub"],
    )
    info = HierarchyInfo(parents=[parent], children=[child])
    assert len(info.parents) == 1
    assert len(info.children) == 1
    assert info.parents[0].name == "Base"
    assert info.children[0].name == "Sub"


def test_explore_response_serialization():
    """Test ExploreResponse serialization and deserialization."""
    target = SymbolInfo(
        name="MyClass",
        kind=SymbolKind.Class,
        file_path=Path("test.py"),
        range=Range(
            start=Position(line=5, character=1), end=Position(line=15, character=1)
        ),
        path=["MyClass"],
    )

    sibling = SymbolInfo(
        name="OtherClass",
        kind=SymbolKind.Class,
        file_path=Path("test.py"),
        range=Range(
            start=Position(line=20, character=1), end=Position(line=30, character=1)
        ),
        path=["OtherClass"],
    )

    resp = ExploreResponse(
        target=target,
        siblings=[sibling],
        dependencies=[],
        dependents=[],
        hierarchy=None,
        calls=None,
    )

    # Serialize to dict
    data = resp.model_dump()
    assert data["target"]["name"] == "MyClass"
    assert len(data["siblings"]) == 1
    assert data["siblings"][0]["name"] == "OtherClass"

    # Deserialize back
    resp2 = ExploreResponse.model_validate(data)
    assert resp2.target.name == "MyClass"
    assert len(resp2.siblings) == 1
    assert resp2.siblings[0].name == "OtherClass"


def test_explore_response_markdown_rendering():
    """Test ExploreResponse.format('markdown') renders correctly."""
    target = SymbolInfo(
        name="MyClass",
        kind=SymbolKind.Class,
        file_path=Path("test.py"),
        range=Range(
            start=Position(line=5, character=1), end=Position(line=15, character=1)
        ),
        path=["MyClass"],
    )

    sibling = SymbolInfo(
        name="OtherClass",
        kind=SymbolKind.Class,
        file_path=Path("test.py"),
        range=Range(
            start=Position(line=20, character=1), end=Position(line=30, character=1)
        ),
        path=["OtherClass"],
    )

    dependency = SymbolInfo(
        name="Helper",
        kind=SymbolKind.Class,
        file_path=Path("utils.py"),
        range=Range(
            start=Position(line=1, character=1), end=Position(line=5, character=1)
        ),
        path=["Helper"],
    )

    dependent = SymbolInfo(
        name="Main",
        kind=SymbolKind.Class,
        file_path=Path("main.py"),
        range=Range(
            start=Position(line=10, character=1), end=Position(line=20, character=1)
        ),
        path=["Main"],
    )

    hierarchy = HierarchyInfo(
        parents=[
            SymbolInfo(
                name="BaseClass",
                kind=SymbolKind.Class,
                file_path=Path("base.py"),
                range=Range(
                    start=Position(line=1, character=1),
                    end=Position(line=10, character=1),
                ),
                path=["BaseClass"],
            )
        ],
        children=[
            SymbolInfo(
                name="SubClass",
                kind=SymbolKind.Class,
                file_path=Path("sub.py"),
                range=Range(
                    start=Position(line=1, character=1),
                    end=Position(line=10, character=1),
                ),
                path=["SubClass"],
            )
        ],
    )

    calls = CallHierarchy(
        incoming=[
            CallHierarchyItem(
                name="caller_func",
                kind=SymbolKind.Function,
                file_path=Path("caller.py"),
                range=Range(
                    start=Position(line=5, character=1),
                    end=Position(line=5, character=10),
                ),
            )
        ],
        outgoing=[
            CallHierarchyItem(
                name="callee_func",
                kind=SymbolKind.Function,
                file_path=Path("callee.py"),
                range=Range(
                    start=Position(line=10, character=1),
                    end=Position(line=10, character=10),
                ),
            )
        ],
    )

    resp = ExploreResponse(
        target=target,
        siblings=[sibling],
        dependencies=[dependency],
        dependents=[dependent],
        hierarchy=hierarchy,
        calls=calls,
    )

    markdown = resp.format("markdown")

    assert "# Explore: `MyClass` (`class`)" in markdown
    assert "## Siblings" in markdown
    assert "- `OtherClass` (`class`) at line 21" in markdown
    assert "## Dependencies" in markdown
    assert "- `Helper` (`class`) in `utils.py`" in markdown
    assert "## Dependents" in markdown
    assert "- `Main` (`class`) in `main.py`" in markdown
    assert "## Hierarchy" in markdown
    assert "### Parents" in markdown
    assert "- `BaseClass` (`class`) in `base.py`" in markdown
    assert "### Children" in markdown
    assert "- `SubClass` (`class`) in `sub.py`" in markdown
    assert "## Call Hierarchy" in markdown
    assert "### Incoming Calls" in markdown
    assert "- `caller_func` (`function`) at `caller.py:6`" in markdown
    assert "### Outgoing Calls" in markdown
    assert "- `callee_func` (`function`) at `callee.py:11`" in markdown
    assert "Use this map to understand" in markdown
