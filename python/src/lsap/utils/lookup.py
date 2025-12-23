from pathlib import Path
from typing import Protocol, Sequence

from attrs import frozen
from lsp_client.capability.request import WithRequestDocumentSymbol
from lsprotocol.types import DocumentSymbol, Position, Range


class LookupClient(WithRequestDocumentSymbol, Protocol): ...


@frozen
class PositionLookupResult:
    symbol_path: list[str]


def _contains(range: Range, position: Position) -> bool:
    return (
        (range.start.line, range.start.character)
        <= (position.line, position.character)
        < (range.end.line, range.end.character)
    )


def _get_doc_path(nodes: Sequence[DocumentSymbol], p: Position) -> list[str]:
    for n in nodes:
        if not _contains(n.range, p):
            continue
        return [n.name] + _get_doc_path(n.children or [], p)
    return []


async def lookup_position(
    client: LookupClient, file_path: Path, position: Position
) -> PositionLookupResult:
    if symbols := await client.request_document_symbol_list(file_path):
        if path := _get_doc_path(symbols, position):
            return PositionLookupResult(path)

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
        return PositionLookupResult([s.name for s in matches])

    return PositionLookupResult([])
