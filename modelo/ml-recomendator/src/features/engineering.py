"""
Feature Engineering para evaluación nutricional.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class FeatureEngineer:
    """
    Genera features para el modelo ML desde datos crudos.
    """
    
    def __init__(self):
        self.feature_names = []
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea todos los features desde el dataset crudo.
        
        Args:
            df: DataFrame con datos crudos
            
        Returns:
            DataFrame con features procesados
        """
        df = df.copy()
        
        # Features básicos
        df = self._add_basic_features(df)
        
        # Features temporales
        df = self._add_temporal_features(df)
        
        # Features de alergias
        df = self._add_allergy_features(df)
        
        # Features de adherencia
        df = self._add_adherence_features(df)
        
        # Features de síntomas
        df = self._add_symptom_features(df)
        
        # Features nutricionales
        df = self._add_nutritional_features(df)
        
        # Features contextuales
        df = self._add_contextual_features(df)
        
        return df
    
    def _add_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Features antropométricos básicos."""
        
        # BMI si no existe
        if "BMI" not in df.columns:
            if "weight_kg" in df.columns and "height_cm" in df.columns:
                df["BMI"] = df["weight_kg"] / (df["height_cm"] / 100) ** 2
        
        # Edad en años
        if "age_months" in df.columns:
            df["age_years"] = df["age_months"] / 12
        
        # Categoría de edad
        if "age_months" in df.columns:
            df["age_category"] = pd.cut(
                df["age_months"],
                bins=[0, 24, 60, 120, 228],
                labels=["0-2y", "2-5y", "5-10y", "10-19y"],
            )
        
        # Sexo como numérico
        if "sex" in df.columns:
            df["sex_numeric"] = df["sex"].map({"M": 0, "F": 1})
        
        return df
    
    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Features de tendencias temporales."""
        
        # Estos features requieren datos históricos por niño
        # Por ahora, valores por defecto si no existen
        
        if "bmi_velocity" not in df.columns:
            df["bmi_velocity"] = 0.0
        
        if "weight_velocity" not in df.columns:
            df["weight_velocity"] = 0.0
        
        if "height_velocity" not in df.columns:
            df["height_velocity"] = 0.0
        
        if "baz_trend" not in df.columns:
            df["baz_trend"] = 0.0
        
        if "measurements_count" not in df.columns:
            df["measurements_count"] = 1
        
        # Indicador de tendencia
        df["is_improving"] = (df["baz_trend"] > 0).astype(int)
        df["is_worsening"] = (df["baz_trend"] < -0.1).astype(int)
        
        return df
    
    def _add_allergy_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Features relacionados con alergias."""
        
        if "allergy_count" not in df.columns:
            df["allergy_count"] = 0
        
        if "allergy_severity_max" not in df.columns:
            df["allergy_severity_max"] = 0
        
        if "food_allergy_count" not in df.columns:
            df["food_allergy_count"] = 0
        
        # Features derivados
        df["has_allergies"] = (df["allergy_count"] > 0).astype(int)
        df["has_severe_allergy"] = (df["allergy_severity_max"] >= 3).astype(int)
        df["has_food_allergy"] = (df["food_allergy_count"] > 0).astype(int)
        
        # Ratio de alergias alimentarias
        df["food_allergy_ratio"] = np.where(
            df["allergy_count"] > 0,
            df["food_allergy_count"] / df["allergy_count"],
            0.0
        )
        
        return df
    
    def _add_adherence_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Features de adherencia a menús."""
        
        if "adherence_score" not in df.columns:
            df["adherence_score"] = 75.0  # Default medio-alto
        
        if "adherence_consistency" not in df.columns:
            df["adherence_consistency"] = 70.0
        
        if "menu_completion_rate" not in df.columns:
            df["menu_completion_rate"] = 80.0
        
        # Features derivados
        df["good_adherence"] = (df["adherence_score"] >= 70).astype(int)
        df["poor_adherence"] = (df["adherence_score"] < 50).astype(int)
        
        # Score combinado de adherencia
        df["adherence_combined"] = (
            df["adherence_score"] * 0.5 +
            df["adherence_consistency"] * 0.3 +
            df["menu_completion_rate"] * 0.2
        )
        
        return df
    
    def _add_symptom_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Features de síntomas."""
        
        if "symptom_frequency" not in df.columns:
            df["symptom_frequency"] = 0
        
        if "symptom_severity_avg" not in df.columns:
            df["symptom_severity_avg"] = 0.0
        
        if "has_recent_symptoms" not in df.columns:
            df["has_recent_symptoms"] = 0
        
        # Features derivados
        df["has_symptoms"] = (df["symptom_frequency"] > 0).astype(int)
        df["frequent_symptoms"] = (df["symptom_frequency"] >= 5).astype(int)
        
        # Score de riesgo por síntomas
        df["symptom_risk_score"] = (
            df["symptom_frequency"] * 0.4 +
            df["symptom_severity_avg"] * 10 * 0.4 +
            df["has_recent_symptoms"] * 20 * 0.2
        )
        
        return df
    
    def _add_nutritional_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Features nutricionales."""
        
        if "dietary_diversity_score" not in df.columns:
            df["dietary_diversity_score"] = 60.0
        
        if "menu_kcal_avg" not in df.columns:
            df["menu_kcal_avg"] = 1500
        
        if "protein_intake_score" not in df.columns:
            df["protein_intake_score"] = 65.0
        
        # Features derivados
        df["good_diversity"] = (df["dietary_diversity_score"] >= 70).astype(int)
        df["poor_diversity"] = (df["dietary_diversity_score"] < 40).astype(int)
        
        # Adecuación calórica (simplificado)
        if "age_months" in df.columns:
            # Requerimiento aproximado: 1000 + (edad_años * 100)
            df["kcal_requirement"] = 1000 + (df["age_months"] / 12 * 100)
            df["kcal_adequacy"] = (df["menu_kcal_avg"] / df["kcal_requirement"]) * 100
            df["kcal_adequate"] = (
                (df["kcal_adequacy"] >= 90) & (df["kcal_adequacy"] <= 110)
            ).astype(int)
        
        return df
    
    def _add_contextual_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Features contextuales (geográficos, socioeconómicos)."""
        
        if "altitude_m" not in df.columns:
            df["altitude_m"] = 0
        
        # Categoría de altitud
        df["altitude_category"] = pd.cut(
            df["altitude_m"],
            bins=[-1, 500, 2500, 10000],
            labels=["costa", "sierra_baja", "sierra_alta"],
        )
        
        # Zona (si existe)
        if "entity_type" in df.columns:
            df["is_hospital"] = (df["entity_type"] == "HOSPITAL").astype(int)
            df["is_rural"] = (df["entity_type"].isin(["POSTA", "CENTRO_COMUNITARIO"])).astype(int)
        
        return df
    
    def get_feature_list(self) -> List[str]:
        """Retorna lista de features generados."""
        return [
            # Básicos
            "age_months", "sex_numeric", "BMI", "baz",
            
            # Temporales
            "bmi_velocity", "weight_velocity", "height_velocity",
            "baz_trend", "measurements_count", "is_improving", "is_worsening",
            
            # Alergias
            "allergy_count", "allergy_severity_max", "food_allergy_count",
            "has_allergies", "has_severe_allergy", "has_food_allergy",
            "food_allergy_ratio",
            
            # Adherencia
            "adherence_score", "adherence_consistency", "menu_completion_rate",
            "good_adherence", "poor_adherence", "adherence_combined",
            
            # Síntomas
            "symptom_frequency", "symptom_severity_avg", "has_recent_symptoms",
            "has_symptoms", "frequent_symptoms", "symptom_risk_score",
            
            # Nutricionales
            "dietary_diversity_score", "menu_kcal_avg", "protein_intake_score",
            "good_diversity", "poor_diversity", "kcal_adequacy", "kcal_adequate",
            
            # Contextuales
            "altitude_m",
        ]
    
    def select_features(
        self,
        df: pd.DataFrame,
        feature_list: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Selecciona solo los features especificados.
        
        Args:
            df: DataFrame con todos los features
            feature_list: Lista de features a seleccionar (None = todos disponibles)
            
        Returns:
            DataFrame con features seleccionados
        """
        if feature_list is None:
            feature_list = self.get_feature_list()
        
        # Filtrar solo features que existen
        available = [f for f in feature_list if f in df.columns]
        
        if len(available) < len(feature_list):
            missing = set(feature_list) - set(available)
            print(f"⚠️  Features faltantes: {missing}")
        
        return df[available]
