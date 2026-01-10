from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from lsap.schema.abc import Response
from lsap.schema.locate import LocateRequest
from lsap.schema.models import Position


class HierarchyNode(BaseModel):
    """Represents a symbol node in a hierarchy graph."""

    id: str
    name: str
    kind: str
    file_path: Path
    range_start: Position
    detail: str | None = None


class HierarchyItem(BaseModel):
    """A node in the flattened hierarchy tree with its path from root."""

    name: str
    kind: str
    file_path: Path
    level: int
    """Depth level (1 = direct caller/callee of root)"""
    chain: list[str]
    """Full path from this node to root, e.g. ["caller", "root"]"""
    detail: str | None = None
    is_cycle: bool = False


# =============================================================================
# Call Hierarchy
# =============================================================================


class CallSite(BaseModel):
    """A specific location where a call occurs."""

    position: Position
    snippet: str | None = None


class CallHierarchyEdge(BaseModel):
    """An edge in the call hierarchy graph."""

    from_node_id: str
    to_node_id: str
    call_sites: list[CallSite] = Field(default_factory=list)


class CallHierarchyRequest(LocateRequest):
    """
    Traces function/method call relationships.

    Direction:
    - "incoming": Find callers (who calls this?)
    - "outgoing": Find callees (what does this call?)
    - "both": Both directions
    """

    direction: Literal["incoming", "outgoing", "both"] = "both"
    depth: int = 2
    include_external: bool = False


call_hierarchy_template: Final = """\
# Call Hierarchy: `{{ root.name }}`

Root: `{{ root.name }}` (`{{ root.kind }}`) at `{{ root.file_path }}`
{%- if root.detail %}
Detail: {{ root.detail }}
{%- endif %}

{% if direction == "incoming" or direction == "both" -%}
## Callers (incoming)

{% if items_incoming.size == 0 -%}
No callers found.
{% else -%}
{% for item in items_incoming -%}
{% for i in (1..item.level) %}#{% endfor %}## `{{ item.name }}`
{{ item.chain | join: " -> " }}
- Kind: `{{ item.kind }}`
- File: `{{ item.file_path }}`
{%- if item.detail %}
- Detail: {{ item.detail }}
{%- endif %}
{%- if item.is_cycle %}
- (cycle detected)
{%- endif %}

{% endfor -%}
{% endif %}
{% endif -%}

{% if direction == "outgoing" or direction == "both" -%}
## Callees (outgoing)

{% if items_outgoing.size == 0 -%}
No callees found.
{% else -%}
{% for item in items_outgoing -%}
{% for i in (1..item.level) %}#{% endfor %}## `{{ item.name }}`
{{ item.chain | join: " -> " }}
- Kind: `{{ item.kind }}`
- File: `{{ item.file_path }}`
{%- if item.detail %}
- Detail: {{ item.detail }}
{%- endif %}
{%- if item.is_cycle %}
- (cycle detected)
{%- endif %}

{% endfor -%}
{% endif %}
{% endif -%}
"""


class CallHierarchyResponse(Response):
    """Response containing the call hierarchy."""

    root: HierarchyNode
    nodes: dict[str, HierarchyNode]
    edges_incoming: dict[str, list[CallHierarchyEdge]]
    edges_outgoing: dict[str, list[CallHierarchyEdge]]
    items_incoming: list[HierarchyItem] = Field(default_factory=list)
    items_outgoing: list[HierarchyItem] = Field(default_factory=list)
    direction: Literal["incoming", "outgoing", "both"]
    depth: int

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": call_hierarchy_template,
        }
    )


# =============================================================================
# Type Hierarchy
# =============================================================================


class TypeRelation(BaseModel):
    """Describes the inheritance relationship type."""

    kind: Literal["extends", "implements"]


class TypeHierarchyEdge(BaseModel):
    """An edge in the type hierarchy graph."""

    from_node_id: str
    to_node_id: str
    relation: TypeRelation


class TypeHierarchyRequest(LocateRequest):
    """
    Traces class/interface inheritance relationships.

    Direction:
    - "supertypes": Find parent classes (what does this inherit?)
    - "subtypes": Find child classes (what inherits from this?)
    - "both": Both directions
    """

    direction: Literal["supertypes", "subtypes", "both"] = "both"
    depth: int = 2


type_hierarchy_template: Final = """\
# Type Hierarchy: `{{ root.name }}`

Root: `{{ root.name }}` (`{{ root.kind }}`) at `{{ root.file_path }}`
{%- if root.detail %}
Detail: {{ root.detail }}
{%- endif %}

{% if direction == "supertypes" or direction == "both" -%}
## Supertypes (parents)

{% if items_supertypes.size == 0 -%}
No supertypes found.
{% else -%}
{% for item in items_supertypes -%}
{% for i in (1..item.level) %}#{% endfor %}## `{{ item.name }}`
{{ item.chain | join: " <- " }}
- Kind: `{{ item.kind }}`
- File: `{{ item.file_path }}`
{%- if item.detail %}
- Detail: {{ item.detail }}
{%- endif %}
{%- if item.is_cycle %}
- (cycle detected)
{%- endif %}

{% endfor -%}
{% endif %}
{% endif -%}

{% if direction == "subtypes" or direction == "both" -%}
## Subtypes (children)

{% if items_subtypes.size == 0 -%}
No subtypes found.
{% else -%}
{% for item in items_subtypes -%}
{% for i in (1..item.level) %}#{% endfor %}## `{{ item.name }}`
{{ item.chain | join: " -> " }}
- Kind: `{{ item.kind }}`
- File: `{{ item.file_path }}`
{%- if item.detail %}
- Detail: {{ item.detail }}
{%- endif %}
{%- if item.is_cycle %}
- (cycle detected)
{%- endif %}

{% endfor -%}
{% endif %}
{% endif -%}
"""


class TypeHierarchyResponse(Response):
    """Response containing the type hierarchy."""

    root: HierarchyNode
    nodes: dict[str, HierarchyNode]
    edges_supertypes: dict[str, list[TypeHierarchyEdge]]
    edges_subtypes: dict[str, list[TypeHierarchyEdge]]
    items_supertypes: list[HierarchyItem] = Field(default_factory=list)
    items_subtypes: list[HierarchyItem] = Field(default_factory=list)
    direction: Literal["supertypes", "subtypes", "both"]
    depth: int

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": type_hierarchy_template,
        }
    )


__all__ = [
    "CallHierarchyEdge",
    "CallHierarchyRequest",
    "CallHierarchyResponse",
    "CallSite",
    "HierarchyItem",
    "HierarchyNode",
    "TypeHierarchyEdge",
    "TypeHierarchyRequest",
    "TypeHierarchyResponse",
    "TypeRelation",
]
