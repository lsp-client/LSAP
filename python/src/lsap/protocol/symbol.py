from functools import cached_property
from pathlib import Path
from typing import Protocol, Sequence, final, override

from attrs import define
from lsp_client.capability.request import WithRequestDocumentSymbol
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import DocumentSymbol, Position, Range

from lsap.utils.content import SnippetReader
from lsap.utils.symbol import Symbol, SymbolPath

from .abc import Capability, Response
from .locate import LocateCapability, LocateRequest


class SymbolClient(
    WithRequestDocumentSymbol,
    CapabilityClientProtocol,
    Protocol,
): ...


def _contains(range: Range, position: Position) -> bool:
    return (
        (range.start.line, range.start.character)
        <= (position.line, position.character)
        < (range.end.line, range.end.character)
    )


def _lookup_position(nodes: Sequence[DocumentSymbol], p: Position) -> SymbolPath:
    for n in nodes:
        if not _contains(n.range, p):
            continue
        return SymbolPath([Symbol(n.name)] + _lookup_position(n.children or [], p))
    return SymbolPath([])


async def lookup_position(
    client: SymbolClient, file_path: Path, position: Position
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


@define
class SymbolRequest(LocateRequest): ...


@final
@define
class SymbolResponse(Response):
    file_path: Path
    symbol_path: SymbolPath
    symbol_content: str

    templates = {
        "markdown": "### Symbol: `{{ symbol_path | join('.') }}` in `{{ file_path }}`\n\n```python\n{{ symbol_content }}\n```"
    }


@define
class SymbolCapability(Capability[SymbolClient, SymbolRequest, SymbolResponse]):
    """Get info about a symbol located in a specific position."""

    client: SymbolClient

    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(client=self.client)

    async def __call__(self, req: SymbolRequest) -> SymbolResponse | None:
        location = await self.locate(req)
        path = location and await lookup_position(
            self.client,
            req.locate.file_path,
            location.position,
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
