from unittest.mock import MagicMock, patch

from project_rosetta.utils.run_esmini import build_esmini_config, run_esmini, setup_run_config


def test_build_esmini_config_headless():
    """Test that the config is built correctly for headless mode."""
    result = build_esmini_config("scenario.xosc", "record")

    assert "osc: scenario.xosc" in result
    assert "record: record.dat" in result
    assert "headless: true" in result


def test_build_esmini_config_window():
    """Test that the config is built correctly for window mode."""
    result = build_esmini_config("scenario.xosc", "record", window=True)

    assert "window: 60 60 800 400" in result
    assert "headless" not in result


def test_setup_run_config(tmp_path):
    """Test that the config file is created with the correct content."""
    output_file = tmp_path / "config.yml"

    path = setup_run_config("scenario.xosc", "record", output_path=output_file)

    assert path.exists()
    content = path.read_text()

    assert "scenario.xosc" in content


@patch("project_rosetta.utils.run_esmini.subprocess.run")
def test_run_esmini(mock_run):
    """Test that run_esmini correctly runs the subprocess and returns the expected result."""
    mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")

    result = run_esmini("config.yml", cwd=".")

    assert result.returncode == 0
    assert result.stdout == "ok"


@patch("project_rosetta.utils.run_esmini.subprocess.run")
def test_run_esmini_writes_log_file(mock_run, tmp_path):
    """Test that run_esmini persists the subprocess output when a log path is provided."""
    mock_run.return_value = MagicMock(returncode=7, stdout="stdout text", stderr="stderr text")
    log_file = tmp_path / "esmini.log"

    run_esmini("config.yml", cwd=".", log_file=log_file)

    assert log_file.exists()
    content = log_file.read_text()

    assert "Command: ./bin/esmini --config_file_path config.yml" in content
    assert "Return code: 7" in content
    assert "[stdout]" in content
    assert "stdout text" in content
    assert "[stderr]" in content
    assert "stderr text" in content
