"""
Call Hierarchy API - Backward compatibility module.

This module maintains backward compatibility by re-exporting from the unified hierarchy API.
The unified hierarchy API (hierarchy.py) should be used for new code.
"""

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from lsap_schema.abc import Response
from lsap_schema.draft.hierarchy import (
    HierarchyItem as CallHierarchyItem,
    HierarchyNode as CallHierarchyNode,
    Position,
)
from lsap_schema.locate import LocateRequest


class CallEdge(BaseModel):
    """Call edge with call sites"""

    from_node_id: str
    to_node_id: str
    call_sites: list[Position]
    """Exact positions where the call occurs"""


class CallHierarchyRequest(LocateRequest):
    """
    Traces incoming or outgoing calls for a symbol.

    Use this to understand function call relationships, find callers (who uses this?),
    or callees (what does this call?).

    Note: This is maintained for backward compatibility. Use HierarchyRequest with
    hierarchy_type='call' for new code.
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
    """
    Call Hierarchy Response - Backward compatibility class.

    Note: This is maintained for backward compatibility. Use HierarchyResponse with
    hierarchy_type='call' for new code.
    """

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


__all__ = [
    "CallHierarchyNode",
    "CallHierarchyItem",
    "CallEdge",
    "CallHierarchyRequest",
    "CallHierarchyResponse",
]
