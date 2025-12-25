from typing import Final

from pydantic import BaseModel, ConfigDict

from .locate import LocateRequest
from .symbol import SymbolResponse


class ReferenceRequest(LocateRequest): ...


markdown_template: Final = """
{% for item in items -%}
- `{{ item.file_path }}` - `{{ item.symbol_path | join('.') }}`
```python
{{ item.symbol_content }}
```
{% if not loop.last %}
{% endif %}
{%- endfor %}
"""


class ReferenceResponse(BaseModel):
    items: list[SymbolResponse]

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
