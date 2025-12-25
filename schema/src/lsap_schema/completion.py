from typing import Final

from pydantic import BaseModel, ConfigDict

from .locate import LocateRequest


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


class CompletionRequest(LocateRequest):
    """
    Gets code completion suggestions at a specific position.

    Use this when you need to discover available attributes, methods, or variables
    at a cursor position to help write or edit code.
    """

    limit: int = 15
    """Limit the number of suggestions to avoid token bloat (default: 15)"""


markdown_template: Final = """
### Code Completion at the requested location

{% if not items -%}
No completion suggestions found.
{%- else -%}
| Symbol | Kind | Detail |
| :--- | :--- | :--- |
{%- for item in items %}
| `{{ item.label }}` | {{ item.kind }} | {{ item.detail or "" }} |
{%- endfor %}

{% if items[0].documentation %}
#### Top Suggestion Detail: `{{ items[0].label }}`
{{ items[0].documentation }}
{% endif %}

---
> [!TIP]
> Use these symbols to construct your next code edit. You can focus on a specific method to get more details.
{%- endif %}
"""


class CompletionResponse(BaseModel):
    items: list[CompletionItem]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
