from pathlib import Path
import pandas as pd

from scanner.ranker import compute_score
from scanner.filters import is_high_probability


def generate_combined_report(input_dir: Path, output_file: Path):
    all_rows = []

    for csv_file in input_dir.glob("*.csv"):
        df = pd.read_csv(csv_file)
        if df.empty:
            continue

        for _, row in df.iterrows():
            row_dict = row.to_dict()

            if not is_high_probability(row_dict):
                continue

            row_dict["score"] = compute_score(row_dict)
            all_rows.append(row_dict)

    if not all_rows:
        return None

    final_df = pd.DataFrame(all_rows)
    final_df = final_df.sort_values(by="score", ascending=False)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_file, index=False)
    return output_file
