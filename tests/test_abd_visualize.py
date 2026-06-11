from unittest.mock import MagicMock, patch

from project_rosetta.cli.abd_visualize import main


@patch("project_rosetta.cli.abd_visualize.run_esmini")
def test_abd_visualize_runs_esmini_with_window(mock_run, tmp_path):
    """Convert an ABD log and launch esmini."""
    log_path = tmp_path / "abd.txt"
    log_path.write_text(
        "\n".join(
            [
                "Anthony Best Dynamics Ltd",
                "Points=2",
                (
                    "System Time\tActual X (front axle)\tActual Y (front axle)"
                    "\tActual X (rear axle)\tActual Y (rear axle)"
                ),
                "s\tm\tm\tm\tm",
                "10,0\t2,0\t0,0\t0,0\t0,0",
                "11,0\t4,0\t0,0\t2,0\t0,0",
            ]
        ),
        encoding="ISO-8859-1",
    )
    config_contents = []

    def run_esmini(config_path):
        config_contents.append(config_path.read_text())
        return MagicMock(returncode=0)

    mock_run.side_effect = run_esmini

    assert main([str(log_path)]) == 0
    assert "window: 60 60 800 400" in config_contents[0]
