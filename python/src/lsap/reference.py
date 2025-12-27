from functools import cached_property
from typing import runtime_checkable

import asyncer
from lsap_schema.reference import ReferenceItem, ReferenceRequest, ReferenceResponse
from lsap_schema.types import SymbolInfo, SymbolKind
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
from lsap.utils.symbol import symbol_at

from .abc import Capability, Protocol
from .locate import LocateCapability


@runtime_checkable
class ReferenceClient(
    WithRequestReferences,
    WithRequestImplementation,
    WithRequestDocumentSymbol,
    WithRequestHover,
    CapabilityClientProtocol,
    Protocol,
): ...


class ReferenceCapability(
    Capability[ReferenceClient, ReferenceRequest, ReferenceResponse]
):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(client=self.client)

    async def __call__(self, req: ReferenceRequest) -> ReferenceResponse | None:
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
            if impls := await self.client.request_implementation(file_path, lsp_pos):
                if isinstance(impls, (Location, LocationLink)):
                    locations.append(impls)
                else:
                    locations.extend(impls)

        if not locations:
            return ReferenceResponse(
                request=req,
                items=[],
                start_index=req.start_index,
                max_items=req.max_items,
                total=0,
                has_more=False,
            )

        items: list[ReferenceItem] = []
        async with asyncer.create_task_group() as tg:
            for loc in locations:
                tg.soonify(self._process_reference)(loc, req.context_lines, items)

        items.sort(key=lambda x: (x.file_path, x.line))
        total, start, limit = len(items), req.start_index, req.max_items
        paginated = items[start : start + limit] if limit is not None else items[start:]

        return ReferenceResponse(
            request=req,
            items=paginated,
            start_index=start,
            max_items=limit,
            total=total,
            has_more=(start + len(paginated)) < total,
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

        symbol: SymbolInfo | None = None
        if symbols := await self.client.request_document_symbol_list(file_path):
            if match := symbol_at(symbols, range_.start):
                path, sym = match
                kind = SymbolKind.from_lsp(sym.kind)

                symbol = SymbolInfo(
                    file_path=file_path,
                    name=sym.name,
                    path=path,
                    kind=kind,
                    detail=sym.detail,
                )

        items.append(
            ReferenceItem(
                file_path=file_path,
                line=line + 1,
                code=snippet.content,
                symbol=symbol,
            )
        )
