import pandas as pd
from pathlib import Path


def load_dpr(file_path: str | Path) -> pd.DataFrame:
    """Load DPR file (CSV or JSON) into a pandas DataFrame.

    Supported formats:
    - .csv: expects columns [date, activity, progress]
    - .json: list of dicts with same keys
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"DPR file not found: {file_path}")

    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path, parse_dates=["date"])
    elif file_path.suffix.lower() in {".json", ".ndjson"}:
        df = pd.read_json(file_path, convert_dates=["date"])
    else:
        raise ValueError("Unsupported DPR file format. Use .csv or .json")

    required_cols = {"date", "activity", "progress"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"DPR file must contain columns {required_cols}")

    return df