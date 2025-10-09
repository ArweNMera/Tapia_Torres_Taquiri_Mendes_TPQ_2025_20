"""
Validadores de datos para el pipeline ML.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np


class DataValidator:
    """
    Valida datos de entrada para el modelo ML.
    """
    
    @staticmethod
    def validate_anthropometric_data(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valida datos antropométricos básicos.
        
        Args:
            df: DataFrame con datos
            
        Returns:
            Dict con resultados de validación
        """
        issues = []
        warnings = []
        
        # Columnas requeridas
        required_cols = ["age_months", "sex", "weight_kg", "height_cm"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            issues.append(f"Columnas faltantes: {missing_cols}")
        
        if issues:
            return {"valid": False, "issues": issues, "warnings": warnings}
        
        # Validar rangos
        if (df["age_months"] < 0).any() or (df["age_months"] > 228).any():
            issues.append("Edad fuera de rango (0-228 meses)")
        
        if (df["weight_kg"] <= 0).any() or (df["weight_kg"] > 200).any():
            issues.append("Peso fuera de rango (0-200 kg)")
        
        if (df["height_cm"] <= 0).any() or (df["height_cm"] > 250).any():
            issues.append("Talla fuera de rango (0-250 cm)")
        
        # Validar sexo
        valid_sex = df["sex"].isin(["M", "F", "m", "f"])
        if not valid_sex.all():
            issues.append("Valores de sexo inválidos (debe ser M o F)")
        
        # Warnings
        if df["age_months"].isna().any():
            warnings.append(f"{df['age_months'].isna().sum()} valores nulos en age_months")
        
        if df["weight_kg"].isna().any():
            warnings.append(f"{df['weight_kg'].isna().sum()} valores nulos en weight_kg")
        
        if df["height_cm"].isna().any():
            warnings.append(f"{df['height_cm'].isna().sum()} valores nulos en height_cm")
        
        # BMI extremo
        bmi = df["weight_kg"] / (df["height_cm"] / 100) ** 2
        extreme_bmi = (bmi < 10) | (bmi > 40)
        if extreme_bmi.any():
            warnings.append(f"{extreme_bmi.sum()} casos con BMI extremo (<10 o >40)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "n_rows": len(df),
            "n_complete": df[required_cols].notna().all(axis=1).sum(),
        }
    
    @staticmethod
    def validate_features(
        df: pd.DataFrame,
        required_features: List[str]
    ) -> Dict[str, Any]:
        """
        Valida que existan los features requeridos.
        
        Args:
            df: DataFrame con features
            required_features: Lista de features requeridos
            
        Returns:
            Dict con resultados de validación
        """
        missing = [f for f in required_features if f not in df.columns]
        
        if missing:
            return {
                "valid": False,
                "missing_features": missing,
                "available_features": list(df.columns),
            }
        
        # Verificar tipos de datos
        numeric_features = df[required_features].select_dtypes(
            include=[np.number]
        ).columns.tolist()
        
        non_numeric = [f for f in required_features if f not in numeric_features]
        
        return {
            "valid": True,
            "missing_features": [],
            "numeric_features": numeric_features,
            "non_numeric_features": non_numeric,
            "n_features": len(required_features),
        }
    
    @staticmethod
    def check_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analiza calidad general de los datos.
        
        Args:
            df: DataFrame
            
        Returns:
            Dict con métricas de calidad
        """
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isna().sum().sum()
        
        # Duplicados
        n_duplicates = df.duplicated().sum()
        
        # Columnas con muchos nulos
        high_null_cols = df.columns[df.isna().mean() > 0.5].tolist()
        
        # Columnas constantes
        constant_cols = [
            col for col in df.columns
            if df[col].nunique() <= 1
        ]
        
        return {
            "n_rows": len(df),
            "n_cols": len(df.columns),
            "null_percentage": (null_cells / total_cells) * 100,
            "n_duplicates": n_duplicates,
            "high_null_columns": high_null_cols,
            "constant_columns": constant_cols,
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        }
    
    @staticmethod
    def detect_outliers(
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = "iqr",
        threshold: float = 3.0
    ) -> Dict[str, Any]:
        """
        Detecta outliers en columnas numéricas.
        
        Args:
            df: DataFrame
            columns: Columnas a analizar (None = todas numéricas)
            method: 'iqr' o 'zscore'
            threshold: Umbral para z-score (default 3.0)
            
        Returns:
            Dict con outliers detectados por columna
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        outliers = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            data = df[col].dropna()
            
            if method == "iqr":
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                mask = (data < lower) | (data > upper)
            
            elif method == "zscore":
                z_scores = np.abs((data - data.mean()) / data.std())
                mask = z_scores > threshold
            
            else:
                raise ValueError(f"Método desconocido: {method}")
            
            n_outliers = mask.sum()
            if n_outliers > 0:
                outliers[col] = {
                    "n_outliers": int(n_outliers),
                    "percentage": (n_outliers / len(data)) * 100,
                    "min": float(data.min()),
                    "max": float(data.max()),
                }
        
        return {
            "method": method,
            "outliers_by_column": outliers,
            "total_outliers": sum(o["n_outliers"] for o in outliers.values()),
        }
    
    @staticmethod
    def validate_labels(y: pd.Series, expected_classes: List[int]) -> Dict[str, Any]:
        """
        Valida labels de clasificación.
        
        Args:
            y: Serie con labels
            expected_classes: Clases esperadas (ej: [0, 1, 2, 3])
            
        Returns:
            Dict con resultados de validación
        """
        unique_labels = y.unique().tolist()
        missing_classes = [c for c in expected_classes if c not in unique_labels]
        unexpected_classes = [c for c in unique_labels if c not in expected_classes]
        
        # Distribución de clases
        class_distribution = y.value_counts().to_dict()
        
        # Balance de clases
        counts = y.value_counts()
        max_count = counts.max()
        min_count = counts.min()
        imbalance_ratio = max_count / min_count if min_count > 0 else float("inf")
        
        return {
            "valid": len(unexpected_classes) == 0,
            "unique_labels": unique_labels,
            "missing_classes": missing_classes,
            "unexpected_classes": unexpected_classes,
            "class_distribution": class_distribution,
            "imbalance_ratio": float(imbalance_ratio),
            "is_balanced": imbalance_ratio < 3.0,
        }
