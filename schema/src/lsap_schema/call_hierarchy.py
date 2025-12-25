from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from .locate import LocateRequest, Position


class CallHierarchyNode(BaseModel):
    id: str
    name: str
    kind: str
    file_path: Path
    range_start: Position


class CallEdge(BaseModel):
    from_node_id: str
    to_node_id: str
    call_sites: list[Position]
    """Exact positions where the call occurs"""


class CallHierarchyRequest(LocateRequest):
    """
    Traces incoming or outgoing calls for a symbol.

    Use this to understand function call relationships, find callers (who uses this?),
    or callees (what does this call?).
    """

    direction: Literal["incoming", "outgoing", "both"] = "both"
    """Whether to trace callers (incoming) or callees (outgoing)"""

    depth: int = 2
    """How many hops to trace (default: 2)"""

    include_external: bool = False
    """Whether to include calls to/from external libraries"""


markdown_template: Final = """
### Call Hierarchy for `{{ root.name }}` (Depth: {{ depth }}, Direction: {{ direction }})

{%- macro render_tree(node_id, current_depth, visited, dir_label) %}
  {%- if current_depth <= depth %}
    {%- set node = nodes[node_id] %}
    {%- set edges_to_show = edges_out[node_id] if dir_label == "Calls" else edges_in[node_id] %}
{{ "  " * current_depth }}- **{{ node.name }}** (`{{ node.kind }}`) in `{{ node.file_path }}`
    {%- if node_id in visited %} (recursive cycle)
    {%- else %}
      {%- set new_visited = visited + [node_id] %}
      {%- for edge in edges_to_show %}
        {%- set target_id = edge.to_node_id if dir_label == "Calls" else edge.from_node_id %}
{{ render_tree(target_id, current_depth + 1, new_visited, dir_label) }}
      {%- endfor %}
    {%- endif %}
  {%- endif %}
{%- endmacro %}

{% if direction in ["incoming", "both"] %}
#### Incoming Calls (Who calls this?)
{{ render_tree(root.id, 0, [], "Called By") }}
{% endif %}

{% if direction in ["outgoing", "both"] %}
#### Outgoing Calls (What does this call?)
{{ render_tree(root.id, 0, [], "Calls") }}
{% endif %}

---
> [!NOTE]
> Tree is truncated at depth {{ depth }}. Use `depth` parameter to explore further.
"""


class CallHierarchyResponse(BaseModel):
    root: CallHierarchyNode
    nodes: dict[str, CallHierarchyNode]
    """Map of node ID to node details"""

    edges_in: dict[str, list[CallEdge]]
    """Map of node ID to its incoming edges"""

    edges_out: dict[str, list[CallEdge]]
    """Map of node ID to its outgoing edges"""

    direction: str
    depth: int

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
