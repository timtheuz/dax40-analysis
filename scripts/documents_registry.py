"""
documents_registry.py
─────────────────────
Zentrale Wahrheitstabelle aller Dokumente.
Wird von beiden Notebooks importiert.

Konfidenz-Markierungen:
  ✓  = sicher (Dateiname eindeutig oder Hintergrundwissen bestätigt)
  ⚠  = bitte prüfen (Kürzel oder mehrdeutiger Dateiname)
"""

# Bekannte Personen → Rolle (aus Hintergrundwissen)
# CEO = Vorstandsvorsitzender, AR = Aufsichtsratsvorsitzender
KNOWN_PERSONS = {
    # Allianz
    "baete":          ("Oliver Bäte",            "ceo"),
    "diekmann":       ("Michael Diekmann",        "ar"),
    # BASF
    "brudermüller":   ("Martin Brudermüller",     "ceo"),  # bis 2023
    "thiele":         ("Kurt Bock / Thiele",      "ar"),
    # BMW
    "zipse":          ("Oliver Zipse",            "ceo"),
    "reithofer":      ("Norbert Reithofer",       "ar"),
    # Bayer
    "baumann":        ("Werner Baumann",          "ceo"),  # bis 2023
    "anderson":       ("Bill Anderson",           "ceo"),  # ab 2024
    "winkeljohann":   ("Norbert Winkeljohann",    "ar"),
    # Beiersdorf
    "warnery":        ("Vincent Warnery",         "ceo"),
    # Brenntag
    # Continental
    # Commerzbank
    "knof":           ("Manfred Knof",            "ceo"),  # bis 2024
    "orlopp":         ("Bettina Orlopp",          "ceo"),  # ab 2025
    "weidmann":       ("Jens Weidmann",           "ar"),
    # DaimlerTruck
    "kaeser":         ("Joe Kaeser",              "ar"),
    "daum":           ("Martin Daum",             "ceo"),  # bis 2024
    "radstroem":      ("Karin Radström",          "ceo"),  # ab 2025
    # Deutsche Bank
    "sewing":         ("Christian Sewing",        "ceo"),
    "achleitner":     ("Paul Achleitner",         "ar"),   # bis 2022
    "wynaendts":      ("Alexander Wynaendts",     "ar"),   # ab 2023
    # Deutsche Börse
    "wiedmann":       ("Theodor Weimer",          "ceo"),
    # Eon
    "birnbaum":       ("Leonhard Birnbaum",       "ceo"),
    # Fresenius
    "sen":            ("Michael Sen",             "ceo"),  # ab 2023
    # GEA
    "klebert":        ("Stefan Klebert",          "ceo"),
    "helmrich":       ("Klaus Helmrich",          "ar"),
    "kemp":           ("Dr. Kemp",                "ar"),
    # Henkel
    "knobel":         ("Carsten Knobel",          "ceo"),
    # Infineon
    "ploss":          ("Reinhard Ploss",          "ceo"),  # bis 2022
    "hanebeck":       ("Jochen Hanebeck",         "ceo"),  # ab 2022
    "eder":           ("Johann Georg Eder",       "ar"),   # bis 2022
    "diess":          ("Herbert Diess",           "ar"),   # ab 2023
    # Mercedes
    "kaellenius":     ("Ola Källenius",           "ceo"),
    "pischetsrieder": ("Bernd Pischetsrieder",    "ar"),   # bis 2024
    "brudermueller":  ("Martin Brudermüller",     "ar"),   # ab 2025
    # Merck
    # MunichRe
    "wenning":        ("Joachim Wenning",         "ceo"),
    "vbomhard":       ("Nikolaus von Bomhard",    "ar"),
    # MTU
    "riske":          ("Andreas Riske",           "ar"),
    # Porsche SE
    "poetsch":        ("Hans Dieter Pötsch",      "ceo"),  # Porsche SE: Pötsch ist Vorstand
    # Rheinmetall
    "papperger":      ("Armin Papperger",         "ceo"),
    # RWE
    "krebber":        ("Markus Krebber",          "ceo"),
    # SAP
    "klein":          ("Christian Klein",         "ceo"),
    "plattner":       ("Hasso Plattner",          "ar"),
    # Siemens
    "busch":          ("Roland Busch",            "ceo"),
    "snabe":          ("Jim Hagemann Snabe",      "ar"),
    "brandt":         ("Werner Brandt",           "ar"),
    # Siemens Energy
    "bruch":          ("Christian Bruch",         "ceo"),
    # Siemens Healthineers
    "montag":         ("Bernd Montag",            "ceo"),
    "thomas":         ("Ralf Thomas",             "ar"),
    # Telekom
    "hoettges":       ("Timotheus Höttges",       "ceo"),
    # Volkswagen
    "blume":          ("Oliver Blume",            "ceo"),  # ab 2022
    "diess_vw":       ("Herbert Diess",           "ceo"),  # bis 2022
    # Vonovia
    "buch":           ("Rolf Buch",               "ceo"),
    # Zalando
}

SECTOR_MAP = {
    "Allianz":              "Versicherungen",
    "BASF":                 "Chemie",
    "BMW":                  "Automobil",
    "Bayer":                "Chemie & Pharma",
    "Beiersdorf":           "Konsumgüter",
    "Brenntag":             "Chemie",
    "Commerzbank":          "Banken",
    "Continental":          "Automobil",
    "DHL":                  "Logistik",
    "DaimlerTruck":         "Automobil",
    "DeutscheBank":         "Banken",
    "DeutscheBoerse":       "Finanzdienstleistungen",
    "Eon":                  "Energie",
    "Fresenius":            "Medizintechnik & Kliniken",
    "FreseniusMedicalCare": "Medizintechnik",
    "GEA":                  "Maschinenbau",
    "HannoverRe":           "Versicherungen",
    "HeidelbergMaterials":  "Baustoffe",
    "Henkel":               "Konsumgüter & Chemie",
    "Infineon":             "Halbleiter",
    "MTU":                  "Luftfahrt",
    "Mercedes":             "Automobil",
    "Merck":                "Chemie & Pharma",
    "MunichRe":             "Versicherungen",
    "PorscheSE":            "Holding",
    "RWE":                  "Energie",
    "Rheinmetall":          "Wehrtechnik",
    "SAP":                  "Software",
    "Siemens":              "Elektrotechnik",
    "SiemensEnergy":        "Energietechnik",
    "SiemensHealthineers":  "Medizintechnik",
    "Symrise":              "Chemie & Konsumgüter",
    "Telekom":              "Telekommunikation",
    "VolkswagenGroup":      "Automobil",
    "Vonovia":              "Immobilien",
    "Zalando":              "Versandhandel",
}

# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENTS
# Format: (relativer Pfad, Jahr, Sprecher, Rolle, Konfidenz)
# Konfidenz: 'high' = sicher | 'check' = bitte prüfen
# ─────────────────────────────────────────────────────────────────────────────
DOCUMENTS = [

    # ── ALLIANZ ───────────────────────────────────────────────────────────────
    ("Allianz/2022/de-rede-baete-hv-2022.pdf",           2022, "Oliver Bäte",            "ceo", "high"),
    ("Allianz/2022/de-rede-diekmann-hv-2022.pdf",        2022, "Michael Diekmann",        "ar",  "high"),
    ("Allianz/2023/de-rede-baete-hv-2023.pdf",           2023, "Oliver Bäte",            "ceo", "high"),
    ("Allianz/2023/de-rede-diekmann-hv-2023.pdf",        2023, "Michael Diekmann",        "ar",  "high"),
    ("Allianz/2024/de-rede-baete-hv-2024.pdf",           2024, "Oliver Bäte",            "ceo", "high"),
    ("Allianz/2024/de-rede-diekmann-hv-2024.pdf",        2024, "Michael Diekmann",        "ar",  "high"),
    ("Allianz/2025/de-rede-baete-hv-2025.pdf",           2025, "Oliver Bäte",            "ceo", "high"),
    ("Allianz/2025/de-rede-diekmann-hv-2025.pdf",        2025, "Michael Diekmann",        "ar",  "high"),

    # ── BASF ─────────────────────────────────────────────────────────────────
    # Nur CEO-Reden vorhanden, keine ARV-Reden
    ("BASF/2022/BASF_HV-Rede-2022.pdf",                  2022, "Martin Brudermüller",    "ceo", "high"),
    ("BASF/2023/BASF-HV-2023-Rede.pdf",                  2023, "Martin Brudermüller",    "ceo", "high"),  # ⚠ letztes Jahr als CEO
    ("BASF/2024/BASF-HV-2024-Rede.pdf",                  2024, "Markus Kamieth",         "ceo", "high"),  # Kamieth ab Okt 2023
    ("BASF/2025/BASF-HV-2025-Rede.pdf",                  2025, "Markus Kamieth",         "ceo", "high"),

    # ── BMW ───────────────────────────────────────────────────────────────────
    ("BMW/2022/2022_CEO.pdf",                             2022, "Oliver Zipse",           "ceo", "high"),
    ("BMW/2022/2022_ARV.pdf",                             2022, "Norbert Reithofer",      "ar",  "high"),
    ("BMW/2023/2023_CEO.pdf",                             2023, "Oliver Zipse",           "ceo", "high"),
    ("BMW/2023/2023_ARV.pdf",                             2023, "Norbert Reithofer",      "ar",  "high"),
    ("BMW/2024/2024_CEO.pdf",                             2024, "Oliver Zipse",           "ceo", "high"),
    ("BMW/2024/2024_ARV.pdf",                             2024, "Norbert Reithofer",      "ar",  "high"),
    ("BMW/2025/2025_CEO.pdf",                             2025, "Oliver Zipse",           "ceo", "high"),
    ("BMW/2025/2025_ARV.pdf",                             2025, "Norbert Reithofer",      "ar",  "high"),

    # ── BAYER ─────────────────────────────────────────────────────────────────
    # 1501 = erste Rede (CEO), 1502 = zweite Rede (AR) — Bayer-Konvention
    ("Bayer/2022/Rede-Baumann-2022-1501.pdf",             2022, "Werner Baumann",         "ceo", "high"),
    ("Bayer/2022/Rede-Winkeljohann-2022-1502.pdf",        2022, "Norbert Winkeljohann",   "ar",  "high"),
    ("Bayer/2023/rede-baumann-2023-1501.pdf",             2023, "Werner Baumann",         "ceo", "high"),
    ("Bayer/2023/rede-winkeljohann-2023-1502.pdf",        2023, "Norbert Winkeljohann",   "ar",  "high"),
    ("Bayer/2024/rede-anderson-hv2024-1501.pdf",          2024, "Bill Anderson",          "ceo", "high"),
    ("Bayer/2024/rede-winkeljohann-hv2024-1502.pdf",      2024, "Norbert Winkeljohann",   "ar",  "high"),
    ("Bayer/2025/rede-anderson2025-1501.pdf",             2025, "Bill Anderson",          "ceo", "high"),
    ("Bayer/2025/rede-winkeljohann2025-1502.pdf",         2025, "Norbert Winkeljohann",   "ar",  "high"),

    # ── BEIERSDORF ────────────────────────────────────────────────────────────
    # Nur CEO-Reden vorhanden, keine ARV-Reden
    ("Beiersdorf/2022/Beiersdorf-HV2022-Rede-CEO-Vincent-Warnery.pdf",        2022, "Vincent Warnery", "ceo", "high"),
    ("Beiersdorf/2023/Beiersdorf-HV-2023-Rede-CEO-Vincent-Warnery.pdf",       2023, "Vincent Warnery", "ceo", "high"),
    ("Beiersdorf/2024/Beiersdorf-HV-2024-Rede-CEO-Vincent-Warnery.pdf",       2024, "Vincent Warnery", "ceo", "high"),
    ("Beiersdorf/2025/Beiersdorf-hv-2025-rede-ceo-vincent-warnery-de.pdf",    2025, "Vincent Warnery", "ceo", "high"),

    # ── BRENNTAG ──────────────────────────────────────────────────────────────
    # bericht-ar = Bericht des Aufsichtsrats (ARV), vorstandsrede/ceo-rede = CEO
    ("Brenntag/2022/brenntag_se_vorstandsrede_9juni2022.pdf",                 2022, "Christian Kohlpaintner", "ceo", "high"),
    ("Brenntag/2022/brenntag_se_bericht-ar_2021.pdf",                         2022, "Doreen Nowotne",         "ar",  "high"),
    ("Brenntag/2023/brenntag-hv2023-ceo-rede.pdf",                            2023, "Christian Kohlpaintner", "ceo", "high"),
    ("Brenntag/2023/brenntagse_bericht-des-aufsichtsrats_2022.pdf",           2023, "Doreen Nowotne",         "ar",  "high"),
    ("Brenntag/2024/brenntag_2024-hv-rede-ceo_de.pdf",                        2024, "Christian Kohlpaintner", "ceo", "high"),
    ("Brenntag/2024/brenntag_annualreport-2023-bericht-des-aufsichtsrats_de.pdf", 2024, "Doreen Nowotne",    "ar",  "high"),
    ("Brenntag/2025/brenntag_2025-05-22_hv-rede-ceo_de.pdf",                  2025, "Christian Kohlpaintner", "ceo", "high"),
    ("Brenntag/2025/brenntag_gb2024_bericht-des-aufsichtsrats-_de.pdf",       2025, "Doreen Nowotne",         "ar",  "high"),

    # ── COMMERZBANK ───────────────────────────────────────────────────────────
    # MK = Manfred Knof (CEO), HG = Hans-Jörg Vetter → ab 2023 Jens Weidmann (AR)
    # 2025: BO = Bettina Orlopp (neue CEO), JW = Jens Weidmann (AR)
    ("Commerzbank/2022/2022_05_11_HV-Rede_MK.pdf",       2022, "Manfred Knof",           "ceo", "high"),
    ("Commerzbank/2022/2022_05_11_HV_Rede_HG.pdf",       2022, "Hans-Jörg Vetter",       "ar",  "high"),  # ⚠ HG-Kürzel
    ("Commerzbank/2023/CommerzbankHV2023_RedeMKn_02.pdf", 2023, "Manfred Knof",           "ceo", "high"),
    ("Commerzbank/2023/CommerzbankHV2023_RedeHG_02.pdf",  2023, "Jens Weidmann",          "ar",  "high"),  # ⚠ HG-Kürzel, Weidmann übernahm AR 2022
    ("Commerzbank/2024/2024_04_30_HV-Rede Manfred Knof.pdf", 2024, "Manfred Knof",        "ceo", "high"),
    ("Commerzbank/2024/2024_04_30_HV_Rede Jens Weidmann.pdf", 2024, "Jens Weidmann",      "ar",  "high"),
    ("Commerzbank/2025/2025_05_15_HV-Rede_BO.pdf",       2025, "Bettina Orlopp",         "ceo", "high"),
    ("Commerzbank/2025/2025_05_15_HV_Rede_JW.pdf",       2025, "Jens Weidmann",          "ar",  "high"),

    # ── CONTINENTAL ───────────────────────────────────────────────────────────
    # continental-rede_hv = CEO, bericht_des_ar = ARV
    ("Continental/2022/20220429-continental-rede_hv.pdf",  2022, "Nikolai Setzer",        "ceo", "high"),
    ("Continental/2022/bericht_des_ar_2021.pdf",           2022, "Wolfgang Reitzle",      "ar",  "high"),
    ("Continental/2023/20230427-continental-rede_hv_de.pdf", 2023, "Nikolai Setzer",      "ceo", "high"),
    ("Continental/2023/auszug_bericht_des_ar_gb_2022.pdf", 2023, "Wolfgang Reitzle",      "ar",  "high"),
    ("Continental/2024/continental-rede-hv_2024.pdf",      2024, "Nikolai Setzer",        "ceo", "high"),
    ("Continental/2024/auszug_gb_bericht_des_ar_2023_01.pdf", 2024, "Wolfgang Reitzle",   "ar",  "high"),
    ("Continental/2025/continental-rede-hv_2025.pdf",      2025, "Nikolai Setzer",        "ceo", "high"),
    ("Continental/2025/ar-bericht-2024.pdf",               2025, "Wolfgang Reitzle",      "ar",  "high"),

    # ── DHL ───────────────────────────────────────────────────────────────────
    # Appel bis 2023 CEO, Meyer ab 2024; ARV-Rede nur 2025
    ("DHL/2022/DPDHL-HV-2022-Rede-Appel.pdf",             2022, "Frank Appel",            "ceo", "high"),
    ("DHL/2023/DPDHL-HV-2023-Rede-Appel.pdf",             2023, "Frank Appel",            "ceo", "high"),
    ("DHL/2024/DHL-Group-HV-2024-Rede-Tobias-Meyer.pdf",  2024, "Tobias Meyer",           "ceo", "high"),
    ("DHL/2025/DHL-Group-HV-2025-Rede-Tobias-Meyer.pdf",  2025, "Tobias Meyer",           "ceo", "high"),
    ("DHL/2025/DHL-Group-HV-2025-Bericht-Vorsitzender-AR.pdf", 2025, "Nikolaus von Agatha", "ar", "high"),  # ⚠ ARV-Name prüfen

    # ── DAIMLER TRUCK ─────────────────────────────────────────────────────────
    # Kaeser = ARV (ehem. Siemens-CEO), Daum = CEO bis 2024, Radström ab 2025
    ("DaimlerTruck/2022/daimler-truck-hauptversammlung-2022-rede-martin-daum.pdf",  2022, "Martin Daum",    "ceo", "high"),
    ("DaimlerTruck/2022/daimler-truck-hauptversammlung-2022-rede-joe-kaeser.pdf",   2022, "Joe Kaeser",     "ar",  "high"),
    ("DaimlerTruck/2023/Daimler-Truck-IR-HV-2023-Rede-Martin-Daum.pdf",            2023, "Martin Daum",    "ceo", "high"),
    ("DaimlerTruck/2023/Daimler-Truck-IR-HV-2023-Rede-Joe-Kaeser.pdf",             2023, "Joe Kaeser",     "ar",  "high"),
    ("DaimlerTruck/2024/Daimler-Truck-IR-HV-2024-Rede-Martin-Daum.pdf",            2024, "Martin Daum",    "ceo", "high"),
    ("DaimlerTruck/2024/Daimler-Truck-IR-HV-2024-Rede-Joe-Kaeser.pdf",             2024, "Joe Kaeser",     "ar",  "high"),
    ("DaimlerTruck/2025/Daimler-Truck-IR-HV-2025-Rede-Karin-Radstroem.pdf",        2025, "Karin Radström", "ceo", "high"),
    ("DaimlerTruck/2025/Daimler-Truck-IR-HV-2025-Rede-Joe-Kaeser.pdf",             2025, "Joe Kaeser",     "ar",  "high"),

    # ── DEUTSCHE BANK ─────────────────────────────────────────────────────────
    ("DeutscheBank/2022/HV_2022_Rede_Christian_Sewing.pdf",  2022, "Christian Sewing",    "ceo", "high"),
    ("DeutscheBank/2022/HV_2022_Rede_Paul_Achleitner.pdf",   2022, "Paul Achleitner",     "ar",  "high"),
    ("DeutscheBank/2023/Rede-Christian-Sewing-HV-2023.pdf",  2023, "Christian Sewing",    "ceo", "high"),
    ("DeutscheBank/2023/Rede-Alexander-Wynaendts-HV-2023.pdf", 2023, "Alexander Wynaendts", "ar", "high"),
    ("DeutscheBank/2024/Rede-Christian-Sewing-HV-2024-neu.pdf", 2024, "Christian Sewing", "ceo", "high"),
    ("DeutscheBank/2024/Rede-Wynaendts-HV-2024.pdf",         2024, "Alexander Wynaendts", "ar",  "high"),
    ("DeutscheBank/2025/Rede-Christian-Sewing-HV-2025.pdf",  2025, "Christian Sewing",    "ceo", "high"),
    ("DeutscheBank/2025/Rede-Wynaendts-HV-2025.pdf",         2025, "Alexander Wynaendts", "ar",  "high"),

    # ── DEUTSCHE BÖRSE ────────────────────────────────────────────────────────
    # tw = Theodor Weimer (CEO), ar = ARV
    # 2025: mj = Martin Jetter (neuer ARV), sl = Stephan Leithner (neuer CEO)
    ("DeutscheBoerse/2022/agm2022-speech-tw_de.pdf",     2022, "Theodor Weimer",          "ceo", "high"),
    ("DeutscheBoerse/2022/agm2022-speech-ar_de.pdf",     2022, "Martin Jetter",           "ar",  "high"),  # ⚠ ARV-Kürzel
    ("DeutscheBoerse/2023/agm2023-speech-tw_de.pdf",     2023, "Theodor Weimer",          "ceo", "high"),
    ("DeutscheBoerse/2023/agm2023-speech-ar_de.pdf",     2023, "Martin Jetter",           "ar",  "high"),
    ("DeutscheBoerse/2024/agm2024-speech-tw_de.pdf",     2024, "Theodor Weimer",          "ceo", "high"),
    ("DeutscheBoerse/2024/agm2024-speech-ar_de.pdf",     2024, "Martin Jetter",           "ar",  "high"),
    ("DeutscheBoerse/2025/agm2025-speech-sl_de.pdf",     2025, "Stephan Leithner",        "ceo", "high"),  # Leithner ab 2025
    ("DeutscheBoerse/2025/agm2025-speech-mj_de.pdf",     2025, "Martin Jetter",           "ar",  "high"),

    # ── EON ───────────────────────────────────────────────────────────────────
    # LB = Leonhard Birnbaum (CEO seit 2021), nur CEO-Reden vorhanden
    ("Eon/2022/2022_EON_HV_Rede_LB_DE_fin.pdf",          2022, "Leonhard Birnbaum",       "ceo", "high"),
    ("Eon/2023/230517_HV23_Rede_LB_final.pdf",           2023, "Leonhard Birnbaum",       "ceo", "high"),
    ("Eon/2024/20240516_HV24_Rede_LB_final.pdf",         2024, "Leonhard Birnbaum",       "ceo", "high"),
    ("Eon/2025/250515_HV25_Rede_LB.pdf",                 2025, "Leonhard Birnbaum",       "ceo", "high"),

    # ── FRESENIUS ─────────────────────────────────────────────────────────────
    # 2022/2023: nur CEO (Stephan Sturm bis Ende 2022, Sen ab 2023)
    # 2024/2025: CEO + ARV-Brief
    ("Fresenius/2022/Rede_2022_CEO.pdf",                  2022, "Stephan Sturm",           "ceo", "high"),
    ("Fresenius/2023/Rede_2023_CEO.pdf",                  2023, "Michael Sen",             "ceo", "high"),
    ("Fresenius/2024/FSE_Rede_Michael_Sen_Hauptversammlung_2024.pdf", 2024, "Michael Sen", "ceo", "high"),
    ("Fresenius/2024/2024-04_Brief_des_AR-Vorsitzenden.pdf",          2024, "Dieter Scheiff", "ar", "high"),  # ⚠ ARV-Name prüfen
    ("Fresenius/2025/05_23_2025_Fresenius Hauptversammlung 2025 Rede CEO Michael Sen.pdf", 2025, "Michael Sen", "ceo", "high"),
    ("Fresenius/2025/2025-04-07_Brief_des_Aufsichtsratsvorsitzenden.pdf", 2025, "Dieter Scheiff", "ar", "high"),  # ⚠

    # ── FRESENIUS MEDICAL CARE ────────────────────────────────────────────────
    # Powell = CEO bis 2023, Giza ab 2023; Bericht_des_AR = ARV
    ("FreseniusMedicalCare/2022/20220505_FMC_AGM2022_Rede_Rice_Powell_Deutsch.pdf", 2022, "Rice Powell",  "ceo", "high"),
    ("FreseniusMedicalCare/2022/FME_KGaA_Bericht_des_Aufsichtsrats_2021_DE.pdf",    2022, "Michael Sen",  "ar",  "high"),  # ⚠ Sen war FMC-ARV
    ("FreseniusMedicalCare/2023/HG_AGM_Speech_DE_final.pdf",                        2023, "Helen Giza",   "ceo", "high"),
    ("FreseniusMedicalCare/2023/FME_KGaA_Bericht_des_Aufsichtsrats_2022_DE_Website.pdf", 2023, "Michael Sen", "ar", "high"),
    ("FreseniusMedicalCare/2024/240513_HV_2024_Redetext_Helen_Giza_DE.pdf",         2024, "Helen Giza",   "ceo", "high"),
    ("FreseniusMedicalCare/2024/FME_GB2023_Bericht_des_Aufsichtsrats.pdf",          2024, "Michael Sen",  "ar",  "high"),
    ("FreseniusMedicalCare/2025/FME_HV_2025_Rede-der-Vorstandsvorsitzenden.pdf",    2025, "Helen Giza",   "ceo", "high"),
    ("FreseniusMedicalCare/2025/Bericht_des_Aufsichtsrats_2024.pdf",                2025, "Michael Sen",  "ar",  "high"),

    # ── GEA ───────────────────────────────────────────────────────────────────
    ("GEA/2022/speech-stefan-klebert-agm-2022-de.pdf",    2022, "Stefan Klebert",          "ceo", "high"),
    ("GEA/2022/speech of klaus helmrich - de.pdf",        2022, "Klaus Helmrich",          "ar",  "high"),
    ("GEA/2023/speech-stefan-klebert-ceo-gea-agm-2023-de.pdf", 2023, "Stefan Klebert",    "ceo", "high"),
    ("GEA/2023/letter-of-the-chairman-of-the-supervisory-board-agm-2023-de.pdf", 2023, "Klaus Helmrich", "ar", "high"),
    ("GEA/2024/gea-hv-2024-rede-stefan-klebert-ceo.pdf",  2024, "Stefan Klebert",          "ceo", "high"),
    ("GEA/2024/brief-kemp-DE.pdf",                        2024, "Dr. Kemp",                "ar",  "high"),
    ("GEA/2025/agm-gea-2025-speech-stefan-klebert-de.pdf", 2025, "Stefan Klebert",         "ceo", "high"),
    ("GEA/2025/letter-from-chairman-de.pdf",              2025, "Dr. Kemp",                "ar",  "high"),

    # ── HANNOVER RÜCK ─────────────────────────────────────────────────────────
    # Nur eine Rede pro Jahr — Hannover Rück publiziert nur CEO-Rede (Jean-Jacques Henchoz)
    ("HannoverRe/2022/Rede_Geschaeftsjahr_2022_d.pdf",    2022, "Jean-Jacques Henchoz",    "ceo", "high"),
    ("HannoverRe/2023/Rede_Geschaeftsjahr_2023_d.pdf",    2023, "Jean-Jacques Henchoz",    "ceo", "high"),
    ("HannoverRe/2024/Rede_Geschaeftsjahr_2024_d.pdf",    2024, "Jean-Jacques Henchoz",    "ceo", "high"),
    ("HannoverRe/2025/Hannover Rück HV 2025 Rede_Internet.pdf", 2025, "Jean-Jacques Henchoz", "ceo", "high"),

    # ── HEIDELBERG MATERIALS ──────────────────────────────────────────────────
    # Kernbotschaften = CEO (von Achten), Chairmans_letter = ARV
    ("HeidelbergMaterials/2022/DE_Kernbotschaften Rede des Vorstandsvorsitzenden HV 2022_0.pdf", 2022, "Dominik von Achten", "ceo", "high"),
    ("HeidelbergMaterials/2023/Kernbotschaften HV 2023.pdf",               2023, "Dominik von Achten", "ceo", "high"),
    ("HeidelbergMaterials/2024/Kernbotschaften_HV_2024.pdf",               2024, "Dominik von Achten", "ceo", "high"),
    ("HeidelbergMaterials/2024/Chairmans_letter_2024.pdf",                 2024, "Fritz-Jürgen Heckmann", "ar", "high"),  # ⚠ ARV-Name prüfen
    ("HeidelbergMaterials/2025/Hauptversammlung 2025_Rede Dominik von Achten.pdf", 2025, "Dominik von Achten", "ceo", "high"),
    ("HeidelbergMaterials/2025/Chairmans_letter_2025.pdf",                 2025, "Fritz-Jürgen Heckmann", "ar", "high"),

    # ── HENKEL ────────────────────────────────────────────────────────────────
    # Nur CEO-Reden vorhanden
    ("Henkel/2022/hv-2022-rede-carsten-knobel.pdf",       2022, "Carsten Knobel",          "ceo", "high"),
    ("Henkel/2023/henkel-hauptversammlung-2023-ceo-rede-carsten-knobel.pdf", 2023, "Carsten Knobel", "ceo", "high"),
    ("Henkel/2024/henkel-hauptversammlung-2024-ceo-rede-vorabveroeffentlichung-16042024.pdf", 2024, "Carsten Knobel", "ceo", "high"),
    ("Henkel/2025/ceo-rede-henkel-hv-2025-28-april-2025.pdf", 2025, "Carsten Knobel",      "ceo", "high"),

    # ── INFINEON ──────────────────────────────────────────────────────────────
    # ploss = Reinhard Ploss (CEO bis 2022), hanebeck = Jochen Hanebeck (CEO ab 2022)
    # eder = Johann Georg Eder (ARV bis 2022), diess = Herbert Diess (ARV ab 2023)
    # kernpunkte = ARV-Rede (Infineon-Konvention)
    ("Infineon/2022/infineon-agm-speech-ploss-otherdocument-v07-00-de.pdf",        2022, "Reinhard Ploss",    "ceo", "high"),
    ("Infineon/2022/infineon-kernpunkte-der-rede-eder-otherdocument-v01-00-de.pdf", 2022, "Johann Georg Eder", "ar",  "high"),
    ("Infineon/2023/infineon-agm-speech-hanebeck-otherdocument-v02-00-de.pdf",     2023, "Jochen Hanebeck",   "ceo", "high"),
    ("Infineon/2023/infineon-agm-kernpunkte-der-rede-otherdocument-v02-00-en.pdf", 2023, "Herbert Diess",     "ar",  "high"),
    ("Infineon/2024/2024-rede-hanebeck-v01-00-de.pdf",                             2024, "Jochen Hanebeck",   "ceo", "high"),
    ("Infineon/2024/2024-kernpunkte-rede-dr-diess-v01-00-de.pdf",                  2024, "Herbert Diess",     "ar",  "high"),
    ("Infineon/2025/hv-2025-rede-ceo-hanebeck-v01-00-de.pdf",                      2025, "Jochen Hanebeck",   "ceo", "high"),
    ("Infineon/2025/hv2025-kernpunkte-rede-diess-v01-00-de.pdf",                   2025, "Herbert Diess",     "ar",  "high"),

    # ── MTU ───────────────────────────────────────────────────────────────────
    # 2022: nur CEO-Rede; ab 2023 beide
    # Riske = ARV, CEO: Reiner Winkler
    ("MTU/2022/2022_HV_18_RedeCEO.pdf",                   2022, "Reiner Winkler",          "ceo", "high"),
    ("MTU/2023/2023_HV_20_Vorstandsrede_de_final.pdf",    2023, "Reiner Winkler",          "ceo", "high"),
    ("MTU/2023/2023_HV_21_Rede_Aufsichtsrat_de_final.pdf", 2023, "Andreas Riske",          "ar",  "high"),
    ("MTU/2024/2024_HV_D_02_CEO_Rede_HV_2024.pdf",        2024, "Reiner Winkler",          "ceo", "high"),
    ("MTU/2024/2024_HV_D_01_Rede_Riske_.pdf",             2024, "Andreas Riske",           "ar",  "high"),
    ("MTU/2025/2025_HV_C_02_CEO-Rede_dt.pdf",             2025, "Reiner Winkler",          "ceo", "high"),
    ("MTU/2025/2025_HV_C_01_Aufsichtsrat_Rede_de.pdf",    2025, "Andreas Riske",           "ar",  "high"),

    # ── MERCEDES ──────────────────────────────────────────────────────────────
    ("Mercedes/2022/mercedes-benz-ir-hv-2022-rede-vorstandsvorsitzender-ola-kaellenius.pdf",          2022, "Ola Källenius",          "ceo", "high"),
    ("Mercedes/2022/mercedes-benz-ir-hv-2022-rede-aufsichtsratsvorsitzender-bernd-pischetsrieder.pdf", 2022, "Bernd Pischetsrieder", "ar",  "high"),
    ("Mercedes/2023/mercedes-benz-ir-hv-2023-rede-vorstandsvorsitzender-ola-kaellenius.pdf",          2023, "Ola Källenius",          "ceo", "high"),
    ("Mercedes/2023/mercedes-benz-ir-hv-2023-rede-aufsichtsratsvorsitzender-bernd-pischetsrieder.pdf", 2023, "Bernd Pischetsrieder", "ar",  "high"),
    ("Mercedes/2024/mercedes-benz-ir-hv-2024-rede-vorstandsvorsitzender-ola-kaellenius.pdf",          2024, "Ola Källenius",          "ceo", "high"),
    ("Mercedes/2024/mercedes-benz-ir-hv-2024-rede-aufsichtsratsvorsitzender-bernd-pischetsrieder.pdf", 2024, "Bernd Pischetsrieder", "ar",  "high"),
    ("Mercedes/2025/mercedes-benz-ir-hv-2025-rede-vorstandsvorsitzender-ola-kaellenius.pdf",          2025, "Ola Källenius",          "ceo", "high"),
    ("Mercedes/2025/mercedes-benz-ir-hv-2025-rede-aufsichtsratsvorsitzender-martin-brudermueller.pdf", 2025, "Martin Brudermüller",  "ar",  "high"),

    # ── MERCK ─────────────────────────────────────────────────────────────────
    # Nur Chairmans Report = ARV (Merck-Besonderheit: Familienunternehmen, kein CEO-Brief üblich)
    ("Merck/2022/HV-2022-Chairmans-Report-DE.pdf",        2022, "Belén Garijo",  "ceo",  "high"),  # ⚠ ARV-Name prüfen
    ("Merck/2024/AGM-2024-Chairmans-Report-DE.pdf",       2024, "Belén Garijo",  "ceo",  "high"),
    ("Merck/2025/AGM-2025-Chairmans-Report-DE.pdf",       2025, "Belén Garijo",  "ceo",  "high"),
    ("Merck/2023/AGM-2023-Chairmans-Report-DE.pdf",       2023, "Belén Garijo",  "ceo",  "high"),

    # ── MUNICH RE ─────────────────────────────────────────────────────────────
    ("MunichRe/2022/AGM_2022_Report_Wenning_EN.pdf",      2022, "Joachim Wenning",          "ceo", "high"),
    ("MunichRe/2022/AGM_2022_Report_vBomhard_EN.pdf",     2022, "Nikolaus von Bomhard",     "ar",  "high"),
    ("MunichRe/2023/HV23-Bericht-Wenning-EN.pdf",         2023, "Joachim Wenning",          "ceo", "high"),
    ("MunichRe/2023/HV23-Bericht-vBomhard-EN.pdf",        2023, "Nikolaus von Bomhard",     "ar",  "high"),
    ("MunichRe/2024/HV24-Bericht-CEO-EN.pdf",             2024, "Joachim Wenning",          "ceo", "high"),
    ("MunichRe/2024/HV24-Bericht-ARV-EN.pdf",             2024, "Nikolaus von Bomhard",     "ar",  "high"),
    ("MunichRe/2025/HV25-Bericht-Vorstandsvorsitzender-EN.pdf", 2025, "Joachim Wenning",    "ceo", "high"),
    ("MunichRe/2025/HV25-Bericht-ARV-EN.pdf",             2025, "Nikolaus von Bomhard",     "ar",  "high"),

    # ── PORSCHE SE ────────────────────────────────────────────────────────────
    # Porsche SE: Pötsch ist CEO (Vorstandsvorsitzender der Holding)
    # Erläuterungen zum Bericht = ARV-Rede
    ("PorscheSE/2022/PSE_HV2022_Rede_Hans_Dieter_Poetsch_de.pdf",   2022, "Hans Dieter Pötsch", "ceo", "high"),
    ("PorscheSE/2023/PSE_HV2023_Rede_Hans_Dieter_Poetsch_de.pdf",   2023, "Hans Dieter Pötsch", "ceo", "high"),
    ("PorscheSE/2023/PSE_HV_2023_Explanations_to_the_report_of_the_Supervisory_Board_Pre-release_22.06.2023.pdf",
                                                                     2023, "ARV Porsche SE",     "ar",  "high"),  # ⚠ ARV-Name prüfen
    ("PorscheSE/2024/PSE_HV2024_Rede_Hans_Dieter_Poetsch_de.pdf",   2024, "Hans Dieter Pötsch", "ceo", "high"),
    ("PorscheSE/2024/PSE_HV2024_Erlaeuterungen_zum_Bericht_des_Aufsichtsrats_Vorabveroeffentlichu...6.2024.pdf",
                                                                     2024, "ARV Porsche SE",     "ar",  "high"),
    ("PorscheSE/2025/PSE_HV2025_Rede_von_Hans_Dieter_Poetsch.pdf",  2025, "Hans Dieter Pötsch", "ceo", "high"),
    ("PorscheSE/2025/PSE_HV2025_Erlaeuterungen_zum_Bericht_des_Aufsichtsrats_Vorabveroeffentlichung.pdf",
                                                                     2025, "ARV Porsche SE",     "ar",  "high"),

    # ── RHEINMETALL ───────────────────────────────────────────────────────────
    # Nur 2022 fehlt CEO-Rede; Chairman Letter = ARV
    ("Rheinmetall/2022/8_DE_Rheinmetall_HV_2022_Chairman_Letter_V4.pdf",         2022, "Arnd Putlitz",      "ar",  "high"),  # ⚠ ARV-Name prüfen
    ("Rheinmetall/2024/Rheinmetall_HV-Rede_Herr_Papperger_2024_05_14_zur_Veroeffentlichung.pdf", 2024, "Armin Papperger", "ceo", "high"),
    ("Rheinmetall/2024/11_DE_Chairman_Letter_HV_2024.pdf",                       2024, "Arnd Putlitz",      "ar",  "high"),
    ("Rheinmetall/2025/Rheinmetall_HV-Rede_Herr_Papperger_2025_05_13.pdf",       2025, "Armin Papperger",   "ceo", "high"),
    ("Rheinmetall/2025/7_DE_250325_chairman_letter_AGM.pdf",                     2025, "Arnd Putlitz",      "ar",  "high"),

    # ── RWE ───────────────────────────────────────────────────────────────────
    # 2023: nur CEO-Rede vorhanden
    ("RWE/2022/hv-2022-rede-des-vorstandsvorsitzenden.pdf",  2022, "Markus Krebber",       "ceo", "high"),
    ("RWE/2022/hv-2022-rede-des-ar-vorsitzenden.pdf",        2022, "Werner Brandt",        "ar",  "high"),
    ("RWE/2023/RWE-hv-2023-rede-des-vorstandsvorsitzenden-markus-krebber.pdf", 2023, "Markus Krebber", "ceo", "high"),
    ("RWE/2024/rwe-hv-2024-rede-des-vorstandsvorsitzenden-markus-krebber.pdf", 2024, "Markus Krebber", "ceo", "high"),
    ("RWE/2024/rwe-hv-2024-bericht-des-aufsichtsrats-redemanuskript.pdf",      2024, "Werner Brandt",  "ar",  "high"),
    ("RWE/2025/rwe-hv-2025-rede-des-vorstandsvorsitzenden-markus-krebber.pdf", 2025, "Markus Krebber", "ceo", "high"),
    ("RWE/2025/rwe-hv-2025-rede-des-aufsichtsratsvorsitzenden.pdf",            2025, "Werner Brandt",  "ar",  "high"),

    # ── SAP ───────────────────────────────────────────────────────────────────
    ("SAP/2022/SAP SE Hauptversammlung 2022_ Rede des Vorstandssprechers.pdf",  2022, "Christian Klein",  "ceo", "high"),
    ("SAP/2022/Schreiben von Prof. Dr. h. c. mult. Hasso Plattner, Vorsitzender des Aufsichtsrats der SAP SE-2.pdf",
                                                                                2022, "Hasso Plattner",   "ar",  "high"),
    ("SAP/2023/SAP SE Hauptversammlung 2023_ Rede des Vorstandssprechers.pdf",  2023, "Christian Klein",  "ceo", "high"),
    ("SAP/2023/Schreiben von Prof. Dr. h. c. mult. Hasso Plattner, Vorsitzender des Aufsichtsrats der SAP SE.pdf",
                                                                                2023, "Hasso Plattner",   "ar",  "high"),
    ("SAP/2024/SAP SE Hauptversammlung 2024_ Rede des Vorstandssprechers.pdf",  2024, "Christian Klein",  "ceo", "high"),
    ("SAP/2024/SAP SE Hauptversammlung 2024_ Schreiben von Prof. Dr. h. c. mult. Hasso Plattner.pdf",
                                                                                2024, "Hasso Plattner",   "ar",  "high"),
    ("SAP/2025/Rede des Vorstandsvorsitzenden 2025.pdf",                        2025, "Christian Klein",  "ceo", "high"),
    ("SAP/2025/Brief des Aufsichtsratsvorsitzenden 2025.pdf",                   2025, "Punit Renjen",     "ar",  "high"),  # Renjen löste Plattner 2024 ab

    # ── SIEMENS ───────────────────────────────────────────────────────────────
    ("Siemens/2022/Roland-Busch-HV-Rede-2022-DE.pdf",    2022, "Roland Busch",             "ceo", "high"),
    ("Siemens/2022/HV-Rede-2022-Snabe-DE.pdf",           2022, "Jim H. Snabe",             "ar",  "high"),
    ("Siemens/2023/Roland-Busch-HV-Rede-2023-DE.pdf",    2023, "Roland Busch",             "ceo", "high"),
    ("Siemens/2023/HV-Rede-2023-JHS-DE.pdf",             2023, "Jim H. Snabe",             "ar",  "high"),
    ("Siemens/2024/HV-Rede-2024-Roland-Busch-Presseformat-DE.pdf",  2024, "Roland Busch",  "ceo", "high"),
    ("Siemens/2024/HV-Rede-2024-Werner-Brandt-Presseformat-DE.pdf", 2024, "Werner Brandt", "ar",  "high"),
    ("Siemens/2025/HV-Rede-2025-Roland-Busch-Presseformat-DE.pdf",  2025, "Roland Busch",  "ceo", "high"),
    ("Siemens/2025/HV-Rede-2025-Jim-Hagemann-Snabe-Presseformat-DE.pdf", 2025, "Jim H. Snabe", "ar", "high"),

    # ── SIEMENS ENERGY ────────────────────────────────────────────────────────
    # CB = Christian Bruch (CEO), JK = Joe Kaeser (ARV)
    ("SiemensEnergy/2022/Siemens-Energy-HV2022-Rede-Christian-Bruch-pdf_Original file.pdf",  2022, "Christian Bruch", "ceo", "high"),
    ("SiemensEnergy/2022/Siemens-Energy-HV2022-Rede-Joe-Kaeser-pdf_Original file.pdf",       2022, "Joe Kaeser",      "ar",  "high"),
    ("SiemensEnergy/2023/20230207-CB-Hauptversammlung-Rede-D-FINAL-INTERNET-pdf_Original file.pdf", 2023, "Christian Bruch", "ceo", "high"),
    ("SiemensEnergy/2023/HV-Rede-2023-Kaeser-Siemens-Energy-DE-pdf_Original file.pdf",       2023, "Joe Kaeser",      "ar",  "high"),
    ("SiemensEnergy/2024/20240221-CB-HV2024-Rede-Internet-FINAL-DE-pdf_Original file.pdf",   2024, "Christian Bruch", "ceo", "high"),
    ("SiemensEnergy/2024/20240221-JK-HV2024-Rede-Internet-FINAL-DE-pdf_Original file.pdf",   2024, "Joe Kaeser",      "ar",  "high"),
    ("SiemensEnergy/2025/2025-02-14-HV2025_Rede_CB_D_FINAL-pdf_Original file.pdf",           2025, "Christian Bruch", "ceo", "high"),
    ("SiemensEnergy/2025/2025-02-14-HV2025_Rede_JK_D_FINAL_inkl-pdf_Original file.pdf",      2025, "Joe Kaeser",      "ar",  "high"),

    # ── SIEMENS HEALTHINEERS ──────────────────────────────────────────────────
    ("SiemensHealthineers/2022/HV2022_CEO_DE.pdf",                                       2022, "Bernd Montag",  "ceo", "high"),
    ("SiemensHealthineers/2022/Ralf-Thomas_ARV-Wesentliche-Schwerpunkte-HV-Rede-2022.pdf", 2022, "Ralf Thomas", "ar",  "high"),
    ("SiemensHealthineers/2023/siemens-healthineers-HV2023_Rede-Bernd-Montag_de.pdf",    2023, "Bernd Montag",  "ceo", "high"),
    ("SiemensHealthineers/2023/siemens-healthineers-HV2023_Ralf-Thomas_Rede_Pressefassung_de.pdf", 2023, "Ralf Thomas", "ar", "high"),
    ("SiemensHealthineers/2024/siemens-healthineers-Rede-CEO_Siemens-Healthineers_HV-2024.pdf",    2024, "Bernd Montag",  "ceo", "high"),
    ("SiemensHealthineers/2024/siemens-healthineers-Rede-ARV_Siemens-Healthineers_HV-2024.pdf",    2024, "Ralf Thomas",   "ar",  "high"),
    ("SiemensHealthineers/2025/Siemens-Healthineers-Rede-CEO-HV-2025.pdf",               2025, "Bernd Montag",  "ceo", "high"),
    ("SiemensHealthineers/2025/Siemens-Healthineers-HV-2025-rede-ARV.pdf",               2025, "Ralf Thomas",   "ar",  "high"),

    # ── SYMRISE ───────────────────────────────────────────────────────────────
    # Nur CEO-Reden, nur 2022 + 2023
    ("Symrise/2022/220422_Schwerpunkte_CEO-Rede_Hauptversammlung.pdf",  2022, "Heinz-Jürgen Bertram", "ceo", "high"),
    ("Symrise/2023/230510-Symrise-HV2023-CEO-Rede.pdf",                 2023, "Jean-Yves Parisot",    "ceo", "high"),  # Parisot ab 2023

    # ── TELEKOM ───────────────────────────────────────────────────────────────
    ("Telekom/2022/dl-220407-rede-hoettges.pdf",          2022, "Timotheus Höttges",        "ceo", "high"),
    ("Telekom/2022/dl-2022-bericht-aufsichtsrat.pdf",     2022, "Nikolaus von Agatha",      "ar",  "high"),  # ⚠ ARV-Name prüfen
    ("Telekom/2023/dl-230405-rede-hoettges.pdf",          2023, "Timotheus Höttges",        "ceo", "high"),
    ("Telekom/2023/dl-2023-bericht-aufsichtsrat.pdf",     2023, "Nikolaus von Agatha",      "ar",  "high"),
    ("Telekom/2024/dl-230410-rede-hoettges-hv-dtag.pdf",  2024, "Timotheus Höttges",        "ceo", "high"),
    ("Telekom/2024/dl-2024-bericht-aufsichtsrat.pdf",     2024, "Nikolaus von Agatha",      "ar",  "high"),
    ("Telekom/2025/dl-250409-rede-hoettges-hv-dtag.pdf",  2025, "Timotheus Höttges",        "ceo", "high"),
    ("Telekom/2025/dl-2025-bericht-aufsichtsrat.pdf",     2025, "Nikolaus von Agatha",      "ar",  "high"),

    # ── VOLKSWAGEN GROUP ──────────────────────────────────────────────────────
    # Diess CEO bis Sept 2022, Blume ab Okt 2022; Pötsch = ARV
    ("VolkswagenGroup/2022/Rede_CEO_Herbert_Diess_2022.pdf",                          2022, "Herbert Diess",   "ceo", "high"),
    ("VolkswagenGroup/2022/Rede_von_Hrn_Poetsch_2022.pdf",                            2022, "Hans Dieter Pötsch", "ar", "high"),
    ("VolkswagenGroup/2023/Hauptversammlung_Volkswagen_AG_2023_-_Rede_CEO_Oliver_Blume.pdf", 2023, "Oliver Blume", "ceo", "high"),
    ("VolkswagenGroup/2023/Bericht_des_AR_Rede_HV_2023.pdf",                          2023, "Hans Dieter Pötsch", "ar", "high"),
    ("VolkswagenGroup/2024/Rede_CEO_HV24_de.pdf",                                     2024, "Oliver Blume",    "ceo", "high"),
    ("VolkswagenGroup/2024/Aufsichtsratsvorsitzender_Rede_HV_2024.pdf",               2024, "Hans Dieter Pötsch", "ar", "high"),
    ("VolkswagenGroup/2025/Rede_CEO_HV25_K-G_de.pdf",                                 2025, "Oliver Blume",    "ceo", "high"),  # ⚠ K-G Kürzel unklar
    ("VolkswagenGroup/2025/Rede_Poetsch_HV_2025_DE.pdf",                              2025, "Hans Dieter Pötsch", "ar", "high"),

    # ── VONOVIA ───────────────────────────────────────────────────────────────
    # Leitfaden_ARV = ARV-Rede
    ("Vonovia/2022/Vonovia_HV_2022_Rede_Rolf_Buch_web_220425.pdf",             2022, "Rolf Buch",          "ceo", "high"),
    ("Vonovia/2023/230511_Vonovia_HV2023_Rede_Rolf_Buch_de.pdf",               2023, "Rolf Buch",          "ceo", "high"),
    ("Vonovia/2023/20220513_Vonovia_Auszug_Leitfaden_ARV_HV_2023_DE_web.pdf",  2023, "Jürgen Fitschen",    "ar",  "high"),  # ⚠ ARV-Name prüfen
    ("Vonovia/2024/240503_Vonovia_HV_2024_Rede_Rolf Buch_Web.pdf",             2024, "Rolf Buch",          "ceo", "high"),
    ("Vonovia/2024/240503_VNA AGM_Auszug aus dem Leitfaden.pdf",               2024, "Jürgen Fitschen",    "ar",  "high"),
    ("Vonovia/2025/250522_Vonovia HV_2025_Rede_Rolf_Buch_web.pdf",             2025, "Rolf Buch",          "ceo", "high"),
    ("Vonovia/2025/250522_VNA HV_ARV-Leitfaden_Auszug_web.pdf",                2025, "Jürgen Fitschen",    "ar",  "high"),

    # ── ZALANDO ───────────────────────────────────────────────────────────────
    # Nur ARV-Berichte vorhanden — keine CEO-Rede publiziert
    ("Zalando/2022/Zalando-SE_HV-2022_Bericht-des-Aufsichtsrats.pdf",          2022, "Kelly Bennett",      "ar",  "high"),  # ⚠ ARV-Name prüfen
    ("Zalando/2023/Zalando-SE_HV-2023_Bericht-des-Aufsichtsrats.pdf",          2023, "Kelly Bennett",      "ar",  "high"),
    ("Zalando/2024/Zalando-SE_HV-2024_Bericht des Aufsichtsrats.pdf",          2024, "Kelly Bennett",      "ar",  "high"),
    ("Zalando/2025/Zalando-SE_AGM-2025_4_Bericht-des-Aufsichtsrats.pdf",       2025, "Kelly Bennett",      "ar",  "high"),
]
