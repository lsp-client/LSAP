from pathlib import Path
from typing import Literal, Protocol, override

from attrs import define, frozen
from lsp_client.capability.request import WithRequestDocumentSymbol
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import Position, Range

from lsap.exception import AmbiguousError
from lsap.utils.content import SnippetReader
from lsap.utils.symbol import SymbolPath

from .abc import Capability, Request, Response


class LocateClient(
    WithRequestDocumentSymbol,
    CapabilityClientProtocol,
    Protocol,
): ...


@frozen
class LocateText:
    file_path: Path
    """Relative file path"""

    line: int | tuple[int, int]
    """Line number or range (start, end)"""

    find: str
    """Text snippet to find"""

    position: Literal["start", "end"] = "start"
    """Position in the snippet to locate, default to 'start'"""


@frozen
class LocateSymbol:
    """Locate by symbol path"""

    file_path: Path
    """Relative file path"""

    symbol_path: SymbolPath
    """Symbol hierarchy path, e.g., ["MyClass", "my_method"]"""


@define
class LocateRequest(Request):
    locate: LocateText | LocateSymbol
    """Locate a specific text position in the file."""


@define
class LocateResponse(Response):
    file_path: Path
    position: Position

    @override
    def format(self) -> str:
        return f"Located {self.file_path} at {self.position.line + 1}:{self.position.character + 1}"


@define
class LocateCapability(Capability[LocateClient, LocateRequest, LocateResponse]):
    async def __call__(self, req: LocateRequest) -> LocateResponse | None:
        match req.locate:
            case LocateText() as lt:
                reader = SnippetReader(self.client.read_file(lt.file_path))
                start, end = (lt.line, lt.line) if isinstance(lt.line, int) else lt.line

                content = reader.read(
                    Range(
                        start=Position(line=start, character=0),
                        end=Position(line=end + 1, character=0),
                    )
                )
                if not content:
                    return

                if (idx := content.exact_content.find(lt.find)) == -1:
                    return

                if content.exact_content.find(lt.find, idx + 1) != -1:
                    raise AmbiguousError(
                        f"Multiple matches for {lt.find!r} in {lt.file_path}:{lt.line}. "
                        "Provide a more precise 'find' string."
                    )

                offset = idx + (len(lt.find) if lt.position == "end" else 0)
                pos = reader.offset_to_position(content.range.start, offset)

            case LocateSymbol() as ls:
                from .symbol import lookup_symbol

                symbols = await self.client.request_document_symbol_list(ls.file_path)
                if not symbols or not ls.symbol_path:
                    return

                if target := lookup_symbol(symbols, ls.symbol_path):
                    pos = target.selection_range.start
                else:
                    return

        return LocateResponse(
            file_path=req.locate.file_path,
            position=pos,
        )
