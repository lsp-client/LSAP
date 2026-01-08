from collections.abc import Iterator
from typing import Sequence

from lsprotocol.types import DocumentSymbol
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import Range as LSPRange

from lsap.schema.types import SymbolPath


def _pos(p: LSPPosition) -> tuple[int, int]:
    return (p.line, p.character)


def contains(range: LSPRange, position: LSPPosition) -> bool:
    return _pos(range.start) <= _pos(position) < _pos(range.end)


def is_narrower(inner: LSPRange, outer: LSPRange) -> bool:
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
    symbols: Sequence[DocumentSymbol], position: LSPPosition
) -> tuple[SymbolPath, DocumentSymbol] | None:
    """Find the most specific DocumentSymbol containing the given position."""
    best_match: tuple[SymbolPath, DocumentSymbol] | None = None
    for path, symbol in iter_symbols(symbols):
        if contains(symbol.range, position):
            if best_match is None or is_narrower(symbol.range, best_match[1].range):
                best_match = (path, symbol)
    return best_match
