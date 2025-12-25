import pytest
from liquid import Environment
from liquid.extra import MacroTag, CallTag
import importlib
import pkgutil
import lsap_schema


def get_templates():
    templates = []
    package = lsap_schema
    for loader, module_name, is_pkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        module = importlib.import_module(module_name)
        if hasattr(module, "markdown_template"):
            templates.append((module_name, getattr(module, "markdown_template")))
    return templates


@pytest.mark.parametrize("module_name, template_str", get_templates())
def test_template_compilation(module_name, template_str):
    env = Environment()

    try:
        env.from_string(template_str)
    except Exception as e:
        pytest.fail(f"Template in {module_name} failed to compile: {e}")


if __name__ == "__main__":
    # Manually run if needed
    for name, template in get_templates():
        print(f"Compiling {name}...")
        test_template_compilation(name, template)
    print("All templates compiled successfully!")
