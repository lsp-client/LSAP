from __future__ import annotations

from functools import cached_property

from attrs import define
from lsp_client.capability.request import WithRequestHover

from lsap.schema.hover import HoverRequest, HoverResponse
from lsap.utils.capability import ensure_capability

from .abc import Capability
from .locate import LocateCapability


@define
class HoverCapability(Capability[HoverRequest, HoverResponse]):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(self.client)

    async def __call__(self, req: HoverRequest) -> HoverResponse | None:
        if not (loc_resp := await self.locate(req)):
            return None

        file_path, lsp_pos = loc_resp.file_path, loc_resp.position.to_lsp()
        hover = await ensure_capability(self.client, WithRequestHover).request_hover(
            file_path, lsp_pos
        )

        if hover is None:
            return None

        return HoverResponse(content=hover.value)
