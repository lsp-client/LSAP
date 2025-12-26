import argparse
import json
import inspect
from pathlib import Path
from pydantic import BaseModel
import lsap_schema

...


def export_schemas(output_root: Path):
    output_root.mkdir(parents=True, exist_ok=True)

    # Get package name once
    package_name = lsap_schema.__name__
    
    # Import all exported classes from lsap_schema
    # These are manually defined in __init__.py
    for name in lsap_schema.__all__:
        obj = getattr(lsap_schema, name)
        
        # Only process BaseModel subclasses
        if not (inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel):
            continue
        
        # Get the module name where the class is defined
        module_name = obj.__module__
        
        # Get relative module name starting from lsap_schema
        # e.g., lsap_schema.locate -> locate
        relative_module = module_name.removeprefix(package_name + ".").strip(".")
        
        if not relative_module:
            continue
        
        module_dir = output_root / relative_module.replace(".", "/")
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
