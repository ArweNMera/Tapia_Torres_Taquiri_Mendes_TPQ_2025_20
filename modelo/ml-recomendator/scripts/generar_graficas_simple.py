"""
Script simplificado para generar gráficas sin modelo entrenado.
Solo usa los datos clasificados.
"""

import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 8)
plt.rcParams["font.size"] = 10

# Crear directorio para gráficas
OUTPUT_DIR = BASE_DIR / "reports/figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def cargar_datos():
    """Carga datos clasificados."""
    print("📂 Cargando datos...")
    data_path = BASE_DIR / "data/raw/surveys/datos_historicos.csv"
    df = pd.read_csv(data_path)
    print(f"   Filas: {len(df)}, Columnas: {len(df.columns)}")
    return df


def grafica_distribucion_clases(df):
    """Gráfica: Distribución de Clases."""
    print("\n📊 Generando Gráfica: Distribución de Clases...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Gráfica de barras
    class_counts = df["label_status"].value_counts().sort_index()
    class_labels = [
        "DESNUT_SEV",
        "DESNUT_MOD",
        "RIESGO_DESN",
        "NORMAL",
        "RIESGO_SOB",
        "SOBREPESO",
        "OBESIDAD",
    ]
    colors = ["#c0392b", "#e74c3c", "#e67e22", "#2ecc71", "#f39c12", "#d35400", "#8e44ad"]

    bars = ax1.bar(range(len(class_counts)), class_counts.values, color=colors, alpha=0.7)
    ax1.set_xticks(range(len(class_counts)))
    ax1.set_xticklabels(class_labels, rotation=45, ha="right")
    ax1.set_ylabel("Cantidad de Niños")
    ax1.set_title("Distribución de Clases (7 Categorías OMS)", fontweight="bold")
    ax1.grid(axis="y", alpha=0.3)

    # Agregar valores
    for bar, val in zip(bars, class_counts.values, strict=False):
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{int(val)}\n({val/len(df)*100:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    # Gráfica de pie
    ax2.pie(
        class_counts.values,
        labels=class_labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 9},
    )
    ax2.set_title("Proporción de Clases", fontweight="bold")

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "distribucion_clases_7cat.png", dpi=300, bbox_inches="tight")
    print(f"✅ Guardada: {OUTPUT_DIR / 'distribucion_clases_7cat.png'}")
    plt.close()


def grafica_distribucion_baz(df):
    """Gráfica: Distribución de BAZ por Clase."""
    print("\n📊 Generando Gráfica: Distribución de BAZ...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Histograma
    categories = [
        (0, "DESNUT_SEV", "#c0392b"),
        (1, "DESNUT_MOD", "#e74c3c"),
        (2, "RIESGO_DESN", "#e67e22"),
        (3, "NORMAL", "#2ecc71"),
        (4, "RIESGO_SOB", "#f39c12"),
        (5, "SOBREPESO", "#d35400"),
        (6, "OBESIDAD", "#8e44ad"),
    ]

    for label, name, color in categories:
        data = df[df["label_status"] == label]["baz"]
        if len(data) > 0:
            ax1.hist(data, alpha=0.6, label=name, bins=10, color=color)

    ax1.set_xlabel("BAZ (Z-score)")
    ax1.set_ylabel("Frecuencia")
    ax1.set_title("Distribución de BAZ por Clase (7 Categorías OMS)", fontweight="bold")
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.3)

    # Boxplot
    df_plot = df[["label_status", "baz"]].copy()
    label_map = {
        0: "DESNUT_SEV",
        1: "DESNUT_MOD",
        2: "RIESGO_DESN",
        3: "NORMAL",
        4: "RIESGO_SOB",
        5: "SOBREPESO",
        6: "OBESIDAD",
    }
    df_plot["clase"] = df_plot["label_status"].map(label_map)

    colors_palette = ["#c0392b", "#e74c3c", "#e67e22", "#2ecc71", "#f39c12", "#d35400", "#8e44ad"]

    sns.boxplot(data=df_plot, x="clase", y="baz", palette=colors_palette, ax=ax2)
    ax2.set_xlabel("Clase")
    ax2.set_ylabel("BAZ (Z-score)")
    ax2.set_title("BAZ por Clase (Boxplot)", fontweight="bold")
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha="right")
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "distribucion_baz_7cat.png", dpi=300, bbox_inches="tight")
    print(f"✅ Guardada: {OUTPUT_DIR / 'distribucion_baz_7cat.png'}")
    plt.close()


def grafica_edad_vs_bmi(df):
    """Gráfica: Edad vs BMI por Clase."""
    print("\n📊 Generando Gráfica: Edad vs BMI...")

    plt.figure(figsize=(14, 8))

    colors = {
        0: "#c0392b",
        1: "#e74c3c",
        2: "#e67e22",
        3: "#2ecc71",
        4: "#f39c12",
        5: "#d35400",
        6: "#8e44ad",
    }
    labels = {
        0: "DESNUT_SEV",
        1: "DESNUT_MOD",
        2: "RIESGO_DESN",
        3: "NORMAL",
        4: "RIESGO_SOB",
        5: "SOBREPESO",
        6: "OBESIDAD",
    }

    for label in sorted(df["label_status"].unique()):
        data = df[df["label_status"] == label]
        if len(data) > 0:
            plt.scatter(
                data["age_months"],
                data["BMI"],
                c=colors[label],
                label=labels[label],
                alpha=0.6,
                s=80,
                edgecolors="black",
                linewidth=0.5,
            )

    plt.xlabel("Edad (meses)", fontsize=12)
    plt.ylabel("BMI", fontsize=12)
    plt.title(
        "Edad vs BMI por Clase Nutricional (7 Categorías OMS)", fontsize=14, fontweight="bold"
    )
    plt.legend(title="Clase", fontsize=9, loc="best")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "edad_vs_bmi_7cat.png", dpi=300, bbox_inches="tight")
    print(f"✅ Guardada: {OUTPUT_DIR / 'edad_vs_bmi_7cat.png'}")
    plt.close()


def grafica_resumen_categorias(df):
    """Gráfica: Resumen de categorías con estadísticas."""
    print("\n📊 Generando Gráfica: Resumen de Categorías...")

    fig, ax = plt.subplots(figsize=(14, 8))

    label_map = {
        0: "DESNUT_SEV",
        1: "DESNUT_MOD",
        2: "RIESGO_DESN",
        3: "NORMAL",
        4: "RIESGO_SOB",
        5: "SOBREPESO",
        6: "OBESIDAD",
    }

    colors = ["#c0392b", "#e74c3c", "#e67e22", "#2ecc71", "#f39c12", "#d35400", "#8e44ad"]

    # Calcular estadísticas por categoría
    stats = []
    for label in sorted(df["label_status"].unique()):
        data = df[df["label_status"] == label]
        stats.append(
            {
                "label": label,
                "nombre": label_map[label],
                "cantidad": len(data),
                "baz_mean": data["baz"].mean(),
                "baz_min": data["baz"].min(),
                "baz_max": data["baz"].max(),
            }
        )

    stats_df = pd.DataFrame(stats)

    # Crear tabla
    table_data = []
    for _, row in stats_df.iterrows():
        table_data.append(
            [
                row["nombre"],
                f"{row['cantidad']}",
                f"{row['baz_mean']:.2f}",
                f"[{row['baz_min']:.2f}, {row['baz_max']:.2f}]",
            ]
        )

    ax.axis("tight")
    ax.axis("off")

    table = ax.table(
        cellText=table_data,
        colLabels=["Categoría", "Cantidad", "BAZ Promedio", "Rango BAZ"],
        cellLoc="center",
        loc="center",
        colWidths=[0.3, 0.15, 0.2, 0.35],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)

    # Colorear filas
    for i, color in enumerate(colors):
        table[(i + 1, 0)].set_facecolor(color)
        table[(i + 1, 0)].set_text_props(weight="bold", color="white")
        for j in range(1, 4):
            table[(i + 1, j)].set_facecolor("#f0f0f0")

    # Colorear encabezados
    for j in range(4):
        table[(0, j)].set_facecolor("#34495e")
        table[(0, j)].set_text_props(weight="bold", color="white")

    plt.title("Resumen de Categorías Nutricionales OMS", fontsize=16, fontweight="bold", pad=20)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "resumen_categorias_7cat.png", dpi=300, bbox_inches="tight")
    print(f"✅ Guardada: {OUTPUT_DIR / 'resumen_categorias_7cat.png'}")
    plt.close()


def main():
    """Genera todas las gráficas."""
    print("\n" + "=" * 60)
    print("📊 GENERANDO GRÁFICAS (7 CATEGORÍAS OMS)")
    print("=" * 60)

    # Cargar datos
    df = cargar_datos()

    # Generar gráficas
    grafica_distribucion_clases(df)
    grafica_distribucion_baz(df)
    grafica_edad_vs_bmi(df)
    grafica_resumen_categorias(df)

    print("\n" + "=" * 60)
    print("✅ GRÁFICAS GENERADAS")
    print("=" * 60)
    print(f"\n📁 Ubicación: {OUTPUT_DIR}")
    print("\nGráficas generadas:")
    for img in sorted(OUTPUT_DIR.glob("*_7cat.png")):
        print(f"   - {img.name}")


if __name__ == "__main__":
    main()
