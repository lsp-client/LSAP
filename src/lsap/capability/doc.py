from __future__ import annotations

from functools import cached_property

from attrs import define
from lsp_client.capability.request import WithRequestHover

from lsap.schema.doc import DocRequest, DocResponse
from lsap.utils.capability import ensure_capability
from lsap.utils.markdown import clean_hover_content

from .abc import Capability
from .locate import LocateCapability


@define
class DocCapability(Capability[DocRequest, DocResponse]):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(self.client)

    async def __call__(self, req: DocRequest) -> DocResponse | None:
        if not (loc_resp := await self.locate(req)):
            return None

        file_path, lsp_pos = loc_resp.file_path, loc_resp.position.to_lsp()
        hover = await ensure_capability(self.client, WithRequestHover).request_hover(
            file_path, lsp_pos
        )

        if hover is None:
            return None

        return DocResponse(content=clean_hover_content(hover.value))
