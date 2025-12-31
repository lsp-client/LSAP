from functools import cached_property
from typing import Protocol, runtime_checkable

import asyncer
from attrs import Factory, define
from lsap_schema.reference import ReferenceItem, ReferenceRequest, ReferenceResponse
from lsap_schema.types import Position, Range, SymbolDetailInfo, SymbolKind
from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestImplementation,
    WithRequestReferences,
)
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import Location, LocationLink
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import Range as LSPRange

from lsap.utils.content import DocumentReader
from lsap.utils.pagination import paginate
from lsap.utils.symbol import symbol_at

from .abc import Capability
from .locate import LocateCapability
from .utils.cache import PaginationCache


@runtime_checkable
class ReferenceClient(
    WithRequestReferences,
    WithRequestImplementation,
    WithRequestDocumentSymbol,
    WithRequestHover,
    CapabilityClientProtocol,
    Protocol,
): ...


@define
class ReferenceCapability(
    Capability[ReferenceClient, ReferenceRequest, ReferenceResponse]
):
    _cache: PaginationCache[ReferenceItem] = Factory(PaginationCache)

    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(client=self.client)

    async def __call__(self, req: ReferenceRequest) -> ReferenceResponse | None:
        async def fetcher() -> list[ReferenceItem] | None:
            if not (loc_resp := await self.locate(req)):
                return None

            file_path, lsp_pos = loc_resp.file_path, loc_resp.position.to_lsp()
            locations: list[Location | LocationLink] = []

            if req.mode == "references":
                if refs := await self.client.request_references(
                    file_path, lsp_pos, include_declaration=True
                ):
                    locations.extend(refs)
            elif req.mode == "implementations":
                if impls := await self.client.request_implementation(
                    file_path, lsp_pos
                ):
                    if isinstance(impls, (Location, LocationLink)):
                        locations.append(impls)
                    else:
                        locations.extend(impls)

            if not locations:
                return []

            items = []
            async with asyncer.create_task_group() as tg:
                for loc in locations:
                    tg.soonify(self._process_reference)(loc, req.context_lines, items)

            items.sort(key=lambda x: (x.file_path, x.line))
            return items

        result = await paginate(req, self._cache, fetcher)
        if result is None:
            return None

        return ReferenceResponse(
            request=req,
            items=result.items,
            start_index=req.start_index,
            max_items=req.max_items,
            total=result.total,
            has_more=result.has_more,
            pagination_id=result.pagination_id,
        )

    async def _process_reference(
        self,
        loc: Location | LocationLink,
        context_lines: int,
        items: list[ReferenceItem],
    ) -> None:
        uri, range_ = (
            (loc.target_uri, loc.target_range)
            if isinstance(loc, LocationLink)
            else (loc.uri, loc.range)
        )
        file_path = self.client.from_uri(uri)
        content = await self.client.read_file(file_path)
        reader = DocumentReader(content)

        line = range_.start.line
        context_range = LSPRange(
            start=LSPPosition(line=max(0, line - context_lines), character=0),
            end=LSPPosition(line=line + context_lines + 1, character=0),
        )
        if not (snippet := reader.read(context_range)):
            return

        symbol: SymbolDetailInfo | None = None
        if symbols := await self.client.request_document_symbol_list(file_path):
            if match := symbol_at(symbols, range_.start):
                path, sym = match
                kind = SymbolKind.from_lsp(sym.kind)

                symbol = SymbolDetailInfo(
                    file_path=file_path,
                    name=sym.name,
                    path=path,
                    kind=kind,
                    detail=sym.detail or "",
                    hover="",
                    range=Range(
                        start=Position.from_lsp(sym.range.start),
                        end=Position.from_lsp(sym.range.end),
                    ),
                )
                if hover := await self.client.request_hover(file_path, range_.start):
                    symbol.hover = hover.value

        items.append(
            ReferenceItem(
                file_path=file_path,
                line=line + 1,
                code=snippet.content,
                symbol=symbol,
            )
        )
