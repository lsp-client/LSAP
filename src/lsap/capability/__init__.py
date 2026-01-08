from typing import TypedDict

from .definition import DefinitionCapability
from .hover import HoverCapability
from .locate import LocateCapability
from .outline import OutlineCapability
from .reference import ReferenceCapability
from .rename import RenameExecuteCapability, RenamePreviewCapability
from .search import SearchCapability
from .symbol import SymbolCapability


class Capabilities(TypedDict):
    definition: DefinitionCapability
    hover: HoverCapability
    locate: LocateCapability
    outline: OutlineCapability
    references: ReferenceCapability
    rename_preview: RenamePreviewCapability
    rename_execute: RenameExecuteCapability
    search: SearchCapability
    symbol: SymbolCapability
