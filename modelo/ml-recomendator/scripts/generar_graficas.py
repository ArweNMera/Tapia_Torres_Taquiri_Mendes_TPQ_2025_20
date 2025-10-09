"""
Script para generar todas las gráficas del modelo ML.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.preprocessing import label_binarize
from sklearn.tree import plot_tree
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.models import RandomForestNutritionClassifier

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# Crear directorio para gráficas
OUTPUT_DIR = BASE_DIR / "reports/figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def cargar_datos_y_modelo():
    """Carga datos y modelo entrenado."""
    print("📂 Cargando datos y modelo...")
    
    # Cargar datos
    data_path = BASE_DIR / "data/raw/surveys/datos_completos_oms_reales.csv"
    df = pd.read_csv(data_path)
    
    # Cargar modelo
    model_path = BASE_DIR / "models/rf_model.pkl"
    model = RandomForestNutritionClassifier()
    model.load(model_path)
    
    # Usar exactamente los mismos features que el modelo entrenado
    model_features = model.feature_names
    print(f"   Features del modelo: {model_features}")
    
    # Agregar sex_numeric si no existe
    if "sex_numeric" not in df.columns and "sex" in df.columns:
        df["sex_numeric"] = df["sex"].map({"M": 0, "F": 1})
    
    # Agregar features faltantes con valor 0
    for feature in model_features:
        if feature not in df.columns:
            print(f"   ⚠️  Feature '{feature}' no existe, agregando con valor 0")
            df[feature] = 0
    
    X = df[model_features]
    y = df["label_status"]
    
    return df, X, y, model, model_features


def grafica_1_feature_importance(model, feature_names):
    """Gráfica 1: Feature Importance."""
    print("\n📊 Generando Gráfica 1: Feature Importance...")
    
    importance = model.get_feature_importance()
    
    # Ordenar por importancia
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    features, values = zip(*sorted_features[:10])
    
    plt.figure(figsize=(12, 6))
    bars = plt.barh(range(len(features)), values, color='steelblue')
    plt.yticks(range(len(features)), features)
    plt.xlabel('Importancia')
    plt.title('Top 10 Features Más Importantes (Random Forest)', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    
    # Agregar valores
    for i, (bar, val) in enumerate(zip(bars, values)):
        plt.text(val, i, f' {val:.4f}', va='center')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "01_feature_importance.png", dpi=300, bbox_inches='tight')
    print(f"✅ Guardada: {OUTPUT_DIR / '01_feature_importance.png'}")
    plt.close()


def grafica_2_confusion_matrix(model, X, y):
    """Gráfica 2: Matriz de Confusión."""
    print("\n📊 Generando Gráfica 2: Matriz de Confusión...")
    
    y_pred = model.predict(X)
    cm = confusion_matrix(y, y_pred)
    
    labels = ['DESNUT_SEV', 'DESNUT_MOD', 'RIESGO_DESN', 'NORMAL', 
              'RIESGO_SOB', 'SOBREPESO', 'OBESIDAD']
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=labels,
                yticklabels=labels,
                cbar_kws={'label': 'Cantidad'})
    plt.xlabel('Predicción', fontsize=12)
    plt.ylabel('Real', fontsize=12)
    plt.title('Matriz de Confusión - Random Forest (7 Categorías OMS)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "02_confusion_matrix.png", dpi=300, bbox_inches='tight')
    print(f"✅ Guardada: {OUTPUT_DIR / '02_confusion_matrix.png'}")
    plt.close()


def grafica_3_distribucion_clases(df):
    """Gráfica 3: Distribución de Clases."""
    print("\n📊 Generando Gráfica 3: Distribución de Clases...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Gráfica de barras
    class_counts = df['label_status'].value_counts().sort_index()
    class_labels = ['DESNUT_SEV', 'DESNUT_MOD', 'RIESGO_DESN', 'NORMAL', 
                    'RIESGO_SOB', 'SOBREPESO', 'OBESIDAD']
    colors = ['#c0392b', '#e74c3c', '#e67e22', '#2ecc71', '#f39c12', '#d35400', '#8e44ad']
    
    bars = ax1.bar(range(len(class_counts)), class_counts.values, color=colors, alpha=0.7)
    ax1.set_xticks(range(len(class_counts)))
    ax1.set_xticklabels(class_labels, rotation=45, ha='right')
    ax1.set_ylabel('Cantidad de Niños')
    ax1.set_title('Distribución de Clases (7 Categorías OMS)', fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Agregar valores
    for bar, val in zip(bars, class_counts.values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(val)}\n({val/len(df)*100:.1f}%)',
                ha='center', va='bottom', fontsize=9)
    
    # Gráfica de pie
    ax2.pie(class_counts.values, labels=class_labels, colors=colors, autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 9})
    ax2.set_title('Proporción de Clases', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "03_distribucion_clases.png", dpi=300, bbox_inches='tight')
    print(f"✅ Guardada: {OUTPUT_DIR / '03_distribucion_clases.png'}")
    plt.close()


def grafica_4_arbol_decision(model):
    """Gráfica 4: Árbol de Decisión (primer árbol del RF)."""
    print("\n📊 Generando Gráfica 4: Árbol de Decisión...")
    
    # Obtener primer árbol del Random Forest
    tree = model.model.estimators_[0]
    
    class_names = ['DESNUT_SEV', 'DESNUT_MOD', 'RIESGO_DESN', 'NORMAL', 
                   'RIESGO_SOB', 'SOBREPESO', 'OBESIDAD']
    
    plt.figure(figsize=(24, 14))
    plot_tree(tree, 
              feature_names=model.feature_names,
              class_names=class_names,
              filled=True,
              rounded=True,
              fontsize=7,
              max_depth=3)  # Limitar profundidad para legibilidad
    plt.title('Árbol de Decisión (Primer árbol del Random Forest - 7 Categorías OMS)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "04_arbol_decision.png", dpi=300, bbox_inches='tight')
    print(f"✅ Guardada: {OUTPUT_DIR / '04_arbol_decision.png'}")
    plt.close()


def grafica_5_correlacion_features(df, feature_names):
    """Gráfica 5: Correlación entre Features."""
    print("\n📊 Generando Gráfica 5: Correlación entre Features...")
    
    # Seleccionar features numéricos
    numeric_features = [f for f in feature_names if f in df.columns]
    corr_matrix = df[numeric_features].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1,
                cbar_kws={'label': 'Correlación'})
    plt.title('Matriz de Correlación entre Features', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "05_correlacion_features.png", dpi=300, bbox_inches='tight')
    print(f"✅ Guardada: {OUTPUT_DIR / '05_correlacion_features.png'}")
    plt.close()


def grafica_6_distribucion_baz(df):
    """Gráfica 6: Distribución de BAZ por Clase."""
    print("\n📊 Generando Gráfica 6: Distribución de BAZ...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Histograma
    categories = [
        (0, 'DESNUT_SEV', '#c0392b'),
        (1, 'DESNUT_MOD', '#e74c3c'),
        (2, 'RIESGO_DESN', '#e67e22'),
        (3, 'NORMAL', '#2ecc71'),
        (4, 'RIESGO_SOB', '#f39c12'),
        (5, 'SOBREPESO', '#d35400'),
        (6, 'OBESIDAD', '#8e44ad')
    ]
    
    for label, name, color in categories:
        data = df[df['label_status'] == label]['baz']
        if len(data) > 0:
            ax1.hist(data, alpha=0.6, label=name, bins=10, color=color)
    
    ax1.set_xlabel('BAZ (Z-score)')
    ax1.set_ylabel('Frecuencia')
    ax1.set_title('Distribución de BAZ por Clase (7 Categorías OMS)', fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.3)
    
    # Boxplot
    df_plot = df[['label_status', 'baz']].copy()
    label_map = {
        0: 'DESNUT_SEV', 1: 'DESNUT_MOD', 2: 'RIESGO_DESN', 3: 'NORMAL',
        4: 'RIESGO_SOB', 5: 'SOBREPESO', 6: 'OBESIDAD'
    }
    df_plot['clase'] = df_plot['label_status'].map(label_map)
    
    colors_palette = ['#c0392b', '#e74c3c', '#e67e22', '#2ecc71', '#f39c12', '#d35400', '#8e44ad']
    
    sns.boxplot(data=df_plot, x='clase', y='baz', 
                palette=colors_palette,
                ax=ax2)
    ax2.set_xlabel('Clase')
    ax2.set_ylabel('BAZ (Z-score)')
    ax2.set_title('BAZ por Clase (Boxplot)', fontweight='bold')
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "06_distribucion_baz.png", dpi=300, bbox_inches='tight')
    print(f"✅ Guardada: {OUTPUT_DIR / '06_distribucion_baz.png'}")
    plt.close()


def grafica_7_edad_vs_bmi(df):
    """Gráfica 7: Edad vs BMI por Clase."""
    print("\n📊 Generando Gráfica 7: Edad vs BMI...")
    
    plt.figure(figsize=(14, 8))
    
    colors = {
        0: '#c0392b', 1: '#e74c3c', 2: '#e67e22', 3: '#2ecc71',
        4: '#f39c12', 5: '#d35400', 6: '#8e44ad'
    }
    labels = {
        0: 'DESNUT_SEV', 1: 'DESNUT_MOD', 2: 'RIESGO_DESN', 3: 'NORMAL',
        4: 'RIESGO_SOB', 5: 'SOBREPESO', 6: 'OBESIDAD'
    }
    
    for label in sorted(df['label_status'].unique()):
        data = df[df['label_status'] == label]
        if len(data) > 0:
            plt.scatter(data['age_months'], data['BMI'], 
                       c=colors[label], label=labels[label], 
                       alpha=0.6, s=80, edgecolors='black', linewidth=0.5)
    
    plt.xlabel('Edad (meses)', fontsize=12)
    plt.ylabel('BMI', fontsize=12)
    plt.title('Edad vs BMI por Clase Nutricional (7 Categorías OMS)', fontsize=14, fontweight='bold')
    plt.legend(title='Clase', fontsize=9, loc='best')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "07_edad_vs_bmi.png", dpi=300, bbox_inches='tight')
    print(f"✅ Guardada: {OUTPUT_DIR / '07_edad_vs_bmi.png'}")
    plt.close()


def grafica_8_metricas_comparacion(model, X, y):
    """Gráfica 8: Comparación de Métricas por Clase."""
    print("\n📊 Generando Gráfica 8: Métricas por Clase...")
    
    from sklearn.metrics import precision_score, recall_score, f1_score
    
    y_pred = model.predict(X)
    
    classes = ['DESNUT_SEV', 'DESNUT_MOD', 'RIESGO_DESN', 'NORMAL', 
               'RIESGO_SOB', 'SOBREPESO', 'OBESIDAD']
    precision = precision_score(y, y_pred, average=None, zero_division=0)
    recall = recall_score(y, y_pred, average=None, zero_division=0)
    f1 = f1_score(y, y_pred, average=None, zero_division=0)
    
    x = np.arange(len(classes))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(x - width, precision, width, label='Precision', color='#3498db')
    ax.bar(x, recall, width, label='Recall', color='#2ecc71')
    ax.bar(x + width, f1, width, label='F1-Score', color='#e74c3c')
    
    ax.set_xlabel('Clase')
    ax.set_ylabel('Score')
    ax.set_title('Métricas por Clase (7 Categorías OMS)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(classes, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim([0, 1.1])
    
    # Agregar valores
    for i, (p, r, f) in enumerate(zip(precision, recall, f1)):
        ax.text(i - width, p + 0.02, f'{p:.2f}', ha='center', fontsize=7)
        ax.text(i, r + 0.02, f'{r:.2f}', ha='center', fontsize=7)
        ax.text(i + width, f + 0.02, f'{f:.2f}', ha='center', fontsize=7)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "08_metricas_comparacion.png", dpi=300, bbox_inches='tight')
    print(f"✅ Guardada: {OUTPUT_DIR / '08_metricas_comparacion.png'}")
    plt.close()


def main():
    """Genera todas las gráficas."""
    print("\n" + "=" * 60)
    print("📊 GENERANDO GRÁFICAS DEL MODELO ML")
    print("=" * 60)
    
    # Cargar datos y modelo
    df, X, y, model, feature_names = cargar_datos_y_modelo()
    
    # Generar gráficas
    grafica_1_feature_importance(model, feature_names)
    grafica_2_confusion_matrix(model, X, y)
    grafica_3_distribucion_clases(df)
    grafica_4_arbol_decision(model)
    grafica_5_correlacion_features(df, feature_names)
    grafica_6_distribucion_baz(df)
    grafica_7_edad_vs_bmi(df)
    grafica_8_metricas_comparacion(model, X, y)
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS GRÁFICAS GENERADAS")
    print("=" * 60)
    print(f"\n📁 Ubicación: {OUTPUT_DIR}")
    print("\nGráficas generadas:")
    for i in range(1, 9):
        print(f"   {i}. {list(OUTPUT_DIR.glob(f'0{i}_*.png'))[0].name}")


if __name__ == "__main__":
    main()
