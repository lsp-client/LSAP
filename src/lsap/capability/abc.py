from abc import ABC, abstractmethod
from typing import Protocol

from attrs import define
from lsp_client import Client
from lsp_client.protocol import CapabilityClientProtocol
from pydantic import BaseModel


class ClientProtocol(CapabilityClientProtocol, Protocol): ...


@define
class Capability[Req: BaseModel, Resp: BaseModel](ABC):
    client: Client

    @abstractmethod
    async def __call__(self, req: Req) -> Resp | None: ...
