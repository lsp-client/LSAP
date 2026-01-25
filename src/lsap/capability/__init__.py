from typing import TypedDict

from .definition import DefinitionCapability
from .locate import LocateCapability
from .outline import OutlineCapability
from .reference import ReferenceCapability
from .relation import RelationCapability
from .rename import RenameExecuteCapability, RenamePreviewCapability
from .search import SearchCapability
from .symbol import SymbolCapability


class Capabilities(TypedDict):
    definition: DefinitionCapability
    locate: LocateCapability
    outline: OutlineCapability
    references: ReferenceCapability
    relation: RelationCapability
    rename_preview: RenamePreviewCapability
    rename_execute: RenameExecuteCapability
    search: SearchCapability
    symbol: SymbolCapability
