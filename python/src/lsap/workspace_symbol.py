from __future__ import annotations

from functools import cached_property
from typing import Protocol, override, runtime_checkable

import asyncer
from attrs import Factory, define
from lsap_schema.types import SymbolDetailInfo, SymbolKind
from lsap_schema.workspace_symbol import (
    WorkspaceSymbolItem,
    WorkspaceSymbolRequest,
    WorkspaceSymbolResponse,
)
from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestWorkspaceSymbol,
)
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import Location, SymbolInformation, WorkspaceSymbol

from lsap.abc import Capability
from lsap.symbol_outline import SymbolOutlineCapability
from lsap.utils.cache import PaginationCache
from lsap.utils.pagination import paginate
from lsap.utils.symbol import symbol_at


@runtime_checkable
class WorkspaceSymbolClient(
    WithRequestWorkspaceSymbol,
    WithRequestDocumentSymbol,
    WithRequestHover,
    CapabilityClientProtocol,
    Protocol,
): ...


@define
class WorkspaceSymbolCapability(
    Capability[WorkspaceSymbolClient, WorkspaceSymbolRequest, WorkspaceSymbolResponse]
):
    _cache: PaginationCache[WorkspaceSymbolItem] = Factory(PaginationCache)

    @cached_property
    def outline(self) -> SymbolOutlineCapability:
        return SymbolOutlineCapability(self.client)

    @override
    async def __call__(
        self, req: WorkspaceSymbolRequest
    ) -> WorkspaceSymbolResponse | None:
        async def fetcher() -> list[WorkspaceSymbolItem] | None:
            symbols = await self.client.request_workspace_symbol(req.query)
            if symbols is None:
                return None

            items = []
            async with asyncer.create_task_group() as tg:
                for symbol in symbols:
                    tg.soonify(self._process_symbol)(symbol, items)

            items.sort(key=lambda x: (x.name, x.file_path))
            return items

        result = await paginate(req, self._cache, fetcher)
        if result is None:
            return None

        return WorkspaceSymbolResponse(
            request=req,
            items=result.items,
            start_index=req.start_index,
            max_items=req.max_items,
            total=result.total,
            has_more=result.has_more,
            pagination_id=result.pagination_id,
        )

    async def _process_symbol(
        self,
        symbol: SymbolInformation | WorkspaceSymbol,
        items: list[WorkspaceSymbolItem],
    ) -> None:
        location = symbol.location
        file_path = self.client.from_uri(location.uri)
        range_ = location.range if isinstance(location, Location) else None

        info: SymbolDetailInfo | None = None
        if range_:
            symbols = await self.client.request_document_symbol_list(file_path)
            if symbols and (match := symbol_at(symbols, range_.start)):
                path, sym = match
                details = await self.outline.resolve_symbols(file_path, [(path, sym)])
                if details:
                    info = details[0]

        if info:
            items.append(
                WorkspaceSymbolItem(
                    **info.model_dump(),
                    container_name=symbol.container_name,
                )
            )
        else:
            items.append(
                WorkspaceSymbolItem(
                    file_path=file_path,
                    name=symbol.name,
                    kind=SymbolKind.from_lsp(symbol.kind),
                    container_name=symbol.container_name,
                    path=[],
                    detail="",
                    hover="",
                )
            )
