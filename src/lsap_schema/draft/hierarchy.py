from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from lsap_schema.abc import Response
from lsap_schema.locate import LocateRequest, Position


class HierarchyNode(BaseModel):
    """Unified node for both call and type hierarchies"""

    id: str
    name: str
    kind: str
    file_path: Path
    range_start: Position
    detail: str | None = None
    """Optional detail (used for type hierarchy)"""


class HierarchyItem(BaseModel):
    """Unified item for both call and type hierarchies"""

    name: str
    kind: str
    file_path: Path
    level: int
    detail: str | None = None
    """Optional detail (used for type hierarchy)"""
    is_cycle: bool = False


class HierarchyEdge(BaseModel):
    """Unified edge for both call and type hierarchies"""

    from_node_id: str
    to_node_id: str
    call_sites: list[Position] | None = None
    """Exact positions where the call occurs (for call hierarchy)"""
    relationship: Literal["extends", "implements"] | None = None
    """Type of relationship (for type hierarchy)"""


class HierarchyRequest(LocateRequest):
    """
    Unified API for tracing hierarchies - both call relationships and type inheritance.

    For call hierarchy: traces incoming or outgoing calls for a symbol.
    For type hierarchy: traces supertypes or subtypes of a class or interface.
    """

    hierarchy_type: Literal["call", "type"]
    """Type of hierarchy to trace: 'call' for function calls, 'type' for class inheritance"""

    direction: Literal["incoming", "outgoing", "supertypes", "subtypes", "both"] = (
        "both"
    )
    """
    Direction of the trace:
    - For call hierarchy: 'incoming' (callers), 'outgoing' (callees), or 'both'
    - For type hierarchy: 'supertypes' (parents), 'subtypes' (children), or 'both'
    """

    depth: int = 2
    """How many hops/levels to trace (default: 2)"""

    include_external: bool = False
    """Whether to include calls to/from external libraries (only for call hierarchy)"""


markdown_template: Final = """
{% if hierarchy_type == "call" %}
# Call Hierarchy for `{{ root.name }}` (Depth: {{ depth }}, Direction: {{ direction }})

{% if direction == "incoming" or direction == "both" %}
## Incoming Calls (Who calls this?)

{% for item in items_in %}
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

{% for item in items_out %}
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

{% if direction == "supertypes" or direction == "both" %}
## Supertypes (Parents/Base Classes)

{% for item in items_in %}
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

{% if direction == "subtypes" or direction == "both" %}
## Subtypes (Children/Implementations)

{% for item in items_out %}
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
> Tree is truncated at depth {{ depth }}. {% if hierarchy_type == "call" %}Use `depth` parameter to explore further.{% else %}Increase `depth` parameter to explore further if needed.{% endif %}
"""


class HierarchyResponse(Response):
    """Unified response for both call and type hierarchies"""

    hierarchy_type: Literal["call", "type"]
    """Type of hierarchy: 'call' or 'type'"""

    root: HierarchyNode

    nodes: dict[str, HierarchyNode]
    """Map of node ID to node details"""

    edges_in: dict[str, list[HierarchyEdge]]
    """
    Map of node ID to its incoming edges:
    - For call hierarchy: incoming calls (callers)
    - For type hierarchy: edges to supertypes (parent edges)
    """

    edges_out: dict[str, list[HierarchyEdge]]
    """
    Map of node ID to its outgoing edges:
    - For call hierarchy: outgoing calls (callees)
    - For type hierarchy: edges to subtypes (child edges)
    """

    items_in: list[HierarchyItem] = []
    """
    Flat list for tree rendering:
    - For call hierarchy: incoming calls
    - For type hierarchy: supertypes
    """

    items_out: list[HierarchyItem] = []
    """
    Flat list for tree rendering:
    - For call hierarchy: outgoing calls
    - For type hierarchy: subtypes
    """

    direction: str
    depth: int

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
