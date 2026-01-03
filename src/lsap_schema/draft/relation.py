from typing import Final

from pydantic import ConfigDict

from lsap_schema.abc import Request, Response
from lsap_schema.draft.call_hierarchy import CallHierarchyItem
from lsap_schema.locate import Locate


class RelationRequest(Request):
    """
    Finds call chains connecting two symbols.

    Uses call hierarchy to trace paths from source to target.
    """

    source: Locate
    target: Locate

    max_depth: int = 10
    """Maximum depth to search for connections"""


markdown_template: Final = """
# Relation: `{{ source.name }}` → `{{ target.name }}`

{% if chains.size > 0 %}
Found {{ chains | size }} call chain(s):

{% for chain in chains %}
### Chain {{ forloop.index }}
{% for item in chain %}
{{ forloop.index }}. **{{ item.name }}** (`{{ item.kind }}`) - `{{ item.file_path }}`
{% endfor %}
{% endfor %}
{% else %}
No connection found between `{{ source.name }}` and `{{ target.name }}` (depth: {{ max_depth }}).
{% endif %}
"""


class RelationResponse(Response):
    source: CallHierarchyItem
    target: CallHierarchyItem
    chains: list[list[CallHierarchyItem]]
    """List of paths, where each path is a sequence of items from source to target."""

    max_depth: int

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
