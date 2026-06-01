from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED = Path("data/processed/maintenance_features.csv")
REPORT = Path("reports/data_audit.md")
FIGURES = Path("reports/figures")
METRICS = Path("backend/saved_models/metrics.json")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    raw_summaries = []
    for path in sorted(RAW_DIR.glob("*.csv")):
        df = pd.read_csv(path)
        raw_summaries.append({
            "file": path.name,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": ", ".join(df.columns),
            "preview": to_markdown(df.head(5)),
        })

    processed = pd.read_csv(PROCESSED, low_memory=False)
    metrics = json.loads(METRICS.read_text(encoding="utf-8")) if METRICS.exists() else {}

    make_failure_plot(processed)
    make_sensor_plot(processed)
    make_correlation_plot(processed)
    make_model_plot(metrics)

    lines = [
        "# Audit des datasets et du pipeline MinePredict",
        "",
        "## Vue générale",
        "",
        f"- Fichiers CSV détectés : {len(raw_summaries)}",
        f"- Table ML traitée : {len(processed):,} lignes x {len(processed.columns)} colonnes".replace(",", " "),
        f"- Colonne cible : `{metrics.get('target_column', 'failure_binary')}`",
        f"- Colonne temps : `{metrics.get('time_column', 'datetime')}`",
        f"- Colonne équipement : `{metrics.get('equipment_column', 'machineid')}`",
        f"- Lignes utilisées pour l'entraînement de vérification : {metrics.get('training_rows', 'n/a')}",
        "",
        "## Aperçu des fichiers bruts",
        "",
    ]
    for item in raw_summaries:
        lines.extend([
            f"### {item['file']}",
            "",
            f"- Dimensions : {item['rows']:,} lignes x {item['columns']} colonnes".replace(",", " "),
            f"- Colonnes : {item['column_names']}",
            "",
            item["preview"],
            "",
        ])

    failure_counts = processed["failure_binary"].value_counts(dropna=False).to_dict()
    lines.extend([
        "## Table ML unifiée",
        "",
        f"- Pannes détectées : {int(failure_counts.get(1, 0))}",
        f"- Observations normales : {int(failure_counts.get(0, 0))}",
        f"- Taux de panne : {processed['failure_binary'].mean():.4%}",
        "",
        "### Aperçu table processed",
        "",
        to_markdown(processed.head(10)),
        "",
        "## Figures générées",
        "",
        "![Distribution des pannes](figures/failure_distribution.png)",
        "",
        "![Séries capteurs](figures/sensor_timeseries_sample.png)",
        "",
        "![Corrélations](figures/correlation_heatmap.png)",
        "",
        "![Comparaison modèles](figures/model_comparison.png)",
        "",
        "## Métriques ML",
        "",
    ])
    classification = metrics.get("classification", {})
    if classification:
        class_df = pd.DataFrame(classification["metrics"]).T
        lines.extend([
            f"- Meilleur modèle classification : `{classification['best_model']}`",
            "",
            to_markdown(class_df.reset_index().rename(columns={"index": "model"})),
            "",
        ])
    rul = metrics.get("rul", {})
    if rul:
        rul_df = pd.DataFrame(rul["metrics"]).T
        lines.extend([
            f"- Meilleur modèle RUL : `{rul['best_model']}`",
            "",
            to_markdown(rul_df.reset_index().rename(columns={"index": "model"})),
            "",
        ])

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Rapport généré: {REPORT}")


def make_failure_plot(df: pd.DataFrame) -> None:
    counts = df["failure_binary"].value_counts().sort_index()
    plt.figure(figsize=(6, 4))
    plt.bar(["Normal", "Panne"], [counts.get(0, 0), counts.get(1, 0)], color=["#10b981", "#ef4444"])
    plt.title("Distribution panne / pas panne")
    plt.ylabel("Nombre d'observations")
    plt.tight_layout()
    plt.savefig(FIGURES / "failure_distribution.png", dpi=160)
    plt.close()


def to_markdown(df: pd.DataFrame) -> str:
    small = df.copy()
    small = small.fillna("")
    headers = [str(c) for c in small.columns]
    rows = []
    for _, row in small.iterrows():
        rows.append([str(v)[:80].replace("\n", " ") for v in row.tolist()])
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, sep_line, *body])


def make_sensor_plot(df: pd.DataFrame) -> None:
    cols = [c for c in ["volt", "rotate", "pressure", "vibration"] if c in df.columns]
    sample = df[df["machineid"].eq(1)].head(240) if "machineid" in df.columns else df.head(240)
    plt.figure(figsize=(10, 5))
    for col in cols:
        plt.plot(sample[col].to_numpy(), label=col, linewidth=1.2)
    plt.title("Aperçu télémétrie machine 1")
    plt.xlabel("Heures")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "sensor_timeseries_sample.png", dpi=160)
    plt.close()


def make_correlation_plot(df: pd.DataFrame) -> None:
    wanted = [c for c in ["volt", "rotate", "pressure", "vibration", "age", "failure_binary"] if c in df.columns]
    corr = df[wanted].corr(numeric_only=True)
    plt.figure(figsize=(7, 5))
    plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar(label="Corrélation")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=35, ha="right")
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title("Corrélations principales")
    plt.tight_layout()
    plt.savefig(FIGURES / "correlation_heatmap.png", dpi=160)
    plt.close()


def make_model_plot(metrics: dict) -> None:
    class_metrics = metrics.get("classification", {}).get("metrics", {})
    if not class_metrics:
        return
    df = pd.DataFrame(class_metrics).T
    plt.figure(figsize=(9, 5))
    plt.bar(df.index, df["f1"], color="#26313d")
    plt.title("Comparaison des modèles - F1-score")
    plt.ylabel("F1-score")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(FIGURES / "model_comparison.png", dpi=160)
    plt.close()


if __name__ == "__main__":
    main()
