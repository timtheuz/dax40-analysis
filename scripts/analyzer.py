"""
analyzer.py
-----------
N-Gram-Analyse und weitere Text-Analysen auf dem Corpus-DataFrame.

Verwendung:
    python scripts/analyzer.py --company siemens
    python scripts/analyzer.py --all --export
"""

import re
import yaml
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from pathlib import Path
from collections import Counter
from itertools import combinations

# ── Styling ──────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica Neue", "DejaVu Sans"],
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.dpi": 150,
})

COLORS = {
    "data":                     "#5B5EA6",   # Violett
    "daten":                    "#9B2335",   # Rot
    "ai":                       "#E87722",   # Orange
    "ki":                       "#2BAE66",   # Grün
    "artificial intelligence":  "#E87722",
    "künstliche intelligenz":   "#2BAE66",
    "machine learning":         "#1B85B8",
    "data driven":              "#5B5EA6",
    "datengetrieben":           "#9B2335",
}

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_corpus(config: dict) -> pd.DataFrame:
    corpus_path = BASE_DIR / config["paths"]["corpus_file"]
    if not corpus_path.exists():
        raise FileNotFoundError(
            f"Corpus nicht gefunden: {corpus_path}\n"
            "Bitte zuerst 'python scripts/extractor.py --all' ausführen."
        )
    return pd.read_parquet(corpus_path)


# ──────────────────────────────────────────────────────────────────────────────
# N-GRAM KERNFUNKTIONEN
# ──────────────────────────────────────────────────────────────────────────────

def count_term(text: str, term: str, case_sensitive: bool = False) -> int:
    """
    Zählt exakte Vorkommen eines Terms (1- oder 2-Gramm) im Text.
    Verwendet Wortgrenzen für präzise Zählung.
    
    Wichtig: "ki" matcht nicht "risiko", "ai" nicht "Mai"
    """
    if not text or not term:
        return 0

    flags = 0 if case_sensitive else re.IGNORECASE
    # \b ist Wortgrenze – funktioniert auch für deutsche Umlaute
    pattern = r"\b" + re.escape(term) + r"\b"
    return len(re.findall(pattern, text, flags=flags))


def compute_ngram_frequencies(
    df: pd.DataFrame,
    terms: list[str],
    doc_type_col: str,
    wordcount_col: str,
    normalization_factor: int = 1000,
) -> pd.DataFrame:
    """
    Berechnet normalisierte N-Gram-Frequenzen für alle Terms.
    
    Returns:
        DataFrame mit Spalten: company, year, term, count_raw, count_normalized, doc_type
    """
    rows = []
    for _, row in df.iterrows():
        text = row.get(doc_type_col, "")
        wc = row.get(wordcount_col, 0)
        if not text or wc == 0:
            continue

        for term in terms:
            count_raw = count_term(text, term)
            count_norm = (count_raw / wc) * normalization_factor

            rows.append({
                "company": row["company"],
                "company_name": row.get("company_name", row["company"]),
                "year": row["year"],
                "term": term,
                "count_raw": count_raw,
                "count_normalized": round(count_norm, 4),
                "wordcount": wc,
                "doc_type": doc_type_col.replace("text_", ""),
            })

    return pd.DataFrame(rows)


def compute_all_frequencies(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Berechnet Frequenzen für alle Terme und alle Dokument-Typen."""
    all_terms = config["ngrams"]["terms_1gram"] + config["ngrams"]["terms_2gram"]
    norm_factor = config["normalization_factor"]

    all_results = []
    for doc_type in config["doc_types"]:
        text_col = f"text_{doc_type}"
        wc_col = f"wordcount_{doc_type}"
        if text_col not in df.columns:
            continue
        freq_df = compute_ngram_frequencies(df, all_terms, text_col, wc_col, norm_factor)
        all_results.append(freq_df)

    # Auch für kombinierten Text
    freq_combined = compute_ngram_frequencies(
        df, all_terms, "text_combined", "wordcount_total", norm_factor
    )
    all_results.append(freq_combined)

    if not all_results:
        return pd.DataFrame()

    return pd.concat(all_results, ignore_index=True)


# ──────────────────────────────────────────────────────────────────────────────
# VISUALISIERUNGEN
# ──────────────────────────────────────────────────────────────────────────────

def plot_term_over_time(
    freq_df: pd.DataFrame,
    terms: list[str],
    company: str,
    doc_type: str = "annual_report",
    save_path: Path | None = None,
) -> plt.Figure:
    """
    Liniendiagramm: Ausgewählte Terme im Zeitverlauf für ein Unternehmen.
    Y-Achse: Vorkommen pro 1.000 Wörter
    """
    data = freq_df[
        (freq_df["company"] == company) &
        (freq_df["doc_type"] == doc_type) &
        (freq_df["term"].isin(terms))
    ].copy()

    if data.empty:
        print(f"Keine Daten für {company} / {doc_type}")
        return None

    fig, ax = plt.subplots(figsize=(10, 6))
    years = sorted(data["year"].unique())

    for term in terms:
        term_data = data[data["term"] == term].sort_values("year")
        if term_data.empty:
            continue
        color = COLORS.get(term.lower(), "#888888")
        ax.plot(
            term_data["year"],
            term_data["count_normalized"],
            marker="o",
            linewidth=2.5,
            markersize=8,
            label=f'"{term}"',
            color=color,
        )
        # Werte direkt am Datenpunkt beschriften
        for _, point in term_data.iterrows():
            if point["count_normalized"] > 0:
                ax.annotate(
                    f"{point['count_normalized']:.2f}",
                    (point["year"], point["count_normalized"]),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=8,
                    color=color,
                )

    # Vertikale Linie bei ChatGPT-Launch (Dez 2022)
    ax.axvline(x=2022.9, color="gray", linestyle="--", alpha=0.6, linewidth=1)
    ax.text(2022.92, ax.get_ylim()[1] * 0.95, "ChatGPT\nLaunch", fontsize=7, color="gray", va="top")

    company_name = data["company_name"].iloc[0] if "company_name" in data.columns else company
    doc_label = doc_type.replace("_", " ").title()

    ax.set_title(f"{company_name} — KI/Daten-Begriffe im Zeitverlauf\n({doc_label})", 
                 fontsize=14, pad=15)
    ax.set_xlabel("Jahr", fontsize=12)
    ax.set_ylabel("Vorkommen pro 1.000 Wörter", fontsize=12)
    ax.set_xticks(years)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=10)
    ax.set_ylim(bottom=0)

    plt.tight_layout()

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
        print(f"Chart gespeichert: {save_path}")

    return fig


def plot_heatmap_terms_years(
    freq_df: pd.DataFrame,
    terms: list[str],
    company: str,
    doc_type: str = "annual_report",
    save_path: Path | None = None,
) -> plt.Figure:
    """
    Heatmap: Alle Terme × alle Jahre für ein Unternehmen.
    Zeigt visuell, welche Terme wann relevant wurden.
    """
    data = freq_df[
        (freq_df["company"] == company) &
        (freq_df["doc_type"] == doc_type) &
        (freq_df["term"].isin(terms))
    ].pivot_table(index="term", columns="year", values="count_normalized", aggfunc="mean")

    if data.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, max(4, len(terms) * 0.8)))

    sns.heatmap(
        data,
        ax=ax,
        cmap="YlOrRd",
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        cbar_kws={"label": "Vorkommen / 1.000 Wörter"},
    )

    company_name = freq_df[freq_df["company"] == company]["company_name"].iloc[0] \
        if "company_name" in freq_df.columns else company
    doc_label = doc_type.replace("_", " ").title()

    ax.set_title(f"{company_name} — Term-Frequenz-Heatmap\n({doc_label})", fontsize=14, pad=15)
    ax.set_xlabel("Jahr", fontsize=11)
    ax.set_ylabel("")
    ax.tick_params(axis="y", rotation=0)

    plt.tight_layout()

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
        print(f"Chart gespeichert: {save_path}")

    return fig


def plot_doc_type_comparison(
    freq_df: pd.DataFrame,
    term: str,
    company: str,
    save_path: Path | None = None,
) -> plt.Figure:
    """
    Balkendiagramm: Vergleich des Terms über alle Dokument-Typen × Jahre.
    Zeigt z.B. ob CEO anders spricht als Geschäftsbericht.
    """
    doc_types = ["annual_report", "ceo_speech", "supervisory_speech"]
    data = freq_df[
        (freq_df["company"] == company) &
        (freq_df["term"] == term) &
        (freq_df["doc_type"].isin(doc_types))
    ].copy()

    if data.empty:
        return None

    years = sorted(data["year"].unique())
    x = np.arange(len(years))
    width = 0.25
    doc_colors = {"annual_report": "#5B5EA6", "ceo_speech": "#E87722", "supervisory_speech": "#2BAE66"}
    doc_labels = {"annual_report": "Geschäftsbericht", "ceo_speech": "CEO-Rede", "supervisory_speech": "AR-Vorsitz-Rede"}

    fig, ax = plt.subplots(figsize=(11, 6))

    for i, dt in enumerate(doc_types):
        dt_data = data[data["doc_type"] == dt].sort_values("year")
        values = [dt_data[dt_data["year"] == y]["count_normalized"].values[0]
                  if not dt_data[dt_data["year"] == y].empty else 0 for y in years]
        bars = ax.bar(
            x + (i - 1) * width, values, width,
            label=doc_labels[dt], color=doc_colors[dt], alpha=0.85
        )

    company_name = freq_df[freq_df["company"] == company]["company_name"].iloc[0] \
        if "company_name" in freq_df.columns else company

    ax.set_title(f'{company_name} — "{term}" nach Dokumenttyp im Zeitverlauf', fontsize=14, pad=15)
    ax.set_xlabel("Jahr", fontsize=12)
    ax.set_ylabel("Vorkommen pro 1.000 Wörter", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.legend(fontsize=10)
    ax.set_ylim(bottom=0)

    plt.tight_layout()

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
        print(f"Chart gespeichert: {save_path}")

    return fig


# ──────────────────────────────────────────────────────────────────────────────
# HAUPT-ANALYSE-PIPELINE
# ──────────────────────────────────────────────────────────────────────────────

def run_analysis(companies: list[str] | None = None, export: bool = True):
    config = load_config()
    df = load_corpus(config)

    if companies:
        df = df[df["company"].isin(companies)]

    print(f"\nAnalysiere {len(df)} Corpus-Einträge...")

    # Frequenzen berechnen
    freq_df = compute_all_frequencies(df, config)

    if freq_df.empty:
        print("Keine Frequenz-Daten berechnet. Sind PDFs vorhanden und extrahiert?")
        return

    fig_dir = BASE_DIR / config["paths"]["figures"]
    report_dir = BASE_DIR / config["paths"]["reports"]

    for company in df["company"].unique():
        print(f"\n{'='*50}")
        print(f"Visualisierungen für: {company}")
        print(f"{'='*50}")

        # 1. Kernterme im Zeitverlauf (Geschäftsbericht)
        plot_term_over_time(
            freq_df,
            terms=config["ngrams"]["terms_1gram"],
            company=company,
            doc_type="annual_report",
            save_path=fig_dir / company / "01_core_terms_annual_report.png",
        )

        # 2. Alle Terme als Heatmap
        all_terms = config["ngrams"]["terms_1gram"] + config["ngrams"]["terms_2gram"]
        plot_heatmap_terms_years(
            freq_df,
            terms=all_terms,
            company=company,
            doc_type="annual_report",
            save_path=fig_dir / company / "02_heatmap_all_terms.png",
        )

        # 3. "AI"/"KI" nach Dokumenttyp
        for term in ["ai", "ki", "data", "daten"]:
            plot_doc_type_comparison(
                freq_df,
                term=term,
                company=company,
                save_path=fig_dir / company / f"03_doctype_comparison_{term}.png",
            )

    # Export Rohdaten
    if export:
        report_dir.mkdir(parents=True, exist_ok=True)
        freq_df.to_csv(report_dir / "ngram_frequencies.csv", index=False, encoding="utf-8-sig")
        freq_df.to_parquet(report_dir / "ngram_frequencies.parquet", index=False)
        print(f"\n✓ Export: {report_dir}/ngram_frequencies.*")

    plt.show()
    return freq_df


def main():
    parser = argparse.ArgumentParser(description="N-Gram-Analyse auf dem DAX-40-Corpus.")
    parser.add_argument("--company", type=str, help="Einzelnes Unternehmen")
    parser.add_argument("--all", action="store_true", help="Alle Unternehmen")
    parser.add_argument("--export", action="store_true", default=True, help="Ergebnisse exportieren")
    args = parser.parse_args()

    companies = None
    if args.company:
        companies = [args.company]

    run_analysis(companies=companies, export=args.export)


if __name__ == "__main__":
    main()
