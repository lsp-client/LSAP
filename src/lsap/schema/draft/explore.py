"""
# Explore API

The Explore API provides relationship-oriented code exploration, answering "what's around this symbol"
(siblings, dependencies, hierarchy) rather than just "what it is" (definition).

## Example Usage

### Scenario 1: Exploring siblings and dependencies of a class

Request:

```json
{
  "locate": {
    "file_path": "src/models.py",
    "scope": {
      "symbol_path": ["User"]
    }
  },
  "include": ["siblings", "dependencies"],
  "max_items": 10
}
```

### Scenario 2: Exploring class hierarchy and calls

Request:

```json
{
  "locate": {
    "file_path": "src/services.py",
    "scope": {
      "symbol_path": ["AuthService"]
    }
  },
  "include": ["hierarchy", "calls"],
  "resolve_info": true
}
```
"""

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from .._abc import Response
from ..locate import LocateRequest
from ..models import CallHierarchy, SymbolInfo


class HierarchyInfo(BaseModel):
    """Information about the inheritance hierarchy of a symbol."""

    parents: list[SymbolInfo] = Field(
        default_factory=list, description="Parent classes or interfaces"
    )
    children: list[SymbolInfo] = Field(
        default_factory=list, description="Child classes or implementations"
    )


class ExploreRequest(LocateRequest):
    """
    Request to explore relationships around a symbol.

    Provides information about siblings, dependencies, hierarchy, and calls.
    """

    include: list[
        Literal["siblings", "dependencies", "dependents", "hierarchy", "calls"]
    ] = Field(default=["siblings", "dependencies"])
    """Types of relationships to include in the exploration."""

    max_items: int = Field(default=10, ge=1, le=50)
    """Maximum number of items to return for each relationship type."""

    resolve_info: bool = False
    """Whether to resolve detailed information for symbols."""

    include_external: bool = False
    """Whether to include external dependencies if available."""


markdown_template: Final = """
# Explore: `{{ target.path | join: "." }}` (`{{ target.kind }}`)

{% if siblings.size > 0 -%}
## Siblings
{% for item in siblings -%}
- `{{ item.name }}` (`{{ item.kind }}`) {% if item.range != nil %}at line {{ item.range.start.line }}{% endif %}
{% endfor -%}
{%- endif %}

{% if dependencies.size > 0 -%}
## Dependencies
{% for item in dependencies -%}
- `{{ item.name }}` (`{{ item.kind }}`) in `{{ item.file_path }}`
{% endfor -%}
{%- endif %}

{% if dependents.size > 0 -%}
## Dependents
{% for item in dependents -%}
- `{{ item.name }}` (`{{ item.kind }}`) in `{{ item.file_path }}`
{% endfor -%}
{%- endif %}

{% if hierarchy != nil -%}
## Hierarchy
{% if hierarchy.parents.size > 0 -%}
### Parents
{% for item in hierarchy.parents -%}
- `{{ item.name }}` (`{{ item.kind }}`) in `{{ item.file_path }}`
{% endfor -%}
{%- endif %}

{% if hierarchy.children.size > 0 -%}
### Children
{% for item in hierarchy.children -%}
- `{{ item.name }}` (`{{ item.kind }}`) in `{{ item.file_path }}`
{% endfor -%}
{%- endif %}
{%- endif %}

{% if calls != nil -%}
## Call Hierarchy
{% if calls.incoming.size > 0 -%}
### Incoming Calls
{% for item in calls.incoming -%}
- `{{ item.name }}` (`{{ item.kind }}`) at `{{ item.file_path }}:{{ item.range.start.line }}`
{% endfor -%}
{%- endif %}

{% if calls.outgoing.size > 0 -%}
### Outgoing Calls
{% for item in calls.outgoing -%}
- `{{ item.name }}` (`{{ item.kind }}`) at `{{ item.file_path }}:{{ item.range.start.line }}`
{% endfor -%}
{%- endif %}
{%- endif %}

---
> [!TIP]
> Use this map to understand the architectural context and impact of changes to this symbol.
"""


class ExploreResponse(Response):
    """Response containing relationship-oriented information about a symbol."""

    target: SymbolInfo
    """The symbol being explored."""

    siblings: list[SymbolInfo] = Field(default_factory=list)
    """Symbols defined in the same scope or file."""

    dependencies: list[SymbolInfo] = Field(default_factory=list)
    """Symbols that this symbol depends on."""

    dependents: list[SymbolInfo] = Field(default_factory=list)
    """Symbols that depend on this symbol."""

    hierarchy: HierarchyInfo | None = None
    """Inheritance hierarchy information."""

    calls: CallHierarchy | None = None
    """Call hierarchy information."""

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


__all__ = [
    "HierarchyInfo",
    "ExploreRequest",
    "ExploreResponse",
]
