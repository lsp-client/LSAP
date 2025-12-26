from functools import cached_property
from typing import runtime_checkable

import asyncer
from lsap_schema.schema.reference import ReferenceRequest, ReferenceResponse
from lsap_schema.schema.symbol import SymbolResponse
from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestReferences,
)
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import (
    Location,
)
from lsprotocol.types import (
    Position as LSPPosition,
)
from lsprotocol.types import (
    Range as LSPRange,
)

from lsap.utils.content import SnippetReader

from lsap.utils.symbol import lookup_symbol
from .abc import Capability, Protocol
from .locate import LocateCapability
from .symbol_outline import SymbolCapability, lookup_position


@runtime_checkable
class ReferenceClient(
    WithRequestReferences,
    WithRequestDocumentSymbol,
    CapabilityClientProtocol,
    Protocol,
): ...


class ReferenceCapability(
    Capability[ReferenceClient, ReferenceRequest, ReferenceResponse]
):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(client=self.client)

    @cached_property
    def symbol(self) -> SymbolCapability:
        return SymbolCapability(client=self.client)

    async def __call__(self, req: ReferenceRequest) -> ReferenceResponse | None:
        resp = await self.locate(req)
        if not resp:
            return None

        lsp_pos = LSPPosition(
            line=resp.position.line, character=resp.position.character
        )
        ref_result = await self.client.request_references(
            file_path=req.locate.file_path,
            position=lsp_pos,
            include_declaration=True,
        )
        if not ref_result:
            return None

        items: list[SymbolResponse] = []

        async with asyncer.create_task_group() as tg:
            for loc in ref_result:
                tg.soonify(self._process_reference)(loc, items)

        return ReferenceResponse(items=items)

    async def _process_reference(
        self, loc: Location, items: list[SymbolResponse]
    ) -> None:
        file_path = self.client.from_uri(loc.uri)
        path = await lookup_position(self.client, file_path, loc.range.start)

        symbols = await self.client.request_document_symbol_list(file_path)
        reader = SnippetReader(self.client.read_file(file_path))

        if path and symbols and (target := lookup_symbol(symbols, path)):
            snippet = reader.read(target.range)
        else:
            # Fallback to the line of the reference if no symbol found or snippet empty
            snippet = reader.read(
                LSPRange(
                    start=LSPPosition(line=loc.range.start.line, character=0),
                    end=LSPPosition(line=loc.range.start.line + 1, character=0),
                )
            )

        if not snippet:
            return

        items.append(
            SymbolResponse(
                file_path=file_path,
                symbol_path=path,
                symbol_content=snippet.content,
            )
        )
