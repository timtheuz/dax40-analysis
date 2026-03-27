"""
dax40_downloader.py
───────────────────
Lädt HV-Reden (CEO + AR-Vorsitz) für alle DAX-40-Unternehmen herunter.

Verwendung:
    python dax40_downloader.py                    # alle Firmen, alle Jahre
    python dax40_downloader.py --company SAP       # nur eine Firma
    python dax40_downloader.py --dry-run           # nur URLs prüfen, nichts herunterladen
    python dax40_downloader.py --status            # Übersicht was fehlt

Ergebnis:
    data/raw/{FIRMA}/{JAHR}/ceo_speech.pdf
    data/raw/{FIRMA}/{JAHR}/supervisory_speech.pdf
    download_report.csv   ← Übersicht aller Downloads mit Status
"""

import os
import re
import csv
import time
import argparse
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(message)s",
    handlers=[
        logging.FileHandler("download_log.txt", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# ── Konfiguration ─────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data" / "raw"
YEARS      = [2022, 2023, 2024, 2025, 2026]
DELAY      = 2.5      # Sekunden zwischen Downloads (Rate-Limiting)
TIMEOUT    = 30       # HTTP-Timeout in Sekunden

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
}

# ── Suchbegriffe für PDF-Links auf IR-Seiten ──────────────────────────────────
CEO_KEYWORDS = [
    "vorstandsvorsitzend", "ceo", "roland busch", "rede ceo",
    "hauptversammlung rede", "ceo speech", "ceo statement",
    "speech ceo", "vorstand rede", "rede des vorstands",
    "annual general meeting speech", "agm speech", "hauptversammlung 202",
]
AR_KEYWORDS = [
    "aufsichtsratsvorsitzend", "supervisory board", "chairman speech",
    "vorsitzender aufsichtsrat", "chairman statement", "ar-vorsitz",
    "brief.*aufsichtsrat", "letter.*chairman", "letter.*supervisory",
    "vorsitzender.*rede", "chairman.*rede",
]

# ─────────────────────────────────────────────────────────────────────────────
# DIREKT-URL-DATENBANK
# Bekannte direkte Download-URLs (aus IR-Seiten manuell gesammelt).
# Format: COMPANIES[firma][jahr][rolle] = URL
# "rolle" ist "ceo" oder "ar"
# ─────────────────────────────────────────────────────────────────────────────
COMPANIES = {

    "Mercedes-Benz": {
        "ir_url": "https://group.mercedes-benz.com/investors/annual-general-meeting/",
        "folder": "Mercedes-Benz",
        2022: {
            "ceo": "https://group.mercedes-benz.com/dokumente/investoren/hauptversammlung/mercedes-benz-ir-hv-2022-rede-vorstandsvorsitzender-ola-kaellenius.pdf",
            "ar":  "https://group.mercedes-benz.com/dokumente/investoren/hauptversammlung/mercedes-benz-ir-hv-2022-rede-aufsichtsratsvorsitzender-bernd-pischetsrieder.pdf",
        },
        2023: {
            "ceo": "https://group.mercedes-benz.com/dokumente/investoren/hauptversammlung/mercedes-benz-ir-hv-2023-rede-vorstandsvorsitzender-ola-kaellenius.pdf",
            "ar":  "https://group.mercedes-benz.com/dokumente/investoren/hauptversammlung/mercedes-benz-ir-hv-2023-rede-aufsichtsratsvorsitzender-bernd-pischetsrieder.pdf",
        },
        2024: {
            "ceo": "https://group.mercedes-benz.com/dokumente/investoren/hauptversammlung/mercedes-benz-ir-hv-2024-rede-vorstandsvorsitzender-ola-kaellenius.pdf",
            "ar":  "https://group.mercedes-benz.com/dokumente/investoren/hauptversammlung/mercedes-benz-ir-hv-2024-rede-aufsichtsratsvorsitzender-bernd-pischetsrieder.pdf",
        },
        2025: {
            "ceo": "https://group.mercedes-benz.com/dokumente/investoren/hauptversammlung/mercedes-benz-ir-hv-2025-rede-vorstandsvorsitzender-ola-kaellenius.pdf",
            "ar":  "https://group.mercedes-benz.com/dokumente/investoren/hauptversammlung/mercedes-benz-ir-hv-2025-rede-aufsichtsratsvorsitzender-martin-brudermueller.pdf",
        },
    },

    "BMW": {
        "ir_url": "https://www.bmwgroup.com/en/investor-relations/annual-general-meeting.html",
        "folder": "BMW",
        2022: {
            "ceo": "https://www.bmwgroup.com/content/dam/grpw/websites/bmwgroup_com/ir/downloads/de/2022/bericht/Rede_Oliver_Zipse_HV_2022.pdf",
            "ar":  "https://www.bmwgroup.com/content/dam/grpw/websites/bmwgroup_com/ir/downloads/de/2022/bericht/Rede_Norbert_Reithofer_HV_2022.pdf",
        },
        2023: {
            "ceo": "https://www.bmwgroup.com/content/dam/grpw/websites/bmwgroup_com/ir/downloads/de/2023/bericht/Rede_Oliver_Zipse_HV_2023.pdf",
            "ar":  "https://www.bmwgroup.com/content/dam/grpw/websites/bmwgroup_com/ir/downloads/de/2023/bericht/Rede_Norbert_Reithofer_HV_2023.pdf",
        },
        2024: {
            "ceo": "https://www.bmwgroup.com/content/dam/grpw/websites/bmwgroup_com/ir/downloads/de/2024/bericht/Rede_Oliver_Zipse_HV_2024.pdf",
            "ar":  "https://www.bmwgroup.com/content/dam/grpw/websites/bmwgroup_com/ir/downloads/de/2024/bericht/Rede_Norbert_Reithofer_HV_2024.pdf",
        },
        2025: {
            "ceo": "https://www.bmwgroup.com/content/dam/grpw/websites/bmwgroup_com/ir/downloads/de/2025/bericht/Rede_Oliver_Zipse_HV_2025.pdf",
            "ar":  "https://www.bmwgroup.com/content/dam/grpw/websites/bmwgroup_com/ir/downloads/de/2025/bericht/Rede_Norbert_Reithofer_HV_2025.pdf",
        },
        2026: {
            "ceo": "https://www.bmwgroup.com/content/dam/grpw/websites/bmwgroup_com/ir/downloads/en/2026/bericht/Statement_Oliver_Zipse_Annual_Conference_2026.pdf",
        },
    },

    "SAP": {
        "ir_url": "https://www.sap.com/investors/en/agm.html",
        "folder": "SAP",
        2022: {
            "ceo": "https://www.sap.com/docs/download/investors/2022/sap-2022-agm-speech-ceo.pdf",
            "ar":  "https://www.sap.com/docs/download/investors/2022/sap-2022-agm-speech-supervisory-board-chairman.pdf",
        },
        2023: {
            "ceo": "https://www.sap.com/docs/download/investors/2023/sap-2023-agm-speech-ceo.pdf",
            "ar":  "https://www.sap.com/docs/download/investors/2023/sap-2023-agm-speech-supervisory-board-chairman.pdf",
        },
        2024: {
            "ceo": "https://www.sap.com/docs/download/investors/2024/sap-2024-agm-speech-ceo.pdf",
            "ar":  "https://www.sap.com/docs/download/investors/2024/sap-2024-agm-speech-supervisory-board-chairman.pdf",
        },
        2025: {
            "ceo": "https://www.sap.com/docs/download/investors/2025/sap-2025-agm-speech-ceo.pdf",
            "ar":  "https://www.sap.com/docs/download/investors/2025/sap-2025-agm-speech-supervisory-board-chairman.pdf",
        },
    },

    "Deutsche-Telekom": {
        "ir_url": "https://www.telekom.com/de/investor-relations/hauptversammlung",
        "folder": "Deutsche-Telekom",
        2022: {
            "ceo": "https://www.telekom.com/resource/blob/330688/hv2022-rede-ceo.pdf",
            "ar":  "https://www.telekom.com/resource/blob/330690/hv2022-rede-ar-vorsitz.pdf",
        },
        2023: {
            "ceo": "https://www.telekom.com/resource/blob/hv2023-rede-ceo.pdf",
            "ar":  "https://www.telekom.com/resource/blob/hv2023-rede-ar-vorsitz.pdf",
        },
        2024: {
            "ceo": "https://www.telekom.com/resource/blob/hv2024-rede-ceo.pdf",
            "ar":  "https://www.telekom.com/resource/blob/hv2024-rede-ar-vorsitz.pdf",
        },
        2025: {
            "ceo": "https://www.telekom.com/resource/blob/hv2025-rede-ceo.pdf",
            "ar":  "https://www.telekom.com/resource/blob/hv2025-rede-ar-vorsitz.pdf",
        },
    },

    "Allianz": {
        "ir_url": "https://www.allianz.com/de/investor_relations/hauptversammlung.html",
        "folder": "Allianz",
        2022: {
            "ceo": "https://www.allianz.com/content/dam/onemarketing/azcom/Allianz_com/investor-relations/de/hauptversammlung/2022/rede-ceo-hv-2022.pdf",
            "ar":  "https://www.allianz.com/content/dam/onemarketing/azcom/Allianz_com/investor-relations/de/hauptversammlung/2022/rede-ar-vorsitz-hv-2022.pdf",
        },
        2023: {
            "ceo": "https://www.allianz.com/content/dam/onemarketing/azcom/Allianz_com/investor-relations/de/hauptversammlung/2023/rede-ceo-hv-2023.pdf",
            "ar":  "https://www.allianz.com/content/dam/onemarketing/azcom/Allianz_com/investor-relations/de/hauptversammlung/2023/rede-ar-vorsitz-hv-2023.pdf",
        },
        2024: {
            "ceo": "https://www.allianz.com/content/dam/onemarketing/azcom/Allianz_com/investor-relations/de/hauptversammlung/2024/rede-ceo-hv-2024.pdf",
            "ar":  "https://www.allianz.com/content/dam/onemarketing/azcom/Allianz_com/investor-relations/de/hauptversammlung/2024/rede-ar-vorsitz-hv-2024.pdf",
        },
        2025: {
            "ceo": "https://www.allianz.com/content/dam/onemarketing/azcom/Allianz_com/investor-relations/de/hauptversammlung/2025/rede-ceo-hv-2025.pdf",
            "ar":  "https://www.allianz.com/content/dam/onemarketing/azcom/Allianz_com/investor-relations/de/hauptversammlung/2025/rede-ar-vorsitz-hv-2025.pdf",
        },
    },

    "Volkswagen": {
        "ir_url": "https://www.volkswagen-group.com/de/hauptversammlung-1730.html",
        "folder": "Volkswagen",
        2022: {
            "ceo": "https://www.volkswagen-group.com/de/publikationen/mehr/rede-des-vorstandsvorsitzenden-hauptversammlung-2022-1592.bin",
            "ar":  "https://www.volkswagen-group.com/de/publikationen/mehr/rede-des-aufsichtsratsvorsitzenden-hauptversammlung-2022-1590.bin",
        },
        2023: {
            "ceo": "https://www.volkswagen-group.com/de/publikationen/mehr/rede-des-vorstandsvorsitzenden-hauptversammlung-2023.bin",
            "ar":  "https://www.volkswagen-group.com/de/publikationen/mehr/rede-des-aufsichtsratsvorsitzenden-hauptversammlung-2023.bin",
        },
        2024: {
            "ceo": "https://www.volkswagen-group.com/de/publikationen/mehr/rede-vorstandsvorsitzender-hauptversammlung-2024.bin",
            "ar":  "https://www.volkswagen-group.com/de/publikationen/mehr/rede-aufsichtsratsvorsitzender-hauptversammlung-2024.bin",
        },
        2025: {
            "ceo": "https://www.volkswagen-group.com/de/publikationen/mehr/rede-vorstandsvorsitzender-hauptversammlung-2025.bin",
            "ar":  "https://www.volkswagen-group.com/de/publikationen/mehr/rede-aufsichtsratsvorsitzender-hauptversammlung-2025.bin",
        },
    },

    # ── Firmen mit IR-Seite zum Scrapen (keine direkten URLs bekannt) ──────────
    "Adidas":              {"ir_url": "https://www.adidas-group.com/de/investoren/hauptversammlung/", "folder": "Adidas"},
    "Airbus":              {"ir_url": "https://www.airbus.com/en/investors/agm", "folder": "Airbus"},
    "BASF":                {"ir_url": "https://www.basf.com/de/investor-relations/hauptversammlung.html", "folder": "BASF"},
    "Bayer":               {"ir_url": "https://www.investor.bayer.de/de/hauptversammlung/", "folder": "Bayer"},
    "Beiersdorf":          {"ir_url": "https://www.beiersdorf.de/investor-relations/hauptversammlung", "folder": "Beiersdorf"},
    "Brenntag":            {"ir_url": "https://ir.brenntag.com/de/hauptversammlung/", "folder": "Brenntag"},
    "Commerzbank":         {"ir_url": "https://ir.commerzbank.com/de/hauptversammlung/", "folder": "Commerzbank"},
    "Continental":         {"ir_url": "https://www.continental.com/de/investor-relations/hauptversammlung/", "folder": "Continental"},
    "Daimler-Truck":       {"ir_url": "https://ir.daimlertruck.com/de/hauptversammlung", "folder": "Daimler-Truck"},
    "Deutsche-Bank":       {"ir_url": "https://www.db.com/ir/de/hauptversammlung.htm", "folder": "Deutsche-Bank"},
    "Deutsche-Boerse":     {"ir_url": "https://deutsche-boerse.com/dbg-de/investor-relations/hauptversammlung/", "folder": "Deutsche-Boerse"},
    "Deutsche-Post-DHL":   {"ir_url": "https://www.dpdhl.com/de/investor-relations/hauptversammlung.html", "folder": "Deutsche-Post-DHL"},
    "E.ON":                {"ir_url": "https://www.eon.com/de/investor-relations/hauptversammlung.html", "folder": "E.ON"},
    "Fresenius":           {"ir_url": "https://ir.fresenius.com/de/hauptversammlung/", "folder": "Fresenius"},
    "Fresenius-MC":        {"ir_url": "https://fmcag.com/investors/annual-general-meeting/", "folder": "Fresenius-MC"},
    "Hannover-Rueck":      {"ir_url": "https://www.hannover-re.com/de/investor-relations/hauptversammlung/", "folder": "Hannover-Rueck"},
    "Heidelberg-Materials": {"ir_url": "https://www.heidelbergmaterials.com/de/investor-relations/hauptversammlung", "folder": "Heidelberg-Materials"},
    "Henkel":              {"ir_url": "https://www.henkel.de/investoren/hauptversammlung", "folder": "Henkel"},
    "Infineon":            {"ir_url": "https://www.infineon.com/cms/de/about-infineon/investor/hauptversammlung/", "folder": "Infineon"},
    "Merck":               {"ir_url": "https://www.merckgroup.com/de/investor-relations/hauptversammlung.html", "folder": "Merck"},
    "MTU":                 {"ir_url": "https://ir.mtu.de/de/hauptversammlung/", "folder": "MTU"},
    "Muenchener-Rueck":    {"ir_url": "https://www.munichre.com/de/investor-relations/hauptversammlung.html", "folder": "Muenchener-Rueck"},
    "Porsche-Holding":     {"ir_url": "https://www.porsche-se.com/de/investor-relations/hauptversammlung/", "folder": "Porsche-Holding"},
    "Qiagen":              {"ir_url": "https://www.qiagen.com/de/investor-relations/annual-general-meeting/", "folder": "Qiagen"},
    "Rheinmetall":         {"ir_url": "https://www.rheinmetall.com/de/investor-relations/hauptversammlung/", "folder": "Rheinmetall"},
    "RWE":                 {"ir_url": "https://www.rwe.com/investor-relations/hauptversammlung/", "folder": "RWE"},
    "Scout24":             {"ir_url": "https://ir.scout24.com/de/hauptversammlung/", "folder": "Scout24"},
    "Siemens-Energy":      {"ir_url": "https://www.siemens-energy.com/de/unternehmensbereich/investoren/hauptversammlung.html", "folder": "Siemens-Energy"},
    "Siemens-Healthineers": {"ir_url": "https://www.siemens-healthineers.com/de/investor-relations/hauptversammlung", "folder": "Siemens-Healthineers"},
    "Symrise":             {"ir_url": "https://ir.symrise.com/de/hauptversammlung/", "folder": "Symrise"},
    "Vonovia":             {"ir_url": "https://ir.vonovia.de/de/hauptversammlung/", "folder": "Vonovia"},
    "Zalando":             {"ir_url": "https://ir.zalando.com/de/hauptversammlung/", "folder": "Zalando"},
}


# ─────────────────────────────────────────────────────────────────────────────
# KERN-FUNKTIONEN
# ─────────────────────────────────────────────────────────────────────────────

def get_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def download_pdf(url: str, dest: Path, session: requests.Session) -> str:
    """
    Lädt eine PDF herunter.
    Gibt zurück: 'ok' | 'skipped' | 'error:<msg>' | 'not_pdf'
    """
    if dest.exists() and dest.stat().st_size > 10_000:
        return "skipped"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = session.get(url, timeout=TIMEOUT, stream=True)
        r.raise_for_status()
        ct = r.headers.get("content-type", "")
        if "pdf" not in ct.lower() and "octet" not in ct.lower():
            # Evtl. HTML-Seite statt PDF → nicht speichern
            return f"not_pdf:{ct}"
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        size_kb = dest.stat().st_size // 1024
        log.info(f"  ✓  {dest.name}  ({size_kb} KB)")
        time.sleep(DELAY)
        return "ok"
    except Exception as e:
        return f"error:{e}"


def scrape_ir_page_for_pdfs(ir_url: str, year: int, session: requests.Session) -> dict:
    """
    Scraped eine IR-Seite und sucht nach PDF-Links für CEO/AR-Reden.
    Gibt {'ceo': url_or_None, 'ar': url_or_None} zurück.
    """
    found = {"ceo": None, "ar": None}
    try:
        r = session.get(ir_url, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Alle PDF-Links sammeln
        pdf_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            text = a.get_text(separator=" ").lower().strip()
            if ".pdf" in href or "pdf" in text:
                full_url = urljoin(ir_url, a["href"])
                pdf_links.append((full_url, text, a["href"].lower()))

        year_str = str(year)

        for url, text, href in pdf_links:
            # Nur Links die das Jahr enthalten
            if year_str not in href and year_str not in text:
                continue

            combined = text + " " + href

            if found["ceo"] is None:
                if any(kw in combined for kw in CEO_KEYWORDS):
                    found["ceo"] = url
                    log.info(f"    CEO-Link gefunden ({year}): {url}")

            if found["ar"] is None:
                if any(re.search(kw, combined) for kw in AR_KEYWORDS):
                    found["ar"] = url
                    log.info(f"    AR-Link gefunden ({year}): {url}")

            if found["ceo"] and found["ar"]:
                break

    except Exception as e:
        log.warning(f"    Scraping fehlgeschlagen ({ir_url}): {e}")

    return found


def process_company(name: str, cfg: dict, years: list, session: requests.Session,
                    dry_run: bool = False) -> list[dict]:
    """Verarbeitet eine Firma: lädt alle verfügbaren Reden herunter."""
    folder   = cfg["folder"]
    ir_url   = cfg.get("ir_url", "")
    results  = []

    log.info(f"\n{'━'*55}")
    log.info(f"  {name}")
    log.info(f"{'━'*55}")

    for year in years:
        year_cfg = cfg.get(year, {})

        for role in ["ceo", "ar"]:
            url = year_cfg.get(role)

            # Falls keine direkte URL → IR-Seite scrapen
            if not url and ir_url:
                log.info(f"  Scrape IR-Seite für {year} {role.upper()} ...")
                scraped = scrape_ir_page_for_pdfs(ir_url, year, session)
                url = scraped.get(role)

            dest = DATA_DIR / folder / str(year) / f"{role}_speech.pdf"
            row  = {
                "company":  name,
                "year":     year,
                "role":     role,
                "url":      url or "",
                "dest":     str(dest),
                "status":   "",
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }

            if not url:
                row["status"] = "no_url_found"
                log.warning(f"  ✗  {year} {role.upper()} – keine URL gefunden")
            elif dry_run:
                row["status"] = "dry_run"
                log.info(f"  ~  {year} {role.upper()} – {url}")
            else:
                row["status"] = download_pdf(url, dest, session)
                if "error" in row["status"] or "not_pdf" in row["status"]:
                    log.warning(f"  ✗  {year} {role.upper()} – {row['status']}")

            results.append(row)

    return results


def write_report(results: list[dict]) -> Path:
    """Schreibt download_report.csv mit allen Ergebnissen."""
    report = BASE_DIR / "download_report.csv"
    fieldnames = ["company","year","role","status","url","dest","timestamp"]
    with open(report, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)
    return report


def print_status(results: list[dict]) -> None:
    """Gibt eine farbige Übersichtstabelle aus."""
    ok       = [r for r in results if r["status"] in ("ok", "skipped")]
    missing  = [r for r in results if r["status"] == "no_url_found"]
    errors   = [r for r in results if "error" in r["status"] or "not_pdf" in r["status"]]

    print(f"\n{'═'*55}")
    print(f"  DOWNLOAD-ZUSAMMENFASSUNG")
    print(f"{'═'*55}")
    print(f"  ✓ Erfolgreich / übersprungen : {len(ok)}")
    print(f"  ✗ Keine URL gefunden         : {len(missing)}")
    print(f"  ✗ Fehler                     : {len(errors)}")
    print(f"{'─'*55}")

    if missing:
        print("\n  FEHLENDE URLs (manuelle Suche nötig):")
        for r in missing:
            print(f"    {r['company']:25} {r['year']} {r['role'].upper()}")
            print(f"      IR-Seite: {COMPANIES.get(r['company'],{}).get('ir_url','?')}")

    if errors:
        print("\n  FEHLERHAFTE DOWNLOADS:")
        for r in errors:
            print(f"    {r['company']:25} {r['year']} {r['role'].upper()} → {r['status']}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="DAX-40 HV-Reden Downloader")
    parser.add_argument("--company", help="Nur eine Firma (z.B. 'SAP')")
    parser.add_argument("--dry-run", action="store_true", help="Nur URLs prüfen")
    parser.add_argument("--status",  action="store_true", help="Letzten Report anzeigen")
    parser.add_argument("--years",   nargs="+", type=int, default=YEARS,
                        help="Jahre (default: 2022 2023 2024 2025 2026)")
    args = parser.parse_args()

    # Letzten Report anzeigen
    if args.status:
        report = BASE_DIR / "download_report.csv"
        if report.exists():
            import pandas as pd
            df = pd.read_csv(report)
            print(df.groupby("status")["company"].count().to_string())
        else:
            print("Kein Report gefunden. Führe erst den Download aus.")
        return

    # Firmen auswählen
    companies = COMPANIES
    if args.company:
        if args.company not in COMPANIES:
            print(f"Firma '{args.company}' nicht gefunden.")
            print(f"Verfügbar: {', '.join(COMPANIES.keys())}")
            return
        companies = {args.company: COMPANIES[args.company]}

    session = get_session()
    all_results = []

    for name, cfg in companies.items():
        results = process_company(name, cfg, args.years, session, dry_run=args.dry_run)
        all_results.extend(results)

    report_path = write_report(all_results)
    print_status(all_results)
    print(f"\n  Report gespeichert: {report_path}")
    print(f"  Log:               {BASE_DIR / 'download_log.txt'}")


if __name__ == "__main__":
    main()
