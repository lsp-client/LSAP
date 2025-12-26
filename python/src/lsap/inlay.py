from typing import Protocol

from attrs import define
from lsap_schema.schema.inlay_read import InlayReadRequest, InlayReadResponse
from lsp_client.capability.request.inlay_hint import WithRequestInlayHint
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import (
    Position as LSPPosition,
)
from lsprotocol.types import (
    Range as LSPRange,
)

from lsap.utils.content import SnippetReader

from .abc import Capability


class InlayReadClient(
    WithRequestInlayHint,
    CapabilityClientProtocol,
    Protocol,
): ...


@define
class InlayReadCapability(
    Capability[InlayReadClient, InlayReadRequest, InlayReadResponse]
):
    async def __call__(self, req: InlayReadRequest) -> InlayReadResponse | None:
        content = self.client.read_file(req.file_path)
        reader = SnippetReader(content)
        if not reader._lines:
            return InlayReadResponse(content="")

        if req.range:
            target_range = LSPRange(
                start=LSPPosition(
                    line=req.range.start.line, character=req.range.start.character
                ),
                end=LSPPosition(
                    line=req.range.end.line, character=req.range.end.character
                ),
            )
        else:
            target_range = reader.full_range

        hints = await self.client.request_inlay_hint(req.file_path, target_range)

        # Get the base text for the requested range
        start_offset = reader.position_to_offset(target_range.start)
        end_offset = reader.position_to_offset(target_range.end)
        result_content = content[start_offset:end_offset]

        if not hints:
            return InlayReadResponse(content=result_content)

        # Filter and sort hints
        # We only want hints that fall within the requested range
        def is_in_range(pos):
            # Start is inclusive, end is exclusive for the purpose of hint insertion in a snippet
            # though inlay hints are usually at a specific position.
            if pos.line < target_range.start.line:
                return False
            if (
                pos.line == target_range.start.line
                and pos.character < target_range.start.character
            ):
                return False
            if pos.line > target_range.end.line:
                return False
            if (
                pos.line == target_range.end.line
                and pos.character > target_range.end.character
            ):
                return False
            return True

        valid_hints = [(i, h) for i, h in enumerate(hints) if is_in_range(h.position)]

        # Sort hints by position descending
        sorted_hints = sorted(
            valid_hints,
            key=lambda x: (x[1].position.line, x[1].position.character, x[0]),
            reverse=True,
        )

        for _, hint in sorted_hints:
            label = self.client.get_inlay_hint_label(hint)

            if hint.padding_left:
                label = " " + label
            if hint.padding_right:
                label = label + " "

            # Calculate relative offset
            abs_offset = reader.position_to_offset(hint.position)
            relative_offset = abs_offset - start_offset

            # Ensure relative_offset is within result_content bounds
            relative_offset = max(0, min(relative_offset, len(result_content)))

            result_content = (
                result_content[:relative_offset]
                + label
                + result_content[relative_offset:]
            )

        return InlayReadResponse(content=result_content)
