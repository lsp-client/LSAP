"""Refer to [document](docs/locate_design.md) for design details."""

import re
from pathlib import Path
from typing import Protocol

from attrs import define
from lsap_schema.locate import (
    LineScope,
    LocateRangeRequest,
    LocateRangeResponse,
    LocateRequest,
    LocateResponse,
    SymbolScope,
)
from lsap_schema.types import Position, Range
from lsp_client.capability.request import WithRequestDocumentSymbol
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import Position as LSPPosition
from lsprotocol.types import Range as LSPRange

from lsap.error import NotFoundError
from lsap.utils.content import DocumentReader
from lsap.utils.symbol import iter_symbols

from .abc import Capability


class LocateClient(
    WithRequestDocumentSymbol,
    CapabilityClientProtocol,
    Protocol,
): ...


def _to_regex(text: str) -> str:
    """Convert search text to regex with sensible whitespace handling.

    - Explicit whitespace: matches one or more whitespace (\\s+)
    - Identifier-operator boundaries: matches zero or more whitespace (\\s*)
    - Within tokens: literal match (no flexibility)
    """
    tokens = re.findall(r"\w+|[^\w\s]+|\s+", text)
    if not tokens:
        return ""

    result: list[str] = []
    for i, token in enumerate(tokens):
        if token[0].isspace():
            result.append(r"\s+")
        else:
            result.append(re.escape(token))
            if i < len(tokens) - 1 and not tokens[i + 1][0].isspace():
                result.append(r"\s*")
    return "".join(result)


async def _get_scope_info(
    client: LocateClient,
    file_path: Path,
    scope: LineScope | SymbolScope | None,
    reader: DocumentReader,
) -> tuple[LSPRange, LSPPosition | None]:
    match scope:
        case None:
            return reader.full_range, None

        case LineScope(line=line):
            if isinstance(line, int):
                start, end = line - 1, line - 1
            else:
                start, end = line[0] - 1, line[1] - 1

            return (
                LSPRange(
                    start=LSPPosition(line=start, character=0),
                    end=LSPPosition(line=end + 1, character=0),
                ),
                None,
            )

        case SymbolScope(symbol_path=path):
            symbols = await client.request_document_symbol_list(file_path)
            for s_path, symbol in iter_symbols(symbols or []):
                if s_path == path:
                    return symbol.range, symbol.selection_range.start
            raise NotFoundError(f"Symbol {path} not found in {file_path}")

        case _:
            return reader.full_range, None


@define
class LocateCapability(Capability[LocateClient, LocateRequest, LocateResponse]):
    async def __call__(self, req: LocateRequest) -> LocateResponse | None:
        locate = req.locate
        document = await self.client.read_file(locate.file_path)
        reader = DocumentReader(document)

        scope_range, selection_start = await _get_scope_info(
            self.client, locate.file_path, locate.scope, reader
        )

        snippet = reader.read(scope_range)
        if not snippet:
            return None

        pos: LSPPosition | None = None

        if locate.find:
            if locate.marker in locate.find:
                before, _, after = locate.find.partition(locate.marker)
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
        elif isinstance(locate.scope, SymbolScope):
            pos = selection_start
        elif isinstance(locate.scope, LineScope):
            m = re.search(r"\S", snippet.exact_content)
            pos = reader.offset_to_position(snippet.range.start, m.start() if m else 0)

        if pos:
            return LocateResponse(
                file_path=locate.file_path,
                position=Position.from_lsp(pos),
            )
        return None


@define
class LocateRangeCapability(
    Capability[LocateClient, LocateRangeRequest, LocateRangeResponse]
):
    async def __call__(self, req: LocateRangeRequest) -> LocateRangeResponse | None:
        locate = req.locate
        document = await self.client.read_file(locate.file_path)
        reader = DocumentReader(document)

        scope_range, _ = await _get_scope_info(
            self.client, locate.file_path, locate.scope, reader
        )

        final_range: LSPRange | None = None

        if locate.find:
            snippet = reader.read(scope_range)
            if not snippet:
                return None

            re_find = _to_regex(locate.find)
            if not re_find:
                final_range = scope_range
            elif m := re.search(re_find, snippet.exact_content):
                final_range = LSPRange(
                    start=reader.offset_to_position(snippet.range.start, m.start()),
                    end=reader.offset_to_position(snippet.range.start, m.end()),
                )
            else:
                return None
        else:
            final_range = scope_range

        if final_range:
            return LocateRangeResponse(
                file_path=locate.file_path,
                range=Range(
                    start=Position.from_lsp(final_range.start),
                    end=Position.from_lsp(final_range.end),
                ),
            )
