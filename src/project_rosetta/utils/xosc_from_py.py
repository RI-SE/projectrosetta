import importlib.util
import sys
from pathlib import Path

from project_rosetta.utils.utils import BASE_DIR


def py2xosc(py_file: str) -> list[str]:
    """
    Generate an OpenSCENARIO file from a Python scenario definition.

    Args:
        py_file: Path to the Python scenario file.

    Returns:
        A list of strings representing the lines of the generated OpenSCENARIO file.

    Raises:
        FileNotFoundError: If the input Python file does not exist.
        AttributeError: If the Python file does not define a Scenario class.
        ValueError: If Scenario.generate() does not return a tuple of (scenarios, roads).
        ImportError: If the module cannot be loaded from the specified file.

    """
    py_file = Path(py_file)

    if not py_file.exists():
        raise FileNotFoundError(f"Python file not found: {py_file}")

    module_name = f"_dynamic_{py_file.stem}"

    spec = importlib.util.spec_from_file_location(module_name, py_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {py_file}")

    module = importlib.util.module_from_spec(spec)

    try:
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    finally:
        # Clean up to avoid cross-test pollution
        sys.modules.pop(module_name, None)

    if not hasattr(module, "Scenario"):
        raise AttributeError("Module does not define 'Scenario'")

    Scenario = getattr(module, "Scenario")

    obj = Scenario()
    obj.naming = "numerical"

    result = obj.generate(py_file.parent)

    if not isinstance(result, tuple) or len(result) != 2:
        raise ValueError("Scenario.generate() must return (scenarios, roads)")

    scenarios, _ = result

    return [Path(BASE_DIR, scenario) for scenario in scenarios]
