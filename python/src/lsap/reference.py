from functools import cached_property
from typing import runtime_checkable

import asyncer
from lsap_schema.reference import ReferenceRequest, ReferenceResponse
from lsap_schema.symbol import SymbolResponse
from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestHover,
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

from lsap.utils.content import DocumentReader
from lsap.utils.symbol import symbol_at

from .abc import Capability, Protocol
from .locate import LocateCapability
from .symbol import SymbolCapability


@runtime_checkable
class ReferenceClient(
    WithRequestReferences,
    WithRequestDocumentSymbol,
    WithRequestHover,
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

        return ReferenceResponse(
            items=items,
            start_index=req.start_index,
            max_items=req.max_items,
            total=len(items),
            has_more=False,
        )

    async def _process_reference(
        self, loc: Location, items: list[SymbolResponse]
    ) -> None:
        file_path = self.client.from_uri(loc.uri)
        symbols = await self.client.request_document_symbol_list(file_path)
        reader = DocumentReader(self.client.read_file(file_path))

        match = symbol_at(symbols, loc.range.start) if symbols else None

        if match:
            path, symbol = match
            snippet = reader.read(symbol.range)
        else:
            path = []
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
