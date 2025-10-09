"""
Calculadora de métricas OMS (BAZ, percentiles, etc).
Usa tablas OMS desde MySQL.
"""

from pathlib import Path
import math
import pandas as pd
from typing import Tuple, Optional, Union


class WHOCalculator:
    """
    Calcula métricas antropométricas según estándares OMS.
    Puede usar archivos CSV o tablas MySQL.
    """
    
    def __init__(self, who_dir: Union[Path, str, None] = None, db_connector=None):
        """
        Args:
            who_dir: Directorio con tablas LMS de la OMS (CSV) - opcional
            db_connector: Conector a base de datos MySQL - opcional
        """
        self.who_dir = Path(who_dir) if who_dir else None
        self.db_connector = db_connector
        self.lms_data = None
        
        # Cargar datos
        if db_connector:
            self.lms_data = self._load_lms_from_db()
        elif who_dir:
            self.who_dir = Path(who_dir)
            self.lms_data = self._load_lms_from_csv()
    
    def _load_table(self, path: Path) -> pd.DataFrame:
        """Carga y normaliza una tabla CSV."""
        df = pd.read_csv(path)
        cols = {c: c.strip().replace(" ", "_") for c in df.columns}
        df = df.rename(columns=cols)
        
        # Normalizar nombre de columna 'month'
        if "Month" in df.columns:
            df = df.rename(columns={"Month": "month"})
        for c in list(df.columns):
            if c.lower() == "month":
                df = df.rename(columns={c: "month"})
                break
        
        return df
    
    def _load_lms_by_sex(self, sex: str) -> pd.DataFrame:
        """Carga tablas LMS para un sexo específico."""
        parts = []
        
        if sex == "M":
            patterns = [
                "bmi_boys_0-to-2-years_zcores_1.csv",
                "bmi_boys_2-to-5-years_zscores.csv",
                "bmifa-boys-5-19years-z.csv",
            ]
        else:  # F
            patterns = [
                "tab_bmi_girls_p_0_2.csv",
                "tab_bmi_girls_p_2_5.csv",
                "bmifa-girls-5-19years-z.csv",
            ]
        
        for pat in patterns:
            p = self.who_dir / pat
            if p.exists():
                df = self._load_table(p)
                parts.append(df[["month", "L", "M", "S"]].assign(sex=sex))
        
        if not parts:
            raise FileNotFoundError(
                f"No se encontraron tablas OMS para sexo={sex} en {self.who_dir}"
            )
        
        out = pd.concat(parts, ignore_index=True)
        out["month"] = out["month"].astype(int)
        return out.drop_duplicates(subset=["sex", "month"]).sort_values(
            ["sex", "month"]
        ).reset_index(drop=True)
    
    def _load_lms_from_db(self) -> pd.DataFrame:
        """Carga tablas LMS desde MySQL."""
        query = """
        SELECT 
            version,
            sexo as sex,
            edad_meses as month,
            L,
            M,
            S
        FROM oms_bmi_lms
        ORDER BY version, sexo, edad_meses
        """
        
        df = self.db_connector.execute_query(query)
        print(f"✅ Cargados {len(df)} registros OMS desde MySQL")
        return df
    
    def _load_lms_from_csv(self) -> pd.DataFrame:
        """Carga todas las tablas LMS desde CSV (M y F)."""
        return pd.concat(
            [self._load_lms_by_sex("M"), self._load_lms_by_sex("F")],
            ignore_index=True
        )
    
    def get_lms(self, age_months: int, sex: str) -> Tuple[float, float, float]:
        """
        Obtiene parámetros LMS para edad y sexo.
        
        Args:
            age_months: Edad en meses
            sex: 'M' o 'F'
            
        Returns:
            Tupla (L, M, S)
        """
        sex = sex.strip().upper()[0]
        
        subset = self.lms_data[self.lms_data["sex"] == sex]
        if subset.empty:
            raise ValueError(f"Sexo {sex} no encontrado en tablas OMS")
        
        # Buscar coincidencia exacta
        exact = subset[subset["month"] == age_months]
        if not exact.empty:
            row = exact.iloc[0]
            return float(row["L"]), float(row["M"]), float(row["S"])
        
        # Buscar más cercano
        nearest = subset.iloc[
            (subset["month"] - age_months).abs().argsort().iloc[0]
        ]
        return float(nearest["L"]), float(nearest["M"]), float(nearest["S"])
    
    def calculate_baz(
        self,
        bmi: float,
        age_months: int,
        sex: str
    ) -> float:
        """
        Calcula BAZ (BMI-for-age Z-score).
        
        Args:
            bmi: Índice de masa corporal
            age_months: Edad en meses
            sex: 'M' o 'F'
            
        Returns:
            Z-score
        """
        L, M, S = self.get_lms(age_months, sex)
        
        if abs(L) < 0.0001:
            z = math.log(bmi / M) / S
        else:
            z = ((bmi / M) ** L - 1) / (L * S)
        
        # Limitar a rango razonable
        z = max(-5.0, min(5.0, z))
        return round(z, 2)
    
    def calculate_percentile(self, z_score: float) -> float:
        """
        Calcula percentil aproximado desde z-score.
        
        Args:
            z_score: Z-score
            
        Returns:
            Percentil (0-100)
        """
        # Aproximación simple
        percentile = 50 + (z_score * 15)
        percentile = max(0.1, min(99.9, percentile))
        return round(percentile, 1)
    
    def classify_nutritional_status(self, z_score: float) -> str:
        """
        Clasifica estado nutricional según z-score OMS (7 categorías).
        
        Args:
            z_score: Z-score BAZ
            
        Returns:
            Clasificación según OMS:
            - DESNUTRICION_SEVERA: z < -3.0
            - DESNUTRICION_MODERADA: -3.0 <= z < -2.0
            - RIESGO_DESNUTRICION: -2.0 <= z < -1.0
            - NORMAL: -1.0 <= z <= 1.0
            - RIESGO_SOBREPESO: 1.0 < z <= 2.0
            - SOBREPESO: 2.0 < z <= 3.0
            - OBESIDAD: z > 3.0
        """
        if z_score < -3.0:
            return "DESNUTRICION_SEVERA"
        elif -3.0 <= z_score < -2.0:
            return "DESNUTRICION_MODERADA"
        elif -2.0 <= z_score < -1.0:
            return "RIESGO_DESNUTRICION"
        elif -1.0 <= z_score <= 1.0:
            return "NORMAL"
        elif 1.0 < z_score <= 2.0:
            return "RIESGO_SOBREPESO"
        elif 2.0 < z_score <= 3.0:
            return "SOBREPESO"
        else:  # z_score > 3.0
            return "OBESIDAD"
    
    def classify_to_label(self, z_score: float) -> int:
        """
        Convierte clasificación a label numérico (7 categorías OMS).
        
        Args:
            z_score: Z-score BAZ
            
        Returns:
            Label: 0=DESNUTRICION_SEVERA, 1=DESNUTRICION_MODERADA, 
                   2=RIESGO_DESNUTRICION, 3=NORMAL, 4=RIESGO_SOBREPESO,
                   5=SOBREPESO, 6=OBESIDAD
        """
        classification = self.classify_nutritional_status(z_score)
        label_map = {
            "DESNUTRICION_SEVERA": 0,
            "DESNUTRICION_MODERADA": 1,
            "RIESGO_DESNUTRICION": 2,
            "NORMAL": 3,
            "RIESGO_SOBREPESO": 4,
            "SOBREPESO": 5,
            "OBESIDAD": 6,
        }
        return label_map[classification]
    
    def process_dataframe(
        self,
        df: pd.DataFrame,
        bmi_col: str = "BMI",
        age_col: str = "age_months",
        sex_col: str = "sex",
    ) -> pd.DataFrame:
        """
        Procesa un DataFrame completo calculando BAZ y clasificación.
        
        Args:
            df: DataFrame con datos antropométricos
            bmi_col: Nombre de columna BMI
            age_col: Nombre de columna edad en meses
            sex_col: Nombre de columna sexo
            
        Returns:
            DataFrame con columnas adicionales: baz, percentile, classification, label
        """
        df = df.copy()
        
        # Calcular BMI si no existe
        if bmi_col not in df.columns:
            if "weight_kg" in df.columns and "height_cm" in df.columns:
                df[bmi_col] = df["weight_kg"] / (df["height_cm"] / 100) ** 2
        
        # Calcular BAZ
        df["baz"] = df.apply(
            lambda row: self.calculate_baz(
                row[bmi_col],
                int(row[age_col]),
                str(row[sex_col])
            ),
            axis=1
        )
        
        # Calcular percentil
        df["percentile"] = df["baz"].apply(self.calculate_percentile)
        
        # Clasificación
        df["classification"] = df["baz"].apply(self.classify_nutritional_status)
        df["label_status"] = df["baz"].apply(self.classify_to_label)
        
        return df
