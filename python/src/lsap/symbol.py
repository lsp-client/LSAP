from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, override

from lsap_schema.symbol import SymbolRequest, SymbolResponse
from lsap_schema.types import SymbolKind
from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestHover,
)
from lsp_client.protocol import CapabilityClientProtocol

from lsap.abc import Capability
from lsap.locate import LocateCapability
from lsap.utils.content import DocumentReader
from lsap.utils.symbol import symbol_at

from lsprotocol.types import Position as LSPPosition


class SymbolClient(
    WithRequestDocumentSymbol,
    WithRequestHover,
    CapabilityClientProtocol,
    Protocol,
): ...


class SymbolCapability(Capability[SymbolClient, SymbolRequest, SymbolResponse]):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(self.client)

    @override
    async def __call__(self, req: SymbolRequest) -> SymbolResponse | None:
        location = await self.locate(req)
        if not location:
            return None

        file_path = location.file_path
        lsp_pos = location.position.to_lsp()

        return await self.resolve(
            file_path,
            lsp_pos,
            include_hover=req.include_hover,
            include_code=req.include_code,
        )

    async def resolve(
        self,
        file_path: Path,
        lsp_pos: LSPPosition,
        include_hover: bool = True,
        include_code: bool = True,
    ) -> SymbolResponse | None:
        symbols = await self.client.request_document_symbol_list(file_path)
        if not symbols:
            return None

        match = symbol_at(symbols, lsp_pos)
        if not match:
            return None

        symbol_path, symbol = match

        hover_text = None
        if include_hover:
            if hover := await self.client.request_hover(file_path, lsp_pos):
                hover_text = hover.value

        symbol_content = None
        if include_code:
            doc_content = await self.client.read_file(file_path)
            reader = DocumentReader(doc_content)
            if snippet := reader.read(symbol.range):
                symbol_content = snippet.content

        return SymbolResponse(
            file_path=file_path,
            name=symbol.name,
            path=symbol_path,
            kind=SymbolKind.from_lsp(symbol.kind),
            detail=symbol.detail,
            hover=hover_text,
            code=symbol_content,
        )
