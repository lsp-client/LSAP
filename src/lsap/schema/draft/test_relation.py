from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from lsap.schema.abc import Request, Response
from lsap.schema.locate import Locate
from lsap.schema.models import Range, SymbolInfo


class TestRelationItem(BaseModel):
    name: str
    kind: str
    file_path: str
    range: Range
    strategy: Literal["reference", "convention", "import"]
    """
    How the relation was determined:
    - reference: Explicit code reference (e.g. function call).
    - convention: Naming convention (e.g. `test_func` matches `func`).
    - import: The test file imports the source module.
    """


class TestRelationRequest(Request):
    """
    Finds tests related to a symbol, or source code related to a test.

    Helps Agents determine which tests to run after modifying code.
    """

    locate: Locate
    """The symbol to analyze (source code or test case)."""

    direction: Literal["to_test", "to_source"] = "to_test"
    """
    Direction of the relation:
    - to_test: Find tests that cover the given symbol (default).
    - to_source: Find source code covered by the given test.
    """


markdown_template: Final = """
# Test Relation for `{{ symbol.name }}` ({{ direction }})

{% if related_items.size > 0 %}
Found {{ related_items | size }} related item(s):

{% for item in related_items %}
- **{{ item.name }}** (`{{ item.kind }}`)
  - File: `{{ item.file_path }}`
  - Line: {{ item.range.start.line }}
  - Strategy: `{{ item.strategy }}`
{% endfor %}
{% else %}
{% if direction == "to_test" %}
No related tests found for `{{ symbol.name }}`.
{% else %}
No related source code found for `{{ symbol.name }}`.
{% endif %}
{% endif %}
"""


class TestRelationResponse(Response):
    symbol: SymbolInfo
    """The input symbol that was located."""

    direction: Literal["to_test", "to_source"]

    related_items: list[TestRelationItem]
    """List of related tests (or source symbols)."""

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
