from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from lsap_schema.abc import Response
from lsap_schema.locate import LocateRequest, Position


class TypeHierarchyNode(BaseModel):
    id: str
    name: str
    kind: str
    file_path: Path
    range_start: Position
    detail: str | None = None


class TypeHierarchyItem(BaseModel):
    name: str
    kind: str
    file_path: Path
    level: int
    detail: str | None = None
    is_cycle: bool = False


class TypeEdge(BaseModel):
    from_node_id: str
    to_node_id: str
    relationship: Literal["extends", "implements"]


class TypeHierarchyRequest(LocateRequest):
    """
    Traces supertypes or subtypes of a class or interface.

    Use this to explore class inheritance, finding base classes (supertypes)
    or derived classes (subtypes).
    """

    direction: Literal["supertypes", "subtypes", "both"] = "both"
    """Whether to trace supertypes, subtypes, or both (default: both)"""

    depth: int = 2
    """How many levels to trace (default: 2)"""


markdown_template: Final = """
# Type Hierarchy for `{{ root.name }}` (Depth: {{ depth }}, Direction: {{ direction }})

{% if direction == "supertypes" or direction == "both" %}
## Supertypes (Parents/Base Classes)

{% for item in types_up %}
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

{% for item in types_down %}
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

---
> [!NOTE]
> Tree is truncated at depth {{ depth }}. Increase `depth` parameter to explore further if needed.
"""


class TypeHierarchyResponse(Response):
    root: TypeHierarchyNode
    nodes: dict[str, TypeHierarchyNode]
    """Map of node ID to node details"""

    edges_up: dict[str, list[TypeEdge]]
    """Map of node ID to its supertypes (parent edges)"""

    edges_down: dict[str, list[TypeEdge]]
    """Map of node ID to its subtypes (child edges)"""

    types_up: list[TypeHierarchyItem] = []
    """Flat list of supertypes for tree rendering"""

    types_down: list[TypeHierarchyItem] = []
    """Flat list of subtypes for tree rendering"""

    direction: str
    depth: int

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
