from functools import cached_property
from typing import Protocol, override

from lsap_schema.symbol import SymbolRequest, SymbolResponse
from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestHover,
)
from lsp_client.protocol import CapabilityClientProtocol

from lsap.abc import Capability
from lsap.locate import LocateCapability
from lsap.utils.content import DocumentReader
from lsap.utils.symbol import symbol_at


class SymbolClient(
    WithRequestDocumentSymbol,
    WithRequestHover,
    CapabilityClientProtocol,
    Protocol,
): ...


class SymbolCapability(Capability[SymbolClient, SymbolRequest, SymbolResponse]):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(self.client)

    @override
    async def __call__(self, req: SymbolRequest) -> SymbolResponse | None:
        location = await self.locate(req)
        if not location:
            return None

        file_path = location.file_path
        lsp_pos = location.position.to_lsp()

        symbols = await self.client.request_document_symbol_list(file_path)
        if not symbols:
            return None

        match = symbol_at(symbols, lsp_pos)
        if not match:
            return None

        symbol_path, symbol = match

        hover_text = None
        if req.include_hover:
            if hover := await self.client.request_hover(file_path, lsp_pos):
                hover_text = hover.value

        symbol_content = None
        if req.include_content:
            doc_content = self.client.read_file(file_path)
            reader = DocumentReader(doc_content)
            if snippet := reader.read(symbol.range):
                symbol_content = snippet.content

        return SymbolResponse(
            file_path=file_path,
            symbol_path=symbol_path,
            symbol_content=symbol_content,
            hover=hover_text,
        )
