from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from .abc import PaginatedRequest, PaginatedResponse
from .models import SymbolKind


class SearchItem(BaseModel):
    """Concise search result for quick discovery."""

    name: str
    kind: SymbolKind
    file_path: Path
    line: int | None = None
    """1-based line number where the symbol is defined."""
    container: str | None = None
    """Parent symbol name (e.g., class name for a method)."""


class SearchRequest(PaginatedRequest):
    """
    Searches for symbols across the workspace by name pattern.

    Returns concise results for quick discovery. Use SymbolRequest
    to get detailed information about a specific symbol.
    """

    query: str
    """
    Search pattern. Supports:
    - Exact match: "AuthService"
    - Prefix: "Auth"
    """

    kinds: list[SymbolKind] | None = None
    """Filter by symbol kinds (e.g., ["class", "function"])."""


markdown_template: Final = """
# Search: `{{ request.query }}`
{% if total != nil -%}
Found {{ total }} results{% if max_items != nil %} (showing {{ items.size }}){% endif %}
{%- endif %}

{% if items.size == 0 -%}
No matches found.
{%- else -%}
{%- for item in items %}
- `{{ item.name }}` ({{ item.kind }}): `{{ item.file_path }}{% if item.line != nil %}:{{ item.line }}{% endif %}`{% if item.container != nil %} (in `{{ item.container }}`){% endif %}
{%- endfor %}

{% if has_more -%}
> More results available. Use `start_index={{ start_index | plus: items.size }}` for next page.
{%- endif %}
{%- endif %}
"""


class SearchResponse(PaginatedResponse):
    request: SearchRequest
    items: list[SearchItem]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
