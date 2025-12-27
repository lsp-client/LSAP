from collections.abc import Iterator
from functools import cached_property
from typing import Protocol, Sequence, override

from lsap_schema.abc import SymbolPath
from lsap_schema.symbol import SymbolRequest, SymbolResponse
from lsp_client.capability.request import WithRequestDocumentSymbol, WithRequestHover
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import DocumentSymbol

from lsap.abc import Capability
from lsap.locate import LocateCapability
from lsap.utils.content import DocumentReader
from lsap.utils.symbol import iter_symbols, symbol_at


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

    def iter_symbols(
        self, nodes: Sequence[DocumentSymbol]
    ) -> Iterator[tuple[SymbolPath, DocumentSymbol]]:
        return iter_symbols(nodes)

    @override
    async def __call__(self, req: SymbolRequest) -> SymbolResponse | None:
        location = await self.locate(req)
        if location is None:
            return None

        file_path = location.file_path
        position = location.position.to_lsp()

        hover: str | None = None
        if req.include_hover:
            hover_content = await self.client.request_hover(file_path, position)
            if hover_content:
                hover = hover_content.value

        symbols = await self.client.request_document_symbol_list(file_path)
        if symbols is None:
            return None

        match = symbol_at(symbols, position)
        if match is None:
            return None

        symbol_path, symbol = match
        symbol_content: str | None = None
        if req.include_content:
            reader = DocumentReader(self.client.read_file(file_path))
            snippet = reader.read(symbol.range)
            if snippet:
                symbol_content = snippet.content

        return SymbolResponse(
            file_path=file_path,
            symbol_path=symbol_path,
            symbol_content=symbol_content,
            hover=hover,
        )
