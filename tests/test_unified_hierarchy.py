from pathlib import Path

import pytest

from lsap_schema import (
    HierarchyEdge,
    HierarchyItem,
    HierarchyNode,
    HierarchyRequest,
    HierarchyResponse,
    Position,
)


def test_unified_hierarchy_call_type():
    """Test unified hierarchy API with call hierarchy type"""
    node = HierarchyNode(
        id="1",
        name="root_function",
        kind="Function",
        file_path=Path("test.py"),
        range_start=Position(line=1, character=1),
    )
    item = HierarchyItem(
        name="caller_function",
        kind="Function",
        file_path=Path("test.py"),
        level=1,
    )
    edge = HierarchyEdge(
        from_node_id="2",
        to_node_id="1",
        call_sites=[Position(line=5, character=10)],
    )
    resp = HierarchyResponse(
        hierarchy_type="call",
        root=node,
        nodes={"1": node},
        edges_in={"1": [edge]},
        edges_out={},
        items_in=[item],
        items_out=[],
        direction="incoming",
        depth=2,
    )
    rendered = resp.format()
    assert "Call Hierarchy" in rendered
    assert "root_function" in rendered
    assert "caller_function" in rendered
    assert "Incoming Calls" in rendered


def test_unified_hierarchy_type_type():
    """Test unified hierarchy API with type hierarchy type"""
    node = HierarchyNode(
        id="1",
        name="BaseClass",
        kind="Class",
        file_path=Path("test.py"),
        range_start=Position(line=1, character=1),
        detail="base class",
    )
    item = HierarchyItem(
        name="DerivedClass",
        kind="Class",
        file_path=Path("test.py"),
        level=1,
        detail="inherits from BaseClass",
    )
    edge = HierarchyEdge(
        from_node_id="2",
        to_node_id="1",
        relationship="extends",
    )
    resp = HierarchyResponse(
        hierarchy_type="type",
        root=node,
        nodes={"1": node},
        edges_in={"1": [edge]},
        edges_out={},
        items_in=[item],
        items_out=[],
        direction="supertypes",
        depth=2,
    )
    rendered = resp.format()
    assert "Type Hierarchy" in rendered
    assert "BaseClass" in rendered
    assert "DerivedClass" in rendered
    assert "Supertypes" in rendered


def test_unified_hierarchy_request_call():
    """Test unified hierarchy request for call hierarchy"""
    from lsap_schema.locate import Locate, LineScope

    req = HierarchyRequest(
        hierarchy_type="call",
        locate=Locate(
            file_path=Path("test.py"),
            scope=LineScope(line=10),
            find="my_function",
        ),
        direction="both",
        depth=3,
        include_external=True,
    )
    assert req.hierarchy_type == "call"
    assert req.direction == "both"
    assert req.depth == 3
    assert req.include_external is True


def test_unified_hierarchy_request_type():
    """Test unified hierarchy request for type hierarchy"""
    from lsap_schema.locate import Locate, LineScope

    req = HierarchyRequest(
        hierarchy_type="type",
        locate=Locate(
            file_path=Path("test.py"),
            scope=LineScope(line=5),
            find="MyClass",
        ),
        direction="subtypes",
        depth=2,
    )
    assert req.hierarchy_type == "type"
    assert req.direction == "subtypes"
    assert req.depth == 2
    assert req.include_external is False  # default


def test_hierarchy_edge_call_sites():
    """Test hierarchy edge with call sites (for call hierarchy)"""
    edge = HierarchyEdge(
        from_node_id="1",
        to_node_id="2",
        call_sites=[
            Position(line=10, character=5),
            Position(line=15, character=8),
        ],
    )
    assert edge.call_sites is not None
    assert len(edge.call_sites) == 2
    assert edge.relationship is None


def test_hierarchy_edge_relationship():
    """Test hierarchy edge with relationship (for type hierarchy)"""
    edge = HierarchyEdge(
        from_node_id="1",
        to_node_id="2",
        relationship="implements",
    )
    assert edge.relationship == "implements"
    assert edge.call_sites is None


def test_hierarchy_node_with_detail():
    """Test hierarchy node with optional detail field"""
    node = HierarchyNode(
        id="1",
        name="MyClass",
        kind="Class",
        file_path=Path("test.py"),
        range_start=Position(line=1, character=1),
        detail="extends BaseClass",
    )
    assert node.detail == "extends BaseClass"


def test_hierarchy_node_without_detail():
    """Test hierarchy node without optional detail field"""
    node = HierarchyNode(
        id="1",
        name="my_function",
        kind="Function",
        file_path=Path("test.py"),
        range_start=Position(line=1, character=1),
    )
    assert node.detail is None
