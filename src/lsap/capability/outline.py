from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import override

import anyio
import asyncer
from attrs import define, field
from loguru import logger
from lsp_client.capability.request import WithRequestDocumentSymbol, WithRequestHover
from lsprotocol.types import DocumentSymbol
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import SymbolKind as LSPSymbolKind

from lsap.schema.models import Range, SymbolDetailInfo, SymbolKind
from lsap.schema.outline import (
    OutlineFileGroup,
    OutlineFileItem,
    OutlineRequest,
    OutlineResponse,
)
from lsap.schema.types import SymbolPath
from lsap.utils.capability import ensure_capability
from lsap.utils.markdown import clean_hover_content
from lsap.utils.symbol import iter_symbols

from .abc import Capability

# Common directories to exclude for performance in recursive scans
_EXCLUDED_DIRS = frozenset(
    {
        "node_modules",
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        ".tox",
        "dist",
        "build",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
)


@define
class OutlineCapability(Capability[OutlineRequest, OutlineResponse]):
    hover_sem: anyio.Semaphore = field(default=anyio.Semaphore(32), init=False)
    directory_sem: anyio.Semaphore = field(default=anyio.Semaphore(10), init=False)

    @override
    async def __call__(self, req: OutlineRequest) -> OutlineResponse | None:
        # Check if path is a directory - this implicitly checks existence
        # for directories while allowing mock file paths in tests
        try:
            is_dir = req.path.is_dir()
        except OSError:
            # If we can't determine if it's a directory, treat as file
            is_dir = False

        if is_dir:
            if req.scope is not None:
                raise ValueError("scope cannot be used with directory paths")
            return await self._handle_directory(req)
        return await self._handle_file(req)

    async def _handle_directory(self, req: OutlineRequest) -> OutlineResponse | None:
        directory = req.path

        lang_config = self.client.get_language_config()
        code_files: list[Path] = []

        if req.recursive:
            for suffix in lang_config.suffixes:
                code_files.extend(
                    file_path
                    for file_path in directory.rglob(f"*{suffix}")
                    if not any(
                        excluded in file_path.parts for excluded in _EXCLUDED_DIRS
                    )
                )
        else:
            for suffix in lang_config.suffixes:
                code_files.extend(directory.glob(f"*{suffix}"))

        code_files = sorted(set(code_files), key=lambda p: str(p))

        file_groups: list[OutlineFileGroup] = []
        total_symbols = 0

        async with asyncer.create_task_group() as tg:
            for file_path in code_files:
                _ = tg.soonify(self._process_file_for_directory)(file_path, file_groups)

        for group in file_groups:
            total_symbols += len(group.symbols)

        file_groups.sort(key=lambda g: str(g.file_path))

        return OutlineResponse(
            path=directory,
            is_directory=True,
            files=file_groups,
            total_files=len(file_groups),
            total_symbols=total_symbols,
        )

    async def _process_file_for_directory(
        self,
        file_path: Path,
        file_groups: list[OutlineFileGroup],
    ) -> None:
        async with self.directory_sem:
            try:
                symbols = await ensure_capability(
                    self.client, WithRequestDocumentSymbol
                ).request_document_symbol_list(file_path)

                symbols_iter = self._iter_top_symbols(symbols) if symbols else []
                items = [
                    OutlineFileItem(
                        file_path=file_path,
                        name=symbol.name,
                        path=path,
                        kind=SymbolKind.from_lsp(symbol.kind),
                        detail=symbol.detail,
                        range=Range.from_lsp(symbol.range),
                    )
                    for path, symbol in symbols_iter
                ]

                file_groups.append(OutlineFileGroup(file_path=file_path, symbols=items))
            except Exception as e:  # noqa: BLE001
                # Skip files that fail to process (e.g., syntax errors, LSP issues)
                # Continue processing other files to avoid partial failure
                logger.debug(
                    f"Failed to process file {file_path} in directory outline: {e}"
                )

    async def _handle_file(self, req: OutlineRequest) -> OutlineResponse | None:
        file_path = req.path
        symbols = await ensure_capability(
            self.client, WithRequestDocumentSymbol
        ).request_document_symbol_list(file_path)
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
                return OutlineResponse(path=file_path, is_directory=False, items=[])

            symbols_iter: list[tuple[SymbolPath, DocumentSymbol]] = []
            for path, symbol in matched:
                if req.recursive:
                    symbols_iter.extend(
                        self._iter_filtered_symbols([symbol], None, path[:-1])
                    )
                else:
                    symbols_iter.extend(self._iter_top_symbols([symbol], path[:-1]))
        elif req.recursive:
            symbols_iter = list(self._iter_filtered_symbols(symbols))
        else:
            symbols_iter = list(self._iter_top_symbols(symbols))

        items = await self.resolve_symbols(file_path, symbols_iter)

        return OutlineResponse(path=file_path, is_directory=False, items=items)

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
