from pathlib import Path

import pandas as pd


def remove_spaces_from_csv(csv_file: str, output_file: str) -> None:
    """
    Read a CSV file and remove all spaces from column names and values.

    Args:
        csv_file: Path to input CSV file
        output_file: Path to save the cleaned CSV file

    """
    df = pd.read_csv(csv_file)

    # Remove spaces from column names
    df.columns = df.columns.str.replace(" ", "")

    # Remove spaces from all string columns
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.replace(" ", "")

    df.to_csv(output_file, index=False)
    print(f"Cleaned CSV saved to {output_file}")


def run_csv2xyt(csv_file: str, output_dir: str, columns: list[str]) -> None:
    """
    Read a CSV file and generate separate CSV files for each id with specified columns.

    Args:
        csv_file: Path to input CSV file
        output_dir: Directory to save output CSV files
        columns: List of column names to extract (must include 'id')

    """
    # Read the CSV file
    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces from column names
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Get unique ids
    unique_ids = df["id"].unique()

    # Generate a file for each id
    for id_val in unique_ids:
        id_data = df[df["id"] == id_val][columns]

        output_file = Path(output_dir) / f"id_{id_val}.xyt"
        id_data.to_csv(output_file, index=False, header=False)
        print(f"Created {output_file}")


if __name__ == "__main__":
    # Example usage
    run_csv2xyt(
        csv_file="esmini/esmini-demo/replay_20260413_145844.csv",
        output_dir="output",
        columns=["x", "y", "time"],
    )
