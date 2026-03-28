"""
06_analysis_crosscompany.py
────────────────────────────
Lädt corpus.parquet, berechnet Frequenzen und erstellt 4 Plots.
Voraussetzung: 05_extraction.py wurde ausgeführt.

Ausführen: python 06_analysis_crosscompany.py
"""

# ════════════════════════════════════════════════════════════════════════════
# KONFIGURATION — hier alle Parameter anpassen
# ════════════════════════════════════════════════════════════════════════════
import re, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.25,
    'grid.linestyle': '--',
    'figure.dpi': 150,
    'figure.facecolor': 'white',
})

# ── Pfade ──
PROJECT_ROOT = Path('/Users/tgumpp/Documents/MasterThesis/dax40-ai-analysis')
CORPUS_PATH  = PROJECT_ROOT / 'data' / 'processed' / 'corpus.parquet'
FIG_DIR      = PROJECT_ROOT / 'outputs' / 'figures' / 'cross_company'
REP_DIR      = PROJECT_ROOT / 'outputs' / 'reports'
FIG_DIR.mkdir(parents=True, exist_ok=True)
REP_DIR.mkdir(parents=True, exist_ok=True)

# ── Analysejahre ──
YEARS = [2022, 2023, 2024, 2025]

# ── Schlagwortgruppen (Groß-/Kleinschreibung wird ignoriert) ──
TERMS = {
    'KI/AI': [
        'ki', 'ai',
        'künstliche intelligenz',
        'artificial intelligence',
        'generative ai', 'generative ki',
        'machine learning', 'deep learning',
        'large language model',
    ],
    'Daten/Data': [
        'daten', 'data',
        'datengetrieben', 'data-driven', 'data driven',
        'datenarchitektur', 'data architecture',
    ],
}
GROUPS = list(TERMS.keys())

# ── Farben ──
C = {
    'KI/AI':      '#1A5F9E',
    'Daten/Data': '#D95F2B',
    'ceo':        '#1A5F9E',
    'ar':         '#D95F2B',
}

NORM_FACTOR = 1000

print('✓ Konfiguration geladen')
print(f'  KI/AI-Terme     : {TERMS["KI/AI"]}')
print(f'  Daten/Data-Terme: {TERMS["Daten/Data"]}')


# ════════════════════════════════════════════════════════════════════════════
# DATEN LADEN & FREQUENZEN BERECHNEN
# Alle Plot-Funktionen lesen aus `freq` und `agg`
# ════════════════════════════════════════════════════════════════════════════
def count_term(text, term):
    if not text:
        return 0
    return len(re.findall(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE))


corpus = pd.read_parquet(CORPUS_PATH)
corpus = corpus[corpus['year'].isin(YEARS)].copy()
print(f'\nCorpus: {len(corpus)} Dokumente | {corpus["company"].nunique()} Firmen')

rows = []
for _, doc in corpus.iterrows():
    for group, terms in TERMS.items():
        raw  = sum(count_term(doc['text'], t) for t in terms)
        norm = (raw / doc['wordcount']) * NORM_FACTOR if doc['wordcount'] > 0 else 0
        rows.append({
            'company':    doc['company'],
            'sector':     doc['sector'],
            'year':       doc['year'],
            'role':       doc['role'],
            'language':   doc['language'],
            'wordcount':  doc['wordcount'],
            'group':      group,
            'count_raw':  raw,
            'count_norm': round(norm, 4),
        })

freq = pd.DataFrame(rows)

agg = freq.groupby(['company', 'sector', 'year', 'group']).agg(
    count_raw=('count_raw', 'sum'),
    count_norm=('count_norm', 'mean'),
    wordcount=('wordcount', 'sum'),
).reset_index()

freq.to_csv(REP_DIR / 'freq_detail.csv',     index=False, encoding='utf-8-sig')
agg.to_csv(REP_DIR  / 'freq_aggregated.csv', index=False, encoding='utf-8-sig')
print('✓ freq_detail.csv & freq_aggregated.csv exportiert')

# ════════════════════════════════════════════════════════════════════════════
# STUPIDITY CHECK 2: KWIC für Daten/Data
# ════════════════════════════════════════════════════════════════════════════
def kwic_check(corpus, terms, company=None, year=None, window_sentences=1):
    """
    Gibt alle Vorkommen der Terms im Satzkontext aus.
    window_sentences=1 → den ganzen Satz in dem der Treffer liegt.
    """
    subset = corpus.copy()
    if company:
        subset = subset[subset['company'] == company]
    if year:
        subset = subset[subset['year'] == year]

    results = []
    for _, doc in subset.iterrows():
        # Text in Sätze aufteilen
        sentences = re.split(r'(?<=[.!?])\s+', doc['text'])
        for sent in sentences:
            for term in terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, sent, re.IGNORECASE):
                    # Treffer im Satz markieren
                    marked = re.sub(
                        pattern,
                        lambda m: f'>>>{m.group()}<<<',
                        sent,
                        flags=re.IGNORECASE
                    )
                    results.append({
                        'company': doc['company'],
                        'year':    doc['year'],
                        'role':    doc['role'],
                        'term':    term,
                        'context': marked.strip(),
                    })

    df = pd.DataFrame(results)
    return df


# Ausführen — alle Daten/Data-Treffer ausgeben
daten_kwic = kwic_check(
    corpus,
    terms=TERMS['Daten/Data'],
    # company='SAP',   # optional: auf eine Firma einschränken
    # year=2024,       # optional: auf ein Jahr einschränken
)

print(f'\nDaten/Data-Treffer gesamt: {len(daten_kwic)}')
print(f'Davon verdächtig kurze Kontexte (< 20 Zeichen):')
short = daten_kwic[daten_kwic['context'].str.len() < 20]
print(short[['company','year','role','context']].to_string(index=False))

# Export zur manuellen Durchsicht
daten_kwic.to_csv(
    REP_DIR / 'kwic_daten_check.csv',
    index=False,
    encoding='utf-8-sig'
)
print(f'\n✓ Alle Treffer exportiert nach: {REP_DIR}/kwic_daten_check.csv')


# ════════════════════════════════════════════════════════════════════════════
# PLOT 1 — Zeitverlauf: y1 = norm, y2 = Gesamtsumme
# ════════════════════════════════════════════════════════════════════════════
print('\nErstelle Plot 1 ...')

yearly = agg.groupby(['year', 'group']).agg(
    norm_mean=('count_norm', 'mean'),
    raw_sum=('count_raw', 'sum'),
).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()

for group in GROUPS:
    sub   = yearly[yearly['group'] == group].sort_values('year')
    color = C[group]
    ax1.plot(sub['year'], sub['norm_mean'], marker='o', linewidth=2.5,
             markersize=8, color=color, label=f'{group} (/ 1.000 Wörter)', zorder=3)
    ax2.plot(sub['year'], sub['raw_sum'], marker='s', linewidth=1.5,
             markersize=6, color=color, linestyle='--', alpha=0.5,
             label=f'{group} (Gesamtsumme)', zorder=2)
    for _, row in sub.iterrows():
        ax1.annotate(f"{row['norm_mean']:.2f}",
                     (row['year'], row['norm_mean']),
                     xytext=(0, 9), textcoords='offset points',
                     ha='center', fontsize=8, color=color, fontweight='bold')

ax1.axvline(x=2022.88, color='#999', linestyle=':', linewidth=1.2, alpha=0.7)
ax1.text(2022.91, ax1.get_ylim()[1] * 0.95,
         'ChatGPT\nLaunch', fontsize=7.5, color='#666', style='italic', va='top')

ax1.set_xticks(YEARS)
ax1.set_xlabel('Jahr', fontsize=11)
ax1.set_ylabel('Ø Nennungen / 1.000 Wörter', fontsize=10)
ax2.set_ylabel('Gesamtsumme Nennungen (alle Firmen)', fontsize=10, color='#999')
ax1.set_ylim(bottom=0)
ax2.set_ylim(bottom=0)
ax2.tick_params(axis='y', colors='#999')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc='upper left')
ax1.set_title(
    'DAX-Reden: KI/AI & Daten im Zeitverlauf 2022–2025\n'
    '(Ø normalisiert — linke Achse | Gesamtsumme — rechte Achse)',
    fontsize=12, pad=10
)
plt.tight_layout()
plt.savefig(FIG_DIR / 'plot1_zeitverlauf_dual_axis.png', bbox_inches='tight')
print('  ✓ plot1_zeitverlauf_dual_axis.png')
plt.show()


# ════════════════════════════════════════════════════════════════════════════
# PLOT 2 — KI vs. Daten: gestapelte Balken (absolut + prozentual)
# ════════════════════════════════════════════════════════════════════════════
print('\nErstelle Plot 2 ...')

pivot_raw = yearly.pivot_table(
    index='year', columns='group', values='raw_sum', fill_value=0
)
pivot_raw['total'] = pivot_raw.sum(axis=1)
for g in GROUPS:
    pivot_raw[f'{g}_pct'] = pivot_raw[g] / pivot_raw['total'] * 100

fig, (ax_abs, ax_pct) = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('KI/AI vs. Daten/Data — Vergleich der Schlagwortgruppen 2022–2025',
             fontsize=13, y=1.01)

x = np.arange(len(YEARS))
bar_w = 0.5

# Absolut
bottom = np.zeros(len(YEARS))
for group in ['Daten/Data', 'KI/AI']:
    vals = [pivot_raw.loc[y, group] for y in YEARS]
    bars = ax_abs.bar(x, vals, bar_w, bottom=bottom,
                      label=group, color=C[group], alpha=0.85,
                      edgecolor='white', linewidth=0.5)
    for rect, v, b in zip(bars, vals, bottom):
        if v > 5:
            ax_abs.text(rect.get_x() + rect.get_width() / 2,
                        b + v / 2, str(int(v)),
                        ha='center', va='center', fontsize=9,
                        color='white', fontweight='bold')
    bottom += np.array(vals)

ax_abs.set_xticks(x)
ax_abs.set_xticklabels(YEARS)
ax_abs.set_xlabel('Jahr', fontsize=11)
ax_abs.set_ylabel('Gesamtsumme Nennungen', fontsize=10)
ax_abs.set_title('Absolute Nennungen', fontsize=11)
ax_abs.legend(fontsize=10)

# Prozentual
bottom_pct = np.zeros(len(YEARS))
for group in ['Daten/Data', 'KI/AI']:
    pct_vals = [pivot_raw.loc[y, f'{group}_pct'] for y in YEARS]
    bars = ax_pct.bar(x, pct_vals, bar_w, bottom=bottom_pct,
                      label=group, color=C[group], alpha=0.85,
                      edgecolor='white', linewidth=0.5)
    for rect, v, b in zip(bars, pct_vals, bottom_pct):
        if v > 3:
            ax_pct.text(rect.get_x() + rect.get_width() / 2,
                        b + v / 2, f'{v:.0f}%',
                        ha='center', va='center', fontsize=9,
                        color='white', fontweight='bold')
    bottom_pct += np.array(pct_vals)

ax_pct.set_xticks(x)
ax_pct.set_xticklabels(YEARS)
ax_pct.set_xlabel('Jahr', fontsize=11)
ax_pct.set_ylabel('Anteil (%)', fontsize=10)
ax_pct.set_title('Prozentuale Aufteilung', fontsize=11)
ax_pct.set_ylim(0, 105)
ax_pct.legend(fontsize=10)

plt.tight_layout()
plt.savefig(FIG_DIR / 'plot2_ki_vs_daten_gestapelt.png', bbox_inches='tight')
print('  ✓ plot2_ki_vs_daten_gestapelt.png')
plt.show()

print('\nAufteilung KI vs. Daten:')
print(pivot_raw[GROUPS + [f'{g}_pct' for g in GROUPS]].round(1).to_string())


# ════════════════════════════════════════════════════════════════════════════
# PLOT 3 — Anteil Firmen mit mind. 1 Nennung, CEO vs. AR
# ════════════════════════════════════════════════════════════════════════════
print('\nErstelle Plot 3 ...')

pen_rows = []
for year in YEARS:
    for group in GROUPS:
        for role in ['ceo', 'ar']:
            sub = freq[
                (freq['year'] == year) &
                (freq['group'] == group) &
                (freq['role'] == role)
            ]
            if sub.empty:
                continue
            total    = sub['company'].nunique()
            with_hit = sub[sub['count_raw'] > 0]['company'].nunique()
            pen_rows.append({
                'year':        year,
                'group':       group,
                'role':        role,
                'total_cos':   total,
                'cos_with_hit': with_hit,
                'pct':         with_hit / total * 100 if total > 0 else 0,
            })

pen = pd.DataFrame(pen_rows)

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
fig.suptitle(
    'Anteil Firmen mit mind. 1 Nennung — CEO vs. AR-Vorsitz 2022–2025',
    fontsize=13, y=1.01
)

role_labels = {'ceo': 'CEO-Reden', 'ar': 'AR-Vorsitz-Reden'}

for ax, role in zip(axes, ['ceo', 'ar']):
    for group in GROUPS:
        sub = pen[(pen['role'] == role) & (pen['group'] == group)].sort_values('year')
        ax.plot(sub['year'], sub['pct'], marker='o', linewidth=2.5,
                markersize=8, color=C[group], label=group)
        for _, row in sub.iterrows():
            ax.annotate(
                f"{row['pct']:.0f}%\n({int(row['cos_with_hit'])}/{int(row['total_cos'])})",
                (row['year'], row['pct']),
                xytext=(0, 11), textcoords='offset points',
                ha='center', fontsize=7.5, color=C[group]
            )
    ax.axvline(x=2022.88, color='#999', linestyle=':', linewidth=1, alpha=0.7)
    ax.set_xticks(YEARS)
    ax.set_xlabel('Jahr', fontsize=11)
    ax.set_ylim(0, 115)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_title(role_labels[role], fontsize=11)
    ax.legend(fontsize=10)

axes[0].set_ylabel('Anteil Firmen mit mind. 1 Nennung (%)', fontsize=10)
plt.tight_layout()
plt.savefig(FIG_DIR / 'plot3_penetration_ceo_vs_ar.png', bbox_inches='tight')
print('  ✓ plot3_penetration_ceo_vs_ar.png')
plt.show()


# ════════════════════════════════════════════════════════════════════════════
# PLOT 4 — Top-3 & Null-Nennungen pro Jahr & Gruppe
# ════════════════════════════════════════════════════════════════════════════
print('\nErstelle Plot 4 ...')

fig, axes = plt.subplots(
    len(YEARS), 2,
    figsize=(14, len(YEARS) * 3.5),
    sharey=False
)
fig.suptitle(
    'Top-3 Firmen nach Nennungshäufigkeit pro Jahr & Schlagwortgruppe\n'
    '(normalisiert: Ø / 1.000 Wörter, über CEO + AR)',
    fontsize=13, y=1.01
)

summary_rows = []

for row_i, year in enumerate(YEARS):
    for col_i, group in enumerate(GROUPS):
        ax  = axes[row_i][col_i]
        sub = agg[(agg['year'] == year) & (agg['group'] == group)]\
              .sort_values('count_norm', ascending=False).reset_index(drop=True)

        top3 = sub.head(3)
        zero = sub[sub['count_raw'] == 0]

        colors_bar = [C[group] if i < 3 else '#CCCCCC' for i in range(len(sub))]
        ax.barh(sub['company'], sub['count_norm'],
                color=colors_bar, edgecolor='white', linewidth=0.3)
        ax.set_title(f'{year} — {group}', fontsize=10)
        ax.set_xlabel('Ø / 1.000 Wörter', fontsize=8)
        ax.tick_params(axis='y', labelsize=7)
        ax.invert_yaxis()

        for _, r in top3.iterrows():
            summary_rows.append({
                'year': year, 'group': group, 'rank': 'Top',
                'company': r['company'],
                'count_norm': r['count_norm'],
                'count_raw':  r['count_raw'],
            })
        for _, r in zero.iterrows():
            summary_rows.append({
                'year': year, 'group': group, 'rank': 'Null',
                'company': r['company'],
                'count_norm': 0, 'count_raw': 0,
            })

plt.tight_layout()
plt.savefig(FIG_DIR / 'plot4_top3_zero_firmen.png', bbox_inches='tight')
print('  ✓ plot4_top3_zero_firmen.png')
plt.show()

# Textausgabe & Export
summary = pd.DataFrame(summary_rows)
summary.to_csv(REP_DIR / 'top3_zero_summary.csv', index=False, encoding='utf-8-sig')

for year in YEARS:
    print(f'\n{"═"*60}')
    print(f'  {year}')
    print(f'{"═"*60}')
    for group in GROUPS:
        s    = summary[(summary['year'] == year) & (summary['group'] == group)]
        top  = s[s['rank'] == 'Top']
        zero = s[s['rank'] == 'Null']
        print(f'\n  {group}')
        print('  Top-3:')
        for _, r in top.iterrows():
            print(f'    {r["company"]:25}  {r["count_norm"]:.2f}/1000  '
                  f'({int(r["count_raw"])} Nennungen)')
        zero_list = ', '.join(zero['company'].tolist()) if not zero.empty else '–'
        print(f'  Keine Nennung: {zero_list}')

print('\n✓ Alle Plots gespeichert in:', FIG_DIR)
print('✓ Tabellen gespeichert in:  ', REP_DIR)
