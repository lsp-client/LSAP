from __future__ import annotations

from functools import cached_property
from typing import Protocol, Sequence, override, runtime_checkable

from attrs import define
from lsap_schema.definition import DefinitionRequest, DefinitionResponse
from lsp_client.capability.request import (
    WithRequestDeclaration,
    WithRequestDefinition,
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestTypeDefinition,
)
from lsprotocol.types import Location, LocationLink

from .abc import Capability, ClientProtocol
from .locate import LocateCapability
from .symbol import SymbolCapability


@runtime_checkable
class DefinitionClient(
    WithRequestDefinition,
    WithRequestDeclaration,
    WithRequestTypeDefinition,
    WithRequestDocumentSymbol,
    WithRequestHover,
    ClientProtocol,
    Protocol,
): ...


@define
class DefinitionCapability(
    Capability[DefinitionClient, DefinitionRequest, DefinitionResponse]
):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(self.client)

    @cached_property
    def symbol(self) -> SymbolCapability:
        return SymbolCapability(self.client)

    @override
    async def __call__(self, req: DefinitionRequest) -> DefinitionResponse | None:
        if not (loc_resp := await self.locate(req)):
            return None

        file_path, lsp_pos = loc_resp.file_path, loc_resp.position.to_lsp()
        locations: Location | Sequence[Location] | Sequence[LocationLink] | None = None

        match req.mode:
            case "definition":
                locations = await self.client.request_definition(file_path, lsp_pos)
            case "declaration":
                locations = await self.client.request_declaration(file_path, lsp_pos)
            case "type_definition":
                locations = await self.client.request_type_definition(
                    file_path, lsp_pos
                )

        if not locations:
            return None

        if isinstance(locations, Location):
            loc = locations
        elif isinstance(locations, LocationLink):
            loc = locations
        elif isinstance(locations, (list, tuple)) and locations:
            loc = locations[0]
        else:
            return None

        uri, range_ = (
            (loc.target_uri, loc.target_selection_range)
            if isinstance(loc, LocationLink)
            else (loc.uri, loc.range)
        )

        target_file_path = self.client.from_uri(uri)
        symbol_info = await self.symbol.resolve(
            target_file_path,
            range_.start,
            include_hover=req.include_hover,
            include_code=req.include_code,
        )

        if not symbol_info:
            return None

        return DefinitionResponse(
            **symbol_info.model_dump(),
            request=req,
        )
