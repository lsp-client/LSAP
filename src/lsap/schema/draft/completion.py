from typing import Final

from pydantic import BaseModel, ConfigDict

from lsap.schema.abc import PaginatedRequest, PaginatedResponse
from lsap.schema.locate import LocateRequest


class CompletionItem(BaseModel):
    label: str
    """The text to display and insert (e.g., 'send_message')"""

    kind: str
    """Type of item: Method, Variable, Class, etc."""

    detail: str | None = None
    """Short signature or type info (e.g., '(text: str) -> None')"""

    documentation: str | None = None
    """Markdown documentation for this specific option"""

    insert_text: str | None = None
    """The actual snippet that would be inserted"""


class CompletionRequest(LocateRequest, PaginatedRequest):
    """
    Gets code completion suggestions at a specific position.

    Use this when you need to discover available attributes, methods, or variables
    at a cursor position to help write or edit code.
    """

    max_items: int | None = 15
    """Limit the number of suggestions to avoid token bloat (default: 15)"""


markdown_template: Final = """
# Code Completion

{% if items.size == 0 -%}
No completion suggestions found.
{%- else -%}
{% if items[0].documentation != nil %}
## Top Suggestion Detail: `{{ items[0].label }}`
{{ items[0].documentation }}
{% endif %}

{%- for item in items %}
### {{ forloop.index }}. `{{ item.label }}` ({{ item.kind }})
{%- if item.detail %}
- Detail: {{ item.detail }}
{%- endif %}
{%- if item.insert_text and item.insert_text != item.label %}
- Insert: `{{ item.insert_text }}`
{%- endif %}
{%- if item.documentation %}
- Doc: {{ item.documentation }}
{%- endif %}
{%- endfor %}

{% if has_more -%}
---
> [!TIP]
{%- if pagination_id != nil %}
> Use `pagination_id="{{ pagination_id }}"` to fetch more suggestions.
{%- else %}
> More results available. Use `start_index` to fetch more.
{%- endif %}
{%- endif %}

---
> [!TIP]
> Use these symbols to construct your next code edit. You can focus on a specific method to get more details.
{%- endif %}
"""


class CompletionResponse(PaginatedResponse):
    items: list[CompletionItem]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
