from pathlib import Path
from unittest.mock import patch

import pytest

from project_rosetta.utils.scenario_files import (
    adjust_catalogs,
    adjust_references,
    copy_file_to_folder,
    copy_to,
    generate_scenario_dir_tree,
    get_catalog_locations_dict,
    get_xodr_file_path_from_xosc_file_path,
    scenario_list_handler,
)


def test_copy_file_to_folder_success(tmp_path):
    """Test that copy_file_to_folder successfully copies a file to the destination folder."""
    src = tmp_path / "test.txt"
    src.write_text("hello")

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    result = copy_file_to_folder(src, dest_dir)

    assert result.exists()
    assert result.read_text() == "hello"
    assert result.parent == dest_dir


def test_copy_file_to_folder_missing_file(tmp_path):
    """Test that copy_file_to_folder raises FileNotFoundError when the source file is missing."""
    src = tmp_path / "missing.txt"

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    with pytest.raises(FileNotFoundError):
        copy_file_to_folder(src, dest_dir)


def test_copy_file_to_folder_missing_directory(tmp_path):
    """
    Test that copy_file_to_folder raises NotADirectoryError when the destination
    directory is missing.
    """
    src = tmp_path / "test.txt"
    src.write_text("hello")

    dest_dir = tmp_path / "missing_dir"

    with pytest.raises(NotADirectoryError):
        copy_file_to_folder(src, dest_dir)


@patch("project_rosetta.utils.scenario_files.py2xosc")
def test_scenario_list_handler_py(mock_py2xosc):
    """Test that scenario_list_handler correctly handles Python scenario files."""
    mock_py2xosc.return_value = [Path("generated.xosc")]

    result = scenario_list_handler(["scenario.py"])

    assert result == [Path("generated.xosc")]


def test_scenario_list_handler_xosc():
    """Test that scenario_list_handler correctly handles OpenSCENARIO files."""
    result = scenario_list_handler(["scenario.xosc"])

    assert result == [Path("scenario.xosc")]


def test_scenario_list_handler_invalid():
    """Test that scenario_list_handler raises ValueError for unsupported file types."""
    with pytest.raises(ValueError):
        scenario_list_handler(["scenario.txt"])


def test_generate_scenario_dir_tree(tmp_path):
    """Test that generate_scenario_dir_tree correctly creates the directory structure."""
    xosc_dir, xodr_dir = generate_scenario_dir_tree(tmp_path)

    assert xosc_dir.exists()
    assert xodr_dir.exists()

    assert xosc_dir.name == "xosc"
    assert xodr_dir.name == "xodr"


def test_get_xodr_file_path_from_xosc_file_path(tmp_path):
    """
    Test that get_xodr_file_path_from_xosc_file_path correctly extracts the xodr
    file path from the xosc file.
    """
    xosc = tmp_path / "scenario.xosc"

    xosc.write_text(
        """
        <OpenSCENARIO>
            <RoadNetwork>
                <LogicFile filepath="road.xodr"/>
            </RoadNetwork>
        </OpenSCENARIO>
        """
    )

    result = get_xodr_file_path_from_xosc_file_path(xosc)

    assert result == Path("road.xodr")


def test_get_xodr_file_path_missing_roadnetwork(tmp_path):
    """
    Test that get_xodr_file_path_from_xosc_file_path returns None when the
    RoadNetwork is missing.
    """
    xosc = tmp_path / "scenario.xosc"

    xosc.write_text("<OpenSCENARIO></OpenSCENARIO>")

    result = get_xodr_file_path_from_xosc_file_path(xosc)

    assert result is None


def test_get_catalog_locations_dict(tmp_path):
    """
    Test that get_catalog_locations_dict correctly extracts the catalog locations
    from the xosc file.
    """
    xosc = tmp_path / "scenario.xosc"

    xosc.write_text(
        """
        <OpenSCENARIO>
            <CatalogLocations>
                <VehicleCatalog>
                    <Directory path="Catalogs/Vehicles"/>
                </VehicleCatalog>
            </CatalogLocations>
        </OpenSCENARIO>
        """
    )

    result = get_catalog_locations_dict(xosc)

    assert result == {"VehicleCatalog": "Catalogs/Vehicles"}


def test_get_catalog_locations_dict_missing(tmp_path):
    """Test that get_catalog_locations_dict returns None when the CatalogLocations are missing."""
    xosc = tmp_path / "scenario.xosc"

    xosc.write_text("<OpenSCENARIO></OpenSCENARIO>")

    result = get_catalog_locations_dict(xosc)

    assert result is None


def test_adjust_catalogs_success(tmp_path):
    """
    Test that adjust_catalogs correctly adjusts the catalog paths and returns
    the adjusted catalogs.
    """
    original_scenario = tmp_path / "scenario.py"
    original_scenario.write_text("")

    catalogs_dir = tmp_path / "VehicleCatalogs"
    catalogs_dir.mkdir()

    (catalogs_dir / "car.xml").write_text("data")

    xosc_dir = tmp_path / "generated"
    xosc_dir.mkdir()

    xosc_file = xosc_dir / "scenario.xosc"
    xosc_file.write_text("")

    catalogs = {"VehicleCatalog": "VehicleCatalogs"}

    result = adjust_catalogs(
        original_scenario,
        xosc_file,
        catalogs,
    )

    assert "VehicleCatalog" in result


def test_adjust_catalogs_missing_catalog(tmp_path):
    """Test that adjust_catalogs returns None when a catalog is missing."""
    original_scenario = tmp_path / "scenario.py"
    original_scenario.write_text("")

    xosc_file = tmp_path / "scenario.xosc"
    xosc_file.write_text("")

    catalogs = {"VehicleCatalog": "missing_catalog"}

    result = adjust_catalogs(
        original_scenario,
        xosc_file,
        catalogs,
    )

    assert result is None


@patch("project_rosetta.utils.scenario_files.write_xosc_with_updated_catalogs_and_xodr_reference")
@patch("project_rosetta.utils.scenario_files.adjust_catalogs")
@patch("project_rosetta.utils.scenario_files.get_catalog_locations_dict")
def test_adjust_references_success(
    mock_get_catalogs,
    mock_adjust_catalogs,
    mock_write,
):
    """
    Test that adjust_references correctly resolves the catalogs, adjusts the references,
    and writes the updated xosc file.
    """
    mock_get_catalogs.return_value = {"VehicleCatalog": "Catalogs/Vehicles"}

    mock_adjust_catalogs.return_value = {"VehicleCatalog": "catalogs/Vehicles"}

    adjust_references(
        Path("scenario.py"),
        Path("scenario.xosc"),
        Path("road.xodr"),
    )

    mock_write.assert_called_once()


@patch("project_rosetta.utils.scenario_files.get_catalog_locations_dict")
def test_adjust_references_no_catalogs(mock_get_catalogs):
    """Test that adjust_references raises ValueError when no catalogs are found."""
    mock_get_catalogs.return_value = None

    with pytest.raises(ValueError):
        adjust_references(
            Path("scenario.py"),
            Path("scenario.xosc"),
            Path("road.xodr"),
        )


@patch("project_rosetta.utils.scenario_files.adjust_references")
def test_copy_to_success(mock_adjust, tmp_path):
    """Test that copy_to successfully copies the xosc file and adjusts the references."""
    xosc = tmp_path / "scenario.xosc"
    xosc.write_text(
        """
        <OpenSCENARIO>
            <RoadNetwork>
                <LogicFile filepath="road.xodr"/>
            </RoadNetwork>
        </OpenSCENARIO>
        """
    )

    xodr = tmp_path / "road.xodr"
    xodr.write_text("road")

    dest = tmp_path / "dest"
    dest.mkdir()

    result = copy_to(
        dest,
        xosc,
        xosc,
    )

    assert result.exists()
    mock_adjust.assert_called_once()


@patch("project_rosetta.utils.scenario_files.get_xodr_file_path_from_xosc_file_path")
def test_copy_to_missing_xodr(mock_get_xodr, tmp_path):
    """Test that copy_to raises FileNotFoundError when the xodr file is missing."""
    mock_get_xodr.return_value = None

    xosc = tmp_path / "scenario.xosc"
    xosc.write_text("")

    dest = tmp_path / "dest"
    dest.mkdir()

    with pytest.raises(FileNotFoundError):
        copy_to(
            dest,
            xosc,
            xosc,
        )
