from __future__ import annotations
import argparse
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt

# Placeholder: save dummy plots to expected locations

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", type=Path, required=True)
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--pre", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    # Create placeholders
    for name in ["rf_confusion_matrix.png", "rf_roc_micro.png", "rf_pr_micro.png"]:
        p = a.out / name
        fig, ax = plt.subplots(figsize=(4,3))
        ax.text(0.5, 0.5, name, ha='center', va='center')
        ax.axis('off')
        fig.savefig(p, bbox_inches='tight')
        plt.close(fig)

if __name__ == "__main__":
    main()
