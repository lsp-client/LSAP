from collections.abc import Iterator
from typing import Sequence

from lsap_schema.types import SymbolPath
from lsprotocol.types import DocumentSymbol, Position, Range


def _pos(p: Position) -> tuple[int, int]:
    return (p.line, p.character)


def _contains(range: Range, position: Position) -> bool:
    return _pos(range.start) <= _pos(position) < _pos(range.end)


def _is_narrower(inner: Range, outer: Range) -> bool:
    return _pos(inner.start) >= _pos(outer.start) and _pos(inner.end) <= _pos(outer.end)


def iter_symbols(
    nodes: Sequence[DocumentSymbol],
    symbol_path: SymbolPath | None = None,
) -> Iterator[tuple[SymbolPath, DocumentSymbol]]:
    """DFS iterate hierarchy of DocumentSymbol."""
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
    """Find the most specific DocumentSymbol containing the given position."""
    best_match: tuple[SymbolPath, DocumentSymbol] | None = None
    for path, symbol in iter_symbols(symbols):
        if _contains(symbol.range, position):
            if best_match is None or _is_narrower(symbol.range, best_match[1].range):
                best_match = (path, symbol)
    return best_match
