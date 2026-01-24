import re
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

from attrs import define
from lsp_client import Client
from lsp_client.capability.request import WithRequestDocumentSymbol
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import Range as LSPRange

from lsap.exception import NotFoundError
from lsap.schema.locate import (
    LineScope,
    LocateRangeRequest,
    LocateRangeResponse,
    LocateRequest,
    LocateResponse,
    SymbolScope,
)
from lsap.schema.models import Position, Range
from lsap.utils.capability import ensure_capability
from lsap.utils.document import DocumentReader
from lsap.utils.locate import detect_marker
from lsap.utils.symbol import iter_symbols

from .abc import Capability


def _to_regex(text: str) -> str:
    """Convert search text to regex with sensible whitespace handling.

    - Explicit whitespace: matches one or more whitespace (\\s+)
    - Identifier-operator boundaries: matches zero or more whitespace (\\s*)
    - Within tokens: literal match (no flexibility)
    """
    tokens = re.findall(r"\w+|[^\w\s]+|\s+", text)
    if not tokens:
        return ""

    def parts() -> Iterator[str]:
        for i, token in enumerate(tokens):
            if token[0].isspace():
                yield r"\s+"
            else:
                yield re.escape(token)
                if i < len(tokens) - 1 and not tokens[i + 1][0].isspace():
                    yield r"\s*"

    return "".join(parts())


class ScopeInfo(NamedTuple):
    range: LSPRange
    selection_start: LSPPosition | None


async def _get_scope_info(
    client: Client,
    file_path: Path,
    scope: LineScope | SymbolScope | None,
    reader: DocumentReader,
) -> ScopeInfo:
    match scope:
        case None:
            return ScopeInfo(reader.full_range, None)

        case LineScope(start_line=start_line, end_line=end_line):
            start = LSPPosition(line=start_line - 1, character=0)
            end = (
                reader.full_range.end
                if end_line == 0
                else LSPPosition(line=end_line - 1, character=0)
            )

            return ScopeInfo(LSPRange(start=start, end=end), None)
        case SymbolScope(symbol_path=path):
            symbols = await ensure_capability(
                client, WithRequestDocumentSymbol
            ).request_document_symbol_list(file_path)
            for s_path, symbol in iter_symbols(symbols or []):
                if s_path == path:
                    return ScopeInfo(symbol.range, symbol.selection_range.start)
            raise NotFoundError(f"Symbol {path} not found in {file_path}")


@define
class LocateCapability(Capability[LocateRequest, LocateResponse]):
    async def __call__(self, req: LocateRequest) -> LocateResponse | None:
        locate = req.locate
        document = await self.client.read_file(locate.file_path)
        reader = DocumentReader(document)

        info = await _get_scope_info(
            self.client, locate.file_path, locate.scope, reader
        )

        if pos := (
            self._find_position(locate.find, info.range, reader)
            if locate.find
            else self._default_position(locate.scope, info, reader)
        ):
            return LocateResponse(
                file_path=locate.file_path,
                position=Position.from_lsp(pos),
            )

        return None

    def _find_position(
        self, find: str, scope_range: LSPRange, reader: DocumentReader
    ) -> LSPPosition | None:
        """Find the position of the search string or marker within the scope.

        If a marker is present, the position is at the character immediately
        following the marker. If there is no character following the marker,
        the position is at the character immediately preceding the marker.
        The marker itself is only used to identify the position and does not
        represent any characters or whitespace in the content.
        """
        snippet = reader.read(scope_range)
        if not snippet:
            return None

        if marker_info := detect_marker(find):
            before, _, after = find.partition(marker_info.marker)
            match (before, after):
                case ("", ""):
                    offset = 0
                case (before, ""):
                    pattern = re.compile(re.escape(before))
                    if m := pattern.search(snippet.exact_content):
                        offset = m.end()
                    else:
                        return None
                case (before, after):
                    pattern = re.compile(re.escape(before) + re.escape(after))
                    if m := pattern.search(snippet.exact_content):
                        offset = m.start() + len(before)
                    else:
                        return None
        elif m := re.search(_to_regex(find), snippet.exact_content):
            offset = m.start()
        else:
            return None

        return reader.offset_to_position(snippet.range.start, offset)

    def _default_position(
        self,
        scope: LineScope | SymbolScope | None,
        info: ScopeInfo,
        reader: DocumentReader,
    ) -> LSPPosition | None:
        match scope:
            case SymbolScope():
                return info.selection_start
            case LineScope():
                snippet = reader.read(info.range)
                if not snippet:
                    return info.range.start
                m = re.search(r"\S", snippet.exact_content)
                return reader.offset_to_position(
                    snippet.range.start, m.start() if m else 0
                )
            case _:
                return info.range.start


@define
class LocateRangeCapability(Capability[LocateRangeRequest, LocateRangeResponse]):
    async def __call__(self, req: LocateRangeRequest) -> LocateRangeResponse | None:
        locate = req.locate
        document = await self.client.read_file(locate.file_path)
        reader = DocumentReader(document)

        info = await _get_scope_info(
            self.client, locate.file_path, locate.scope, reader
        )

        final_range: LSPRange | None = None

        if locate.find:
            snippet = reader.read(info.range)
            if not snippet:
                return None

            re_find = _to_regex(locate.find)
            if not re_find:
                final_range = info.range
            elif m := re.search(re_find, snippet.exact_content):
                final_range = LSPRange(
                    start=reader.offset_to_position(snippet.range.start, m.start()),
                    end=reader.offset_to_position(snippet.range.start, m.end()),
                )
            else:
                return None
        else:
            final_range = info.range

        if final_range:
            return LocateRangeResponse(
                file_path=locate.file_path,
                range=Range.from_lsp(final_range),
            )
        return None
