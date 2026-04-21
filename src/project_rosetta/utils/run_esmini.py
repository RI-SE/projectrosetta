import argparse
import subprocess
from datetime import datetime
from pathlib import Path

ESMINI_DEMO_DIR = Path("esmini/esmini-demo")


def args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse CLI arguments for running esmini.

    Args:
        argv: Optional list of command-line arguments. If None, defaults to sys.argv.

    Returns:
        An argparse.Namespace object containing the parsed arguments.

    """
    parser = argparse.ArgumentParser(description="Run an esmini scenario.")
    parser.add_argument(
        "--osc",
        required=True,
        help="Path to the OpenSCENARIO file, relative to the esmini demo directory.",
    )
    parser.add_argument(
        "--record",
        default=f"replay_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dat",
        help="Output path for the recorded replay file.",
    )
    parser.add_argument(
        "--window",
        nargs=4,
        metavar=("X", "Y", "WIDTH", "HEIGHT"),
        default=["60", "60", "800", "400"],
        help="Window geometry as four integers: X Y WIDTH HEIGHT.",
    )
    parser.add_argument(
        "esmini_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments passed through to the esmini binary.",
    )
    return parser.parse_args(argv)


def run_esmini(config_file: Path | str) -> int:
    """
    Run esmini with the specified configuration file.

    Args:
        config_file: Path to the esmini configuration file.

    Returns:
        Exit status code.

    """
    command = [
        "./bin/esmini",
        "--config_file_path",
        str(config_file),
    ]
    result = subprocess.run(
        command,
        cwd=ESMINI_DEMO_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.returncode


def setup_run_config(
    scenario_path: Path | str, record_file: Path | str, window: bool = False
) -> Path:
    """
    Set up the esmini run configuration file.

    Args:
        scenario_path: Path to the OpenSCENARIO file.
        record_file: Path to the recorded replay file.
        window: Whether to enable the windowed mode.

    Returns:
        Path to the generated configuration file.

    """
    config_path = "esmini_run_config.yml"
    with open(config_path, "w") as f:
        f.write("esmini:\n")
        f.write(f"\tosc: {scenario_path}\n")
        f.write(f"\trecord: {record_file}.dat\n")
        if window:
            f.write("\twindow: 60 60 800 400\n")
        else:
            f.write("\theadless: true\n")

    return Path(config_path)


def main(argv: list[str] | None = None) -> int:
    """
    Run the esmini CLI command.

    Returns:
        Exit status code.

    """
    return run_esmini(args(argv))
