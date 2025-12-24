from typing import Protocol

from lsp_client.capability.request import WithRequestDocumentSymbol
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import Position as LSPPosition, Range as LSPRange
from lsap_schema.schema.locate import (
    LocateRequest,
    LocateResponse,
    LocateSymbol,
    LocateText,
    Position,
)

from lsap.exception import AmbiguousError
from lsap.utils.content import SnippetReader

from .abc import Capability


class LocateClient(
    WithRequestDocumentSymbol,
    CapabilityClientProtocol,
    Protocol,
): ...


class LocateCapability(Capability[LocateClient, LocateRequest, LocateResponse]):
    async def __call__(self, req: LocateRequest) -> LocateResponse | None:
        pos = None
        match req.locate:
            case LocateText() as lt:
                reader = SnippetReader(self.client.read_file(lt.file_path))
                start, end = (lt.line, lt.line) if isinstance(lt.line, int) else lt.line

                content = reader.read(
                    LSPRange(
                        start=LSPPosition(line=start, character=0),
                        end=LSPPosition(line=end + 1, character=0),
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

        if pos is None:
            return None

        return LocateResponse(
            file_path=req.locate.file_path,
            position=Position(line=pos.line, character=pos.character),
        )
