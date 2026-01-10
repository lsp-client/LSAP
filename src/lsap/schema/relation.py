from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from lsap.schema.abc import Request, Response
from lsap.schema.locate import Locate


class ChainNode(BaseModel):
    """
    A node in a call chain.
    """

    name: str
    kind: str
    file_path: Path
    detail: str | None = None


class RelationRequest(Request):
    """
    Finds call chains connecting two symbols.

    Answers the question: "How does A reach B?"

    Use cases:
    - Code flow understanding: How does handle_request reach db.query?
    - Impact analysis: Which entry points are affected if I modify X?
    - Architecture validation: Verify module A never calls module B
    """

    source: Locate
    target: Locate

    max_depth: int = 10
    """Maximum depth to search for connections"""


markdown_template: Final = """
# Relation: `{{ source.name }}` → `{{ target.name }}`

{% if chains.size > 0 %}
Found {{ chains.size }} call chain(s):

{% for chain in chains %}
### Chain {{ forloop.index }}
{% for node in chain %}
{{ forloop.index }}. **{{ node.name }}** (`{{ node.kind }}`) - `{{ node.file_path }}`
{%- if node.detail %} — {{ node.detail }}{% endif %}
{% endfor %}
{% endfor %}
{% else %}
No connection found between `{{ source.name }}` and `{{ target.name }}` within depth {{ request.max_depth }}.
{% endif %}
"""


class RelationResponse(Response):
    request: RelationRequest
    """The original request"""

    source: ChainNode
    """The resolved source symbol"""

    target: ChainNode
    """The resolved target symbol"""

    chains: list[list[ChainNode]]
    """All paths found. Each path is a sequence of nodes from source to target."""

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


__all__ = [
    "ChainNode",
    "RelationRequest",
    "RelationResponse",
]
