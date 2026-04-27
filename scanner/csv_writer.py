from pathlib import Path
from typing import Dict, List

import pandas as pd


CSV_COLUMNS = [
    "strategy_name",
    "market",
    "stage",
    "symbol",
    "signal_side",
    "scan_time",
    "entry_price",
    "stop_loss",
    "target_price",
    "rr_ratio",
    "reason",
]


def write_strategy_csv(output_dir: Path, strategy_name: str, rows: List[Dict]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / f"{strategy_name}.csv"

    if rows:
        df = pd.DataFrame(rows)
    else:
        df = pd.DataFrame(columns=CSV_COLUMNS)

    missing_columns = [col for col in CSV_COLUMNS if col not in df.columns]
    for col in missing_columns:
        df[col] = ""

    df = df[CSV_COLUMNS]
    df.to_csv(csv_path, index=False)

    return csv_path