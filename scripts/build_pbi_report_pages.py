import os
import sys
import json
import shutil

# ==============================================================================
# ROBUST STISØKING FOR PROSJEKTROT
# ==============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..")) if os.path.basename(SCRIPT_DIR).lower() == "scripts" else SCRIPT_DIR

PBI_DIR = os.path.join(PROJECT_ROOT, "pbi")
REPORT_DEF_DIR = os.path.join(PBI_DIR, "GreenPilotProject.Report", "definition")
PAGES_DIR = os.path.join(REPORT_DEF_DIR, "pages")
SEMANTIC_DEF_DIR = os.path.join(PBI_DIR, "GreenPilotProject.SemanticModel", "definition")
TABLES_DIR = os.path.join(SEMANTIC_DEF_DIR, "tables")

os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)

print("=" * 80)
print("=== GENERERER OG OPPDATERER POWER BI RAPPORT-SIDER & AI-ANALYTICS (PBIP) ===")
print("=" * 80)
print(f"Prosjekt-rot: {PROJECT_ROOT}")
print(f"Rapport-definisjon: {REPORT_DEF_DIR}")

# ==============================================================================
# 1. OPPDATER _MEASURES.TMDL MED DYNAMISKE NARRATIVER OG RAG-METRIKKER
# ==============================================================================
measures_tmdl_path = os.path.join(TABLES_DIR, "_Measures.tmdl")

NEW_DAX_MEASURES = """

\t/// ==============================================================================
\t/// DYNAMISKE SIDE-SPESIFIKKE CONTROLLER-NARRATIVER & AI-METRIKKER
\t/// ==============================================================================

\tmeasure 'Executive RAG Headline' = 
\t\tVAR _cpi = [CPI]
\t\tVAR _exp = [Total Financial Exposure NOK]
\t\tVAR _bac = [BAC NOK]
\t\tRETURN
\t\t\tIF (
\t\t\t\t_cpi < 0.50 || _exp > _bac,
\t\t\t\t"🔴 RØD ALARM: KRITISK KOSTNADSSPREKK & LIKVIDITETSEKSPONERING (Per 31.10.2026)",
\t\t\t\tIF (
\t\t\t\t\t_cpi < 0.80 || _exp > _bac * 0.8,
\t\t\t\t\t"🟡 GULT VARSEL: BETYDELIG KOSTNADSPRESS & OPPFØLGINGSBEHOV",
\t\t\t\t\t"🟢 GRØNT LYS: PROSJEKTET LEVERER INNENFOR VEDTATT BUDSJETTRAMME"
\t\t\t\t)
\t\t\t)
\t\tlineageTag: a1111111-0001-4000-8000-000000000001
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Narrative Part1 Diagnose' = 
\t\tVAR _cpi = [CPI]
\t\tVAR _cv = [CV NOK] / 1000000
\t\tVAR _spi = [SPI]
\t\tRETURN
\t\t\t"1. DIAGNOSE (EVM): Prosjektet opererer med en kostnadseffektivitet på CPI " 
\t\t\t& FORMAT ( _cpi, "0.00" ) 
\t\t\t& " og et akkumulert kostnadsavvik på NOK " 
\t\t\t& FORMAT ( _cv, "0.0" ) 
\t\t\t& "M. Fysisk fremdrift meldes til SPI " 
\t\t\t& FORMAT ( _spi, "0.00" ) 
\t\t\t& " som følge av forsert reaktormontasje."
\t\tlineageTag: a1111111-0002-4000-8000-000000000002
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Narrative Part2 Driver' = 
\t\tVAR _ac = [Total Actual Cost NOK] / 1000000
\t\tVAR _po = [Open Commitments NOK] / 1000000
\t\tVAR _exp = [Total Financial Exposure NOK] / 1000000
\t\tVAR _ratio = DIVIDE ( [Total Financial Exposure NOK], [BAC NOK], 0 )
\t\tRETURN
\t\t\t"2. DRIVER & LIKVIDITET: Bokførte kostnader (NOK " 
\t\t\t& FORMAT ( _ac, "0.0" ) 
\t\t\t& "M) og åpne leverandørforpliktelser (NOK " 
\t\t\t& FORMAT ( _po, "0.0" ) 
\t\t\t& "M) gir en samlet finansiell eksponering på NOK " 
\t\t\t& FORMAT ( _exp, "0.0" ) 
\t\t\t& "M (" 
\t\t\t& FORMAT ( _ratio, "0%" ) 
\t\t\t& " av godkjent totalbudsjett)."
\t\tlineageTag: a1111111-0003-4000-8000-000000000003
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Narrative Part3 Accounting' = 
\t\tVAR _auc = [AuC Capitalized NOK] / 1000000
\t\tRETURN
\t\t\t"3. REGNSKAPSMESSIG KONSEKVENS: Av de bokførte kostnadene er NOK " 
\t\t\t& FORMAT ( _auc, "0.0" ) 
\t\t\t& "M balanseført som anlegg under utførelse (AuC) etter IAS 38. Eksploderende sluttkostnad (EAC) utløser umiddelbart krav om nedskrivningstest etter IAS 36 før årsoppgjøret."
\t\tlineageTag: a1111111-0004-4000-8000-000000000004
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Narrative Part4 Action' = 
\t\tVAR _exp = [Total Financial Exposure NOK]
\t\tVAR _bac = [BAC NOK]
\t\tRETURN
\t\t\tIF (
\t\t\t\t_exp > _bac,
\t\t\t\t"4. PÅBUD TIL STYRET: 1) Umiddelbar innkjøpsfrys på alle nye rekvisisjoner. 2) Kanselleringsaudit av uleverte innkjøpsordrer (NOK 49,2M). 3) Innkall styret til ekstraordinært Stage-Gate møte for 30 dagers Technical Hold / Off-Ramp vurdering.",
\t\t\t\t"4. ANBEFALING: Fortsett månedlig kostnadsavstemming og tett oppfølging av leverandørfakturaer."
\t\t\t)
\t\tlineageTag: a1111111-0005-4000-8000-000000000005
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Page02_SCurve_Narrative' = 
\t\tVAR _cpi = [CPI]
\t\tVAR _spi = [SPI]
\t\tVAR _cv = [CV NOK] / 1000000
\t\tVAR _sv = [SV NOK] / 1000000
\t\tRETURN
\t\t\t"S-KURVE ANALYSE: Prosjektet viser en klassisk overforsering. Fysisk fremdrift (EV 19,2M) ligger foran opprinnelig planlagt tid (SV: +" 
\t\t\t& FORMAT(_sv, "0.0") & " MNOK / SPI: " & FORMAT(_spi, "0.00") 
\t\t\t& "), men enhetskostnaden er ekstremt ineffektiv (CPI: " & FORMAT(_cpi, "0.00") & "). "
\t\t\t& "Dette indikerer at forseringen er kjøpt gjennom massiv overtidsbruk og fordyrende hasteinnkjøp."
\t\tlineageTag: a1111111-0006-4000-8000-000000000006
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Page03_IFRS_Narrative' = 
\t\tVAR _auc = [AuC Capitalized NOK] / 1000000
\t\tVAR _fou = [P&L Expensed NOK] / 1000000
\t\tRETURN
\t\t\t"IFRS IAS 38/36 ANALYSE: Av påløpte kostnader er NOK " & FORMAT(_auc, "0.0") & "M aktivert som anlegg under utførelse (AuC) og NOK " 
\t\t\t& FORMAT(_fou, "0.0") & "M driftsført over resultat. Eksploderende sluttkostnad utløser akutt krav om nedskrivningstest etter IAS 36 før årsoppgjøret."
\t\tlineageTag: a1111111-0007-4000-8000-000000000007
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Page04_CashFlow_Narrative' = 
\t\tVAR _netCash = [Cumulative Net Cash Flow NOK] / 1000000
\t\tVAR _po = [Open Commitments NOK] / 1000000
\t\tRETURN
\t\t\t"LIKVIDITETSVARSEL: Akkumulert netto likviditetsbelastning har nådd NOK " & FORMAT(_netCash, "0.0") 
\t\t\t& "M. Med 30 dagers DPO og åpne ordreforpliktelser på NOK " & FORMAT(_po, "0.0") 
\t\t\t& "M vil likviditetsgapet eskalere ytterligere før eventuelle nye Enova-refusjoner tilfaller."
\t\tlineageTag: a1111111-0008-4000-8000-000000000008
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Page05_AI_Insights_Narrative' = 
\t\t"AI INSIGHTS & ROTÅRSAKSANALYSE: Nedbrytingstreet og Key Influencer-motoren identifiserer WBS-300 (Reaktoranskaffelser) og valutabundne utstyrsleveranser som de dominerende driverne for kostnadssprekk og rød status. Bruk Q&A for naturlig språksøk."
\t\tlineageTag: a1111111-0009-4000-8000-000000000009
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'EVM_Marker_Color' = 
\t\tVAR _cpi = [CPI]
\t\tRETURN
\t\t\tSWITCH(
\t\t\t\tTRUE(),
\t\t\t\tISBLANK(_cpi), "#737373",
\t\t\t\t_cpi < 0.50, "#C00000",
\t\t\t\t_cpi < 0.90, "#E69F00",
\t\t\t\t"#009E73"
\t\t\t)
\t\tlineageTag: a1111111-0010-4000-8000-000000000010
\t\tdisplayFolder: 08 Early Warnings & RAG
"""

if os.path.exists(measures_tmdl_path):
    with open(measures_tmdl_path, "r", encoding="utf-8") as f:
        existing_tmdl = f.read()
    if "Executive RAG Headline" not in existing_tmdl:
        with open(measures_tmdl_path, "a", encoding="utf-8") as f:
            f.write(NEW_DAX_MEASURES)
        print(f" [OK] Beriket {measures_tmdl_path} med nye DAX narrativ- og RAG-mål.")
    else:
        print(f" [OK] DAX-mål allerede tilstede i {measures_tmdl_path}.")
else:
    print(f" [INFO] Fant ikke {measures_tmdl_path} lokalt, oppretter referanse-TMDL.")
    with open(measures_tmdl_path, "w", encoding="utf-8") as f:
        f.write("table _Measures\n\tlineageTag: 00000000-0000-0000-0000-000000000000\n" + NEW_DAX_MEASURES)

# ==============================================================================
# 2. DEFINISJON AV ALLE 6 RAPPORTSIDER I POWER BI
# ==============================================================================
PAGES_METADATA = [
    {
        "name": "ReportSection_ExecNarrative",
        "displayName": "00 Executive Narrative & Governance",
        "folder": "00_exec_narrative"
    },
    {
        "name": "ReportSection_ExecSummary",
        "displayName": "01 Executive Summary",
        "folder": "01_exec_summary"
    },
    {
        "name": "ReportSection_SCurve",
        "displayName": "02 EVM S-Curve & Trends",
        "folder": "02_scurve_trends"
    },
    {
        "name": "ReportSection_IFRS_WBS",
        "displayName": "03 IFRS Accounting & WBS Drilldown",
        "folder": "03_ifrs_wbs"
    },
    {
        "name": "ReportSection_CashFlow_CostCenters",
        "displayName": "04 Likviditet & Koststeder Fiskå",
        "folder": "04_cashflow_costcenters"
    },
    {
        "name": "ReportSection_AI_Analytics",
        "displayName": "05 AI Analytics & Decomposition",
        "folder": "05_ai_analytics"
    }
]

pages_json_content = {
    "pageOrder": [p["name"] for p in PAGES_METADATA],
    "activePageName": "ReportSection_ExecNarrative"
}

pages_json_path = os.path.join(PAGES_DIR, "pages.json")
with open(pages_json_path, "w", encoding="utf-8") as f:
    json.dump(pages_json_content, f, indent=2, ensure_ascii=False)
print(f" [OK] Oppdatert pages.json med {len(PAGES_METADATA)} sider: {pages_json_path}")

def create_visual_container(name: str, x: int, y: int, width: int, height: int, visual_type: str, title: str, config: dict):
    return {
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": 0,
            "width": width,
            "height": height,
            "tabOrder": 0
        },
        "visual": {
            "visualType": visual_type,
            "title": title,
            "config": config
        }
    }

def setup_page(folder_name: str, page_name: str, display_name: str):
    p_folder = os.path.join(PAGES_DIR, folder_name)
    v_folder = os.path.join(p_folder, "visuals")
    os.makedirs(v_folder, exist_ok=True)
    p_json = {
        "name": page_name,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "width": 1280,
        "height": 720
    }
    with open(os.path.join(p_folder, "page.json"), "w", encoding="utf-8") as f:
        json.dump(p_json, f, indent=2, ensure_ascii=False)
    return v_folder

# ------------------------------------------------------------------------------
# SIDE 0: 00 Executive Narrative & Governance
# ------------------------------------------------------------------------------
v0 = setup_page("00_exec_narrative", "ReportSection_ExecNarrative", "00 Executive Narrative & Governance")

# Header
with open(os.path.join(v0, "v1_banner.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v1_banner", 20, 10, 1240, 45, "textbox", "Elkem GreenPilot 2026 – Styringsdokument & Controller Konklusjon", {"subtitle": "Cut-off 31.10.2026 | FAST Standard & IFRS IAS 38/36 Forankret"}), f, indent=2)

# RAG Headline
with open(os.path.join(v0, "v2_rag_headline.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v2_rag_headline", 20, 60, 1240, 55, "card", "Overordnet Statusflagg", {"measure": "Executive RAG Headline", "colorBinding": "Early Warning Color Hex"}), f, indent=2)

# 4 Narrativ-kort
narratives = [
    ("v3_n1_diag", 20, 125, 610, 100, "1. Diagnose (EVM & Kostnadskontroll)", "Narrative Part1 Diagnose"),
    ("v4_n2_driv", 650, 125, 610, 100, "2. Hoveddriver & Forpliktelsesbilde", "Narrative Part2 Driver"),
    ("v5_n3_acct", 20, 235, 610, 100, "3. Regnskapsmessig Konsekvens (IAS 38 / IAS 36)", "Narrative Part3 Accounting"),
    ("v6_n4_act", 650, 235, 610, 100, "4. Påbud til Styret (Stage-Gate Beslutning)", "Narrative Part4 Action"),
]
for n_name, x, y, w, h, t, m in narratives:
    with open(os.path.join(v0, f"{n_name}.json"), "w", encoding="utf-8") as f:
        json.dump(create_visual_container(n_name, x, y, w, h, "card", t, {"measure": m, "target": "_Measures"}), f, indent=2)

# KPI Scorecards
kpis_s0 = [
    ("v7_kpi_bac", 20, 345, 235, 90, "Budsjett (BAC)", "BAC NOK"),
    ("v8_kpi_ac", 270, 345, 235, 90, "Påløpt Kostnad (AC)", "Total Actual Cost NOK"),
    ("v9_kpi_ev", 520, 345, 235, 90, "Opptjent Verdi (EV)", "EV NOK"),
    ("v10_kpi_po", 770, 345, 235, 90, "Åpne PO Forpliktelser", "Open Commitments NOK"),
    ("v11_kpi_exp", 1020, 345, 240, 90, "Total Eksponering", "Total Financial Exposure NOK"),
]
for k_name, x, y, w, h, t, m in kpis_s0:
    with open(os.path.join(v0, f"{k_name}.json"), "w", encoding="utf-8") as f:
        json.dump(create_visual_container(k_name, x, y, w, h, "card", t, {"measure": m, "format": "#,##0.00 NOK", "target": "_Measures"}), f, indent=2)

# Storytelling Waterfall Diagram (Bro fra BAC til Eksponering)
with open(os.path.join(v0, "v12_waterfall_bridge.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v12_waterfall_bridge", 20, 445, 1240, 260, "waterfallChart", "Forpliktelsesisberget: Fra Vedtatt Budsjett (20M) til Total Eksponering (107,2M)", {
        "categoryAxis": "Dim_WBS[wbs_id]",
        "breakdown": "Fact_FinancialEVM_Unified_Flat[category]",
        "yAxis": "Total Financial Exposure NOK"
    }), f, indent=2)
print(" [OK] Side 0: '00 Executive Narrative & Governance' generert.")

# ------------------------------------------------------------------------------
# SIDE 2: 02 EVM S-Curve & Trends (Med Kontinuerlig tidsserie, Trendline, Forecast, Anomaly og Dynamisk RAG)
# ------------------------------------------------------------------------------
v2 = setup_page("02_scurve_trends", "ReportSection_SCurve", "02 EVM S-Curve & Trends")

with open(os.path.join(v2, "v1_banner.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v1_banner", 20, 10, 1240, 40, "textbox", "EVM S-Kurve, Fremskrivning & Avviksdeteksjon", {"subtitle": "Innebygd Trendlinje, 6-måneders ETS Forecast, Anomaly Detection og RAG-markører"}), f, indent=2)

# Side-narrativ
with open(os.path.join(v2, "v2_scurve_narrative.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v2_scurve_narrative", 20, 55, 1240, 65, "card", "Controller S-Kurve Vurdering (Regelbasert)", {"measure": "Page02_SCurve_Narrative", "target": "_Measures"}), f, indent=2)

# S-kurve Linjediagram med Continuous Date Axis, Forecast, Trend og Anomaly
with open(os.path.join(v2, "v3_scurve_chart.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v3_scurve_chart", 20, 130, 840, 570, "lineChart", "EVM S-Kurve: Planlagt (PV) vs Påløpt (AC) vs Opptjent (EV) – Månedlig Avviksdeteksjon", {
        "xAxis": "Dim_Date[Date]",
        "xAxisType": "Continuous",
        "yAxis": ["Cumulative PV NOK", "Cumulative AC NOK", "Cumulative EV NOK"],
        "analytics": {
            "trendline": {"show": True, "style": "dashed", "color": "#737373"},
            "forecast": {"show": True, "length": 6, "confidence": 0.95, "seasonality": 12},
            "anomalyDetection": {"show": True, "sensitivity": 80, "markerStyle": "circle"},
            "conditionalDataPointColor": "EVM_Marker_Color"
        }
    }), f, indent=2)

# CPI / SPI Trendlinje
with open(os.path.join(v2, "v4_index_trends.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v4_index_trends", 880, 130, 380, 275, "lineChart", "Indekstrend: CPI (Kostnad) vs. SPI (Fremdrift)", {
        "xAxis": "Dim_Date[Period]",
        "yAxis": ["CPI", "SPI"],
        "analytics": {"refline": {"value": 1.0, "label": "Baseline 1.0", "color": "#737373"}}
    }), f, indent=2)

# Avvikstabell (CV & SV per måned)
with open(os.path.join(v2, "v5_variance_table.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v5_variance_table", 880, 415, 380, 285, "tableEx", "Månedlig Kostnadsavvik (CV) og Tidsavvik (SV)", {
        "tableColumns": ["Dim_Date[Period]", "CV NOK", "SV NOK", "EVM Status Signal"]
    }), f, indent=2)
print(" [OK] Side 2: '02 EVM S-Curve & Trends' oppdatert med avansert analytics og narrativ.")

# ------------------------------------------------------------------------------
# SIDE 3: 03 IFRS Accounting & WBS Drilldown (Med Decomposition Tree)
# ------------------------------------------------------------------------------
v3 = setup_page("03_ifrs_wbs", "ReportSection_IFRS_WBS", "03 IFRS Accounting & WBS Drilldown")

with open(os.path.join(v3, "v1_banner.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v1_banner", 20, 10, 1240, 40, "textbox", "IFRS IAS 38 Allokering, IAS 36 Nedskrivningsrisiko & WBS Dekomponering", {"subtitle": "Rotårsaksanalyse med Decomposition Tree | Balanse (AuC) vs Resultat (FoU)"}), f, indent=2)

with open(os.path.join(v3, "v2_ifrs_narrative.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v2_ifrs_narrative", 20, 55, 1240, 65, "card", "IFRS Regnskapskonklusjon (Regelbasert)", {"measure": "Page03_IFRS_Narrative", "target": "_Measures"}), f, indent=2)

# Decomposition Tree (Nedbrytingstre for Kostnadsavvik)
with open(os.path.join(v3, "v3_decomp_tree.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v3_decomp_tree", 20, 130, 780, 570, "decompositionTree", "Rotårsaksanalyse: Dekomponering av Kostnadsavvik (CV) og Eksponering", {
        "analyzeMeasure": "CV NOK",
        "explainBy": [
            "Dim_WBS[wbs_name]",
            "Dim_CostElement[cost_element_name]",
            "Dim_Vendor[vendor_name]",
            "Dim_CostCenter[cost_center_name]"
        ],
        "aiSplit": True
    }), f, indent=2)

# WBS Tabell & IAS 38 Bar Chart
with open(os.path.join(v3, "v4_wbs_matrix.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v4_wbs_matrix", 820, 130, 440, 280, "pivotTable", "WBS Regnskapsallokering (AuC vs FoU)", {
        "rowDimensions": ["Dim_WBS[wbs_id]", "Dim_WBS[wbs_name]"],
        "metricValues": ["BAC NOK", "Total Actual Cost NOK", "AuC Capitalized NOK", "P&L Expensed NOK"]
    }), f, indent=2)

with open(os.path.join(v3, "v5_impairment_scenarios.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v5_impairment_scenarios", 820, 420, 440, 280, "barChart", "IAS 36 Nedskrivningsscenarioer ved Stage-Gate Beslutning", {
        "categoryAxis": "Fact_FinancialEVM_Unified_Flat[scenario_name]",
        "columnMeasures": ["Balanseført AuC NOK", "Estimert Verdifall NOK"]
    }), f, indent=2)
print(" [OK] Side 3: '03 IFRS Accounting & WBS Drilldown' oppdatert med Decomposition Tree.")

# ------------------------------------------------------------------------------
# SIDE 4: 04 Likviditet & Koststeder Fiskå
# ------------------------------------------------------------------------------
v4 = setup_page("04_cashflow_costcenters", "ReportSection_CashFlow_CostCenters", "04 Likviditet & Koststeder Fiskå")

with open(os.path.join(v4, "v1_banner.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v1_banner", 20, 10, 1240, 40, "textbox", "Likviditetseksponering, Arbeidskapital & Enheter ved Elkem Fiskå", {"subtitle": "Avstemming fra Påløpt Kostnad til Kontantutbetaling (DPO 30d) | CC-4100, CC-4200, CC-4300"}), f, indent=2)

with open(os.path.join(v4, "v2_cf_narrative.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v2_cf_narrative", 20, 55, 1240, 65, "card", "Likviditets- og Kapasitetsvurdering (Regelbasert)", {"measure": "Page04_CashFlow_Narrative", "target": "_Measures"}), f, indent=2)

with open(os.path.join(v4, "v3_cf_bridge.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v3_cf_bridge", 20, 130, 610, 570, "lineStackedColumnComboChart", "Månedlig Kontantstrøm vs Enova-tilskudd & Netto Posisjon", {
        "categoryAxis": "Dim_Date[Period]",
        "columnMeasures": ["Total Cash Outflow NOK", "Enova Grant Cash In NOK"],
        "lineMeasures": ["Cumulative Net Cash Flow NOK"]
    }), f, indent=2)

with open(os.path.join(v4, "v4_cc_table.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v4_cc_table", 650, 130, 610, 275, "pivotTable", "Enheter & Koststeder – Elkem Fiskå (CC-4100, CC-4200, CC-4300)", {
        "rowDimensions": ["Dim_CostCenter[cost_center_id]", "Dim_CostCenter[cost_center_name]"],
        "metricValues": ["Faktiske Timer Koststed", "Personalkostnad Koststed NOK", "Andel Timer Koststed %"]
    }), f, indent=2)

with open(os.path.join(v4, "v5_ew_table.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v5_ew_table", 650, 415, 610, 285, "tableEx", "Early Warning Månedsoppfølging – Stage-Gate RAG Status", {
        "tableColumns": ["Fact_MonthlyEarlyWarnings[period]", "PO Committed NOK", "PO vs BAC %", "Projected EAC NOK", "Early Warning Status Signal"],
        "conditionalColor": "Early Warning Color Hex"
    }), f, indent=2)
print(" [OK] Side 4: '04 Likviditet & Koststeder Fiskå' oppdatert med narrativ.")

# ------------------------------------------------------------------------------
# SIDE 5: 05 AI Analytics & Key Influencers (NY SIDE)
# ------------------------------------------------------------------------------
v5 = setup_page("05_ai_analytics", "ReportSection_AI_Analytics", "05 AI Analytics & Key Influencers")

with open(os.path.join(v5, "v1_banner.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v1_banner", 20, 10, 1240, 40, "textbox", "Avansert AI-Analyse: Key Influencers, Q&A Språksøk & Anomaly Detection", {"subtitle": "Maskinlæringsdrevet rotårsaksanalyse og naturlig språkgrensesnitt for styret"}), f, indent=2)

with open(os.path.join(v5, "v2_ai_narrative.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v2_ai_narrative", 20, 55, 1240, 65, "card", "AI Insights & Prediksjonsvarsel (Regelbasert)", {"measure": "Page05_AI_Insights_Narrative", "target": "_Measures"}), f, indent=2)

# Key Influencers Visual
with open(os.path.join(v5, "v3_key_influencers.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v3_key_influencers", 20, 130, 680, 570, "keyInfluencers", "Key Influencers: Hva forårsaker RØD ALARM i prosjektet?", {
        "targetMetric": "Early Warning Status Signal",
        "targetValue": "🔴 RØD (PO > 100% BAC)",
        "explainBy": [
            "Dim_WBS[wbs_name]",
            "Fact_PurchaseOrders[currency]",
            "Fact_PurchaseOrders[amount_nok]",
            "Dim_CostCenter[cost_center_name]",
            "Dim_Vendor[vendor_name]"
        ]
    }), f, indent=2)

# Q&A Interactive Box
with open(os.path.join(v5, "v4_qna_box.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v4_qna_box", 720, 130, 540, 275, "qna", "Spørsmål og Svar (Q&A / AI Prepp)", {
        "placeholder": "Still spørsmål om kostnader, leverandører eller timer (f.eks. 'Hva er faktisk kost for reaktor?')",
        "suggestedQuestions": [
            "Hva er Total Financial Exposure vs BAC?",
            "Vis månedlig CPI trend i 2026",
            "Hvilken leverandør har størst åpne PO-forpliktelser?",
            "Hvor mange timer har CC-4300 brukt?"
        ]
    }), f, indent=2)

# AI Prepp Veiledning / Informasjonstekstboks
qna_guide_text = (
    "AI PREPP & Q&A SETUP VEILEDNING:\n"
    "1. Knappen 'Forbered Q&A' / 'AI Prepp' i moduleringsfanen brukes til å lære opp modellen med bedriftsspesifikke synonymer.\n"
    "2. Synonymer er definert for sentrale begreper: 'AC' -> Total Actual Cost, 'PO' -> Open Commitments, 'Fiskå' -> Dim_CostCenter.\n"
    "3. Linguistic schema sikrer at ledelsen kan stille spørsmål på naturlig språk uten å kjenne tabellstrukturen.\n"
    "4. Anomaly detection og ETS forecast i linjediagrammene gir prediktiv fremskriving av forpliktelsene."
)
with open(os.path.join(v5, "v5_ai_guide.json"), "w", encoding="utf-8") as f:
    json.dump(create_visual_container("v5_ai_guide", 720, 415, 540, 285, "textbox", "Om Power BI AI Prepp & Språklig Skjema", {"text": qna_guide_text}), f, indent=2)
print(" [OK] Side 5: '05 AI Analytics & Key Influencers' generert.")

# Side 1 bekreftes
setup_page("01_exec_summary", "ReportSection_ExecSummary", "01 Executive Summary")
print(" [OK] Side 1: '01 Executive Summary' bekreftet i PBIP-strukturen.")

print("=" * 80)
print("=== POWER BI PROJECT (PBIP) MED 6 SIDER & AI-ANALYSE FULLFØRT ===")
print("=" * 80)
