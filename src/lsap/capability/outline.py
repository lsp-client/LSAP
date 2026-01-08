from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import override

import asyncer
from attrs import define
from lsp_client.capability.request import WithRequestDocumentSymbol, WithRequestHover
from lsprotocol.types import DocumentSymbol
from lsprotocol.types import Position as LSPPosition

from lsap.schema.models import Position, Range, SymbolDetailInfo, SymbolKind
from lsap.schema.outline import OutlineRequest, OutlineResponse
from lsap.schema.types import SymbolPath
from lsap.utils.capability import ensure_capability
from lsap.utils.symbol import iter_symbols

from .abc import Capability


@define
class OutlineCapability(Capability[OutlineRequest, OutlineResponse]):
    @override
    async def __call__(self, req: OutlineRequest) -> OutlineResponse | None:
        symbols = await ensure_capability(
            self.client, WithRequestDocumentSymbol
        ).request_document_symbol_list(req.file_path)
        if symbols is None:
            return None

        items = await self.resolve_symbols(
            req.file_path,
            iter_symbols(symbols),
        )

        return OutlineResponse(file_path=req.file_path, items=items)

    async def resolve_symbols(
        self,
        file_path: Path,
        symbols_with_path: Iterable[tuple[SymbolPath, DocumentSymbol]],
    ) -> list[SymbolDetailInfo]:
        items: list[SymbolDetailInfo] = []
        async with asyncer.create_task_group() as tg:
            for path, symbol in symbols_with_path:
                item = self._make_item(file_path, path, symbol)
                items.append(item)
                tg.soonify(self._fill_hover)(item, symbol.selection_range.start)

        return items

    def _make_item(
        self,
        file_path: Path,
        path: SymbolPath,
        symbol: DocumentSymbol,
    ) -> SymbolDetailInfo:
        return SymbolDetailInfo(
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

    async def _fill_hover(self, item: SymbolDetailInfo, pos: LSPPosition) -> None:
        if hover := await ensure_capability(
            self.client, WithRequestHover
        ).request_hover(item.file_path, pos):
            item.hover = hover.value
