from pathlib import Path

from pydantic import BaseModel


class InlayReadRequest(BaseModel):
    file_path: Path
    """
    Relative file path to read with inlay hints.
    """


class InlayReadResponse(BaseModel):
    content: str
    """
    File content with inlay hints.
    """
