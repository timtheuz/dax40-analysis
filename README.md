# DAX 40 AI-Analyse
**Masterarbeit: Data Availability & KI-Wahrnehmung im Zeitverlauf (2022–2025)**

N-Gram-Analyse von Geschäftsberichten und HV-Reden der DAX-40-Unternehmen.

---

## Setup

```bash
# 1. Repository klonen / Ordner öffnen
cd dax40-ai-analysis

# 2. Virtuelle Umgebung erstellen
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
# .venv\Scripts\activate       # Windows

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Sprachmodelle für NLP (optional, für Lemmatisierung)
python -m spacy download de_core_news_lg
python -m spacy download en_core_web_sm

# 5. JupyterLab starten
jupyter lab
```

---

## Workflow

### Schritt 1: Konfiguration prüfen
`config.yaml` enthält alle URLs und Analyse-Parameter.
Fehlende URLs (insb. HV-Reden) manuell ergänzen.

### Schritt 2: PDFs herunterladen
```bash
# Nur Siemens (PoC)
python scripts/downloader.py --company siemens --all-years

# Alle DAX-40-Unternehmen
python scripts/downloader.py --all
```

Nicht automatisch downloadbare Dokumente (HV-Reden) manuell herunterladen und benennen:
```
data/raw/siemens/2022/
    annual_report.pdf      ← Geschäftsbericht
    ceo_speech.pdf         ← CEO-Rede Hauptversammlung
    supervisory_speech.pdf ← Aufsichtsratsvorsitzende-Rede
```

### Schritt 3: Text extrahieren & Corpus aufbauen
```bash
python scripts/extractor.py --company siemens
# Erstellt: data/processed/corpus.parquet
```

### Schritt 4: Analyse in Jupyter
```
notebooks/03_analysis.ipynb   ← Hier starten für Charts & Tabellen
```

### Schritt 5: Batch-Analyse (alle Unternehmen)
```bash
python scripts/analyzer.py --all --export
# Charts → outputs/figures/{company}/
# Tabellen → outputs/reports/
```

---

## Ordnerstruktur

```
dax40-ai-analysis/
├── config.yaml                 ← Zentrale Konfiguration
├── requirements.txt
├── data/
│   ├── raw/                    ← Original-PDFs (nicht ins Git!)
│   │   └── siemens/
│   │       ├── 2022/
│   │       │   ├── annual_report.pdf
│   │       │   ├── ceo_speech.pdf
│   │       │   └── supervisory_speech.pdf
│   │       ├── 2023/ ...
│   └── processed/
│       └── corpus.parquet      ← Zentraler Analyse-Datensatz
├── notebooks/
│   ├── 01_ingest.ipynb         ← Download & Extraktion (interaktiv)
│   ├── 02_clean.ipynb          ← Text-Bereinigung & Qualitätskontrolle
│   └── 03_analysis.ipynb       ← Haupt-Analyse & Charts
├── scripts/
│   ├── downloader.py           ← PDF-Download-Automatisierung
│   ├── extractor.py            ← PDF→Text, Corpus-Aufbau
│   └── analyzer.py             ← N-Gram-Analyse & Visualisierungen
└── outputs/
    ├── figures/                ← Charts (.png, .svg)
    │   └── siemens/
    └── reports/                ← Tabellen (.csv, .xlsx, .parquet)
```

---

## Analyse-Terme

### 1-Gramme (einzelne Wörter)
| Deutsch | Englisch |
|---------|----------|
| daten   | data     |
| ki      | ai       |

### 2-Gramme (Wortpaare)
| Deutsch                  | Englisch               |
|--------------------------|------------------------|
| künstliche intelligenz   | artificial intelligence |
| datengetrieben           | data driven            |
| neuronales netz          | neural network         |
| tiefes lernen            | deep learning          |
| –                        | machine learning       |
| –                        | large language model   |
| –                        | generative ai          |

---

## Dokument-Typen

| Kürzel               | Beschreibung                              |
|----------------------|-------------------------------------------|
| `annual_report`      | Geschäftsbericht / Jahresbericht          |
| `ceo_speech`         | CEO-Rede Hauptversammlung (Transkript)    |
| `supervisory_speech` | AR-Vorsitz-Rede Hauptversammlung          |

---

## IDE-Empfehlung

**Claude Code** (Terminal) + **JupyterLab** (Browser) + **VS Code** (Dateieditor)

```bash
# Claude Code installieren
npm install -g @anthropic-ai/claude-code

# Im Projektordner starten
cd dax40-ai-analysis
claude
```

---

## Hinweise zur Datenbeschaffung

- **Geschäftsberichte**: Meist direkt als PDF auf der IR-Seite verfügbar
- **HV-Reden**: Oft als Webseite oder Video publiziert, Transkripte selten als PDF
  - Tipp: Viele Unternehmen veröffentlichen die Reden als HTML → mit Selenium scrapen
  - Alternativ: YouTube-Transkripte (automatisch) für HV-Streams
  - Notfallplan: Rede-Zusammenfassungen aus Pressemitteilungen

## .gitignore

```
data/raw/           # Keine PDFs ins Repository
data/processed/     # Corpus-Dateien ggf. zu groß
.venv/
__pycache__/
*.pyc
outputs/figures/    # Regenerierbar
```
