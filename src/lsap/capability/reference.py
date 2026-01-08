from functools import cached_property

import asyncer
from attrs import Factory, define
from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestImplementation,
    WithRequestReferences,
)
from lsprotocol.types import Location
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import Range as LSPRange

from lsap.schema.models import Location as LSAPLocation
from lsap.schema.models import Position, Range, SymbolDetailInfo, SymbolKind
from lsap.schema.reference import ReferenceItem, ReferenceRequest, ReferenceResponse
from lsap.utils.cache import PaginationCache
from lsap.utils.capability import ensure_capability
from lsap.utils.document import DocumentReader
from lsap.utils.pagination import paginate
from lsap.utils.symbol import symbol_at

from .abc import Capability
from .locate import LocateCapability


@define
class ReferenceCapability(Capability[ReferenceRequest, ReferenceResponse]):
    _cache: PaginationCache[ReferenceItem] = Factory(PaginationCache)

    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(client=self.client)

    async def __call__(self, req: ReferenceRequest) -> ReferenceResponse | None:
        async def fetcher() -> list[ReferenceItem] | None:
            if not (loc_resp := await self.locate(req)):
                return None

            file_path, lsp_pos = loc_resp.file_path, loc_resp.position.to_lsp()
            locations: list[Location] = []

            if req.mode == "references":
                if refs := await ensure_capability(
                    self.client, WithRequestReferences
                ).request_references(file_path, lsp_pos, include_declaration=True):
                    locations.extend(refs)
            elif req.mode == "implementations":
                if impls := await ensure_capability(
                    self.client,
                    WithRequestImplementation,
                    error="To find implementations, you can: "
                    "1) Use 'references' mode to find all usages (often including implementations); "
                    "2) Find the symbol definition and then search for its references; "
                    "3) Use 'search' or 'symbol' capability to find name-matched definitions.",
                ).request_implementation_locations(file_path, lsp_pos):
                    locations.extend(impls)

            if not locations:
                return []

            items = []
            async with asyncer.create_task_group() as tg:
                for loc in locations:
                    tg.soonify(self._process_reference)(loc, req.context_lines, items)

            items.sort(
                key=lambda x: (x.location.file_path, x.location.range.start.line)
            )
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
        loc: Location,
        context_lines: int,
        items: list[ReferenceItem],
    ) -> None:
        file_path = self.client.from_uri(loc.uri)
        content = await self.client.read_file(file_path)
        reader = DocumentReader(content)

        range = loc.range
        line = range.start.line
        context_range = LSPRange(
            start=LSPPosition(line=max(0, line - context_lines), character=0),
            end=LSPPosition(line=line + context_lines + 1, character=0),
        )
        if not (snippet := reader.read(context_range)):
            return

        symbol: SymbolDetailInfo | None = None
        if symbols := await ensure_capability(
            self.client, WithRequestDocumentSymbol
        ).request_document_symbol_list(file_path):
            if match := symbol_at(symbols, range.start):
                path, sym = match
                kind = SymbolKind.from_lsp(sym.kind)

                symbol = SymbolDetailInfo(
                    file_path=file_path,
                    name=sym.name,
                    path=path,
                    kind=kind,
                    detail=sym.detail,
                    range=Range(
                        start=Position.from_lsp(sym.range.start),
                        end=Position.from_lsp(sym.range.end),
                    ),
                )

                if hover := await ensure_capability(
                    self.client, WithRequestHover
                ).request_hover(file_path, range.start):
                    symbol.hover = hover.value

        items.append(
            ReferenceItem(
                location=LSAPLocation(
                    file_path=file_path,
                    range=Range(
                        start=Position.from_lsp(range.start),
                        end=Position.from_lsp(range.end),
                    ),
                ),
                code=snippet.content,
                symbol=symbol,
            )
        )
