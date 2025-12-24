from typing import NewType, Sequence

from lsprotocol.types import DocumentSymbol

Symbol = NewType("Symbol", str)
SymbolPath = NewType("SymbolPath", list[Symbol])


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
