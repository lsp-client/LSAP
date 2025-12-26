from abc import abstractmethod
from typing import Protocol

from attrs import define
from lsp_client.protocol import CapabilityClientProtocol
from pydantic import BaseModel


class ClientProtocol(CapabilityClientProtocol, Protocol): ...


@define
class Capability[C: ClientProtocol, Req: BaseModel, Resp: BaseModel]:
    client: C

    @abstractmethod
    async def __call__(self, req: Req) -> Resp | None: ...
