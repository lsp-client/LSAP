from pathlib import Path

from attrs import define

from .abc import Request, Response


@define
class InlayReadRequest(Request):
    file_path: Path
    """
    Relative file path to read with inlay hints.
    """


@define
class InlayReadResponse(Response):
    content: str
    """
    File content with inlay hints.
    """
