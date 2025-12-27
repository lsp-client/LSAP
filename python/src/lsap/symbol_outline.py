from typing import Protocol, override

from lsap_schema.locate import Position, Range
from lsap_schema.symbol_outline import (
    SymbolOutlineItem,
    SymbolOutlineRequest,
    SymbolOutlineResponse,
)
from lsp_client.capability.request import WithRequestDocumentSymbol
from lsp_client.protocol import CapabilityClientProtocol

from lsap.abc import Capability
from lsap.utils.content import DocumentReader
from lsap.utils.symbol import iter_symbols


class SymbolOutlineClient(
    WithRequestDocumentSymbol,
    CapabilityClientProtocol,
    Protocol,
): ...


class SymbolOutlineCapability(
    Capability[SymbolOutlineClient, SymbolOutlineRequest, SymbolOutlineResponse]
):
    @override
    async def __call__(self, req: SymbolOutlineRequest) -> SymbolOutlineResponse | None:
        symbols = await self.client.request_document_symbol_list(req.file_path)
        if symbols is None:
            return None

        reader = DocumentReader(self.client.read_file(req.file_path))
        items: list[SymbolOutlineItem] = []

        for path, symbol in iter_symbols(symbols):
            symbol_content: str | None = None
            if symbol.name in req.display_code_for:
                snippet = reader.read(symbol.range)
                if snippet:
                    symbol_content = snippet.content

            items.append(
                SymbolOutlineItem(
                    name=symbol.name,
                    kind=symbol.kind.name,
                    range=Range(
                        start=Position.from_lsp(symbol.range.start),
                        end=Position.from_lsp(symbol.range.end),
                    ),
                    level=len(path) - 1,
                    symbol_content=symbol_content,
                )
            )

        return SymbolOutlineResponse(file_path=req.file_path, items=items)
