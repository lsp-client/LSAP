from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from ..abc import SymbolPath
from .locate import LocateRequest


class SymbolRequest(LocateRequest): ...


markdown_template: Final = """
### Symbol: `{{ symbol_path | join('.') }}` in `{{ file_path }}`

```
{{ symbol_content }}
```
"""


class SymbolResponse(BaseModel):
    file_path: Path
    symbol_path: SymbolPath
    symbol_content: str

    model_config = ConfigDict(
        json_schema_extra={
            "markdown": markdown_template,
        }
    )
