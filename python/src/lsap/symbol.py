from __future__ import annotations

from functools import cached_property
from typing import Protocol, override

from attrs import define
from lsap_schema.symbol import SymbolRequest, SymbolResponse
from lsap_schema.symbol_outline import SymbolOutlineRequest
from lsap_schema.types import SymbolInfo
from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestHover,
)
from lsp_client.protocol import CapabilityClientProtocol

from lsap.abc import Capability
from lsap.locate import LocateCapability

from .symbol_outline import SymbolOutlineCapability


class SymbolClient(
    WithRequestDocumentSymbol,
    WithRequestHover,
    CapabilityClientProtocol,
    Protocol,
): ...


@define
class SymbolCapability(Capability[SymbolClient, SymbolRequest, SymbolResponse]):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(self.client)

    @cached_property
    def outline(self) -> SymbolOutlineCapability:
        return SymbolOutlineCapability(self.client)

    @override
    async def __call__(self, req: SymbolRequest) -> SymbolResponse | None:
        location = await self.locate(req)
        if not location:
            return None

        file_path = location.file_path

        outline = await self.outline(
            SymbolOutlineRequest(
                file_path=file_path,
                include_hover=req.include_hover,
                include_code=req.include_code,
            )
        )
        if not outline:
            return None

        # Find the most specific symbol containing the position
        best_match: SymbolInfo | None = None

        for item in outline.items:
            if not item.range:
                continue

            start = item.range.start
            end = item.range.end
            pos = location.position

            # (start.line, start.character) <= (pos.line, pos.character) < (end.line, end.character)
            if (
                (start.line, start.character)
                <= (pos.line, pos.character)
                < (end.line, end.character)
            ):
                if best_match is None or not best_match.range:
                    best_match = item
                else:
                    # Check if narrower
                    i_s, i_e = item.range.start, item.range.end
                    b_s, b_e = best_match.range.start, best_match.range.end

                    if (i_s.line, i_s.character) >= (b_s.line, b_s.character) and (
                        i_e.line,
                        i_e.character,
                    ) <= (b_e.line, b_e.character):
                        best_match = item

        if not best_match:
            return None

        return SymbolResponse(**best_match.model_dump())
