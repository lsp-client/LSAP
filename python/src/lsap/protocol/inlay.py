from pathlib import Path
from typing import Protocol, override

from attrs import define
from lsp_client.capability.request.inlay_hint import WithRequestInlayHint
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import Range

from lsap.utils.content import SnippetReader

from .abc import Capability, Request, Response


class InlayReadClient(
    WithRequestInlayHint,
    CapabilityClientProtocol,
    Protocol,
): ...


@define
class InlayReadRequest(Request):
    file_path: Path
    """
    Relative file path to read with inlay hints.
    """

    range: Range | None = None
    """
    Optional range to read. If not provided, the whole file is read.
    """


@define
class InlayReadResponse(Response):
    content: str
    """
    File content with inlay hints.
    """

    @override
    def format(self) -> str:
        return self.content


@define
class InlayReadCapability(
    Capability[InlayReadClient, InlayReadRequest, InlayReadResponse]
):
    async def __call__(self, req: InlayReadRequest) -> InlayReadResponse | None:
        content = self.client.read_file(req.file_path)
        reader = SnippetReader(content)
        if not reader._lines:
            return InlayReadResponse(content="")

        target_range = req.range or reader.full_range
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
