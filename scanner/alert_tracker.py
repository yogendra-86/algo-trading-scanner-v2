from pathlib import Path
import pandas as pd


TRACKER_COLUMNS = [
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
    "score",
]


def save_alerted_signals(final_report_path: Path, tracker_path: Path, top_n: int = 3) -> Path | None:
    if not final_report_path.exists():
        return None

    df = pd.read_csv(final_report_path)
    if df.empty:
        return None

    if "score" in df.columns:
        df = df.sort_values(by="score", ascending=False)

    long_df = df[df["signal_side"].astype(str).str.upper() == "LONG"].head(top_n)
    short_df = df[df["signal_side"].astype(str).str.upper() == "SHORT"].head(top_n)
    selected = pd.concat([long_df, short_df], ignore_index=True)

    if selected.empty:
        return None

    for col in TRACKER_COLUMNS:
        if col not in selected.columns:
            selected[col] = ""

    tracker_path.parent.mkdir(parents=True, exist_ok=True)
    selected[TRACKER_COLUMNS].to_csv(tracker_path, index=False)
    return tracker_path
