from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Protocol, override, runtime_checkable

from attrs import define
from lsap_schema.models import Position, Range, SymbolCodeInfo, SymbolKind
from lsap_schema.symbol import SymbolRequest, SymbolResponse
from lsp_client.capability.request import WithRequestDocumentSymbol, WithRequestHover
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import Position as LSPPosition

from lsap.abc import Capability
from lsap.locate import LocateCapability
from lsap.utils.document import DocumentReader
from lsap.utils.symbol import symbol_at

from .symbol_outline import SymbolOutlineCapability


@runtime_checkable
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

        best_match = await self.resolve(
            location.file_path,
            location.position.to_lsp(),
        )

        if not best_match:
            return None

        return SymbolResponse(**best_match.model_dump())

    async def resolve(
        self,
        file_path: Path,
        pos: LSPPosition,
    ) -> SymbolCodeInfo | None:
        symbols = await self.client.request_document_symbol_list(file_path)
        if not symbols:
            return None

        match = symbol_at(symbols, pos)
        if not match:
            return None

        path, symbol = match
        document = await self.client.read_file(file_path)
        reader = DocumentReader(document)

        code = ""
        if snippet := reader.read(symbol.range):
            code = snippet.content

        return SymbolCodeInfo(
            file_path=file_path,
            name=symbol.name,
            path=path,
            kind=SymbolKind.from_lsp(symbol.kind),
            code=code,
            range=Range(
                start=Position.from_lsp(symbol.range.start),
                end=Position.from_lsp(symbol.range.end),
            ),
        )
