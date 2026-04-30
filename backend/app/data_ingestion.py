from typing import List, Dict
import pandas as pd


def ingest_rwanda_csv(file_path: str) -> List[Dict]:
    df = pd.read_csv(file_path)

    required_cols = ["region", "time", "adoption"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    grouped = df.groupby("region")
    dataset = []

    for region, group in grouped:
        group_sorted = group.sort_values("time")
        dataset.append({
            "region": region,
            "time_series": group_sorted["adoption"].tolist(),
        })

    return dataset
