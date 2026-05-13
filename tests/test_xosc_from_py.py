import pytest

from project_rosetta.utils.xosc_from_py import py2xosc


def test_py2xosc_success(tmp_path):
    """
    Test that py2xosc correctly generates OpenSCENARIO files from a valid Python
    scenario definition.
    """
    py_file = tmp_path / "scenario.py"

    py_file.write_text(
        """
class Scenario:
    def __init__(self):
        self.naming = None

    def generate(self, path):
        return ["file1.xosc", "file2.xosc"], []
"""
    )

    result = py2xosc(py_file)

    assert len(result) == 2
    assert result[0].name == "file1.xosc"


def test_py2xosc_missing_file():
    """
    "Test that py2xosc raises FileNotFoundError when the input Python file does
    not exist.
    """
    with pytest.raises(FileNotFoundError):
        py2xosc("nonexistent.py")


def test_py2xosc_no_scenario(tmp_path):
    """
    Test that py2xosc raises AttributeError when the Python file does not define a
    Scenario class.
    """
    py_file = tmp_path / "bad.py"
    py_file.write_text("x = 1")

    with pytest.raises(AttributeError):
        py2xosc(py_file)


def test_py2xosc_invalid_return(tmp_path):
    """
    Test that py2xosc raises ValueError when Scenario.generate() does not return a
    tuple of (scenarios, roads).
    """
    py_file = tmp_path / "bad.py"

    py_file.write_text(
        """
class Scenario:
    def generate(self, path):
        return ["only_one_value"]
"""
    )

    with pytest.raises(ValueError):
        py2xosc(py_file)
