from typing import NewType

Symbol = NewType("Symbol", str)
SymbolPath = NewType("SymbolPath", list[Symbol])
