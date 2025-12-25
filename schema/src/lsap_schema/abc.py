from pydantic import BaseModel
from liquid import Environment

Symbol = str
SymbolPath = list[Symbol]


# Shared environment for all responses
_env = Environment()


def _indent(value: str, n: int = 4) -> str:
    if not isinstance(value, str):
        return value
    indent_str = " " * n
    return "\n".join(
        (indent_str + line) if line else line for line in value.splitlines()
    )


_env.add_filter("indent", _indent)


class Response(BaseModel):
    def format(self, template_name: str = "markdown") -> str:
        extra = self.model_config.get("json_schema_extra")
        if not isinstance(extra, dict) or template_name not in extra:
            raise ValueError(
                f"Template '{template_name}' not found in model_config.json_schema_extra"
            )

        template_str = extra[template_name]
        if not isinstance(template_str, str):
            raise TypeError(
                f"Template '{template_name}' must be a string, got {type(template_str).__name__}"
            )

        template = _env.from_string(template_str)
        return template.render(**self.model_dump())


class Request(BaseModel):
    pass


class PaginatedRequest(Request):
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
    """Token to retrieve the next page of results"""
