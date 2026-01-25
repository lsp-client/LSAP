"""
# Inspect API

The Inspect API provides "how to use" information for a symbol, including usage examples,
signatures, and documentation. It is designed to help Agents understand how to correctly
invoke or interact with a symbol.

## Example Usage

### Scenario 1: Inspecting a function for usage examples

Request:

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "scope": {
      "symbol_path": ["format_date"]
    }
  },
  "include_examples": 5,
  "include_signature": true
}
```

### Scenario 2: Inspecting a class with call hierarchy

Request:

```json
{
  "locate": {
    "file_path": "src/models.py",
    "scope": {
      "symbol_path": ["User"]
    }
  },
  "include_call_hierarchy": true
}
```
"""

from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from .._abc import Response
from ..locate import LocateRequest
from ..models import CallHierarchy, Location, SymbolDetailInfo, SymbolInfo


class UsageExample(BaseModel):
    """A code snippet showing how a symbol is used in context."""

    code: str = Field(..., description="Code snippet with context")
    context: SymbolInfo | None = Field(None, description="Where this usage occurs")
    location: Location = Field(..., description="Exact position of the usage")
    call_pattern: str | None = Field(
        None, description="Extracted pattern like 'func(arg1, arg2)'"
    )


class InspectRequest(LocateRequest):
    """
    Request to inspect a symbol for usage-oriented information.

    Provides signatures, documentation, and real-world usage examples from the codebase.
    """

    include_examples: int = Field(default=3, ge=0, le=20)
    """Number of usage examples to include."""

    include_signature: bool = True
    """Whether to include the symbol's signature."""

    include_doc: bool = True
    """Whether to include the symbol's documentation (hover)."""

    include_call_hierarchy: bool = False
    """Whether to include call hierarchy information."""

    include_external: bool = False
    """Whether to include examples from external libraries if available."""

    context_lines: int = Field(default=2, ge=0, le=10)
    """Number of context lines to include around each example."""


markdown_template: Final = """
# Inspect: `{{ info.path | join: "." }}` (`{{ info.kind }}`)

{% if signature != nil -%}
## Signature
```python
{{ signature }}
```
{%- endif %}

{% if info.hover != nil -%}
## Documentation
{{ info.hover }}
{%- endif %}

{% if examples.size > 0 -%}
## Usage Examples
{% for example in examples -%}
### Example {{ forloop.index }}
{% if example.context != nil -%}
In `{{ example.context.path | join: "." }}` (`{{ example.context.kind }}`) at `{{ example.location.file_path }}:{{ example.location.range.start.line }}`
{%- else -%}
At `{{ example.location.file_path }}:{{ example.location.range.start.line }}`
{%- endif %}

{% if example.call_pattern != nil -%}
Pattern: `{{ example.call_pattern }}`
{%- endif %}

```{{ example.location.file_path.suffix | remove_first: "." }}
{{ example.code }}
```
{% endfor -%}
{%- endif %}

{% if call_hierarchy != nil -%}
{% if call_hierarchy.incoming.size > 0 -%}
## Incoming Calls
{% for item in call_hierarchy.incoming -%}
- `{{ item.name }}` (`{{ item.kind }}`) at `{{ item.file_path }}:{{ item.range.start.line }}`
{% endfor -%}
{%- endif %}

{% if call_hierarchy.outgoing.size > 0 -%}
## Outgoing Calls
{% for item in call_hierarchy.outgoing -%}
- `{{ item.name }}` (`{{ item.kind }}`) at `{{ item.file_path }}:{{ item.range.start.line }}`
{% endfor -%}
{%- endif %}
{%- endif %}

---
> [!TIP]
> Use these examples to understand the expected arguments and common calling patterns for this symbol.
"""


class InspectResponse(Response):
    """Response containing usage-oriented information about a symbol."""

    info: SymbolDetailInfo
    signature: str | None = None
    examples: list[UsageExample] = Field(default_factory=list)
    call_hierarchy: CallHierarchy | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


__all__ = [
    "InspectRequest",
    "InspectResponse",
    "UsageExample",
]
