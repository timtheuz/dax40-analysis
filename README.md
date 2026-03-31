# DAX 40 CEOs - Hauptversammlungsreden Analyse
Systematische Analyse 136 CEO-Reden aus 35 DAX-Unternehmen (2022-2025) zu Erwähnungen aus den Keyword-Gruppen KI (inkl. Künstliche Intelligenz, AI, Machine Learning, GenAI, LLM) und Daten (inkl. Daten, Data, data-driven).


---

## Workflow

### Schritt 1: PDFs herunterladen, Text extrahieren & Corpus aufbauen (optional)
1. HV-Reden manuell herunterladen und ordnen.

2. _documents_registry.py_ anpassen

3. Corpus erstellen
```bash
python scripts/05_extraction.py
Erstellt: data/processed/corpus.parquet
```

Alternativ _/data/processed/corpus.parquet_ nutzen

### Schritt 2: Analyse in Jupyter
```
notebooks/06_analysis_crosscompany.ipynb   ← run all
```


---

## Ordnerstruktur

```
dax40-ai-analysis/
├── data/
│   ├── raw/                    ← Original-PDFs (nicht im Git)
│   │   └── siemens/
│   │       ├── 2022/
│   │       │   ├── ceo_speech.pdf
│   │       │   └── supervisory_speech.pdf
│   │       ├── 2023/ ...
│   └── processed/
│       └── corpus.parquet      ← Zentraler Analyse-Datensatz
├── scripts/
│   ├── documents_registry.py       ← Dokumentenstruktur fürs Einlesen
│   ├── 05_extraction.py            ← PDF→Text, Corpus-Aufbau
│   └── 06_analysis_crosscompany.py ← Haupt-Analyse & Charts
└── outputs/
    ├── figures/                ← Charts (.png, .svg)
    │   └── cross_company/
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
| Deutsch            | Englisch                |
|--------------------|-------------------------|
| künstliche intelligenz | artificial intelligence |
| datengetrieben     | data driven             |
| neuronales netz    | deep learning           |
| etc.               | machine learning        |
|                    | large language model    |
|                    | etc.                    |


---

## .gitignore

```
data/raw/           # Keine PDFs ins Repository
data/processed/     # Corpus-Dateien ggf. zu groß
.venv/
__pycache__/
*.pyc
outputs/figures/    # Regenerierbar
```
