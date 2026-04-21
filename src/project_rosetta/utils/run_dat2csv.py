import argparse
import subprocess
from datetime import datetime
from pathlib import Path

ESMINI_DEMO_DIR = Path("esmini/esmini-demo")


def args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse CLI arguments for dat2csv conversion.

    Args:
        argv: Optional list of command-line arguments. If None, defaults to sys.argv.

    Returns:
        An argparse.Namespace object containing the parsed arguments.

    """
    parser = argparse.ArgumentParser(description="Convert a dat2csv scenario.")
    parser.add_argument(
        "--dat",
        required=True,
        help="Path to the .dat file, relative to the esmini demo directory.",
    )
    parser.add_argument(
        "--csv",
        default=f"replay_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        help="Output path for the converted CSV file.",
    )
    return parser.parse_args(argv)


def run_dat2csv(dat_file: Path | str, csv_file: Path | str) -> int:
    """
    Run the dat2csv conversion process.

    Args:
        dat_file: Path to the input .dat file.
        csv_file: Path to the output .csv file.

    Returns:
        Exit status code.

    """
    command = [
        "./bin/dat2csv",
        str(dat_file),
        "--csv",
        str(csv_file),
    ]
    print(command)
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
