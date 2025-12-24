from typing import Annotated

from lsprotocol import types as lsp_type
from lsprotocol.converters import get_converter
from pydantic import PlainSerializer, PlainValidator

conveter = get_converter()


def position_serializer(v: lsp_type.Position) -> dict:
    return {"line": v.line, "character": v.character}


def position_validator(v: dict) -> lsp_type.Position:
    return conveter.structure(v, lsp_type.Position)


Position = Annotated[
    lsp_type.Position,
    PlainSerializer(position_serializer),
    PlainValidator(position_validator),
]


def range_serializer(v: lsp_type.Range) -> dict:
    return {
        "start": position_serializer(v.start),
        "end": position_serializer(v.end),
    }


def range_validator(v: dict) -> lsp_type.Range:
    return lsp_type.Range(
        start=position_validator(v["start"]),
        end=position_validator(v["end"]),
    )


Range = Annotated[
    lsp_type.Range,
    PlainSerializer(range_serializer),
    PlainValidator(range_validator),
]
