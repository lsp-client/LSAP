from __future__ import annotations

from functools import cached_property
from typing import Protocol, override, runtime_checkable

from lsap_schema.hover import HoverRequest, HoverResponse
from lsp_client.capability.request import (
    WithRequestDocumentSymbol,
    WithRequestHover,
)

from .abc import Capability, ClientProtocol
from .locate import LocateCapability


@runtime_checkable
class HoverClient(
    WithRequestHover,
    WithRequestDocumentSymbol,
    ClientProtocol,
    Protocol,
): ...


class HoverCapability(Capability[HoverClient, HoverRequest, HoverResponse]):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(self.client)

    @override
    async def __call__(self, req: HoverRequest) -> HoverResponse | None:
        if not (loc_resp := await self.locate(req)):
            return None

        file_path, lsp_pos = loc_resp.file_path, loc_resp.position.to_lsp()
        hover = await self.client.request_hover(file_path, lsp_pos)

        if not hover:
            return None

        return HoverResponse(
            contents=hover.value,
            range=None,
        )
