from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import override

import anyio
import asyncer
from attrs import define, field
from lsp_client.capability.request import WithRequestDocumentSymbol, WithRequestHover
from lsprotocol.types import DocumentSymbol
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import SymbolKind as LSPSymbolKind

from lsap.schema.models import Range, SymbolDetailInfo, SymbolKind
from lsap.schema.outline import OutlineRequest, OutlineResponse
from lsap.schema.types import SymbolPath
from lsap.utils.capability import ensure_capability
from lsap.utils.markdown import clean_hover_content
from lsap.utils.symbol import iter_symbols

from .abc import Capability


@define
class OutlineCapability(Capability[OutlineRequest, OutlineResponse]):
    hover_sem: anyio.Semaphore = field(default=anyio.Semaphore(32), init=False)

    @override
    async def __call__(self, req: OutlineRequest) -> OutlineResponse | None:
        symbols = await ensure_capability(
            self.client, WithRequestDocumentSymbol
        ).request_document_symbol_list(req.file_path)
        if symbols is None:
            return None

        if req.scope:
            target_path = req.scope.symbol_path
            matched = [
                (path, symbol)
                for path, symbol in iter_symbols(symbols)
                if path == target_path
            ]
            if not matched:
                return OutlineResponse(file_path=req.file_path, items=[])

            symbols_iter: list[tuple[SymbolPath, DocumentSymbol]] = []
            for path, symbol in matched:
                if req.top:
                    symbols_iter.extend(self._iter_top_symbols([symbol], path[:-1]))
                else:
                    symbols_iter.extend(
                        self._iter_filtered_symbols([symbol], None, path[:-1])
                    )
        elif req.top:
            symbols_iter = list(self._iter_top_symbols(symbols))
        else:
            # Filter symbols: exclude implementation details inside functions/methods
            symbols_iter = list(self._iter_filtered_symbols(symbols))

        items = await self.resolve_symbols(req.file_path, symbols_iter)

        return OutlineResponse(file_path=req.file_path, items=items)

    def _iter_top_symbols(
        self,
        nodes: Sequence[DocumentSymbol],
        symbol_path: SymbolPath | None = None,
    ) -> Iterator[tuple[SymbolPath, DocumentSymbol]]:
        """Iterate only top-level symbols, expanding Modules."""
        if symbol_path is None:
            symbol_path = []
        for node in nodes:
            current_path = [*symbol_path, node.name]
            if node.kind == LSPSymbolKind.Module:
                if node.children:
                    yield from self._iter_top_symbols(node.children, current_path)
            else:
                yield current_path, node

    def _iter_filtered_symbols(
        self,
        nodes: Sequence[DocumentSymbol],
        parent_kind: LSPSymbolKind | None = None,
        symbol_path: SymbolPath | None = None,
    ) -> Iterator[tuple[SymbolPath, DocumentSymbol]]:
        """DFS iterate hierarchy of DocumentSymbol with filtering."""
        if symbol_path is None:
            symbol_path = []

        # If parent is a function/method, we don't yield any of its children
        if parent_kind in (
            LSPSymbolKind.Function,
            LSPSymbolKind.Method,
            LSPSymbolKind.Constructor,
            LSPSymbolKind.Operator,
        ):
            return

        for node in nodes:
            current_path = [*symbol_path, node.name]
            yield current_path, node

            if node.children:
                yield from self._iter_filtered_symbols(
                    node.children, node.kind, current_path
                )

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
            range=Range.from_lsp(symbol.range),
        )

    async def _fill_hover(self, item: SymbolDetailInfo, pos: LSPPosition) -> None:
        async with self.hover_sem:
            if hover := await ensure_capability(
                self.client, WithRequestHover
            ).request_hover(item.file_path, pos):
                item.hover = clean_hover_content(hover.value)
