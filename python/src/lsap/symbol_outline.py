from typing import Protocol, override

from asyncer import create_task_group
from lsap_schema.locate import Position, Range
from lsap_schema.symbol_outline import SymbolOutlineRequest, SymbolOutlineResponse
from lsp_client.capability.request import WithRequestDocumentSymbol, WithRequestHover
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import DocumentSymbol

from lsap.abc import Capability
from lsap.utils.content import DocumentReader
from lsap.utils.symbol import iter_symbols


class SymbolOutlineClient(
    WithRequestDocumentSymbol,
    WithRequestHover,
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

        document = await self.client.read_file(req.file_path)
        reader = DocumentReader(document) if req.include_code else None
        items: list[SymbolOutlineItem] = []

        async def fill_hover(it: SymbolOutlineItem, sym: DocumentSymbol) -> None:
            if hover := await self.client.request_hover(
                req.file_path, sym.selection_range.start
            ):
                it.hover = hover.value

        async with create_task_group() as tg:
            for path, symbol in iter_symbols(symbols):
                item = SymbolOutlineItem(
                    name=symbol.name,
                    kind=symbol.kind.name,
                    range=Range(
                        start=Position.from_lsp(symbol.range.start),
                        end=Position.from_lsp(symbol.range.end),
                    ),
                    level=len(path) - 1,
                )
                items.append(item)

                if reader and (snippet := reader.read(symbol.range)):
                    item.content = snippet.content

                if req.include_hover:
                    tg.soonify(fill_hover)(item, symbol)

        return SymbolOutlineResponse(file_path=req.file_path, items=items)
