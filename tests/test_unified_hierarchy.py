from pathlib import Path

from lsap.schema.draft.hierarchy import (
    CallEdgeMetadata,
    HierarchyEdge,
    HierarchyItem,
    HierarchyNode,
    HierarchyRequest,
    HierarchyResponse,
    Position,
    TypeEdgeMetadata,
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
        metadata=CallEdgeMetadata(call_sites=[Position(line=5, character=10)]),
    )
    resp = HierarchyResponse(
        hierarchy_type="call",
        root=node,
        nodes={"1": node},
        edges_incoming={"1": [edge]},
        edges_outgoing={},
        items_incoming=[item],
        items_outgoing=[],
        direction="incoming",
        depth=2,
    )
    rendered = resp.format()
    assert "root_function" in rendered
    assert "caller_function" in rendered
    assert "Incoming" in rendered
    assert "call" in rendered  # hierarchy_type is shown


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
        metadata=TypeEdgeMetadata(relationship="extends"),
    )
    resp = HierarchyResponse(
        hierarchy_type="type",
        root=node,
        nodes={"1": node},
        edges_incoming={"1": [edge]},
        edges_outgoing={},
        items_incoming=[item],
        items_outgoing=[],
        direction="incoming",
        depth=2,
    )
    rendered = resp.format()
    assert "BaseClass" in rendered
    assert "DerivedClass" in rendered
    assert "Incoming" in rendered
    assert "type" in rendered  # hierarchy_type is shown


def test_unified_hierarchy_request_call():
    """Test unified hierarchy request for call hierarchy"""
    from lsap.schema.locate import LineScope, Locate

    req = HierarchyRequest(
        hierarchy_type="call",
        locate=Locate(
            file_path=Path("test.py"),
            scope=LineScope(start_line=10, end_line=11),
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
    from lsap.schema.locate import LineScope, Locate

    req = HierarchyRequest(
        hierarchy_type="type",
        locate=Locate(
            file_path=Path("test.py"),
            scope=LineScope(start_line=5, end_line=6),
            find="MyClass",
        ),
        direction="outgoing",
        depth=2,
    )
    assert req.hierarchy_type == "type"
    assert req.direction == "outgoing"
    assert req.depth == 2
    assert req.include_external is False  # default


def test_hierarchy_edge_call_metadata():
    """Test hierarchy edge with call metadata (for call hierarchy)"""
    edge = HierarchyEdge(
        from_node_id="1",
        to_node_id="2",
        metadata=CallEdgeMetadata(
            call_sites=[
                Position(line=10, character=5),
                Position(line=15, character=8),
            ]
        ),
    )
    assert edge.metadata is not None
    assert isinstance(edge.metadata, CallEdgeMetadata)
    assert len(edge.metadata.call_sites) == 2


def test_hierarchy_edge_type_metadata():
    """Test hierarchy edge with type metadata (for type hierarchy)"""
    edge = HierarchyEdge(
        from_node_id="1",
        to_node_id="2",
        metadata=TypeEdgeMetadata(relationship="implements"),
    )
    assert edge.metadata is not None
    assert isinstance(edge.metadata, TypeEdgeMetadata)
    assert edge.metadata.relationship == "implements"


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
