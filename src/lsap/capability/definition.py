from __future__ import annotations

from functools import cached_property
from typing import Sequence, override

import asyncer
from attrs import define
from lsp_client.capability.request import (
    WithRequestDeclaration,
    WithRequestDefinition,
    WithRequestTypeDefinition,
)
from lsprotocol.types import Location

from lsap.schema.definition import DefinitionRequest, DefinitionResponse
from lsap.schema.models import SymbolCodeInfo
from lsap.utils.capability import ensure_capability

from .abc import Capability
from .locate import LocateCapability
from .symbol import SymbolCapability


@define
class DefinitionCapability(Capability[DefinitionRequest, DefinitionResponse]):
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
                locations = await ensure_capability(
                    self.client, WithRequestDefinition
                ).request_definition_locations(file_path, lsp_pos)
            case "declaration":
                locations = await ensure_capability(
                    self.client,
                    WithRequestDeclaration,
                    error="""To find declarations, you can:
                    1) Use 'definition' mode (most language servers treat them similarly);
                    2) For C/C++, check corresponding header files manually.""",
                ).request_declaration_locations(file_path, lsp_pos)
            case "type_definition":
                locations = await ensure_capability(
                    self.client,
                    WithRequestTypeDefinition,
                    error="""To find type definitions, you can:
                    1) Use 'definition' on the type name itself if visible;
                    2) Use 'hover' to see the type name and then search for it.""",
                ).request_type_definition_locations(file_path, lsp_pos)

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
