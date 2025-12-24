from pathlib import Path
from pydantic import BaseModel, ConfigDict
from ..abc import SymbolPath
from .locate import LocateRequest


class SymbolRequest(LocateRequest): ...


class SymbolResponse(BaseModel):
    file_path: Path
    symbol_path: SymbolPath
    symbol_content: str

    model_config = ConfigDict(
        json_schema_extra={
            "lsap_templates": {
                "markdown": "### Symbol: `{{ symbol_path | join('.') }}` in `{{ file_path }}`\n\n```python\n{{ symbol_content }}\n```"
            }
        }
    )
