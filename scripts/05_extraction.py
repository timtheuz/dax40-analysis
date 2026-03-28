"""
05_extraction.py
────────────────
Liest alle PDFs, extrahiert Text, erkennt Sprache,
exportiert corpus.parquet + corpus_meta.csv.

Ausführen: python 05_extraction.py
Danach:    jupyter nbconvert --to notebook --execute 05_extraction.py (optional)
"""

# ─── KONFIGURATION ────────────────────────────────────────────────────────────
import sys, re, subprocess, warnings
from pathlib import Path
import pandas as pd
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path('/Users/tgumpp/Documents/MasterThesis/dax40-ai-analysis')
PDF_BASE     = PROJECT_ROOT / 'data' / 'raw'
OUTPUT_DIR   = PROJECT_ROOT / 'data' / 'processed'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PROJECT_ROOT))
from documents_registry import DOCUMENTS, SECTOR_MAP

YEARS = [2022, 2023, 2024, 2025]

print(f'Projektpfad : {PROJECT_ROOT}')
print(f'Dokumente   : {len(DOCUMENTS)} Einträge in Registry')
print(f'Analysejahre: {YEARS}')


# ─── VERFÜGBARKEITS-CHECK ─────────────────────────────────────────────────────
in_scope   = [(f,y,s,r,k) for f,y,s,r,k in DOCUMENTS if y in YEARS]
found      = [(f,y,s,r,k) for f,y,s,r,k in in_scope if (PDF_BASE/f).exists()]
missing    = [(f,y,s,r,k) for f,y,s,r,k in in_scope if not (PDF_BASE/f).exists()]
check_rows = [(f,y,s,r,k) for f,y,s,r,k in in_scope if k == 'check']

print(f'\nIm Analysezeitraum (2022–2025): {len(in_scope)} Einträge')
print(f'  ✓ Gefunden : {len(found)}')
print(f'  ✗ Fehlend  : {len(missing)}')
print(f'  ⚠ Prüfen   : {len(check_rows)}')

if missing:
    print('\nFehlende Dateien:')
    for f,y,s,r,_ in missing:
        print(f'  {f.split("/")[0]:25} {y} {r.upper():3}  {Path(f).name}')

if check_rows:
    print('\n⚠ Bitte Zuordnung prüfen:')
    for f,y,s,r,_ in check_rows:
        print(f'  {f.split("/")[0]:25} {y} {r.upper():3}  {s:30}  {Path(f).name}')


# ─── HILFSFUNKTIONEN ──────────────────────────────────────────────────────────
DE_MARKERS = {'der','die','das','und','ist','wir','für','mit','auf','auch',
              'des','den','dem','ein','eine','nicht','als','bei','nach','von'}
EN_MARKERS = {'the','and','our','we','for','with','are','have','this','that',
              'of','in','to','a','is','it','at','as','from','has'}

def detect_language(text):
    words = text.lower().split()[:500]
    de    = sum(1 for w in words if w in DE_MARKERS)
    en    = sum(1 for w in words if w in EN_MARKERS)
    return 'de' if de >= en else 'en'


def extract_text(path):
    # Versuch 1: pdftotext
    try:
        r = subprocess.run(
            ['pdftotext', '-layout', str(path), '-'],
            capture_output=True, text=True, timeout=30
        )
        text = r.stdout.strip()
        if r.returncode == 0 and len(text.split()) > 50:
            return r.stdout
    except Exception:
        pass

    # Versuch 2: pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(str(path)) as pdf:
            text = '\n'.join(p.extract_text() or '' for p in pdf.pages)
            if len(text.split()) > 50:
                return text
    except Exception:
        pass

    # Versuch 3: OCR (für gescannte PDFs)
    print(f'    → OCR wird verwendet für: {path.name}')
    try:
        from pdf2image import convert_from_path
        import pytesseract
        pages = convert_from_path(str(path), dpi=200)
        lang = 'deu+eng'
        return '\n'.join(
            pytesseract.image_to_string(page, lang=lang)
            for page in pages
        )
    except Exception as e:
        print(f'    → OCR fehlgeschlagen: {e}')
        return ''


def clean_text(raw):
    text = re.sub(r'-\n', '', raw)
    text = re.sub(r'Seite\s+\d+\s+von\s+\d+', '', text, flags=re.IGNORECASE)
    text = text.replace('\x0c', '\n')
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ─── EXTRAKTION ───────────────────────────────────────────────────────────────
print('\nExtrahiere PDFs ...')
records = []

for fname, year, speaker, role, confidence in DOCUMENTS:
    if year not in YEARS:
        continue
    path = PDF_BASE / fname
    if not path.exists():
        continue

    company = fname.split('/')[0]
    raw     = extract_text(path)
    text    = clean_text(raw)
    lang    = detect_language(text)
    wc      = len(text.split())

    records.append({
        'company':    company,
        'sector':     SECTOR_MAP.get(company, 'Unbekannt'),
        'year':       year,
        'role':       role,
        'speaker':    speaker,
        'language':   lang,
        'confidence': confidence,
        'wordcount':  wc,
        'text':       text,
        'filename':   fname,
    })

    flag = '⚠' if confidence == 'check' else '✓'
    print(f'  {flag} {company:25} {year} {role.upper():3} [{lang}] {wc:>5} Wörter')

corpus = pd.DataFrame(records)
print(f'\nCorpus: {len(corpus)} Dokumente | {corpus["wordcount"].sum():,} Wörter gesamt')
print(f'Firmen: {corpus["company"].nunique()} | Jahre: {sorted(corpus["year"].unique())}')

# ─── STUPIDITY CHECK 1: Dokumente mit niedrigem Wordcount ────────────────────
WORDCOUNT_THRESHOLD = 100

low_wc = corpus[corpus['wordcount'] < WORDCOUNT_THRESHOLD].copy()
print(f'\n⚠ Dokumente mit weniger als {WORDCOUNT_THRESHOLD} Wörtern: {len(low_wc)}')

for _, row in low_wc.iterrows():
    print(f'\n{"─"*60}')
    print(f'  {row["company"]} | {row["year"]} | {row["role"].upper()}')
    print(f'  Wordcount: {row["wordcount"]}')
    print(f'  Datei: {row["filename"]}')
    print(f'  Extrahierter Text (komplett):')
    print(f'  >>>{row["text"]}<<<')

# ─── EXPORT ───────────────────────────────────────────────────────────────────
corpus.to_parquet(OUTPUT_DIR / 'corpus.parquet', index=False)
corpus.drop(columns=['text']).to_csv(
    OUTPUT_DIR / 'corpus_meta.csv', index=False, encoding='utf-8-sig'
)

print(f'\n✓ corpus.parquet   → {OUTPUT_DIR / "corpus.parquet"}')
print(f'✓ corpus_meta.csv  → {OUTPUT_DIR / "corpus_meta.csv"}')

print('\nÜbersicht nach Firma / Jahr:')
print(corpus.groupby(['company','year'])['role']
      .apply(lambda x: '/'.join(sorted(x)))
      .unstack()
      .to_string())
