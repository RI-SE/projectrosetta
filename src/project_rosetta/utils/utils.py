from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

LOGS_DIR = BASE_DIR / "logs"

load_dotenv()

# Resolve esmini directory
_esmini_base = BASE_DIR / "esmini"
if (_esmini_base / "bin").exists():
    ESMINI_DIR = _esmini_base
else:
    match = next((d for d in _esmini_base.iterdir() if d.is_dir() and (d / "bin").exists()), None)
    if match is None:
        raise FileNotFoundError(
            "No esmini installation found. Run 'poetry run esmini-setup' first."
        )
    ESMINI_DIR = match
print(f"Using ESMINI_DIR: {ESMINI_DIR}")


@dataclass
class CommandResult:
    """Result of running a command, including return code, stdout, and stderr."""

    returncode: int
    stdout: str
    stderr: str
