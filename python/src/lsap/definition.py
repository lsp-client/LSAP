from __future__ import annotations

from functools import cached_property
from typing import Protocol, Sequence, override, runtime_checkable

import asyncer
from attrs import define
from lsap_schema.definition import DefinitionRequest, DefinitionResponse
from lsap_schema.models import SymbolCodeInfo
from lsp_client.capability.request import (
    WithRequestDeclaration,
    WithRequestDefinition,
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestTypeDefinition,
)
from lsprotocol.types import Location

from .abc import Capability, ClientProtocol
from .exception import UnsupportedCapabilityError
from .locate import LocateCapability
from .symbol import SymbolCapability


@runtime_checkable
class DefinitionClient(
    WithRequestDefinition,
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

        locations: Sequence[Location] | None = None
        match req.mode:
            case "definition":
                locations = await self.client.request_definition_locations(
                    file_path, lsp_pos
                )
            case "declaration":
                if not isinstance(self.client, WithRequestDeclaration):
                    raise UnsupportedCapabilityError(
                        "Client does not support 'textDocument/declaration'. "
                        "To find declarations, you can: "
                        "1) Use 'definition' mode (most language servers treat them similarly); "
                        "2) For C/C++, check corresponding header files manually."
                    )
                locations = await self.client.request_declaration_locations(
                    file_path, lsp_pos
                )
            case "type_definition":
                if not isinstance(self.client, WithRequestTypeDefinition):
                    raise UnsupportedCapabilityError(
                        "Client does not support 'textDocument/typeDefinition'. "
                        "To find type definitions, you can: "
                        "1) Use 'definition' on the type name itself if visible; "
                        "2) Use 'hover' to see the type name and then search for it."
                    )
                locations = await self.client.request_type_definition_locations(
                    file_path, lsp_pos
                )

        if not locations:
            return None

        infos = []
        async with asyncer.create_task_group() as tg:

            async def resolve_item(loc: Location) -> SymbolCodeInfo | None:
                target_file_path = self.client.from_uri(loc.uri)
                if symbol_info := await self.symbol.resolve(
                    target_file_path,
                    loc.range.start,
                ):
                    return symbol_info

            infos = [tg.soonify(resolve_item)(loc) for loc in locations]
        items: list[SymbolCodeInfo] = [
            value for info in infos if (value := info.value) is not None
        ]

        return DefinitionResponse(items=items, request=req)
