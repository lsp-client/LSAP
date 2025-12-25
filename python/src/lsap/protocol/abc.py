from abc import abstractmethod
from typing import Protocol

from attrs import define
from jinja2 import Template
from lsp_client.protocol import CapabilityClientProtocol
from pydantic import BaseModel


class ClientProtocol(
    CapabilityClientProtocol,
    Protocol,
): ...


def format_response(model: BaseModel) -> str:
    """
    Format the response to standard Markdown format for agents to consume.
    Uses jinja2 template from model_config if available.
    """
    config = model.model_config
    json_schema_extra = config.get("json_schema_extra", {})
    if not isinstance(json_schema_extra, dict):
        return str(model)

    template_str = json_schema_extra.get("markdown")
    if not isinstance(template_str, str):
        return str(model)

    template = Template(template_str)
    return template.render(model.model_dump())


@define
class Capability[C: ClientProtocol, Req: BaseModel, Resp: BaseModel]:
    client: C

    @abstractmethod
    async def __call__(self, req: Req) -> Resp | None: ...
