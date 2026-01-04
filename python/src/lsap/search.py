from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, override, runtime_checkable

from attrs import Factory, define
from lsap_schema.models import SymbolKind
from lsap_schema.search import (
    SearchItem,
    SearchRequest,
    SearchResponse,
)
from lsp_client.capability.request import WithRequestWorkspaceSymbol
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import Location, WorkspaceSymbol

from lsap.abc import Capability
from lsap.utils.cache import PaginationCache
from lsap.utils.pagination import paginate


@runtime_checkable
class SearchClient(
    WithRequestWorkspaceSymbol,
    CapabilityClientProtocol,
    Protocol,
): ...


@define
class SearchCapability(Capability[SearchClient, SearchRequest, SearchResponse]):
    _symbol_cache: PaginationCache[WorkspaceSymbol] = Factory(PaginationCache)

    @override
    async def __call__(self, req: SearchRequest) -> SearchResponse | None:
        async def fetcher() -> list[WorkspaceSymbol] | None:
            symbols = await self.client.request_workspace_symbol_list(req.query)
            if symbols is None:
                return None

            filtered = symbols
            if req.kinds:
                kind_set = {k.name for k in req.kinds}
                filtered = [s for s in symbols if s.kind.name in kind_set]

            items = sorted(filtered, key=lambda x: (x.name, x.location.uri))
            return list(items)

        result = await paginate(req, self._symbol_cache, fetcher)
        if result is None:
            return None

        items = self._to_search_items(result.items)

        return SearchResponse(
            request=req,
            items=items,
            start_index=req.start_index,
            max_items=req.max_items,
            total=result.total,
            has_more=result.has_more,
            pagination_id=result.pagination_id,
        )

    def _to_search_items(self, symbols: Sequence[WorkspaceSymbol]) -> list[SearchItem]:
        items = []
        for symbol in symbols:
            location = symbol.location
            if not isinstance(location, Location):
                continue

            items.append(
                SearchItem(
                    name=symbol.name,
                    kind=SymbolKind.from_lsp(symbol.kind),
                    file_path=self.client.from_uri(location.uri),
                    line=location.range.start.line + 1,
                    container=symbol.container_name,
                )
            )
        return items
