"""Clean the raw green-area files: drop cloudy images and statistical outliers.

    python src/clean_data.py --input data/raw --output data/cleaned

Steps, as in the original study:
  1. keep an image only if its cloud cover is at most 50%
  2. drop images with a measured green area below 1 (the image was effectively all cloud or water)
  3. within each (city, month, year) group, drop outliers outside Q1 - 1.5*IQR .. Q3 + 1.5*IQR
"""
import argparse
from pathlib import Path

import pandas as pd


def remove_outliers(group):
    q1, q3 = group["green area"].quantile(0.25), group["green area"].quantile(0.75)
    iqr = q3 - q1
    return group[(group["green area"] >= q1 - 1.5 * iqr) & (group["green area"] <= q3 + 1.5 * iqr)]


def clean(df):
    df = df[(df["cloud cover percentage"].isna()) | (df["cloud cover percentage"].astype(float) <= 50)]
    df = df[df["green area"] >= 1]
    return df.groupby(["city", "month", "year"], group_keys=False).apply(remove_outliers).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", default="data/raw")
    parser.add_argument("--output", default="data/cleaned")
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    for path in sorted(Path(args.input).glob("*.csv")):
        cleaned = clean(pd.read_csv(path))
        cleaned.to_csv(out / f"cleaned_{path.name}", index=False)
        print(f"{path.name}: {len(pd.read_csv(path))} -> {len(cleaned)} rows")


if __name__ == "__main__":
    main()
