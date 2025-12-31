from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol, override, runtime_checkable

import asyncer
from attrs import define
from lsap_schema.symbol_outline import SymbolOutlineRequest, SymbolOutlineResponse
from lsap_schema.types import Position, Range, SymbolInfo, SymbolKind, SymbolPath
from lsp_client.capability.request import WithRequestDocumentSymbol, WithRequestHover
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import DocumentSymbol, Position as LSPPosition

from lsap.abc import Capability
from lsap.utils.content import DocumentReader
from lsap.utils.symbol import iter_symbols


@runtime_checkable
class SymbolOutlineClient(
    WithRequestDocumentSymbol,
    WithRequestHover,
    CapabilityClientProtocol,
    Protocol,
): ...


@define
class SymbolOutlineCapability(
    Capability[SymbolOutlineClient, SymbolOutlineRequest, SymbolOutlineResponse]
):
    @override
    async def __call__(self, req: SymbolOutlineRequest) -> SymbolOutlineResponse | None:
        symbols = await self.client.request_document_symbol_list(req.file_path)
        if symbols is None:
            return None

        items = await self.resolve_symbols(
            req.file_path,
            iter_symbols(symbols),
            include_hover=req.include_hover,
            include_code=req.include_code,
        )

        return SymbolOutlineResponse(file_path=req.file_path, items=items)

    async def resolve_symbols(
        self,
        file_path: Path,
        symbols_with_path: Iterable[tuple[SymbolPath, DocumentSymbol]],
        include_hover: bool = True,
        include_code: bool = True,
    ) -> list[SymbolInfo]:
        reader = None
        if include_code:
            document = await self.client.read_file(file_path)
            reader = DocumentReader(document)

        items: list[SymbolInfo] = []
        async with asyncer.create_task_group() as tg:
            for path, symbol in symbols_with_path:
                item = self._make_item(file_path, path, symbol, reader)
                items.append(item)

                if include_hover:
                    tg.soonify(self._fill_hover)(item, symbol.selection_range.start)

        return items

    def _make_item(
        self,
        file_path: Path,
        path: SymbolPath,
        symbol: DocumentSymbol,
        reader: DocumentReader | None,
    ) -> SymbolInfo:
        item = SymbolInfo(
            file_path=file_path,
            name=symbol.name,
            path=path,
            kind=SymbolKind.from_lsp(symbol.kind),
            detail=symbol.detail,
            range=Range(
                start=Position.from_lsp(symbol.range.start),
                end=Position.from_lsp(symbol.range.end),
            ),
        )

        if reader and (snippet := reader.read(symbol.range)):
            item.code = snippet.content

        return item

    async def _fill_hover(self, item: SymbolInfo, pos: LSPPosition) -> None:
        if hover := await self.client.request_hover(item.file_path, pos):
            item.hover = hover.value
