from typing import Final, NamedTuple

from .abc import Request, Response
from .definition import DefinitionRequest, DefinitionResponse
from .hover import HoverRequest, HoverResponse
from .locate import LocateRequest, LocateResponse
from .outline import OutlineRequest, OutlineResponse
from .reference import ReferenceRequest, ReferenceResponse
from .rename import (
    RenameExecuteRequest,
    RenameExecuteResponse,
    RenamePreviewRequest,
    RenamePreviewResponse,
)
from .search import SearchRequest, SearchResponse
from .symbol import SymbolRequest, SymbolResponse


class Schema(NamedTuple):
    request: type[Request]
    response: type[Response]


capability_schemas: Final = {
    "definition": Schema(
        request=DefinitionRequest,
        response=DefinitionResponse,
    ),
    "hover": Schema(
        request=HoverRequest,
        response=HoverResponse,
    ),
    "locate": Schema(
        request=LocateRequest,
        response=LocateResponse,
    ),
    "outline": Schema(
        request=OutlineRequest,
        response=OutlineResponse,
    ),
    "reference": Schema(
        request=ReferenceRequest,
        response=ReferenceResponse,
    ),
    "rename_preview": Schema(
        request=RenamePreviewRequest,
        response=RenamePreviewResponse,
    ),
    "rename_execute": Schema(
        request=RenameExecuteRequest,
        response=RenameExecuteResponse,
    ),
    "search": Schema(
        request=SearchRequest,
        response=SearchResponse,
    ),
    "symbol": Schema(
        request=SymbolRequest,
        response=SymbolResponse,
    ),
}

__all__ = [
    "Schema",
    "capability_schemas",
]
