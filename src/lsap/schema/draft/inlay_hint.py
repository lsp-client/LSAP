"""
# Inlay Hints & Inline Values API

LSAP provides the ability to read code with "decorations" that inject static type
hints, parameter names, and runtime variable values directly into the text as
comments.

## Example Usage

### Scenario 1: Getting type hints for a function

Request (`InlayHintRequest`):

```json
{
  "file_path": "src/api.py",
  "range": {
    "start": { "line": 10, "character": 0 },
    "end": { "line": 15, "character": 0 }
  }
}
```

### Scenario 2: Debugging an error with runtime values

Request (`InlineValueRequest`):

```json
{
  "file_path": "src/logic.py",
  "range": {
    "start": { "line": 10, "character": 0 },
    "end": { "line": 20, "character": 0 }
  }
}
```
"""

from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from lsap.schema._abc import Request, Response
from lsap.schema.models import Range


class InlayHintItem(BaseModel):
    label: str
    """The hint text (e.g., 'arg_name:', ': int')"""

    kind: Literal["Type", "Parameter"] | None = None
    position: str
    """Specific position where the hint should be placed"""


class InlayHintRequest(Request):
    """
    Retrieves inline hints like parameter names or inferred types.

    Use this to get better context for code by seeing "hidden" details
    that are normally provided by an IDE's visual overlay.
    """

    file_path: Path
    range: Range | None = None
    """Range to fetch hints for. If None, fetches for the visible area or small snippet."""


class InlineValueItem(BaseModel):
    line: int
    text: str
    """The value text to display (e.g., 'x = 42')"""


class InlineValueRequest(Request):
    """
    Retrieves runtime or contextual values for variables in a range.

    Use this when debugging or inspecting code to see the actual values
    of variables at specific lines.
    """

    file_path: Path
    range: Range
    """Range to fetch values for (usually the current execution context)"""


markdown_template: Final = """
# Code with Annotations: `{{ file_path }}`

```
{{ decorated_content }}
```

---
> [!NOTE]
> Annotations like `/* :type */` or `/* param:= */` are injected for clarity.
> Runtime values (if any) are shown as `// value: x=42`.
"""


class DecoratedContentResponse(Response):
    file_path: Path
    decorated_content: str
    """Content with hints/values baked in as comments"""

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )


__all__ = [
    "DecoratedContentResponse",
    "InlayHintItem",
    "InlayHintRequest",
    "InlineValueItem",
    "InlineValueRequest",
]
