import importlib.util
import sys
from pathlib import Path

from project_rosetta.utils.paths import BASE_DIR


def py2xosc(py_file: str) -> list[str]:
    """
    Generate an OpenSCENARIO file from a Python scenario definition.

    Args:
        py_file: Path to the Python scenario file.

    Returns:
        A list of strings representing the lines of the generated OpenSCENARIO file.

    """
    module_name = "my_dynamic_module"

    spec = importlib.util.spec_from_file_location(module_name, py_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # Now access your class
    Scenario = getattr(module, "Scenario")

    # Use it
    obj = Scenario()
    obj.naming = "numerical"

    scenarios, roads = obj.generate(Path(py_file).parent)
    scenarios = [Path(BASE_DIR, scenario) for scenario in scenarios]
    return scenarios
