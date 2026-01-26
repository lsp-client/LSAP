"""
# Outline API

The Outline API returns a hierarchical tree of all symbols defined within a specific file,
or lists top-level symbols across all code files in a directory.

## Example Usage

### Scenario 1: Getting outline for a model file (top-level symbols only)

Request:

```json
{
  "path": "src/models.py"
}
```

### Scenario 2: Getting outline for a controller file (all nested symbols)

Request:

```json
{
  "path": "src/controllers.py",
  "recursive": true
}
```

### Scenario 3: Getting outline for a specific class

Request:

```json
{
  "path": "src/models.py",
  "scope": {
    "symbol_path": ["MyClass"]
  }
}
```

### Scenario 4: Getting outline for all files in a directory (immediate directory only)

Request:

```json
{
  "path": "src/models"
}
```

### Scenario 5: Getting outline for all files in a directory (recursive scan)

Request:

```json
{
  "path": "src/models",
  "recursive": true
}
```
"""

from pathlib import Path
from typing import Final, Self, override

from pydantic import ConfigDict, model_validator

from ._abc import Request, Response
from .locate import SymbolScope
from .models import SymbolDetailInfo


class OutlineFileItem(SymbolDetailInfo):
    """
    Thin semantic wrapper around :class:`SymbolDetailInfo` used for directory outline mode.

    This class intentionally does not add any new fields or behaviour today; it exists as a
    distinct type to make directory outline responses self-documenting and to preserve a
    stable extension point for adding directory-specific metadata in the future without
    breaking the public API.
    """


class OutlineRequest(Request):
    """
    Retrieves a hierarchical outline of symbols within a file or directory.

    Use this to understand the structure of a file (classes, methods, functions)
    and quickly navigate its contents, or to get an overview of all code files
    in a directory.

    **File Mode**: When `path` points to a file, returns symbol hierarchy.
    - recursive=False (default): Only top-level symbols (classes, top-level functions)
    - recursive=True: All symbols including nested members (methods, nested functions)

    **Directory Mode**: When `path` points to a directory, lists code files and symbols.
    - recursive=False (default): Only files in the immediate directory
    - recursive=True: Recursively scan subdirectories

    If `scope` is provided (file mode only), it will locate the specified symbol
    and return the outline for that symbol and its children.
    """

    path: Path
    scope: SymbolScope | None = None
    """Optional symbol path to narrow the outline (e.g. `MyClass` or `MyClass.my_method`). Only valid for files."""
    recursive: bool = False
    """If true: for directories, scan subdirectories; for files, include all nested symbols."""

    @model_validator(mode="after")
    def validate_request_fields(self) -> Self:
        if self.scope and self.path.is_dir():
            raise ValueError("scope cannot be used with directory paths")
        return self


file_markdown_template: Final = """
# Outline for `{{ path }}`

{% for item in items -%}
{% assign level = item.path | size | plus: 1 -%}
{% for i in (1..level) %}#{% endfor %} `{{ item.path | join: "." }}` (`{{ item.kind }}`)
{% if item.detail != nil %}{{ item.detail }}{% endif %}
{% if item.hover != nil %}{{ item.hover | strip }}{% endif %}

{% endfor -%}
"""

directory_markdown_template: Final = """
# Directory Outline: `{{ path }}`

Found {{ total_files }} code file(s) with {{ total_symbols }} top-level symbol(s)

{% for group in files -%}
## `{{ group.file_path }}`

{% if group.symbols.size == 0 -%}
No symbols found.
{%- else -%}
{%- for symbol in group.symbols %}
- `{{ symbol.name }}` (`{{ symbol.kind }}`)
{%- endfor %}
{%- endif %}

{% endfor -%}

{% if has_subdirs and request.recursive == false -%}
---

> [!TIP]
> Subdirectories found. Set `recursive=true` to scan them.
{%- endif %}
"""


class OutlineFileGroup(Response):
    file_path: Path
    symbols: list[OutlineFileItem]


class OutlineResponse(Response):
    path: Path
    is_directory: bool
    request: OutlineRequest
    items: list[SymbolDetailInfo] | None = None
    files: list[OutlineFileGroup] | None = None
    total_files: int | None = None
    total_symbols: int | None = None
    has_subdirs: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": file_markdown_template,
            "directory_markdown": directory_markdown_template,
        }
    )

    @model_validator(mode="after")
    def validate_response_fields(self) -> Self:
        """Ensure correct fields are populated based on is_directory flag."""
        if self.is_directory:
            if self.files is None:
                raise ValueError("files must be provided when is_directory=True")
            if self.items is not None:
                raise ValueError("items must be None when is_directory=True")
        else:
            if self.items is None:
                raise ValueError("items must be provided when is_directory=False")
            if self.files is not None:
                raise ValueError("files must be None when is_directory=False")
        return self

    @override
    def format(self, template_name: str = "markdown") -> str:
        if template_name == "markdown" and self.is_directory:
            template_name = "directory_markdown"
        return super().format(template_name)


__all__ = [
    "OutlineFileGroup",
    "OutlineFileItem",
    "OutlineRequest",
    "OutlineResponse",
]
