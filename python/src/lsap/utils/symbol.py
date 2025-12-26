from collections.abc import Iterator
from typing import Sequence

from lsap_schema.abc import SymbolPath
from lsprotocol.types import DocumentSymbol


def lookup_symbol(
    nodes: Sequence[DocumentSymbol], path: SymbolPath
) -> DocumentSymbol | None:
    current_nodes = nodes
    target = None
    for name in path:
        target = next((s for s in current_nodes if s.name == name), None)
        if not target:
            return None
        current_nodes = target.children or []
    return target


def iter_symbols(
    nodes: Sequence[DocumentSymbol],
) -> Iterator[tuple[SymbolPath, DocumentSymbol]]:
    p = SymbolPath([])
    for n in nodes:
        current_path = SymbolPath([*p, n.name])
        yield current_path, n
        if n.children:
            yield from iter_symbols(n.children)
