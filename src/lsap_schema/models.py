from enum import Enum
from pathlib import Path
from typing import Self

from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import SymbolKind as LSPSymbolKind
from pydantic import BaseModel, Field

from .types import Symbol, SymbolPath


class Position(BaseModel):
    """
    Represents a specific position in a file using line and character numbers.

    Note: Line and character are 1-based indices. 0-based indices are used in LSP, so conversion is needed when interfacing with LSP.
    """

    line: int = Field(ge=1)
    """1-based line number"""

    character: int = Field(ge=1)
    """1-based character (column) number"""

    @classmethod
    def from_lsp(cls, position: LSPPosition) -> Self:
        """Convert from LSP Position (0-based) to Position (1-based)"""
        return cls(line=position.line + 1, character=position.character + 1)

    def to_lsp(self) -> LSPPosition:
        return LSPPosition(line=self.line - 1, character=self.character - 1)


class Range(BaseModel):
    start: Position
    end: Position


class Location(BaseModel):
    file_path: Path
    range: Range


class SymbolKind(str, Enum):
    File = "file"
    Module = "module"
    Namespace = "namespace"
    Package = "package"
    Class = "class"
    Method = "method"
    Property = "property"
    Field = "field"
    Constructor = "constructor"
    Enum = "enum"
    Interface = "interface"
    Function = "function"
    Variable = "variable"
    Constant = "constant"
    String = "string"
    Number = "number"
    Boolean = "boolean"
    Array = "array"
    Object = "object"
    Key = "key"
    Null = "null"
    EnumMember = "enumMember"
    Struct = "struct"
    Event = "event"
    Operator = "operator"
    TypeParameter = "typeParameter"

    @classmethod
    def from_lsp(cls, kind: LSPSymbolKind) -> Self:
        """Convert from LSP SymbolKind to LSAP SymbolKind"""
        return cls[kind.name]


class SymbolInfo(BaseModel):
    file_path: Path
    name: Symbol
    path: SymbolPath
    kind: SymbolKind

    range: Range | None = None
    """Source code range of the symbol"""


class SymbolCodeInfo(SymbolInfo):
    code: str | None = None
    """Source code of the symbol"""


class SymbolDetailInfo(SymbolInfo):
    detail: str | None = None
    hover: str | None = None
    """Markdown formatted hover/documentation information"""
