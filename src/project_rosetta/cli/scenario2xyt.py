import argparse
import shutil
from datetime import datetime
from pathlib import Path

from project_rosetta.utils.csv2xyt import run_csv2xyt
from project_rosetta.utils.paths import LOGS_DIR
from project_rosetta.utils.run_dat2csv import run_dat2csv
from project_rosetta.utils.run_esmini import run_esmini, setup_run_config

ALLOWED_SCENARIO_SUFFIXES = {".py", ".xosc"}


class ScenarioRunner:
    """Class to manage the execution of a scenario and conversion to XYT format."""

    def __init__(self, scenario_path: Path):
        self.scenario_path = scenario_path
        self.scenario_name = scenario_path.stem

    def set_log_path(self, log_folder: Path | None = None) -> Path:
        """
        Set the log folder path for the scenario runner.

        Args:
            log_folder:
                Optional custom log folder name. If None, a timestamped folder will be created.

        Returns:
            The path to the log folder.

        """
        if log_folder is None:
            log_folder = Path(LOGS_DIR, datetime.now().strftime("%Y%m%d_%H%M%S"))
        else:
            log_folder = Path(LOGS_DIR, log_folder)
        log_folder.mkdir(parents=True, exist_ok=True)
        self.log_folder = log_folder
        return log_folder

    def setup(self, log_folder: Path | None = None) -> None:
        """
        Set up the scenario runner by preparing the log folder and copying necessary files.

        Args:
            log_folder:
                Optional custom log folder name. If None, a timestamped folder will be created.

        """
        print(f"Setting up scenario runner for: {self.scenario_path}")
        self.set_log_path(log_folder)
        self.scenario_path = copy_file_to_folder(self.scenario_path, self.log_folder)
        print(f"Scenario file copied to log folder: {self.scenario_path}")

        self.dat_file = Path(self.log_folder) / f"{self.scenario_name}.dat"
        self.csv_file = Path(self.log_folder) / f"{self.scenario_name}.csv"
        self.xyt_dir = Path(self.log_folder) / f"{self.scenario_name}_xyt"

        self.esmini_run_config = setup_run_config(
            self.scenario_path, self.scenario_path.parent / self.scenario_path.stem, window=False
        )
        self.esmini_run_config = copy_file_to_folder(self.esmini_run_config, self.log_folder)
        print(f"esmini run config set up: {self.esmini_run_config}")

    def run(self) -> None:
        """Run the scenario through esmini, convert the output to CSV, and then to XYT format."""
        print(f"Running esmini with config: {self.esmini_run_config}")
        run_esmini(self.esmini_run_config)

        run_dat2csv(self.dat_file, self.csv_file)

        run_csv2xyt(self.csv_file, self.xyt_dir, columns=["x", "y", "time"])


def scenario_path_arg(value: str) -> Path:
    """
    Validate and normalize supported scenario file paths.

    Args:
        value: The scenario file path as a string.

    Returns:
        The validated and normalized scenario file path as a Path object.

    Raises:
        argparse.ArgumentTypeError: If the file extension is not supported.

    """
    path = Path(value)
    suffix = path.suffix.lower()
    if suffix not in ALLOWED_SCENARIO_SUFFIXES:
        allowed = ", ".join(sorted(ALLOWED_SCENARIO_SUFFIXES))
        raise argparse.ArgumentTypeError(
            f"Unsupported scenario file extension '{path.suffix}'. Expected one of: {allowed}."
        )
    return path


def args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse CLI arguments for scenario-to-XYT conversion.

    Args:
        argv: Optional list of command-line arguments. If None, defaults to sys.argv.

    Returns:
        An argparse.Namespace object containing the parsed arguments.

    """
    parser = argparse.ArgumentParser(description="Convert a scenario into XYT files.")
    parser.add_argument(
        "scenario_path",
        type=scenario_path_arg,
        help="Path to a scenario file (.py or .xosc).",
    )
    parser.add_argument(
        "--window",
        default=False,
        action="store_true",
        help="Run esmini with viewer.",
    )
    return parser.parse_args(argv)


def copy_file_to_folder(file_path: Path, folder: Path) -> None:
    """
    Copy a file to a specified folder.

    Args:
        file_path: The path to the file to be copied.
        folder: The destination folder.

    Returns:
        The path to the copied file.

    Raises:
        FileNotFoundError: If the source file does not exist.
        NotADirectoryError: If the destination folder does not exist.

    """
    if not file_path.is_file():
        raise FileNotFoundError(f"{file_path} does not exist or is not a file.")
    if not folder.is_dir():
        raise NotADirectoryError(f"{folder} does not exist or is not a directory.")
    destination = folder / file_path.name
    shutil.copy2(file_path, destination)
    return destination


def main(argv: list[str] | None = None) -> int:
    """
    Run the scenario2xyt CLI command.

    Returns:
        Exit status code.

    """
    parsed_args = args(argv)
    scenario_path = parsed_args.scenario_path

    scenario_run = ScenarioRunner(scenario_path)
    scenario_run.setup()
    scenario_run.run()

    return 0
