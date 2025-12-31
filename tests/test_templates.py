import pytest
from liquid import Environment
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
        # Check for any variable ending with _markdown_template or exactly markdown_template
        for attr_name in dir(module):
            if attr_name == "markdown_template" or attr_name.endswith(
                "_markdown_template"
            ):
                attr_value = getattr(module, attr_name)
                if isinstance(attr_value, str):
                    templates.append((f"{module_name}.{attr_name}", attr_value))
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
