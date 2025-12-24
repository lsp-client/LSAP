from abc import ABC, abstractmethod
from typing import Protocol

from attrs import define
from cattrs import Converter
from lsp_client.protocol import CapabilityClientProtocol

conveter = Converter()


class ClientProtocol(
    CapabilityClientProtocol,
    Protocol,
): ...


@define
class Request: ...


@define
class Response(ABC):
    @abstractmethod
    def format(self) -> str:
        """
        Format the response to standard Markdown format for agents to consume.
        """

    def to_json(self) -> dict:
        """
        Convert the response to a JSON-serializable dictionary.
        """

        return conveter.unstructure(self)


@define
class Capability[C: ClientProtocol, Req: Request, Resp: Response]:
    client: C

    @abstractmethod
    async def __call__(self, req: Req) -> Resp | None: ...
