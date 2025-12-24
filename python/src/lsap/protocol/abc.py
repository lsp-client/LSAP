from abc import ABC, abstractmethod
from typing import Protocol, Any, ClassVar

from attrs import define
from cattrs import Converter
from lsp_client.protocol import CapabilityClientProtocol
from jinja2 import Template

conveter = Converter()


class ClientProtocol(
    CapabilityClientProtocol,
    Protocol,
): ...


@define
class Request: ...


@define
class Response(ABC):
    templates: ClassVar[dict[str, str]] = {}

    def format(self) -> str:
        """
        Format the response to standard Markdown format for agents to consume.
        Uses jinja2 template from ClassVar if available.
        """
        template_str = self.templates.get("markdown")
        if not template_str:
            return self._fallback_format()

        template = Template(template_str)
        # We unstructure to dict for jinja2 rendering
        return template.render(conveter.unstructure(self))

    def _fallback_format(self) -> str:
        raise NotImplementedError(
            f"No markdown template defined for {self.__class__.__name__}"
        )

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
