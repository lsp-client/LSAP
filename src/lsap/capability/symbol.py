from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import override

from attrs import define
from lsp_client.capability.request import (
    WithRequestCallHierarchy,
    WithRequestDocumentSymbol,
)
from lsprotocol.types import Position as LSPPosition

from lsap.schema.models import (
    CallHierarchy,
    CallHierarchyItem,
    Range,
    SymbolCodeInfo,
    SymbolKind,
)
from lsap.schema.symbol import SymbolRequest, SymbolResponse
from lsap.utils.capability import ensure_capability, get_capability
from lsap.utils.document import DocumentReader
from lsap.utils.symbol import symbol_at

from .abc import Capability
from .locate import LocateCapability
from .outline import OutlineCapability


@define
class SymbolCapability(Capability[SymbolRequest, SymbolResponse]):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(self.client)

    @cached_property
    def outline(self) -> OutlineCapability:
        return OutlineCapability(self.client)

    @override
    async def __call__(self, req: SymbolRequest) -> SymbolResponse | None:
        location = await self.locate(req)
        if not location:
            return None

        lsp_pos = location.position.to_lsp()
        best_match = await self.resolve(
            location.file_path,
            lsp_pos,
        )

        if not best_match:
            return None

        call_hierarchy = await self._get_call_hierarchy(location.file_path, lsp_pos)

        return SymbolResponse(
            info=best_match,
            call_hierarchy=call_hierarchy,
        )

    async def _get_call_hierarchy(
        self, file_path: Path, pos: LSPPosition
    ) -> CallHierarchy | None:
        cap = get_capability(self.client, WithRequestCallHierarchy)
        if not cap:
            return None

        incoming = await cap.request_call_hierarchy_incoming_call(file_path, pos)
        outgoing = await cap.request_call_hierarchy_outgoing_call(file_path, pos)

        incoming = [
            CallHierarchyItem(
                file_path=self.client.from_uri(call.from_.uri, relative=False),
                name=call.from_.name,
                kind=SymbolKind.from_lsp(call.from_.kind),
                range=Range.from_lsp(call.from_.range),
            )
            for call in incoming or []
        ]

        outgoing = [
            CallHierarchyItem(
                file_path=self.client.from_uri(call.to.uri, relative=False),
                name=call.to.name,
                kind=SymbolKind.from_lsp(call.to.kind),
                range=Range.from_lsp(call.to.range),
            )
            for call in outgoing or []
        ]

        return CallHierarchy(incoming=incoming, outgoing=outgoing)

    async def resolve(
        self,
        file_path: Path,
        pos: LSPPosition,
    ) -> SymbolCodeInfo | None:
        symbols = await ensure_capability(
            self.client, WithRequestDocumentSymbol
        ).request_document_symbol_list(file_path)
        if not symbols:
            return None

        match = symbol_at(symbols, pos)
        if not match:
            return None

        path, symbol = match
        document = await self.client.read_file(file_path)
        reader = DocumentReader(document)

        code: str | None = None
        if snippet := reader.read(symbol.range):
            code = snippet.content

        return SymbolCodeInfo(
            file_path=file_path,
            name=symbol.name,
            path=path,
            kind=SymbolKind.from_lsp(symbol.kind),
            code=code,
            range=Range.from_lsp(symbol.range),
        )
