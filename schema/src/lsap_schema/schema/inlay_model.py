from pathlib import Path
from pydantic import BaseModel, ConfigDict
from .locate import Range


class InlayReadRequest(BaseModel):
    file_path: Path
    range: Range | None = None


class InlayReadResponse(BaseModel):
    content: str

    model_config = ConfigDict(
        json_schema_extra={"lsap_templates": {"markdown": "{{ content }}"}}
    )
