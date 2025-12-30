from __future__ import annotations

from typing import Protocol, override, runtime_checkable

import asyncer
from attrs import Factory, define
from lsap_schema.types import SymbolKind
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
from lsprotocol.types import SymbolInformation, WorkspaceSymbol

from lsap.abc import Capability
from lsap.utils.cache import PaginationCache
from lsap.utils.content import DocumentReader
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
                    tg.soonify(self._process_symbol)(symbol, req, items)

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
        req: WorkspaceSymbolRequest,
        items: list[WorkspaceSymbolItem],
    ) -> None:
        location = symbol.location
        uri = location.uri
        range_ = getattr(location, "range", None)

        file_path = self.client.from_uri(uri)
        container_name = getattr(symbol, "container_name", None)

        hover_text = None
        if req.include_hover and range_:
            if hover := await self.client.request_hover(file_path, range_.start):
                hover_text = hover.value

        symbol_content = None
        if req.include_code and range_:
            doc_content = await self.client.read_file(file_path)
            reader = DocumentReader(doc_content)
            if snippet := reader.read(range_):
                symbol_content = snippet.content

        symbol_path = []
        if range_:
            if doc_symbols := await self.client.request_document_symbol_list(file_path):
                if match := symbol_at(doc_symbols, range_.start):
                    symbol_path, _ = match

        items.append(
            WorkspaceSymbolItem(
                file_path=file_path,
                name=symbol.name,
                kind=SymbolKind.from_lsp(symbol.kind),
                container_name=container_name,
                detail=getattr(symbol, "detail", None),
                path=symbol_path,
                hover=hover_text,
                code=symbol_content,
            )
        )
