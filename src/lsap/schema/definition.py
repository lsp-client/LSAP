"""
# Definition & Navigation API

The Navigation API provides the ability to jump from a symbol usage to its primary
declaration or definition.

## Example Usage

### Scenario 1: Finding the definition of a method

If an Agent is reading `main.py` and sees `client.send_message()`, it can find
the definition of `send_message`.

Request:

```json
{
    "locate": {
      "file_path": "main.py",
      "scope": {
        "start_line": 15,
        "end_line": 16
      },
      "find": "send_message"
    },
  "mode": "definition",
  "include_code": true
}
```

### Scenario 2: Finding the declaration (useful in languages with header files)

Request:

```json
{
    "locate": {
      "file_path": "main.cpp",
      "scope": {
        "start_line": 20,
        "end_line": 21
      },
      "find": "process_data"
    },
  "mode": "declaration",
  "include_code": true
}
```

### Scenario 3: Finding the type definition of a variable

Request:

```json
{
    "locate": {
      "file_path": "main.py",
      "scope": {
        "start_line": 30,
        "end_line": 31
      },
      "find": "result"
    },
  "mode": "type_definition",
  "include_code": true
}
```
"""

from typing import Final, Literal

from pydantic import ConfigDict

from ._abc import Response
from .locate import LocateRequest
from .models import SymbolCodeInfo


class DefinitionRequest(LocateRequest):
    """
    Finds the definition, declaration, or type definition of a symbol.

    Use this to jump to the actual source code where a symbol is defined,
    its declaration site, or the definition of its type/class.
    """

    mode: Literal["definition", "declaration", "type_definition"] = "definition"
    """The type of location to find."""


markdown_template: Final = """
# {{ request.mode | replace: "_", " " | capitalize }} Result

{% if items.size == 0 -%}
No {{ request.mode | replace: "_", " " }} found.
{%- else -%}
{%- for item in items -%}
## `{{ item.file_path }}`: `{{ item.path | join: "." }}` (`{{ item.kind }}`)

{% if item.code != nil -%}
### Content
```{{ item.file_path.suffix | remove_first: "." }}
{{ item.code }}
```
{%- endif %}

{% endfor -%}
{%- endif %}
"""


class DefinitionResponse(Response):
    request: DefinitionRequest
    items: list[SymbolCodeInfo]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


__all__ = [
    "DefinitionRequest",
    "DefinitionResponse",
]
