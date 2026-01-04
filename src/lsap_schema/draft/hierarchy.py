from pathlib import Path
from typing import Annotated, Final, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from lsap_schema.abc import Response
from lsap_schema.locate import LocateRequest, Position


class HierarchyNode(BaseModel):
    """
    Represents a node in a hierarchy graph.

    Applicable to any hierarchical relationship: function calls, type inheritance, etc.
    """

    id: str
    name: str
    kind: str
    file_path: Path
    range_start: Position
    detail: str | None = None


class HierarchyItem(BaseModel):
    """
    Represents an item in a flattened hierarchy tree for rendering.

    Applicable to any hierarchical relationship.
    """

    name: str
    kind: str
    file_path: Path
    level: int
    detail: str | None = None
    is_cycle: bool = False


class CallEdgeMetadata(BaseModel):
    """Metadata specific to call relationships"""

    call_sites: list[Position]
    """Positions where the call occurs"""


class TypeEdgeMetadata(BaseModel):
    """Metadata specific to type inheritance relationships"""

    relationship: Literal["extends", "implements"]
    """Type of inheritance relationship"""


class HierarchyEdge(BaseModel):
    """
    Represents a directed edge in the hierarchy graph.

    The edge connects two nodes and may carry metadata specific to the relationship type.
    """

    from_node_id: str
    to_node_id: str
    metadata: (
        Annotated[
            Union[CallEdgeMetadata, TypeEdgeMetadata],
            Field(
                discriminator="relationship"
                if hasattr(TypeEdgeMetadata, "relationship")
                else None
            ),
        ]
        | None
    ) = None


class HierarchyRequest(LocateRequest):
    """
    Traces hierarchical relationships in a directed graph.

    The hierarchy type determines the semantic meaning of relationships:
    - "call": function/method call relationships
    - "type": class/interface inheritance relationships

    Direction is specified in graph terms:
    - "incoming": predecessors in the graph (callers for calls, supertypes for inheritance)
    - "outgoing": successors in the graph (callees for calls, subtypes for inheritance)
    - "both": explore both directions
    """

    hierarchy_type: Literal["call", "type"]
    """Type of hierarchical relationship to trace"""

    direction: Literal["incoming", "outgoing", "both"] = "both"
    """Graph traversal direction"""

    depth: int = 2
    """Maximum traversal depth"""

    include_external: bool = False
    """Whether to include external references (applicable to certain hierarchy types)"""


# Template that adapts based on hierarchy_type
markdown_template: Final = """
{% if hierarchy_type == "call" %}
# Call Hierarchy for `{{ root.name }}` (Depth: {{ depth }}, Direction: {{ direction }})

{% if direction == "incoming" or direction == "both" %}
## Incoming Calls (Who calls this?)

{% for item in items_incoming %}
{% for i in (1..item.level) %}#{% endfor %}## {{ item.name }}
- **Kind**: `{{ item.kind }}`
- **File**: `{{ item.file_path }}`
{%- if item.is_cycle %}
- **Recursive cycle detected**
{%- endif %}

{% endfor %}
{% endif %}

{% if direction == "outgoing" or direction == "both" %}
## Outgoing Calls (What does this call?)

{% for item in items_outgoing %}
{% for i in (1..item.level) %}#{% endfor %}## {{ item.name }}
- **Kind**: `{{ item.kind }}`
- **File**: `{{ item.file_path }}`
{%- if item.is_cycle %}
- **Recursive cycle detected**
{%- endif %}

{% endfor %}
{% endif %}
{% else %}
# Type Hierarchy for `{{ root.name }}` (Depth: {{ depth }}, Direction: {{ direction }})

{% if direction == "incoming" or direction == "both" %}
## Supertypes (Parents/Base Classes)

{% for item in items_incoming %}
{% for i in (1..item.level) %}#{% endfor %}## {{ item.name }}
- Kind: `{{ item.kind }}`
- File: `{{ item.file_path }}`
{%- if item.detail != nil %}
- Detail: {{ item.detail }}
{%- endif %}
{%- if item.is_cycle %}
- Recursive cycle detected
{%- endif %}

{% endfor %}
{% endif %}

{% if direction == "outgoing" or direction == "both" %}
## Subtypes (Children/Implementations)

{% for item in items_outgoing %}
{% for i in (1..item.level) %}#{% endfor %}## {{ item.name }}
- Kind: `{{ item.kind }}`
- File: `{{ item.file_path }}`
{%- if item.detail != nil %}
- Detail: {{ item.detail }}
{%- endif %}
{%- if item.is_cycle %}
- Recursive cycle detected
{%- endif %}

{% endfor %}
{% endif %}
{% endif %}

---
> [!NOTE]
> Tree is truncated at depth {{ depth }}.
"""


class HierarchyResponse(Response):
    """
    Response containing the hierarchy graph and flattened tree.

    The response uses generic graph terminology:
    - edges_incoming: edges pointing to nodes (callers or supertypes)
    - edges_outgoing: edges pointing from nodes (callees or subtypes)
    - items_incoming: flattened list of incoming relationships
    - items_outgoing: flattened list of outgoing relationships
    """

    hierarchy_type: Literal["call", "type"]
    """Type of hierarchical relationship"""

    root: HierarchyNode
    """The starting node"""

    nodes: dict[str, HierarchyNode]
    """All nodes in the hierarchy graph"""

    edges_incoming: dict[str, list[HierarchyEdge]]
    """Incoming edges for each node (predecessors in the graph)"""

    edges_outgoing: dict[str, list[HierarchyEdge]]
    """Outgoing edges for each node (successors in the graph)"""

    items_incoming: list[HierarchyItem] = []
    """Flattened list of incoming relationships for tree rendering"""

    items_outgoing: list[HierarchyItem] = []
    """Flattened list of outgoing relationships for tree rendering"""

    direction: str
    depth: int

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


__all__ = [
    "HierarchyNode",
    "HierarchyItem",
    "HierarchyEdge",
    "CallEdgeMetadata",
    "TypeEdgeMetadata",
    "HierarchyRequest",
    "HierarchyResponse",
]
