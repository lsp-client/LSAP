from typing import Protocol, override

import asyncer
from lsap_schema.symbol_outline import SymbolOutlineRequest, SymbolOutlineResponse
from lsap_schema.types import SymbolInfo, SymbolKind
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
        items: list[SymbolInfo] = []

        async def fill_hover(it: SymbolInfo, sym: DocumentSymbol) -> None:
            if hover := await self.client.request_hover(
                req.file_path, sym.selection_range.start
            ):
                it.hover = hover.value

        async with asyncer.create_task_group() as tg:
            for path, symbol in iter_symbols(symbols):
                item = SymbolInfo(
                    file_path=req.file_path,
                    name=symbol.name,
                    path=path,
                    kind=SymbolKind.from_lsp(symbol.kind),
                    detail=symbol.detail,
                )
                items.append(item)

                if reader and (snippet := reader.read(symbol.range)):
                    item.code = snippet.content

                if req.include_hover:
                    tg.soonify(fill_hover)(item, symbol)

        return SymbolOutlineResponse(file_path=req.file_path, items=items)
