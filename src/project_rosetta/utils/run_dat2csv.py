import subprocess
from pathlib import Path

from project_rosetta.utils.utils import ESMINI_DIR, CommandResult


def run_dat2csv(
    dat_file: Path | str,
    csv_file: Path | str,
    cwd: Path | str = ESMINI_DIR,
) -> CommandResult:
    """
    Run the dat2csv conversion process.

    Args:
        dat_file: Path to the input .dat file.
        csv_file: Path to the output .csv file.
        cwd: Working directory for the command.

    Returns:
        CommandResult with return code, stdout, stderr.

    """
    command = [
        "./bin/dat2csv",
        str(dat_file),
        "--csv",
        str(csv_file),
        "--precision",
        "16"
    ]

    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"dat2csv stdout: {result.stdout}")
        raise RuntimeError(f"dat2csv failed with exit code {result.returncode}. See stderr for details.")

    return CommandResult(
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )
