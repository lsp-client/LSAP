from functools import lru_cache

from liquid import Environment
from pydantic import BaseModel

_env = Environment()


@lru_cache()
def get_template(template_source: str):
    return _env.from_string(template_source)


class Request(BaseModel): ...


class Response(BaseModel):
    def format(self, template_name: str = "markdown") -> str:
        match self.model_config.get("json_schema_extra"):
            case dict() as templates if (
                template_str := templates.get(template_name)
            ) and isinstance(template_str, str):
                return get_template(template_str).render(**self.model_dump())
            case _:
                raise ValueError(
                    f"No template named '{template_name}' found in model_config.json_schema_extra"
                )


class PaginatedRequest(Request):
    """
    Base request for paginated results.
    """

    max_items: int | None = None
    """Maximum number of items to return"""

    start_index: int = 0
    """Number of items to skip"""

    pagination_id: str | None = None
    """Token to retrieve the next page of results"""


class PaginatedResponse(Response):
    start_index: int
    max_items: int | None = None
    total: int | None = None
    has_more: bool = False

    pagination_id: str | None = None
