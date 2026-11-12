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
SEMANTIC_DEF_DIR = os.path.join(PBI_DIR, "GreenPilotProject.SemanticModel", "definition", "tables")
MEASURES_TMDL = os.path.join(SEMANTIC_DEF_DIR, "_Measures.tmdl")
PAGES_DIR = os.path.join(REPORT_DEF_DIR, "pages")

os.makedirs(PAGES_DIR, exist_ok=True)

print("=" * 80)
print("=== GENERERER OG OPPDATERER POWER BI RAPPORT-SIDER (PBIP FORMAT) ===")
print("=" * 80)
print(f"Prosjekt-rot: {PROJECT_ROOT}")
print(f"Rapport-definisjon: {REPORT_DEF_DIR}")

# ==============================================================================
# 0. SJEKK OG LEGG TIL NARRATIV-DAX MÅL I _Measures.tmdl DERSOM DE MANGLER
# ==============================================================================
DAX_NARRATIVE_BLOCK = '''
\t/// --- 09 EXECUTIVE NARRATIVE & GOVERNANCE MEASURES ---
\tmeasure 'Executive RAG Headline' = 
\t\t\tVAR _cpi = [CPI]
\t\t\tVAR _exp = [Total Financial Exposure NOK]
\t\t\tVAR _bac = [BAC NOK]
\t\t\tRETURN
\t\t\t\tIF (
\t\t\t\t\t_cpi < 0.50 || _exp > _bac,
\t\t\t\t\t"🔴 RØD ALARM: KRITISK KOSTNADSSPREKK & LIKVIDITETSEKSPONERING (Per 31.10.2026)",
\t\t\t\t\tIF (
\t\t\t\t\t\t_cpi < 0.80 || _exp > _bac * 0.8,
\t\t\t\t\t\t"🟡 GULT VARSEL: BETYDELIG KOSTNADSPRESS & OPPFØLGINGSBEHOV",
\t\t\t\t\t\t"🟢 GRØNT LYS: PROSJEKTET LEVERER INNENFOR VEDTATT BUDSJETTRAMME"
\t\t\t\t\t)
\t\t\t\t)
\t\tlineageTag: da990001-0001-4000-8000-000000000001
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Narrative Part1 Diagnose' = 
\t\t\tVAR _cpi = [CPI]
\t\t\tVAR _cv = [CV NOK] / 1000000
\t\t\tVAR _spi = [SPI]
\t\t\tRETURN
\t\t\t\t"1. DIAGNOSE (EVM): Prosjektet opererer med en kostnadseffektivitet på CPI " 
\t\t\t\t& FORMAT ( _cpi, "0.00" ) 
\t\t\t\t& " og et akkumulert kostnadsavvik på NOK " 
\t\t\t\t& FORMAT ( _cv, "0.0" ) 
\t\t\t\t& "M. Fysisk fremdrift meldes til SPI " 
\t\t\t\t& FORMAT ( _spi, "0.00" ) 
\t\t\t\t& " som følge av forsert reaktormontasje."
\t\tlineageTag: da990001-0002-4000-8000-000000000002
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Narrative Part2 Driver' = 
\t\t\tVAR _ac = [Total Actual Cost NOK] / 1000000
\t\t\tVAR _po = [Open Commitments NOK] / 1000000
\t\t\tVAR _exp = [Total Financial Exposure NOK] / 1000000
\t\t\tVAR _ratio = DIVIDE ( [Total Financial Exposure NOK], [BAC NOK], 0 )
\t\t\tRETURN
\t\t\t\t"2. DRIVER & LIKVIDITET: Bokførte kostnader (NOK " 
\t\t\t\t& FORMAT ( _ac, "0.0" ) 
\t\t\t\t& "M) og åpne leverandørforpliktelser (NOK " 
\t\t\t\t& FORMAT ( _po, "0.0" ) 
\t\t\t\t& "M) gir en samlet finansiell eksponering på NOK " 
\t\t\t\t& FORMAT ( _exp, "0.0" ) 
\t\t\t\t& "M (" 
\t\t\t\t& FORMAT ( _ratio, "0%" ) 
\t\t\t\t& " av godkjent totalbudsjett)."
\t\tlineageTag: da990001-0003-4000-8000-000000000003
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Narrative Part3 Accounting' = 
\t\t\tVAR _auc = [AuC Capitalized NOK] / 1000000
\t\t\tRETURN
\t\t\t\t"3. REGNSKAPSMESSIG KONSEKVENS: Av de bokførte kostnadene er NOK " 
\t\t\t\t& FORMAT ( _auc, "0.0" ) 
\t\t\t\t& "M balanseført som anlegg under utførelse (AuC) etter IAS 38. Eksploderende sluttkostnad (EAC) utløser umiddelbart krav om nedskrivningstest etter IAS 36 før årsoppgjøret."
\t\tlineageTag: da990001-0004-4000-8000-000000000004
\t\tdisplayFolder: 08 Early Warnings & RAG

\tmeasure 'Narrative Part4 Action' = 
\t\t\tVAR _exp = [Total Financial Exposure NOK]
\t\t\tVAR _bac = [BAC NOK]
\t\t\tRETURN
\t\t\t\tIF (
\t\t\t\t\t_exp > _bac,
\t\t\t\t\t"4. PÅBUD TIL STYRET: 1) Umiddelbar innkjøpsfrys på alle nye rekvisisjoner. 2) Kanselleringsaudit av uleverte innkjøpsordrer (NOK 49,2M). 3) Innkall styret til ekstraordinært Stage-Gate møte for 30 dagers Technical Hold / Off-Ramp vurdering.",
\t\t\t\t\t"4. ANBEFALING: Fortsett månedlig kostnadsavstemming og tett oppfølging av leverandørfakturaer."
\t\t\t\t)
\t\tlineageTag: da990001-0005-4000-8000-000000000005
\t\tdisplayFolder: 08 Early Warnings & RAG
'''

if os.path.exists(MEASURES_TMDL):
    with open(MEASURES_TMDL, "r", encoding="utf-8") as f:
        tmdl_content = f.read()
    if "Executive RAG Headline" not in tmdl_content:
        with open(MEASURES_TMDL, "a", encoding="utf-8") as f:
            f.write(DAX_NARRATIVE_BLOCK)
        print(" [OK] 5 nye regelbaserte DAX-mål lagt til i _Measures.tmdl")
    else:
        print(" [INFO] DAX-narrativmål finnes allerede i _Measures.tmdl")

# ==============================================================================
# 1. METADATA FOR ALLE 5 RAPPORTSIDER (NARRATIV-SIDE FØRST)
# ==============================================================================
PAGES_METADATA = [
    {
        "name": "ReportSection_ExecutiveNarrative",
        "displayName": "00 Executive Narrative & Governance",
        "folder": "00_executive_narrative"
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
    }
]

# Oppdater pages.json
pages_json_content = {
    "pageOrder": [p["name"] for p in PAGES_METADATA],
    "activePageName": "ReportSection_ExecutiveNarrative"
}

pages_json_path = os.path.join(PAGES_DIR, "pages.json")
with open(pages_json_path, "w", encoding="utf-8") as f:
    json.dump(pages_json_content, f, indent=2, ensure_ascii=False)
print(f" [OK] Oppdatert pages.json med 5 sider: {pages_json_path}")

# ==============================================================================
# 2. GENERER HVER ENKELT SIDE (PAGE.JSON OG VISUALS)
# ==============================================================================

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

# ------------------------------------------------------------------------------
# SIDE 0: 00 EXECUTIVE NARRATIVE & GOVERNANCE (NY HOVEDFORSIDE)
# ------------------------------------------------------------------------------
p0_folder = os.path.join(PAGES_DIR, "00_executive_narrative")
p0_vis_folder = os.path.join(p0_folder, "visuals")
os.makedirs(p0_vis_folder, exist_ok=True)
p0_page_json = {
    "name": "ReportSection_ExecutiveNarrative",
    "displayName": "00 Executive Narrative & Governance",
    "displayOption": "FitToPage",
    "width": 1280,
    "height": 720
}
with open(os.path.join(p0_folder, "page.json"), "w", encoding="utf-8") as f:
    json.dump(p0_page_json, f, indent=2, ensure_ascii=False)

# Visuals for Side 0
v0_title = create_visual_container(
    name="v0_header_banner",
    x=20, y=10, width=1240, height=45,
    visual_type="textbox",
    title="ELKEM GREENPILOT 2026 — EXECUTIVE GOVERNANCE & CONTROLLER NARRATIVE",
    config={"subtitle": "Enova Pilotprosjekt | Cut-off: 31.10.2026 | IFRS IAS 38 & ISA 805 Compliant | Fast Standard SSOT"}
)
with open(os.path.join(p0_vis_folder, "v0_header_banner.json"), "w", encoding="utf-8") as f:
    json.dump(v0_title, f, indent=2, ensure_ascii=False)

v0_rag_banner = create_visual_container(
    name="v0_rag_callout_banner",
    x=20, y=65, width=1240, height=65,
    visual_type="card",
    title="Overordnet Prosjektstatus & RAG Flagg",
    config={"measure": "Executive RAG Headline", "format": "Text", "style": "alertBannerRed"}
)
with open(os.path.join(p0_vis_folder, "v0_rag_callout_banner.json"), "w", encoding="utf-8") as f:
    json.dump(v0_rag_banner, f, indent=2, ensure_ascii=False)

v0_narrative1 = create_visual_container(
    name="v0_card_part1_diagnose",
    x=20, y=140, width=610, height=130,
    visual_type="card",
    title="1. Diagnose & Kostnadskontroll (EVM)",
    config={"measure": "Narrative Part1 Diagnose", "format": "Text", "fontSize": 12}
)
with open(os.path.join(p0_vis_folder, "v0_card_part1_diagnose.json"), "w", encoding="utf-8") as f:
    json.dump(v0_narrative1, f, indent=2, ensure_ascii=False)

v0_narrative2 = create_visual_container(
    name="v0_card_part2_driver",
    x=650, y=140, width=610, height=130,
    visual_type="card",
    title="2. Hoveddriver & Likviditetseksponering",
    config={"measure": "Narrative Part2 Driver", "format": "Text", "fontSize": 12}
)
with open(os.path.join(p0_vis_folder, "v0_card_part2_driver.json"), "w", encoding="utf-8") as f:
    json.dump(v0_narrative2, f, indent=2, ensure_ascii=False)

v0_narrative3 = create_visual_container(
    name="v0_card_part3_accounting",
    x=20, y=280, width=610, height=130,
    visual_type="card",
    title="3. Regnskapsmessig Konsekvens (IFRS IAS 38 / IAS 36)",
    config={"measure": "Narrative Part3 Accounting", "format": "Text", "fontSize": 12}
)
with open(os.path.join(p0_vis_folder, "v0_card_part3_accounting.json"), "w", encoding="utf-8") as f:
    json.dump(v0_narrative3, f, indent=2, ensure_ascii=False)

v0_narrative4 = create_visual_container(
    name="v0_card_part4_action",
    x=650, y=280, width=610, height=130,
    visual_type="card",
    title="4. Påbud til Styret & Governance (Action)",
    config={"measure": "Narrative Part4 Action", "format": "Text", "fontSize": 12}
)
with open(os.path.join(p0_vis_folder, "v0_card_part4_action.json"), "w", encoding="utf-8") as f:
    json.dump(v0_narrative4, f, indent=2, ensure_ascii=False)

# KPI Scorecards nederst
v0_kpis = [
    ("v0_kpi_bac", 20, 420, 235, 110, "Totalbudsjett (BAC)", "BAC NOK", "#,##0.00 NOK"),
    ("v0_kpi_ac", 270, 420, 235, 110, "Bokført Kostnad (AC)", "Total Actual Cost NOK", "#,##0.00 NOK"),
    ("v0_kpi_ev", 520, 420, 235, 110, "Opptjent Verdi (EV)", "EV NOK", "#,##0.00 NOK"),
    ("v0_kpi_po", 770, 420, 235, 110, "Åpne Forpliktelser", "Open Commitments NOK", "#,##0.00 NOK"),
    ("v0_kpi_exp", 1020, 420, 240, 110, "Samlet Eksponering", "Total Financial Exposure NOK", "#,##0.00 NOK"),
]
for k_name, k_x, k_y, k_w, k_h, k_title, k_meas, k_fmt in v0_kpis:
    card_json = create_visual_container(
        name=k_name, x=k_x, y=k_y, width=k_w, height=k_h,
        visual_type="card", title=k_title,
        config={"measure": k_meas, "format": k_fmt}
    )
    with open(os.path.join(p0_vis_folder, f"{k_name}.json"), "w", encoding="utf-8") as f:
        json.dump(card_json, f, indent=2, ensure_ascii=False)

v0_nav_box = create_visual_container(
    name="v0_nav_instructions",
    x=20, y=540, width=1240, height=160,
    visual_type="textbox",
    title="Controller Veiledning til Styret & Drilldown-Oversikt",
    config={
        "line1": "• Side 01 Executive Summary: EVM KPI-er og Tufte in-cell avvikstabeller.",
        "line2": "• Side 02 EVM S-Curve: Visuell tidsserie som viser kostnadskollapsen fra Q1 2026.",
        "line3": "• Side 03 IFRS Accounting: WBS-nivå splitt mellom balanseført AuC (43,4M) og FoU P&L (14,6M).",
        "line4": "• Side 04 Likviditet & Koststeder: Kontantstrømsbro (DPO 30d) og ressursbruk ved Elkem Fiskå (CC-4100/4200/4300)."
    }
)
with open(os.path.join(p0_vis_folder, "v0_nav_instructions.json"), "w", encoding="utf-8") as f:
    json.dump(v0_nav_box, f, indent=2, ensure_ascii=False)

print(" [OK] Side 0: '00 Executive Narrative & Governance' generert med 12 visual-komponenter.")

# ------------------------------------------------------------------------------
# SIDE 1: 01 EXECUTIVE SUMMARY
# ------------------------------------------------------------------------------
p1_folder = os.path.join(PAGES_DIR, "01_exec_summary")
os.makedirs(os.path.join(p1_folder, "visuals"), exist_ok=True)
p1_page_json = {
    "name": "ReportSection_ExecSummary",
    "displayName": "01 Executive Summary",
    "displayOption": "FitToPage",
    "width": 1280,
    "height": 720
}
with open(os.path.join(p1_folder, "page.json"), "w", encoding="utf-8") as f:
    json.dump(p1_page_json, f, indent=2, ensure_ascii=False)
print(" [OK] Side 1: '01 Executive Summary' bekreftet i PBIP-strukturen.")

# ------------------------------------------------------------------------------
# SIDE 2: 02 EVM S-CURVE & TRENDS
# ------------------------------------------------------------------------------
p2_folder = os.path.join(PAGES_DIR, "02_scurve_trends")
os.makedirs(os.path.join(p2_folder, "visuals"), exist_ok=True)
p2_page_json = {
    "name": "ReportSection_SCurve",
    "displayName": "02 EVM S-Curve & Trends",
    "displayOption": "FitToPage",
    "width": 1280,
    "height": 720
}
with open(os.path.join(p2_folder, "page.json"), "w", encoding="utf-8") as f:
    json.dump(p2_page_json, f, indent=2, ensure_ascii=False)
print(" [OK] Side 2: '02 EVM S-Curve & Trends' bekreftet i PBIP-strukturen.")

# ------------------------------------------------------------------------------
# SIDE 3: 03 IFRS ACCOUNTING & WBS DRILLDOWN
# ------------------------------------------------------------------------------
p3_folder = os.path.join(PAGES_DIR, "03_ifrs_wbs")
os.makedirs(os.path.join(p3_folder, "visuals"), exist_ok=True)
p3_page_json = {
    "name": "ReportSection_IFRS_WBS",
    "displayName": "03 IFRS Accounting & WBS Drilldown",
    "displayOption": "FitToPage",
    "width": 1280,
    "height": 720
}
with open(os.path.join(p3_folder, "page.json"), "w", encoding="utf-8") as f:
    json.dump(p3_page_json, f, indent=2, ensure_ascii=False)
print(" [OK] Side 3: '03 IFRS Accounting & WBS Drilldown' bekreftet i PBIP-strukturen.")

# ------------------------------------------------------------------------------
# SIDE 4: 04 LIKVIDITET & KOSTSTEDER FISKÅ
# ------------------------------------------------------------------------------
p4_folder = os.path.join(PAGES_DIR, "04_cashflow_costcenters")
p4_vis_folder = os.path.join(p4_folder, "visuals")
os.makedirs(p4_vis_folder, exist_ok=True)
p4_page_json = {
    "name": "ReportSection_CashFlow_CostCenters",
    "displayName": "04 Likviditet & Koststeder Fiskå",
    "displayOption": "FitToPage",
    "width": 1280,
    "height": 720
}
with open(os.path.join(p4_folder, "page.json"), "w", encoding="utf-8") as f:
    json.dump(p4_page_json, f, indent=2, ensure_ascii=False)

# Visuals for Side 4
v1_title = create_visual_container(
    name="v1_header_banner",
    x=20, y=10, width=1240, height=45,
    visual_type="textbox",
    title="Elkem Technology – Likviditetseksponering, Arbeidskapital & Enheter Fiskå",
    config={"subtitle": "Cut-off 31.10.2026 | Avstemming fra Påløpt Regnskapskostnad til Kontantutgang | CC-4100, CC-4200, CC-4300"}
)
with open(os.path.join(p4_vis_folder, "v1_header_banner.json"), "w", encoding="utf-8") as f:
    json.dump(v1_title, f, indent=2, ensure_ascii=False)

v2_card1 = create_visual_container(
    name="v2_kpi_cash_out",
    x=20, y=65, width=295, height=95,
    visual_type="card",
    title="Total Kontantutbetaling (AC justert DPO)",
    config={"measure": "Total Cash Outflow NOK", "format": "#,##0.00 NOK", "target": "Fact_CashFlowBridge"}
)
with open(os.path.join(p4_vis_folder, "v2_kpi_cash_out.json"), "w", encoding="utf-8") as f:
    json.dump(v2_card1, f, indent=2, ensure_ascii=False)

v2_card2 = create_visual_container(
    name="v2_kpi_enova_in",
    x=335, y=65, width=295, height=95,
    visual_type="card",
    title="Enova Tilskudd Innbetalt (Juni 2026)",
    config={"measure": "Enova Grant Cash In NOK", "format": "#,##0.00 NOK", "target": "Fact_CashFlowBridge"}
)
with open(os.path.join(p4_vis_folder, "v2_kpi_enova_in.json"), "w", encoding="utf-8") as f:
    json.dump(v2_card2, f, indent=2, ensure_ascii=False)

v2_card3 = create_visual_container(
    name="v2_kpi_net_cash",
    x=650, y=65, width=295, height=95,
    visual_type="card",
    title="Kumulativ Likviditetseksponering",
    config={"measure": "Cumulative Net Cash Flow NOK", "format": "#,##0.00 NOK", "target": "Fact_CashFlowBridge"}
)
with open(os.path.join(p4_vis_folder, "v2_kpi_net_cash.json"), "w", encoding="utf-8") as f:
    json.dump(v2_card3, f, indent=2, ensure_ascii=False)

v2_card4 = create_visual_container(
    name="v2_kpi_open_po",
    x=965, y=65, width=295, height=95,
    visual_type="card",
    title="Åpne Leverandørforpliktelser (PO)",
    config={"measure": "Open Commitments NOK", "format": "#,##0.00 NOK", "target": "Fact_PurchaseOrders"}
)
with open(os.path.join(p4_vis_folder, "v2_kpi_open_po.json"), "w", encoding="utf-8") as f:
    json.dump(v2_card4, f, indent=2, ensure_ascii=False)

v3_cf_chart = create_visual_container(
    name="v3_cf_bridge_chart",
    x=20, y=170, width=610, height=530,
    visual_type="lineStackedColumnComboChart",
    title="Månedlig Kontantstrøm (DPO 30d & Lønn) vs. Enova-tilskudd & Netto Posisjon",
    config={
        "categoryAxis": "Dim_Date[Period]",
        "columnMeasures": ["Total Cash Outflow NOK", "Enova Grant Cash In NOK"],
        "lineMeasures": ["Cumulative Net Cash Flow NOK"]
    }
)
with open(os.path.join(p4_vis_folder, "v3_cf_bridge_chart.json"), "w", encoding="utf-8") as f:
    json.dump(v3_cf_chart, f, indent=2, ensure_ascii=False)

v4_cc_table = create_visual_container(
    name="v4_cost_centers_table",
    x=650, y=170, width=610, height=255,
    visual_type="pivotTable",
    title="Enheter og Koststeder – Elkem Fiskå (CC-4100, CC-4200, CC-4300)",
    config={
        "rowDimensions": ["Dim_CostCenter[cost_center_id]", "Dim_CostCenter[cost_center_name]"],
        "metricValues": ["Faktiske Timer Koststed", "Personalkostnad Koststed NOK", "Andel Timer Koststed %"]
    }
)
with open(os.path.join(p4_vis_folder, "v4_cost_centers_table.json"), "w", encoding="utf-8") as f:
    json.dump(v4_cc_table, f, indent=2, ensure_ascii=False)

v5_ew_table = create_visual_container(
    name="v5_early_warning_table",
    x=650, y=435, width=610, height=265,
    visual_type="tableEx",
    title="Early Warning Månedsoppfølging (Jan-Okt 2026) – Stage-Gate RAG Status",
    config={
        "tableColumns": ["Fact_MonthlyEarlyWarnings[period]", "PO Committed NOK", "PO vs BAC %", "Projected EAC NOK", "Early Warning Status Signal"],
        "conditionalColor": "Early Warning Color Hex"
    }
)
with open(os.path.join(p4_vis_folder, "v5_early_warning_table.json"), "w", encoding="utf-8") as f:
    json.dump(v5_ew_table, f, indent=2, ensure_ascii=False)

print(" [OK] Side 4: '04 Likviditet & Koststeder Fiskå' bekreftet med 5 visual-komponenter.")

print("=" * 80)
print("=== POWER BI PROJECT (PBIP) MED 5 SIDER VELLYKKET FULLFØRT ===")
print("=" * 80)
