from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from lsap_schema.abc import Response
from lsap_schema.locate import LocateRequest, Position


class CallHierarchyNode(BaseModel):
    id: str
    name: str
    kind: str
    file_path: Path
    range_start: Position


class CallHierarchyItem(BaseModel):
    name: str
    kind: str
    file_path: Path
    level: int
    is_cycle: bool = False


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
# Call Hierarchy for `{{ root.name }}` (Depth: {{ depth }}, Direction: {{ direction }})

{% if direction == "incoming" or direction == "both" %}
## Incoming Calls (Who calls this?)

{% for item in calls_in %}
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

{% for item in calls_out %}
{% for i in (1..item.level) %}#{% endfor %}## {{ item.name }}
- **Kind**: `{{ item.kind }}`
- **File**: `{{ item.file_path }}`
{%- if item.is_cycle %}
- **Recursive cycle detected**
{%- endif %}

{% endfor %}
{% endif %}

---
> [!NOTE]
> Tree is truncated at depth {{ depth }}. Use `depth` parameter to explore further.
"""


class CallHierarchyResponse(Response):
    root: CallHierarchyNode

    nodes: dict[str, CallHierarchyNode]
    """Map of node ID to node details"""

    edges_in: dict[str, list[CallEdge]]
    """Map of node ID to its incoming edges"""

    edges_out: dict[str, list[CallEdge]]
    """Map of node ID to its outgoing edges"""

    calls_in: list[CallHierarchyItem] = []
    """Flat list of incoming calls for tree rendering"""

    calls_out: list[CallHierarchyItem] = []
    """Flat list of outgoing calls for tree rendering"""

    direction: str
    depth: int

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
