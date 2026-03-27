"""
downloader.py
-------------
Lädt Geschäftsberichte und HV-Reden von Investor-Relations-Seiten herunter.

Verwendung:
    python scripts/downloader.py --company siemens --year 2022
    python scripts/downloader.py --company siemens --all-years
    python scripts/downloader.py --all  # alle Unternehmen, alle Jahre
"""

import os
import time
import yaml
import requests
import argparse
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("download_log.txt"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# Basis-Pfad relativ zu diesem Skript
BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def download_pdf(url: str, dest_path: Path, delay: float = 2.0) -> bool:
    """
    Lädt eine PDF-Datei herunter.
    
    Args:
        url: Download-URL
        dest_path: Zielpfad (inkl. Dateiname)
        delay: Wartezeit nach Download (Rate Limiting)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    if dest_path.exists():
        log.info(f"  Bereits vorhanden: {dest_path.name} – übersprungen")
        return True

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/pdf,*/*",
    }

    try:
        log.info(f"  Lade herunter: {url}")
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()

        # Content-Type prüfen
        content_type = response.headers.get("content-type", "")
        if "pdf" not in content_type.lower() and "octet-stream" not in content_type.lower():
            log.warning(f"  Unerwarteter Content-Type: {content_type}")

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size_kb = dest_path.stat().st_size / 1024
        log.info(f"  ✓ Gespeichert: {dest_path.name} ({file_size_kb:.0f} KB)")
        time.sleep(delay)
        return True

    except requests.exceptions.RequestException as e:
        log.error(f"  ✗ Fehler beim Download von {url}: {e}")
        return False


def download_company_year(company: str, year: int, config: dict) -> dict:
    """
    Lädt alle Dokumente für ein Unternehmen und Jahr herunter.
    
    Returns:
        Status-Dictionary mit Ergebnis pro Dokument-Typ
    """
    company_config = config["companies"].get(company)
    if not company_config:
        log.error(f"Unternehmen '{company}' nicht in config.yaml gefunden.")
        return {}

    year_config = company_config.get("years", {}).get(year, {})
    raw_dir = BASE_DIR / config["paths"]["raw_data"] / company / str(year)
    raw_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    log.info(f"\n{'='*50}")
    log.info(f"Unternehmen: {company_config['name']} | Jahr: {year}")
    log.info(f"{'='*50}")

    # 1. Geschäftsbericht
    annual_url = year_config.get("annual_report")
    if annual_url:
        dest = raw_dir / "annual_report.pdf"
        results["annual_report"] = download_pdf(annual_url, dest)
    else:
        log.warning(f"  Kein Annual Report URL für {company} {year}")
        results["annual_report"] = None

    # 2. CEO-Rede (muss manuell ergänzt werden oder via Selenium gescraped)
    ceo_url = year_config.get("ceo_speech")
    if ceo_url:
        dest = raw_dir / "ceo_speech.pdf"
        results["ceo_speech"] = download_pdf(ceo_url, dest)
    else:
        log.warning(
            f"  CEO-Rede für {company} {year} nicht konfiguriert. "
            f"Bitte manuell unter: {year_config.get('agm_url', 'unbekannt')}"
        )
        results["ceo_speech"] = None

    # 3. Aufsichtsratsvorsitzende-Rede
    supervisory_url = year_config.get("supervisory_speech")
    if supervisory_url:
        dest = raw_dir / "supervisory_speech.pdf"
        results["supervisory_speech"] = download_pdf(supervisory_url, dest)
    else:
        log.warning(
            f"  Aufsichtsratsrede für {company} {year} nicht konfiguriert."
        )
        results["supervisory_speech"] = None

    return results


def generate_download_report(all_results: dict, config: dict) -> None:
    """Erstellt eine Übersichtstabelle aller Download-Status."""
    import pandas as pd

    rows = []
    for company, years in all_results.items():
        for year, docs in years.items():
            for doc_type, status in docs.items():
                rows.append({
                    "company": company,
                    "year": year,
                    "doc_type": doc_type,
                    "status": "✓" if status is True else ("—" if status is None else "✗"),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })

    df = pd.DataFrame(rows)
    report_path = BASE_DIR / config["paths"]["reports"] / "download_status.csv"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(report_path, index=False, encoding="utf-8-sig")
    log.info(f"\nDownload-Report gespeichert: {report_path}")

    # Übersicht in Terminal
    pivot = df.pivot_table(
        index=["company", "year"],
        columns="doc_type",
        values="status",
        aggfunc="first"
    )
    print("\n" + "="*60)
    print("DOWNLOAD-ÜBERSICHT")
    print("="*60)
    print(pivot.to_string())


def main():
    parser = argparse.ArgumentParser(
        description="Lädt IR-Dokumente der DAX-40-Unternehmen herunter."
    )
    parser.add_argument("--company", type=str, help="Unternehmensname (z.B. 'siemens')")
    parser.add_argument("--year", type=int, help="Jahr (z.B. 2022)")
    parser.add_argument("--all-years", action="store_true", help="Alle konfigurierten Jahre")
    parser.add_argument("--all", action="store_true", help="Alle Unternehmen & Jahre")
    args = parser.parse_args()

    config = load_config()
    all_results = {}

    if args.all:
        for company in config["companies"]:
            all_results[company] = {}
            for year in config["years"]:
                all_results[company][year] = download_company_year(company, year, config)
    elif args.company and args.all_years:
        company = args.company
        all_results[company] = {}
        for year in config["years"]:
            all_results[company][year] = download_company_year(company, year, config)
    elif args.company and args.year:
        company = args.company
        all_results[company] = {args.year: download_company_year(company, args.year, config)}
    else:
        parser.print_help()
        return

    generate_download_report(all_results, config)


if __name__ == "__main__":
    main()
