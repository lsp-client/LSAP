import argparse
import importlib
import json
import logging
import pkgutil
from collections.abc import Sequence
from pathlib import Path
from typing import Final

from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger: Final = logging.getLogger(__name__)


def export_module_schemas(
    *,
    module_name: str,
    package_name: str,
    output_dir: Path,
) -> None:
    """Export schemas and documentation for a single module.

    Raises:
        ModuleNotFoundError: If the module cannot be imported.
        OSError: If file operations fail.
    """
    full_module_name = f"{package_name}.{module_name}"
    try:
        module = importlib.import_module(full_module_name)
    except (ImportError, ModuleNotFoundError) as e:
        logger.exception("Failed to import module: %s", full_module_name)
        raise ModuleNotFoundError(f"Could not import {full_module_name}: {e}") from e

    generated_schemas: list[str] = []

    # 1. Export Pydantic models in __all__ to JSON schema
    module_all: Sequence[str] = getattr(module, "__all__", [])
    for attr_name in module_all:
        obj = getattr(module, attr_name, None)
        # Check if it's a Pydantic model class
        if isinstance(obj, type) and issubclass(obj, BaseModel):
            schema = obj.model_json_schema()
            json_filename = f"{attr_name}.json"
            json_path = output_dir / json_filename

            with json_path.open("w", encoding="utf-8") as f:
                json.dump(schema, f, indent=2)
                f.write("\n")

            generated_schemas.append(json_filename)
            logger.debug("Exported schema: %s", json_filename)

    # 2. Export Markdown documentation from module __doc__ and include References
    md_content = module.__doc__
    if not md_content:
        raise ValueError("Module documentation is empty")

    if not generated_schemas:
        return

    md_filename = f"{module_name}.md"
    md_path = output_dir / md_filename

    with md_path.open("w", encoding="utf-8") as f:
        f.write(md_content.strip() + "\n\n")

        if generated_schemas:
            f.write("## References\n\n")
            for schema_file in sorted(generated_schemas):
                f.write(f"- [{schema_file}](./{schema_file})\n")
    logger.info("Generated: %s", md_filename)


def main() -> None:
    """Main entry point for the schema exporter.

    Handles all unhandled exceptions at the entry point level.
    """

    parser = argparse.ArgumentParser(
        description="Export LSAP capability schemas to JSON schema files and Markdown documentation."
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Directory to store the generated files.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use the directory of this file to find sibling modules
    package_dir: Final = Path(__file__).parent
    # Assume the package name is the parent's name if not set
    package_name: Final = __package__ or "lsap.schema"

    logger.info("Exporting schemas from %s to %s", package_name, output_dir)

    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        if module_name.startswith("_") or module_name == "combined":
            continue

        export_module_schemas(
            module_name=module_name,
            package_name=package_name,
            output_dir=output_dir,
        )


if __name__ == "__main__":
    main()
