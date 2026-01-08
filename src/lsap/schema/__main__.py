import argparse
import json
from pathlib import Path
from typing import Final, NamedTuple

from .abc import Request, Response
from .definition import DefinitionRequest, DefinitionResponse
from .hover import HoverRequest, HoverResponse
from .locate import LocateRequest, LocateResponse
from .outline import OutlineRequest, OutlineResponse
from .reference import ReferenceRequest, ReferenceResponse
from .rename import (
    RenameExecuteRequest,
    RenameExecuteResponse,
    RenamePreviewRequest,
    RenamePreviewResponse,
)
from .search import SearchRequest, SearchResponse
from .symbol import SymbolRequest, SymbolResponse


class Capability(NamedTuple):
    request: type[Request]
    response: type[Response]


capability_schemas: Final = {
    "definition": Capability(
        request=DefinitionRequest,
        response=DefinitionResponse,
    ),
    "hover": Capability(
        request=HoverRequest,
        response=HoverResponse,
    ),
    "locate": Capability(
        request=LocateRequest,
        response=LocateResponse,
    ),
    "outline": Capability(
        request=OutlineRequest,
        response=OutlineResponse,
    ),
    "reference": Capability(
        request=ReferenceRequest,
        response=ReferenceResponse,
    ),
    "rename_preview": Capability(
        request=RenamePreviewRequest,
        response=RenamePreviewResponse,
    ),
    "rename_execute": Capability(
        request=RenameExecuteRequest,
        response=RenameExecuteResponse,
    ),
    "search": Capability(
        request=SearchRequest,
        response=SearchResponse,
    ),
    "symbol": Capability(
        request=SymbolRequest,
        response=SymbolResponse,
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export LSAP capability schemas to JSON schema files."
    )
    parser.add_argument(
        "output_dir", type=Path, help="Directory to store the JSON schema files."
    )
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, capability in capability_schemas.items():
        request_schema = capability.request.model_json_schema()
        response_schema = capability.response.model_json_schema()

        with (output_dir / f"{name}.request.json").open("w") as f:
            json.dump(request_schema, f, indent=2)
            f.write("\n")
        with (output_dir / f"{name}.response.json").open("w") as f:
            json.dump(response_schema, f, indent=2)
            f.write("\n")


if __name__ == "__main__":
    main()
