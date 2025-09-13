import os
import pandas as pd
from sqlalchemy import create_engine, text

# ==== CONFIG ====
MYSQL_URL = "mysql+pymysql://root:root123456@localhost:3306/nutricion?charset=utf8mb4"
BASE_DIR = os.path.dirname(__file__)

FILES = [
    # Boys 0–2 y 2–5 (z-scores)
    ("bmi_boys_0-to-2-years_zcores.xlsx", "OMS_2006", "M", "z_0_5"),
    ("bmi_boys_2-to-5-years_zscores.xlsx", "OMS_2006", "M", "z_0_5"),
    # Girls 0–2 y 2–5 (percentiles)
    ("tab_bmi_girls_p_0_2.xlsx", "OMS_2006", "F", "p_0_5"),
    ("tab_bmi_girls_p_2_5.xlsx", "OMS_2006", "F", "p_0_5"),
    # 5–19 años (OMS 2007) — percentiles y z-scores
    ("bmifa-boys-5-19years-per.xlsx",  "OMS_2007", "M", "p_5_19"),
    ("bmifa-boys-5-19years-z.xlsx",    "OMS_2007", "M", "z_5_19"),
    ("bmifa-girls-5-19years-per.xlsx", "OMS_2007", "F", "p_5_19"),
    ("bmifa-girls-5-19years-z.xlsx",   "OMS_2007", "F", "z_5_19"),
]

engine = create_engine(MYSQL_URL, future=True)

# ---------- utilidades ----------

def has_cols(df: pd.DataFrame, cols: list[str]) -> bool:
    return set(cols).issubset(set(df.columns))

def read_who_excel(path: str) -> pd.DataFrame:
    """
    Lee XLSX OMS detectando la fila del encabezado real.
    Busca una fila que contenga al menos 'Month' y algunos de: L, M, S
    o etiquetas de z/percentiles (5–19).
    """
    raw = pd.read_excel(path, header=None)
    header_row = None

    targets_sets = [
        {"Month", "L", "M", "S"},
        {"Month", "-3 SD", "-2 SD", "-1 SD", "Median", "1 SD", "2 SD", "3 SD"},
        {"Month", "1st", "3rd", "5th", "15th", "25th", "50th", "75th", "85th", "95th", "97th", "99th"},
    ]

    max_scan = min(50, len(raw))
    for i in range(max_scan):
        row_vals = [str(x).strip() for x in raw.iloc[i].tolist()]
        row_set = set(row_vals)
        if any(t.issubset(row_set) for t in targets_sets):
            header_row = i
            break

    if header_row is not None:
        df = pd.read_excel(path, header=header_row)
    else:
        # fallback
        df = pd.read_excel(path)

    # normaliza nombres (quita espacios)
    df.columns = [str(c).strip() for c in df.columns]
    return df

# ---------- upserts ----------

def upsert_lms(df, version, sexo):
    # espera columnas: Month, L, M, S
    if not has_cols(df, ["Month", "L", "M", "S"]):
        print(f"   ⚠️  LMS omitido: faltan columnas Month/L/M/S en este archivo.")
        return
    df = df.rename(columns={"Month":"edad_meses"})
    df = df[["edad_meses","L","M","S"]].dropna()
    df["edad_meses"] = df["edad_meses"].astype(int)
    sql = text("""
        INSERT INTO oms_bmi_lms (version, sexo, edad_meses, L, M, S)
        VALUES (:v, :s, :m, :L, :M, :S)
        ON DUPLICATE KEY UPDATE L=VALUES(L), M=VALUES(M), S=VALUES(S)
    """)
    with engine.begin() as conn:
        conn.execute(sql, [
            dict(v=version, s=sexo, m=int(r.edad_meses), L=float(r.L), M=float(r.M), S=float(r.S))
            for r in df.itertuples(index=False)
        ])

def upsert_zscores_from_sdlabels(df, version, sexo):
    # 0–5 (boys) con SD3neg, SD2neg, SD1neg, SD0, SD1, SD2, SD3
    rename = {"Month":"edad_meses", "SD3neg":"sd_m3", "SD2neg":"sd_m2", "SD1neg":"sd_m1",
              "SD0":"median", "SD1":"sd_p1", "SD2":"sd_p2", "SD3":"sd_p3"}
    if not has_cols(df, ["Month","SD3neg","SD2neg","SD1neg","SD0","SD1","SD2","SD3"]):
        print("   ⚠️  Z 0–5 omitido: columnas SD* no encontradas.")
        return
    df = df.rename(columns=rename)
    need = ["edad_meses","sd_m3","sd_m2","sd_m1","median","sd_p1","sd_p2","sd_p3"]
    df = df[need].dropna(subset=["edad_meses"])
    df["edad_meses"] = df["edad_meses"].astype(int)
    sql = text("""
        INSERT INTO oms_bmi_zscores
        (lms_version, lms_sexo, lms_edad_meses, sd_m3, sd_m2, sd_m1, median, sd_p1, sd_p2, sd_p3)
        VALUES (:v, :s, :m, :sdm3, :sdm2, :sdm1, :median, :sdp1, :sdp2, :sdp3)
        ON DUPLICATE KEY UPDATE
          sd_m3=VALUES(sd_m3), sd_m2=VALUES(sd_m2), sd_m1=VALUES(sd_m1),
          median=VALUES(median), sd_p1=VALUES(sd_p1), sd_p2=VALUES(sd_p2), sd_p3=VALUES(sd_p3)
    """)
    with engine.begin() as conn:
        conn.execute(sql, [
            dict(v=version, s=sexo, m=int(r.edad_meses),
                 sdm3=r.sd_m3, sdm2=r.sd_m2, sdm1=r.sd_m1,
                 median=r.median, sdp1=r.sd_p1, sdp2=r.sd_p2, sdp3=r.sd_p3)
            for r in df.itertuples(index=False)
        ])

def upsert_zscores_5_19(df, version, sexo):
    # 5–19 z-scores: -3 SD ... 3 SD
    if not has_cols(df, ["Month","-3 SD","-2 SD","-1 SD","Median","1 SD","2 SD","3 SD"]):
        print("   ⚠️  Z 5–19 omitido: columnas z no encontradas.")
        return
    # Carga LMS desde el mismo sheet (si está)
    upsert_lms(df, version, sexo)

    rename = {"Month":"edad_meses", "-3 SD":"sd_m3", "-2 SD":"sd_m2", "-1 SD":"sd_m1",
              "Median":"median", "1 SD":"sd_p1", "2 SD":"sd_p2", "3 SD":"sd_p3"}
    df = df.rename(columns=rename)
    need = ["edad_meses","sd_m3","sd_m2","sd_m1","median","sd_p1","sd_p2","sd_p3"]
    df = df[need].dropna(subset=["edad_meses"])
    df["edad_meses"] = df["edad_meses"].astype(int)
    sql = text("""
        INSERT INTO oms_bmi_zscores
        (lms_version, lms_sexo, lms_edad_meses, sd_m3, sd_m2, sd_m1, median, sd_p1, sd_p2, sd_p3)
        VALUES (:v, :s, :m, :sdm3, :sdm2, :sdm1, :median, :sdp1, :sdp2, :sdp3)
        ON DUPLICATE KEY UPDATE
          sd_m3=VALUES(sd_m3), sd_m2=VALUES(sd_m2), sd_m1=VALUES(sd_m1),
          median=VALUES(median), sd_p1=VALUES(sd_p1), sd_p2=VALUES(sd_p2), sd_p3=VALUES(sd_p3)
    """)
    with engine.begin() as conn:
        conn.execute(sql, [
            dict(v=version, s=sexo, m=int(r.edad_meses),
                 sdm3=r.sd_m3, sdm2=r.sd_m2, sdm1=r.sd_m1,
                 median=r.median, sdp1=r.sd_p1, sdp2=r.sd_p2, sdp3=r.sd_p3)
            for r in df.itertuples(index=False)
        ])

def upsert_percentiles_0_5(df, sexo):
    if not has_cols(df, ["Month","P01","P1","P3","P5","P10","P15","P25","P50","P75","P85","P90","P95","P97","P99","P999"]):
        print("   ⚠️  Percentiles 0–5 omitido: columnas no encontradas.")
        return
    # si el sheet trae LMS, también insertamos
    upsert_lms(df, "OMS_2006", sexo)

    df = df.rename(columns={"Month":"edad_meses"})
    keep = ["edad_meses","P01","P1","P3","P5","P10","P15","P25","P50","P75","P85","P90","P95","P97","P99","P999"]
    df = df[keep].dropna(subset=["edad_meses"])
    df["edad_meses"] = df["edad_meses"].astype(int)
    sql = text("""
        INSERT INTO oms_bmi_percentiles
          (lms_version, lms_sexo, lms_edad_meses, P01,P1,P3,P5,P10,P15,P25,P50,P75,P85,P90,P95,P97,P99,P999)
        VALUES
          ('OMS_2006', :s, :m, :P01,:P1,:P3,:P5,:P10,:P15,:P25,:P50,:P75,:P85,:P90,:P95,:P97,:P99,:P999)
        ON DUPLICATE KEY UPDATE
          P01=VALUES(P01), P1=VALUES(P1), P3=VALUES(P3), P5=VALUES(P5), P10=VALUES(P10),
          P15=VALUES(P15), P25=VALUES(P25), P50=VALUES(P50), P75=VALUES(P75),
          P85=VALUES(P85), P90=VALUES(P90), P95=VALUES(P95), P97=VALUES(P97),
          P99=VALUES(P99), P999=VALUES(P999)
    """)
    with engine.begin() as conn:
        conn.execute(sql, [
            dict(s=sexo, m=int(r.edad_meses),
                 P01=r.P01, P1=r.P1, P3=r.P3, P5=r.P5, P10=r.P10, P15=r.P15,
                 P25=r.P25, P50=r.P50, P75=r.P75, P85=r.P85, P90=r.P90,
                 P95=r.P95, P97=r.P97, P99=r.P99, P999=r.P999)
            for r in df.itertuples(index=False)
        ])

def upsert_percentiles_5_19(df, version, sexo):
    # 5–19 percentiles
    if not has_cols(df, ["Month","1st","3rd","5th","15th","25th","50th","75th","85th","95th","97th","99th"]):
        print("   ⚠️  Percentiles 5–19 omitido: columnas no encontradas.")
        return
    # intenta generar LMS con el mismo sheet (si trae L/M/S)
    upsert_lms(df, version, sexo)

    rename = {"Month":"edad_meses",
              "1st":"pct_1","3rd":"pct_3","5th":"pct_5","15th":"pct_15",
              "25th":"pct_25","50th":"pct_50","75th":"pct_75",
              "85th":"pct_85","95th":"pct_95","97th":"pct_97","99th":"pct_99"}
    df = df.rename(columns=rename)
    keep = ["edad_meses","pct_1","pct_3","pct_5","pct_15","pct_25","pct_50","pct_75","pct_85","pct_95","pct_97","pct_99"]
    df = df[keep].dropna(subset=["edad_meses"])
    df["edad_meses"] = df["edad_meses"].astype(int)
    sql = text("""
        INSERT INTO oms_bmi_percentiles
        (lms_version, lms_sexo, lms_edad_meses,
         pct_1,pct_3,pct_5,pct_15,pct_25,pct_50,pct_75,pct_85,pct_95,pct_97,pct_99)
        VALUES (:v, :s, :m, :p1,:p3,:p5,:p15,:p25,:p50,:p75,:p85,:p95,:p97,:p99)
        ON DUPLICATE KEY UPDATE
         pct_1=VALUES(pct_1), pct_3=VALUES(pct_3), pct_5=VALUES(pct_5), pct_15=VALUES(pct_15),
         pct_25=VALUES(pct_25), pct_50=VALUES(pct_50), pct_75=VALUES(pct_75),
         pct_85=VALUES(pct_85), pct_95=VALUES(pct_95), pct_97=VALUES(pct_97), pct_99=VALUES(pct_99)
    """)
    with engine.begin() as conn:
        conn.execute(sql, [
            dict(v=version, s=sexo, m=int(r.edad_meses),
                 p1=r.pct_1, p3=r.pct_3, p5=r.pct_5, p15=r.pct_15, p25=r.pct_25,
                 p50=r.pct_50, p75=r.pct_75, p85=r.pct_85, p95=r.pct_95, p97=r.pct_97, p99=r.pct_99)
            for r in df.itertuples(index=False)
        ])


def main():
    try:
        import pymysql  
    except Exception:
        print("Install first: pip install pandas sqlalchemy pymysql openpyxl")
        return

    for fname, version, sexo, kind in FILES:
        path = os.path.join(BASE_DIR, fname)
        if not os.path.exists(path):
            print(f"⚠️ Not found: {path}")
            continue
        print(f"→ Processing {fname} [{version} {sexo} {kind}]")

        df = read_who_excel(path)  

        # rutas por tipo
        if kind == "z_0_5":
            upsert_lms(df, version, sexo)
            upsert_zscores_from_sdlabels(df, version, sexo)
        elif kind == "p_0_5":
            upsert_percentiles_0_5(df, sexo)
        elif kind == "z_5_19":
            upsert_zscores_5_19(df, version, sexo)
        elif kind == "p_5_19":
            upsert_percentiles_5_19(df, version, sexo)

    print("✅ Done.")

if __name__ == "__main__":
    main()