import re
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

    def parts():
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

        case LineScope(line=line):
            match line:
                case int():
                    start, end = line - 1, line - 1
                case (s, e):
                    start, end = s - 1, e - 1

            return ScopeInfo(
                LSPRange(
                    start=LSPPosition(line=start, character=0),
                    end=LSPPosition(line=end + 1, character=0),
                ),
                None,
            )
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

        snippet = reader.read(info.range)
        if not snippet:
            return None

        pos: LSPPosition | None = None

        if locate.find:
            if marker_info := detect_marker(locate.find):
                marker, _, _ = marker_info
                before, _, after = locate.find.partition(marker)
                re_before, re_after = _to_regex(before), _to_regex(after)

                if not re_before and not re_after:
                    offset = 0
                elif m := re.search(
                    f"({re_before})\\s*({re_after})", snippet.exact_content
                ):
                    offset = m.end(1)
                else:
                    return None
            elif m := re.search(_to_regex(locate.find), snippet.exact_content):
                offset = m.start()
            else:
                return None

            pos = reader.offset_to_position(snippet.range.start, offset)
        else:
            match locate.scope:
                case SymbolScope():
                    pos = info.selection_start
                case LineScope():
                    m = re.search(r"\S", snippet.exact_content)
                    pos = reader.offset_to_position(
                        snippet.range.start, m.start() if m else 0
                    )
                case _:
                    pos = info.range.start

        if pos:
            return LocateResponse(
                file_path=locate.file_path,
                position=Position.from_lsp(pos),
            )
        return None


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
                range=Range(
                    start=Position.from_lsp(final_range.start),
                    end=Position.from_lsp(final_range.end),
                ),
            )
        return None
