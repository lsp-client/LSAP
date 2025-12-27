import re
from typing import Protocol

from lsap_schema.locate import (
    LocateRequest,
    LocateResponse,
    LocateSymbol,
    LocateText,
    Position,
)
from lsp_client.capability.request import WithRequestDocumentSymbol
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import Range as LSPRange

from lsap.exception import AmbiguousError
from lsap.utils.content import DocumentReader
from lsap.utils.symbol import iter_symbols

from .abc import Capability


class LocateClient(
    WithRequestDocumentSymbol,
    CapabilityClientProtocol,
    Protocol,
): ...


class LocateCapability(Capability[LocateClient, LocateRequest, LocateResponse]):
    async def __call__(self, req: LocateRequest) -> LocateResponse | None:
        position: LSPPosition | None = None

        match req.locate:
            case LocateText(
                file_path=file_path, line=line, find=find, find_end=find_end
            ):
                document = await self.client.read_file(file_path)
                reader = DocumentReader(document)
                start, end = (line, line) if isinstance(line, int) else line

                content = reader.read(
                    LSPRange(
                        start=LSPPosition(line=start, character=0),
                        end=LSPPosition(line=end + 1, character=0),
                    )
                )

                if not content:
                    return

                # Build a regex to match characters while ignoring any interleaving whitespace.
                # This ensures that "abc" matches "a b c" in the document.
                chars = [re.escape(c) for c in find if not c.isspace()]
                if not chars:
                    return

                pattern = r"\s*".join(chars)
                matches = list(re.finditer(pattern, content.exact_content))

                if not matches:
                    return

                if len(matches) > 1:
                    raise AmbiguousError(
                        f"Multiple matches for {find!r} in {file_path}:{line}. "
                        "Provide a more precise 'find' string."
                    )

                match = matches[0]
                offset = match.end() if find_end == "end" else match.start()
                position = reader.offset_to_position(content.range.start, offset)

            case LocateSymbol(file_path=file_path, symbol_path=symbol_path):
                symbols = await self.client.request_document_symbol_list(file_path)
                if not symbols or not symbol_path:
                    return

                for path, symbol in iter_symbols(symbols):
                    if path == symbol_path:
                        position = symbol.selection_range.start
                        break

        if position:
            return LocateResponse(
                file_path=req.locate.file_path,
                position=Position.from_lsp(position),
            )
