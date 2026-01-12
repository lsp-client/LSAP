"""
# Doc API

The Doc API provides quick access to documentation, type information, or other
relevant metadata for a symbol at a specific location. It's useful for getting
context without navigating to the definition.

## Example Usage

### Scenario 1: Getting documentation for a function

Request:

```json
{
  "locate": {
    "file_path": "src/utils.py",
    "find": "def calculate"
  }
}
```

### Scenario 2: Getting type information for a variable

Request:

```json
{
  "locate": {
    "file_path": "src/main.py",
    "find": "config"
  }
}
```

### Scenario 3: Getting documentation for a class method

Request:

```json
{
  "locate": {
    "file_path": "src/models/user.py",
    "scope": {
      "symbol_path": ["User", "save"]
    }
  }
}
```

### Scenario 4: Getting documentation for an imported module

Request:

```json
{
  "locate": {
    "file_path": "src/main.py",
    "find": "import numpy"
  }
}
```
"""

from typing import Final

from pydantic import ConfigDict

from ._abc import Response
from .locate import LocateRequest


class DocRequest(LocateRequest):
    """
    Retrieves documentation or type information for a symbol at a specific location.

    Use this to quickly see the documentation, type signature, or other relevant
    information for a symbol without jumping to its definition.
    """


markdown_template: Final = """
# Doc Information

{{ content }}
"""


class DocResponse(Response):
    content: str
    """The documentation content, usually markdown."""

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


__all__ = [
    "DocRequest",
    "DocResponse",
]
