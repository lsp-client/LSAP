from functools import cached_property
from pathlib import Path
from typing import Protocol, Sequence

from lsp_client.capability.request import WithRequestDocumentSymbol
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import DocumentSymbol, Position as LSPPosition, Range as LSPRange
from lsap_schema.schema.symbol import SymbolRequest, SymbolResponse

from lsap.utils.content import SnippetReader
from lsap.utils.symbol import Symbol, SymbolPath

from .abc import Capability
from .locate import LocateCapability


class SymbolClient(
    WithRequestDocumentSymbol,
    CapabilityClientProtocol,
    Protocol,
): ...


def _contains(range: LSPRange, position: LSPPosition) -> bool:
    return (
        (range.start.line, range.start.character)
        <= (position.line, position.character)
        < (range.end.line, range.end.character)
    )


def _lookup_position(nodes: Sequence[DocumentSymbol], p: LSPPosition) -> SymbolPath:
    for n in nodes:
        if not _contains(n.range, p):
            continue
        return SymbolPath([Symbol(n.name)] + _lookup_position(n.children or [], p))
    return SymbolPath([])


async def lookup_position(
    client: SymbolClient, file_path: Path, position: LSPPosition
) -> SymbolPath:
    if symbols := await client.request_document_symbol_list(file_path):
        if path := _lookup_position(symbols, position):
            return path

    if symbols := await client.request_document_symbol_information_list(file_path):
        matches = [s for s in symbols if _contains(s.location.range, position)]
        # Sort by nesting: Root starts earlier and ends later
        matches.sort(
            key=lambda s: (
                s.location.range.start.line,
                s.location.range.start.character,
                -s.location.range.end.line,
                -s.location.range.end.character,
            )
        )
        return SymbolPath([Symbol(s.name) for s in matches])

    return SymbolPath([])


def lookup_symbol(
    nodes: Sequence[DocumentSymbol], path: SymbolPath
) -> DocumentSymbol | None:
    current_nodes: list[DocumentSymbol] = list(nodes)
    target: DocumentSymbol | None = None

    for name in path:
        target = next((s for s in current_nodes if s.name == name), None)
        if not target:
            return
        current_nodes = list(target.children or [])
    return target


class SymbolCapability(Capability[SymbolClient, SymbolRequest, SymbolResponse]):
    """Get info about a symbol located in a specific position."""

    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(client=self.client)

    async def __call__(self, req: SymbolRequest) -> SymbolResponse | None:
        location = await self.locate(req)
        if not location:
            return None

        lsp_pos = LSPPosition(
            line=location.position.line, character=location.position.character
        )
        path = await lookup_position(
            self.client,
            req.locate.file_path,
            lsp_pos,
        )
        symbols = await self.client.request_document_symbol_list(req.locate.file_path)

        if not (path and symbols):
            return

        target = lookup_symbol(symbols, path)
        if not target:
            return

        reader = SnippetReader(self.client.read_file(req.locate.file_path))
        if not (snippet := reader.read(target.range)):
            return

        return SymbolResponse(
            file_path=req.locate.file_path,
            symbol_path=path,
            symbol_content=snippet.content,
        )
