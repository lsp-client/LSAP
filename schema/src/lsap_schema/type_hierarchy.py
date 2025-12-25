from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from .locate import LocateRequest, Position


class TypeHierarchyNode(BaseModel):
    id: str
    name: str
    kind: str
    file_path: Path
    range_start: Position
    detail: str | None = None


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
    """Whether to trace parents (supertypes) or children (subtypes)"""

    depth: int = 2
    """How many levels to trace (default: 2)"""


markdown_template: Final = """
### Type Hierarchy for `{{ root.name }}` (Depth: {{ depth }}, Direction: {{ direction }})

{%- macro render_tree(node_id, current_depth, visited, dir_label) %}
  {%- if current_depth <= depth %}
    {%- set node = nodes[node_id] %}
    {%- set edges_to_show = edges_down[node_id] if dir_label == "Subtypes" else edges_up[node_id] %}
{{ "  " * current_depth }}- {{ node.name }} (`{{ node.kind }}`) {% if node.detail %}[{{ node.detail }}]{% endif %} in `{{ node.file_path }}`
    {%- if node_id in visited %} (recursive cycle)
    {%- else %}
      {%- do visited.append(node_id) %}
      {%- for edge in edges_to_show %}
        {%- set target_id = edge.to_node_id if dir_label == "Subtypes" else edge.from_node_id %}
{{ render_tree(target_id, current_depth + 1, visited, dir_label) }}
      {%- endfor %}
    {%- endif %}
  {%- endif %}
{%- endmacro %}

{% if direction in ["supertypes", "both"] %}
#### Supertypes (Parents/Base Classes)
{{ render_tree(root.id, 0, [], "Supertypes") }}
{% endif %}

{% if direction in ["subtypes", "both"] %}
#### Subtypes (Children/Implementations)
{{ render_tree(root.id, 0, [], "Subtypes") }}
{% endif %}

---
> [!NOTE]
> Tree is truncated at depth {{ depth }}. Use `depth` parameter to explore further.
"""


class TypeHierarchyResponse(BaseModel):
    root: TypeHierarchyNode
    nodes: dict[str, TypeHierarchyNode]
    """Map of node ID to node details"""

    edges_up: dict[str, list[TypeEdge]]
    """Map of node ID to its supertypes (parent edges)"""

    edges_down: dict[str, list[TypeEdge]]
    """Map of node ID to its subtypes (child edges)"""

    direction: str
    depth: int

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
