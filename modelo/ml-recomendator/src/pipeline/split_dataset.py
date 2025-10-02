from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split


def main():
    ap = argparse.ArgumentParser(description="Train/test split stratificado")
    ap.add_argument("--in", dest="inp", required=True, type=Path)
    ap.add_argument("--train", required=True, type=Path)
    ap.add_argument("--test", required=True, type=Path)
    ap.add_argument("--stratify", default="label_status")
    ap.add_argument("--test_size", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    df = pd.read_csv(a.inp)
    y = df[a.stratify] if a.stratify in df.columns else None
    tr, te = train_test_split(df, test_size=a.test_size, random_state=a.seed, stratify=y)
    a.train.parent.mkdir(parents=True, exist_ok=True)
    tr.to_csv(a.train, index=False)
    te.to_csv(a.test, index=False)

if __name__ == "__main__":
    main()
