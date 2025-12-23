from pathlib import Path
from typing import Protocol, Self

from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestReferences,
)
from lsprotocol.types import ReferencesResult
from pydantic import BaseModel

from .abc import Response
from .base import Locate


class ReferenceClient(
    WithRequestReferences,
    WithRequestDocumentSymbol,
    Protocol,
): ...


class ReferenceRequest(Locate): ...


class ReferenceResponse(Response):
    class ReferenceItem(BaseModel):
        file_path: Path
        symbol_path: list[str]
        snippet: str

    items: list[ReferenceItem]


class Reference(BaseModel):
    file_path: Path
    snippet: str

    @classmethod
    def from_result(cls, result: ReferencesResult) -> Self:
        raise NotImplementedError()
