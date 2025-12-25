import argparse
import json
import importlib
import inspect
import pkgutil
from pathlib import Path
from pydantic import BaseModel
import lsap_schema

...


def export_schemas(output_root: Path):
    output_root.mkdir(parents=True, exist_ok=True)

    # We use lsap_schema as the base package for exports
    path = list(lsap_schema.__path__)
    package_name = lsap_schema.__name__

    for _, module_name, _ in pkgutil.walk_packages(path, package_name + "."):
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue

        # Get relative module name starting from lsap_schema
        # e.g., lsap_schema.locate -> locate
        relative_module = module_name.removeprefix(package_name).strip(".")
        if not relative_module:
            continue

        module_dir = output_root / relative_module.replace(".", "/")

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, BaseModel)
                and obj is not BaseModel
                and obj.__module__ == module_name
            ):
                module_dir.mkdir(parents=True, exist_ok=True)
                schema = obj.model_json_schema()
                schema_path = module_dir / f"{obj.__name__}.json"
                schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
                print(f"Exported {obj.__name__} to {schema_path}")


def main():
    parser = argparse.ArgumentParser(description="Export LSAP schemas to JSON files")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("dist/schemas"),
        help="Output root directory (default: dist/schemas)",
    )
    args = parser.parse_args()
    export_schemas(args.output)


if __name__ == "__main__":
    main()
