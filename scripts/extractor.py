"""
extractor.py
------------
Extrahiert Text aus PDFs und baut den zentralen Corpus-DataFrame auf.

Verwendung:
    python scripts/extractor.py --company siemens
    python scripts/extractor.py --all
    python scripts/extractor.py --rebuild  # alles neu verarbeiten
"""

import re
import yaml
import fitz          # PyMuPDF
import argparse
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ──────────────────────────────────────────────
# PDF-Extraktion
# ──────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extrahiert den gesamten Fließtext aus einer PDF.
    Verwendet PyMuPDF (fitz) für zuverlässige Unicode-Unterstützung (wichtig für DE).
    """
    if not pdf_path.exists():
        log.warning(f"  PDF nicht gefunden: {pdf_path}")
        return ""

    doc = fitz.open(str(pdf_path))
    pages_text = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")   # "text" = Fließtext ohne Koordinaten
        if text.strip():
            pages_text.append(text)

    full_text = "\n".join(pages_text)
    log.info(f"  Extrahiert: {pdf_path.name} ({len(doc)} Seiten, {len(full_text):,} Zeichen)")
    doc.close()
    return full_text


def clean_text(raw_text: str) -> str:
    """
    Bereinigt extrahierten PDF-Text für die Analyse.
    Behält deutschen und englischen Text bei.
    """
    # Silbentrennungen zusammenführen (häufig in deutschen Jahresberichten)
    text = re.sub(r"-\n", "", raw_text)

    # Zeilenumbrüche innerhalb von Sätzen entfernen
    text = re.sub(r"(?<![.!?])\n(?![A-ZÄÖÜ\d•–])", " ", text)

    # Mehrfache Leerzeichen normalisieren
    text = re.sub(r" {2,}", " ", text)

    # Seitenköpfe/-füße entfernen (typische Muster in Geschäftsberichten)
    text = re.sub(r"\d+\s+Siemens\s+Geschäftsbericht\s+\d{4}", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Siemens\s+Annual\s+Report\s+\d{4}", "", text, flags=re.IGNORECASE)

    # Bullet-Zeichen normalisieren
    text = re.sub(r"[•·▪■▶►]", " ", text)

    # URLs entfernen (verzerren Wortfrequenzen)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"www\.\S+", " ", text)

    # Überflüssige Leerzeichen am Zeilenende
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def count_words(text: str) -> int:
    """Zählt Wörter (Tokens) im Text."""
    return len(text.split()) if text else 0


# ──────────────────────────────────────────────
# Corpus-Aufbau
# ──────────────────────────────────────────────

def process_company_year(
    company: str,
    year: int,
    config: dict,
    existing_df: pd.DataFrame | None = None
) -> dict | None:
    """
    Verarbeitet alle Dokumente eines Unternehmens/Jahres.
    Gibt einen DataFrame-Row als Dictionary zurück.
    """
    raw_dir = BASE_DIR / config["paths"]["raw_data"] / company / str(year)

    if not raw_dir.exists():
        log.warning(f"  Ordner nicht gefunden: {raw_dir}")
        return None

    # Prüfen, ob bereits verarbeitet (Skip-Logik)
    if existing_df is not None and len(existing_df) > 0:
        existing = existing_df[
            (existing_df["company"] == company) &
            (existing_df["year"] == year)
        ]
        if not existing.empty:
            log.info(f"  Bereits im Corpus: {company} {year} – übersprungen")
            return None

    row = {
        "company": company,
        "company_name": config["companies"][company]["name"],
        "year": year,
        "processed_at": datetime.now().isoformat(),
    }

    for doc_type in config["doc_types"]:
        pdf_path = raw_dir / f"{doc_type}.pdf"
        raw_text = extract_text_from_pdf(pdf_path)
        clean = clean_text(raw_text)

        row[f"text_{doc_type}"] = clean
        row[f"wordcount_{doc_type}"] = count_words(clean)
        row[f"available_{doc_type}"] = bool(clean)

    # Kombinierter Text für unternehmensspezifische Analysen
    all_texts = [
        row.get(f"text_{dt}", "") for dt in config["doc_types"]
        if row.get(f"text_{dt}")
    ]
    row["text_combined"] = "\n\n".join(all_texts)
    row["wordcount_total"] = count_words(row["text_combined"])

    return row


def build_corpus(config: dict, companies: list[str] | None = None, rebuild: bool = False) -> pd.DataFrame:
    """
    Baut den gesamten Corpus-DataFrame auf und speichert ihn als .parquet.
    """
    corpus_path = BASE_DIR / config["paths"]["corpus_file"]
    corpus_path.parent.mkdir(parents=True, exist_ok=True)

    # Bestehenden Corpus laden (Incremental Build)
    existing_df = None
    if not rebuild and corpus_path.exists():
        existing_df = pd.read_parquet(corpus_path)
        log.info(f"Bestehenden Corpus geladen: {len(existing_df)} Einträge")

    companies_to_process = companies or list(config["companies"].keys())
    new_rows = []

    for company in companies_to_process:
        log.info(f"\n{'─'*40}\nVerarbeite: {company}")
        for year in config["years"]:
            row = process_company_year(company, year, config, existing_df)
            if row:
                new_rows.append(row)

    if not new_rows:
        log.info("Keine neuen Einträge. Corpus ist aktuell.")
        return existing_df if existing_df is not None else pd.DataFrame()

    new_df = pd.DataFrame(new_rows)

    # Zusammenführen
    if existing_df is not None and not rebuild:
        corpus_df = pd.concat([existing_df, new_df], ignore_index=True)
        # Duplikate entfernen (company + year als Key)
        corpus_df = corpus_df.drop_duplicates(subset=["company", "year"], keep="last")
    else:
        corpus_df = new_df

    corpus_df = corpus_df.sort_values(["company", "year"]).reset_index(drop=True)

    # Speichern
    corpus_df.to_parquet(corpus_path, index=False, engine="pyarrow")
    log.info(f"\n✓ Corpus gespeichert: {corpus_path}")
    log.info(f"  Einträge gesamt: {len(corpus_df)}")
    log.info(f"  Unternehmen: {corpus_df['company'].nunique()}")
    log.info(f"  Jahre: {sorted(corpus_df['year'].unique().tolist())}")

    # Schnelle Übersicht
    print("\n" + "="*60)
    print("CORPUS-ÜBERSICHT")
    print("="*60)
    overview = corpus_df.groupby(["company", "year"])[["wordcount_total"]].sum()
    print(overview.to_string())

    return corpus_df


def main():
    parser = argparse.ArgumentParser(description="Extrahiert PDF-Text und baut Corpus auf.")
    parser.add_argument("--company", type=str, help="Einzelnes Unternehmen")
    parser.add_argument("--all", action="store_true", help="Alle Unternehmen")
    parser.add_argument("--rebuild", action="store_true", help="Corpus komplett neu aufbauen")
    args = parser.parse_args()

    config = load_config()

    if args.all or (not args.company):
        build_corpus(config, rebuild=args.rebuild)
    elif args.company:
        build_corpus(config, companies=[args.company], rebuild=args.rebuild)


if __name__ == "__main__":
    main()
