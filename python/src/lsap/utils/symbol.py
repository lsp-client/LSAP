from collections.abc import Iterator
from typing import Sequence

from lsap_schema.abc import SymbolPath
from lsprotocol.types import DocumentSymbol, Position, Range


def _contains(range: Range, position: Position) -> bool:
    return (
        (range.start.line, range.start.character)
        <= (position.line, position.character)
        < (range.end.line, range.end.character)
    )


def iter_symbols(
    nodes: Sequence[DocumentSymbol],
    symbol_path: SymbolPath | None = None,
) -> Iterator[tuple[SymbolPath, DocumentSymbol]]:
    if symbol_path is None:
        symbol_path = []
    for node in nodes:
        current_path = [*symbol_path, node.name]
        yield current_path, node
        if node.children:
            yield from iter_symbols(node.children, current_path)


def symbol_at(
    symbols: Sequence[DocumentSymbol], position: Position
) -> tuple[SymbolPath, DocumentSymbol] | None:
    best_match: tuple[SymbolPath, DocumentSymbol] | None = None
    for path, symbol in iter_symbols(symbols):
        if (
            (symbol.range.start.line, symbol.range.start.character)
            <= (position.line, position.character)
            < (symbol.range.end.line, symbol.range.end.character)
        ):
            if best_match is None or (
                (symbol.range.start.line, symbol.range.start.character)
                >= (best_match[1].range.start.line, best_match[1].range.start.character)
                and (symbol.range.end.line, symbol.range.end.character)
                <= (best_match[1].range.end.line, best_match[1].range.end.character)
            ):
                best_match = (path, symbol)
    return best_match
