from __future__ import annotations
import argparse
from pathlib import Path
import math
import pandas as pd

# WHO LMS loader (boys + girls) from data/raw/who

def _load_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalize column names
    cols = {c: c.strip().replace(" ", "_") for c in df.columns}
    df = df.rename(columns=cols)
    # Try common names
    if "Month" in df.columns:
        df = df.rename(columns={"Month": "month"})
    if "month" not in df.columns:
        # Try lowercase variations
        for c in df.columns:
            if c.lower() == "month":
                df = df.rename(columns={c: "month"})
                break
    return df


def _lms_cat(who_dir: Path, sex: str) -> pd.DataFrame:
    parts = []
    if sex == "M":
        for pat in [
            "bmi_boys_0-to-2-years_zcores_1.csv",
            "bmi_boys_2-to-5-years_zscores.csv",
            "bmifa-boys-5-19years-z.csv",
        ]:
            p = who_dir / pat
            if p.exists():
                df = _load_table(p)
                parts.append(df[["month", "L", "M", "S"]].assign(sex=sex))
    else:
        for pat in [
            "tab_bmi_girls_p_0_2.csv",
            "tab_bmi_girls_p_2_5.csv",
            "bmifa-girls-5-19years-z.csv",
        ]:
            p = who_dir / pat
            if p.exists():
                df = _load_table(p)
                parts.append(df[["month", "L", "M", "S"]].assign(sex=sex))
    if not parts:
        raise FileNotFoundError(f"No WHO LMS tables found for sex={sex} under {who_dir}")
    out = pd.concat(parts, ignore_index=True)
    out["month"] = out["month"].astype(int)
    return out.drop_duplicates(subset=["sex", "month"]).sort_values(["sex", "month"]).reset_index(drop=True)


def _load_lms(who_dir: Path) -> pd.DataFrame:
    return pd.concat([_lms_cat(who_dir, "M"), _lms_cat(who_dir, "F")], ignore_index=True)


def _baz_from_bmi(bmi: float, L: float, M: float, S: float) -> float:
    if L == 0:
        return math.log(bmi / M) / S
    return ((bmi / M) ** L - 1) / (L * S)


def _nearest_lms(df: pd.DataFrame, sex: str, month: int) -> tuple[float, float, float]:
    d = df[df["sex"] == sex]
    if d.empty:
        raise ValueError(f"Sex {sex} not in LMS table")
    row = d[d["month"] == month]
    if not row.empty:
        r = row.iloc[0]
        return float(r["L"]), float(r["M"]), float(r["S"])
    nearest = d.iloc[(d["month"] - month).abs().argsort().iloc[0]]
    return float(nearest["L"]), float(nearest["M"]), float(nearest["S"])


def _ensure_children_cols(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    required = ["age_months", "sex"]
    if not all(c in cols for c in required):
        raise ValueError("Se requieren columnas: age_months, sex")
    # BMI from columns if needed
    if "bmi" in cols:
        df["BMI"] = df[cols["bmi"]]
    else:
        if "weight_kg" in cols and "height_cm" in cols:
            w = df[cols["weight_kg"]].astype(float)
            h_m = df[cols["height_cm"]].astype(float) / 100.0
            df["BMI"] = w / (h_m ** 2)
        else:
            raise ValueError("Se requiere BMI o (weight_kg y height_cm)")
    df["age_months"] = df[cols["age_months"]].astype(int)
    df["sex"] = df[cols["sex"]].astype(str).str.strip().str[0].str.upper()
    return df


def classify_from_baz(z: float) -> int:
    if z < -3 or z > 3:
        return 2
    if (-3 <= z < -2) or (2 < z <= 3):
        return 1
    return 0


def run(input_dir: Path, who_dir: Path, out_csv: Path) -> None:
    who = _load_lms(who_dir)
    # Merge all CSVs in input_dir
    files = sorted(list(input_dir.glob("*.csv")))
    if not files:
        raise FileNotFoundError(f"No CSV files in {input_dir}")
    frames = [pd.read_csv(p) for p in files]
    df = pd.concat(frames, ignore_index=True)
    df = _ensure_children_cols(df)
    # Compute BAZ per row
    z_list = []
    for _, row in df.iterrows():
        L, M, S = _nearest_lms(who, row["sex"], int(round(row["age_months"])) )
        z = _baz_from_bmi(float(row["BMI"]), L, M, S)
        z_list.append(z)
    df["baz"] = z_list
    df["label_status"] = [classify_from_baz(z) for z in z_list]
    df.to_csv(out_csv, index=False)


def main():
    ap = argparse.ArgumentParser(description="Label dataset with BAZ using WHO tables")
    ap.add_argument("--in", dest="inp", required=True, type=Path, help="Input folder with surveys CSVs")
    ap.add_argument("--who", dest="who", required=True, type=Path, help="WHO tables folder")
    ap.add_argument("--out", dest="out", required=True, type=Path, help="Output labeled CSV")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    run(args.inp, args.who, args.out)

if __name__ == "__main__":
    main()
