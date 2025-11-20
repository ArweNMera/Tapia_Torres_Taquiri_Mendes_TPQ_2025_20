"""
Construcción consistente de features para el ranker LightGBM.

Se reutiliza tanto en entrenamiento como en inferencia para garantizar
el mismo orden de columnas y los mismos encoders categóricos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder


@dataclass
class RankerFeatureBuilder:
    """
    Builder reutilizable que replica la lógica de _prepare_features.

    Aporta métodos para ajustar encoders durante entrenamiento y
    reutilizarlos en inferencia.
    """

    encoders: Dict[str, LabelEncoder] = field(default_factory=dict)
    feature_names: List[str] = field(default_factory=list)

    categorical_columns: Tuple[str, ...] = (
        "mei_comida",
        "pnn_clasificacion",
        "nin_sexo",
        "men_generado_por",
    )

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Genera la matriz de features ajustando encoders."""
        matrix, feature_names = self._build_matrix(df.copy(), fit=True)
        self.feature_names = feature_names
        return matrix

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Genera la matriz reutilizando encoders ya ajustados."""
        if not self.feature_names:
            raise ValueError("El builder no tiene feature_names cargadas.")
        matrix, _ = self._build_matrix(df.copy(), fit=False)
        return matrix

    def _build_matrix(self, df: pd.DataFrame, fit: bool) -> Tuple[np.ndarray, List[str]]:
        """Replica la lógica previa de _prepare_features."""
        df_processed = df.copy()

        # Alias útiles
        df_processed["edad_meses"] = self._get_column(df_processed, "edad_meses", np.nan).fillna(
            self._get_column(df_processed, "pnn_edad_meses", 72)
        )
        df_processed["edad_final"] = df_processed["edad_meses"].fillna(72)

        # Peso/talla -> IMC
        df_processed["ant_peso_kg"] = pd.to_numeric(
            self._get_column(df_processed, "ant_peso_kg", 35).fillna(35), errors="coerce"
        )
        df_processed["ant_talla_cm"] = pd.to_numeric(
            self._get_column(df_processed, "ant_talla_cm", 140).fillna(140), errors="coerce"
        )
        talla_m = df_processed["ant_talla_cm"] / 100.0
        df_processed["en_imc"] = df_processed["ant_peso_kg"] / (talla_m.pow(2).replace(0, np.nan))
        df_processed["en_imc"] = df_processed["en_imc"].fillna(df_processed["en_imc"].median())

        df_processed["en_zscore_imc"] = self._get_column(df_processed, "en_zscore_imc", 0).fillna(0)
        df_processed["pnn_calorias_diarias"] = self._get_column(
            df_processed, "pnn_calorias_diarias", 1500
        ).fillna(1500)
        default_protein = df_processed["pnn_calorias_diarias"] * 0.15 / 4
        df_processed["pnn_proteinas_g"] = self._get_column(
            df_processed, "pnn_proteinas_g", default_protein
        ).fillna(default_protein)
        df_processed["mei_kcal"] = self._get_column(df_processed, "mei_kcal", 400).fillna(400)
        df_processed["men_kcal_total"] = self._get_column(
            df_processed, "men_kcal_total", df_processed["mei_kcal"]
        ).fillna(df_processed["mei_kcal"])

        # Score calórico por comida
        df_processed["caloric_compatibility"] = 1 - np.abs(
            df_processed["mei_kcal"] - (df_processed["pnn_calorias_diarias"] / 3.0)
        ) / (df_processed["pnn_calorias_diarias"] / 3.0).replace(0, np.nan)
        df_processed["caloric_compatibility"] = df_processed["caloric_compatibility"].clip(0, 1).fillna(0)

        default_cats = {
            "mei_comida": "ALMUERZO",
            "pnn_clasificacion": "NORMAL",
            "nin_sexo": "M",
            "men_generado_por": "IA",
        }

        for col, default in default_cats.items():
            values = self._get_column(df_processed, col, default).fillna(default).astype(str)
            df_processed[col] = values
            encoded = self._encode_column(col, values, fit, default)
            df_processed[f"{col}_enc"] = encoded

        df_processed["num_alergias"] = df_processed.get("num_alergias", 0).fillna(0)
        df_processed["mf_porcentaje_consumido"] = df_processed.get("mf_porcentaje_consumido", 75).fillna(75)

        feature_order = [
            "edad_final",
            "en_imc",
            "en_zscore_imc",
            "pnn_calorias_diarias",
            "pnn_proteinas_g",
            "mei_kcal",
            "men_kcal_total",
            "caloric_compatibility",
            "mei_comida_enc",
            "pnn_clasificacion_enc",
            "nin_sexo_enc",
            "men_generado_por_enc",
            "num_alergias",
            "mf_porcentaje_consumido",
        ]

        if fit:
            available = [col for col in feature_order if col in df_processed.columns]
            self.feature_names = available
        else:
            for col in self.feature_names:
                if col not in df_processed.columns:
                    df_processed[col] = 0

        matrix = (
            df_processed[self.feature_names or feature_order]
            .fillna(0)
            .astype(np.float32)
            .values
        )
        return matrix, (self.feature_names or feature_order)

    def _encode_column(self, key: str, values: pd.Series, fit: bool, default: str) -> np.ndarray:
        """Codifica columnas categóricas manteniendo coherencia."""
        if fit or key not in self.encoders:
            encoder = LabelEncoder()
            encoded = encoder.fit_transform(values)
            self.encoders[key] = encoder
            return encoded

        encoder = self.encoders[key]
        known = set(encoder.classes_)
        cleaned = values.apply(lambda x: x if x in known else default)
        return encoder.transform(cleaned)

    def _get_column(self, df: pd.DataFrame, column: str, default) -> pd.Series:
        """Obtiene columna o crea una serie por defecto del mismo tamaño."""
        if column in df.columns:
            return df[column]

        if isinstance(default, pd.Series):
            return default

        if not len(df):
            return pd.Series(dtype=np.float32)

        return pd.Series([default] * len(df), index=df.index)
