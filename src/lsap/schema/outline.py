"""
# Outline API

The Outline API returns a hierarchical tree of all symbols defined within a specific file.
This allows an Agent to understand the structure of a file without reading the entire
source code.

## Example Usage

### Scenario 1: Getting outline for a model file

Request:

```json
{
  "file_path": "src/models.py"
}
```

### Scenario 2: Getting outline for a controller file

Request:

```json
{
  "file_path": "src/controllers.py"
}
```

### Scenario 3: Getting outline for a specific class

Request:

```json
{
  "file_path": "src/models.py",
  "scope": {
    "symbol_path": ["MyClass"]
  }
}
```
"""

from pathlib import Path
from typing import Final

from pydantic import ConfigDict

from ._abc import Request, Response
from .locate import SymbolScope
from .models import SymbolDetailInfo


class OutlineRequest(Request):
    """
    Retrieves a hierarchical outline of symbols within a file.

    Use this to understand the structure of a file (classes, methods, functions)
    and quickly navigate its contents.

    If `scope` is provided, it will locate the specified symbol and return the
    outline for that symbol and its children.

    Note: By default (top=False), this API returns structural symbols only
    (classes, methods, top-level functions/variables), excluding symbols
    defined inside functions or methods (like local variables or nested
    functions) to reduce noise. When top=True, only first-level symbols
    are returned.
    """

    file_path: Path
    scope: SymbolScope | None = None
    """Optional symbol path to narrow the outline (e.g. `MyClass` or `MyClass.my_method`)."""
    top: bool = False
    """If true, return only top-level symbols (expanding Module containers to show their direct children, and excluding nested members of classes and functions)."""


markdown_template: Final = """
# Outline for `{{ file_path }}`

{% for item in items -%}
{% assign level = item.path | size | plus: 1 -%}
{% for i in (1..level) %}#{% endfor %} `{{ item.path | join: "." }}` (`{{ item.kind }}`)
{% if item.detail != nil %}{{ item.detail }}{% endif %}
{% if item.hover != nil %}{{ item.hover | strip }}{% endif %}

{% endfor -%}
"""


class OutlineResponse(Response):
    file_path: Path
    items: list[SymbolDetailInfo]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


__all__ = [
    "OutlineRequest",
    "OutlineResponse",
]
