"""esmini setup for project-rosetta."""

import argparse
import os
import shutil
import stat
import zipfile

import requests
from dotenv import load_dotenv


ESMINI_RELEAVE_VERSION = "v3.0.1"

# Currently not used, only demo atm
ESMINI_BIN_URL = f"https://github.com/esmini/esmini/releases/download/{ESMINI_RELEAVE_VERSION}/esmini-bin_Linux.zip"
ESMINI_SRC_URL = f"https://github.com/esmini/esmini/archive/refs/tags/{ESMINI_RELEAVE_VERSION}.zip"
ESMINI_BIN = "esmini_bin"
ESMINI_SRC = "esmini_src"

ESMINI_DEMO_URL = f"https://github.com/esmini/esmini/releases/download/{ESMINI_RELEAVE_VERSION}/esmini-demo_Linux.zip"
ESMINI_DEMO = "esmini_demo"


OUTPUT_FOLDER = "esmini"


def ensure_executable(path):
    """
    Ensure the given file is executable.

    Args:
        path: Path to the file to check and modify.

    Raises:
        FileNotFoundError: If the specified file does not exist.

    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"{path} not found")

    st = os.stat(path)
    if not (st.st_mode & stat.S_IXUSR):
        # Add execute bit for user (and optionally group/others)
        os.chmod(path, st.st_mode | stat.S_IXUSR)
        print(f"Made {path} executable")


def esmini_directory() -> None:
    """Ensure the output directory for esmini exists and is clean."""
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.mkdir(OUTPUT_FOLDER)


def fetch_esmini_zip(url: str, output_path: str) -> None:
    """
    Fetch a zip file from the given URL and save it to the specified output path.

    Args:
        url: URL of the zip file to fetch.
        output_path: Path to save the fetched zip file (without .zip extension).

    """
    response = requests.get(url)
    response.raise_for_status()

    with open(output_path + ".zip", "wb") as f:
        f.write(response.content)


def unzip_esmini(zip_file: str, output_dir: str) -> None:
    """
    Unzip the specified zip file into the given output directory.

    Args:
        zip_file: Path to the zip file (without .zip extension).
        output_dir: Directory to extract the contents to.

    """
    with zipfile.ZipFile(zip_file + ".zip", "r") as zip_ref:
        zip_ref.extractall(output_dir)


def setup_esmini() -> None:
    """Set up esmini by fetching and extracting necessary files."""
    print("Setting up esmini...")

    esmini_directory()

    files_to_fetch = [
        # [ESMINI_BIN_URL, ESMINI_BIN],
        # [ESMINI_SRC_URL, ESMINI_SRC],
        [ESMINI_DEMO_URL, ESMINI_DEMO]
    ]
    for url, output in files_to_fetch:
        print(f"Fetching {url}...")
        fetch_esmini_zip(url, output)
        print(f"Unzipping {output}...")
        unzip_esmini(output, OUTPUT_FOLDER)

    for binary in ["esmini", "dat2csv", "replayer"]:
        ensure_executable(os.path.join(OUTPUT_FOLDER, "bin", binary))

    
def setup_esmini_local(esmini_path: str | None = None) -> None:
    """
    Set up esmini from a local installation by symlinking to the output folder.

    Args:
        esmini_path: Path to the local esmini directory containing bin/.
                     Defaults to ESMINI_DIR environment variable.

    Raises:
        ValueError: If no local esmini path is provided or set in environment.
        FileNotFoundError: If the local esmini path does not exist.

    """
    load_dotenv()  # loads .env from current directory

    esmini_path = os.getenv("ESMINI_DIR")
    if not esmini_path:
        raise ValueError(
            "No local esmini path provided. Set ESMINI_DIR environment variable or pass esmini_path."
        )

    esmini_dir = os.path.abspath(esmini_path)
    if not os.path.isdir(esmini_dir):
        raise FileNotFoundError(f"Local esmini directory not found: {esmini_dir}")

    print(f"Setting up esmini from local path: {esmini_dir}")

    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)


    # Symlink the local esmini into the expected output structure
    link_target = os.path.join(OUTPUT_FOLDER)
    os.symlink(esmini_dir, link_target)
    print(f"Created symlink: {link_target} -> {esmini_dir}")

    for binary in ["esmini", "dat2csv", "replayer"]:
        ensure_executable(os.path.join(link_target, "bin", binary))



def args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse CLI arguments for esmini setup.

    Args:
        argv: Optional list of command-line arguments. If None, defaults to sys.argv.

    Returns:
        An argparse.Namespace object containing the parsed arguments.

    """
    parser = argparse.ArgumentParser(description="Set up esmini.")

    parser.add_argument(
        "--local",
        default=False,
        action="store_true",
        help="Setup local esmini installation.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """
    Run the esmini setup CLI command.
    If --local is specified, it will set up esmini from a local installation.
    Otherwise, it will fetch and set up esmini-demo from GitHub releases.
    
    Returns:
        Exit status code.

    """
    parsed_args = args(argv)
    if parsed_args.local:
        print("Setting up local esmini installation")
        setup_esmini_local()
    else:
        print("Setting up esmini from GitHub release")
        setup_esmini()

    print("Setup of esmini complete")
    return 0