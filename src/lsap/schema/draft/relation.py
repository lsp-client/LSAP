"""
# Relation API

The Relation API allows finding all call chains (paths) that connect two specific symbols.
This is useful for understanding how one part of the system interacts with another,
validating architectural dependencies, or impact analysis.

## Example Usage

### Scenario 1: How does `handle_request` reach `db.query`?

Request:

```json
{
  "source": {
    "file_path": "src/controllers.py",
    "scope": {
      "symbol_path": ["handle_request"]
    }
  },
  "target": {
    "file_path": "src/db.py",
    "scope": {
      "symbol_path": ["query"]
    }
  },
  "max_depth": 5
}
```
"""

from typing import Final

from pydantic import ConfigDict

from lsap.schema._abc import Request, Response
from lsap.schema.draft.hierarchy import HierarchyItem
from lsap.schema.locate import Locate


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
{{ forloop.index }}. **`{{ item.name }}`** (`{{ item.kind }}`) - `{{ item.file_path }}`
{% endfor %}
{% endfor %}
{% else %}
No connection found between `{{ source.name }}` and `{{ target.name }}` (depth: {{ max_depth }}).
{% endif %}
"""


class RelationResponse(Response):
    source: HierarchyItem
    target: HierarchyItem
    chains: list[list[HierarchyItem]]
    """List of paths, where each path is a sequence of items from source to target."""

    max_depth: int

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


__all__ = [
    "RelationRequest",
    "RelationResponse",
]
