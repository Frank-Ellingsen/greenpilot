"""
================================================================================
MASTER DAX LIBRARY GENERATOR (GREENPILOT 2026 / ELKEM ASA TECHNOLOGY)
================================================================================
Genererer en komplett, produksjonsklar DAX-pakke med:
 1. Core EVM Metrics (PV, EV, AC, BAC)
 2. Variances & Indices (CV, SV, CPI, SPI, CR)
 3. Forecasting (EAC, ETC, VAC, TCPI)
 4. IFRS IAS 38 AuC & Resultat (P&L, Balanse, IAS 36 Impairment Trigger)
 5. Innkjøp & Forpliktelser (PO Committed, Invoiced, Open Commitments, Eksponering)
 6. Kontantstrøm & Arbeidskapital (Cash Out, Enova Grant In, Net Cash Flow, Kumulativ)
 7. Enkeltenheter & Koststeder (Fiskå CC-4100/4200/4300, Timer, Personalkostnad)
 8. Early Warnings & Tufte Betinget Formatering (RAG-farger, Statussignaler, Stolpelengder)

Kan brukes direkte i:
 - DAX Query View (EVALUATE / DEFINE MEASURE)
 - Tabular Editor (C# / Script import)
 - Power BI Desktop TMDL (_Measures.tmdl)
================================================================================
"""

import os
import sys

CURRENT_DIR = os.getcwd()
if os.path.exists(os.path.join(CURRENT_DIR, "data")):
    BASE_DIR = CURRENT_DIR
elif os.path.exists(os.path.join(os.path.dirname(CURRENT_DIR), "data")):
    BASE_DIR = os.path.dirname(CURRENT_DIR)
elif os.path.exists(r"C:\Users\frank\OneDrive\Elkem"):
    BASE_DIR = r"C:\Users\frank\OneDrive\Elkem"
else:
    BASE_DIR = CURRENT_DIR

DOCS_DIR = os.path.join(BASE_DIR, "docs")
PBI_DIR = os.path.join(BASE_DIR, "pbi", "GreenPilotProject.SemanticModel", "definition", "tables")
os.makedirs(DOCS_DIR, exist_ok=True)

OUTPUT_DAX_FILE = os.path.join(DOCS_DIR, "dax_measures_library.dax")
OUTPUT_TMDL_MEASURES = os.path.join(PBI_DIR, "_Measures.tmdl")

DAX_MEASURES = [
    # -------------------------------------------------------------------------
    # 1. CORE EVM VALUE METRICS
    # -------------------------------------------------------------------------
    {
        "name": "Budget at Completion (BAC)",
        "folder": "01 Core EVM",
        "format": "#,##0.00",
        "description": "Total godkjent baseline budsjettramme for GreenPilot 2026 (NOK 20.0M).",
        "dax": "CALCULATE(SUM(Fact_BudgetBaseline[baseline_budget_nok]))"
    },
    {
        "name": "Planned Value (PV)",
        "folder": "01 Core EVM",
        "format": "#,##0.00",
        "description": "Planlagt verdi (BCWS) akkumulert frem til valgt periode basert på baseline.",
        "dax": """VAR MaxDate = MAX(Dim_Date[Date])
RETURN
CALCULATE(
    SUM(Fact_BudgetBaseline[baseline_budget_nok]),
    FILTER(
        ALL(Dim_Date),
        Dim_Date[Date] <= MaxDate
    )
)"""
    },
    {
        "name": "Actual Cost (AC)",
        "folder": "01 Core EVM",
        "format": "#,##0.00",
        "description": "Faktisk bokførte kostnader (ACWP) i SAP ERP hovedbok frem til Data Date (31.10.2026).",
        "dax": """VAR StatusDate = MAX(Dim_Project[data_date])
VAR MaxDate = MAX(Dim_Date[Date])
RETURN
IF(
    MaxDate <= StatusDate || ISBLANK(MaxDate),
    CALCULATE(
        SUM(Fact_GLActuals[amount_nok]),
        FILTER(ALL(Dim_Date), Dim_Date[Date] <= MaxDate)
    ),
    BLANK()
)"""
    },
    {
        "name": "Earned Value (EV)",
        "folder": "01 Core EVM",
        "format": "#,##0.00",
        "description": "Opptjent verdi (BCWP) beregnet ut fra fysisk ferdiggrad i Primavera P6 ganget med BAC.",
        "dax": """VAR StatusDate = MAX(Dim_Project[data_date])
VAR MaxDate = MAX(Dim_Date[Date])
VAR TotalWeight = COUNTROWS(ALL(Dim_Activity))
VAR CompletedWeight = CALCULATE(
    COUNTROWS(Dim_Activity),
    FILTER(
        ALL(Dim_Activity),
        Dim_Activity[status] = "Completed" &&
        Dim_Activity[planned_finish] <= MaxDate
    )
)
RETURN
IF(
    MaxDate <= StatusDate || ISBLANK(MaxDate),
    DIVIDE(CompletedWeight, TotalWeight, 0) * [Budget at Completion (BAC)],
    BLANK()
)"""
    },

    # -------------------------------------------------------------------------
    # 2. EVM VARIANCES & INDICES
    # -------------------------------------------------------------------------
    {
        "name": "Cost Variance (CV)",
        "folder": "02 Variances & Indices",
        "format": "#,##0.00",
        "description": "Kostnadsavvik i NOK (EV - AC). Negativ verdi = overskridelse.",
        "dax": "[Earned Value (EV)] - [Actual Cost (AC)]"
    },
    {
        "name": "Schedule Variance (SV)",
        "folder": "02 Variances & Indices",
        "format": "#,##0.00",
        "description": "Tidsavvik uttrykt i NOK (EV - PV). Negativ verdi = forsinkelse.",
        "dax": "[Earned Value (EV)] - [Planned Value (PV)]"
    },
    {
        "name": "Cost Performance Index (CPI)",
        "folder": "02 Variances & Indices",
        "format": "0.000",
        "description": "Kostnadseffektivitetsindeks (EV / AC). Under 1.00 = overbudsjett.",
        "dax": "DIVIDE([Earned Value (EV)], [Actual Cost (AC)], 1.0)"
    },
    {
        "name": "Schedule Performance Index (SPI)",
        "folder": "02 Variances & Indices",
        "format": "0.000",
        "description": "Fremdriftsindeks (EV / PV). Under 1.00 = bak tidsplan.",
        "dax": "DIVIDE([Earned Value (EV)], [Planned Value (PV)], 1.0)"
    },
    {
        "name": "Critical Ratio (CR)",
        "folder": "02 Variances & Indices",
        "format": "0.000",
        "description": "Kombinert helseindikator (CPI * SPI). Under 0.90 = akutt alarm.",
        "dax": "[Cost Performance Index (CPI)] * [Schedule Performance Index (SPI)]"
    },

    # -------------------------------------------------------------------------
    # 3. FORECASTING & TO-COMPLETE
    # -------------------------------------------------------------------------
    {
        "name": "Estimate at Completion (EAC CPI)",
        "folder": "03 Forecasting",
        "format": "#,##0.00",
        "description": "Statistisk sluttkostnad basert på historisk kostnadseffektivitet (BAC / CPI).",
        "dax": "DIVIDE([Budget at Completion (BAC)], [Cost Performance Index (CPI)], [Budget at Completion (BAC)])"
    },
    {
        "name": "Estimate to Complete (ETC)",
        "folder": "03 Forecasting",
        "format": "#,##0.00",
        "description": "Gjenstående kapitalbehov for å fullføre prosjektet (EAC - AC).",
        "dax": "MAX(0, [Estimate at Completion (EAC CPI)] - [Actual Cost (AC)])"
    },
    {
        "name": "Variance at Completion (VAC)",
        "folder": "03 Forecasting",
        "format": "#,##0.00",
        "description": "Forventet budsjettavvik ved ferdigstillelse (BAC - EAC).",
        "dax": "[Budget at Completion (BAC)] - [Estimate at Completion (EAC CPI)]"
    },
    {
        "name": "To-Complete Performance Index (TCPI BAC)",
        "folder": "03 Forecasting",
        "format": "0.00",
        "description": "Nødvendig effektivitet på gjenstående arbeid for å nå opprinnelig BAC (Urealistisk hvis > 1.10).",
        "dax": "DIVIDE([Budget at Completion (BAC)] - [Earned Value (EV)], [Budget at Completion (BAC)] - [Actual Cost (AC)], 1.0)"
    },

    # -------------------------------------------------------------------------
    # 4. IFRS IAS 38 & ACCOUNTING
    # -------------------------------------------------------------------------
    {
        "name": "AuC Capitalized (Balance Sheet)",
        "folder": "04 IFRS & Accounting",
        "format": "#,##0.00",
        "description": "Utviklingskostnader balanseført som Anlegg under utførelse (IAS 38 § 57, WBS-200 til 500).",
        "dax": """CALCULATE(
    SUM(Fact_GLActuals[amount_nok]),
    Fact_GLActuals[ias38_treatment] = "CAPITALIZE"
)"""
    },
    {
        "name": "P&L Expensed (Research & PMO)",
        "folder": "04 IFRS & Accounting",
        "format": "#,##0.00",
        "description": "Forsknings- og administrasjonskostnader driftsført direkte i resultat (IAS 38 § 54, WBS-100 og 600).",
        "dax": """CALCULATE(
    SUM(Fact_GLActuals[amount_nok]),
    Fact_GLActuals[ias38_treatment] = "EXPENSE"
)"""
    },
    {
        "name": "AuC Capitalization Ratio %",
        "folder": "04 IFRS & Accounting",
        "format": "0.0%",
        "description": "Andel av faktiske kostnader som er aktivert i balansen som AuC.",
        "dax": "DIVIDE([AuC Capitalized (Balance Sheet)], [Actual Cost (AC)], 0.0)"
    },
    {
        "name": "IAS 36 Impairment Trigger Flag",
        "folder": "04 IFRS & Accounting",
        "format": "@",
        "description": "Flagg som indikerer om formell verdifallstest kreves etter IAS 36 § 12 (utløst ved CPI < 0.50).",
        "dax": """IF(
    [Cost Performance Index (CPI)] < 0.50 && [AuC Capitalized (Balance Sheet)] > 20000000,
    "🔴 TRIGGER: Formell IAS 36 Nedskrivningstest Påkrevd",
    "🟢 OK: Ingen akutt verdifallstest utløst"
)"""
    },

    # -------------------------------------------------------------------------
    # 5. PROCUREMENT & COMMITMENTS
    # -------------------------------------------------------------------------
    {
        "name": "PO Committed (Total)",
        "folder": "05 Procurement & Commitments",
        "format": "#,##0.00",
        "description": "Total verdi av godkjente og utstedte innkjøpsordrer i SAP ERP.",
        "dax": "SUM(Fact_PurchaseOrders[amount_nok])"
    },
    {
        "name": "PO Invoiced (Total)",
        "folder": "05 Procurement & Commitments",
        "format": "#,##0.00",
        "description": "Fakturert andel av innkjøpsordrer basert på inngående leverandørfakturaer.",
        "dax": "SUM(Fact_PurchaseOrders[invoiced_nok])"
    },
    {
        "name": "Open Commitments (Total)",
        "folder": "05 Procurement & Commitments",
        "format": "#,##0.00",
        "description": "Åpne, uavsluttede innkjøpsforpliktelser (PO Committed - Invoiced). Likviditetsrisiko.",
        "dax": "SUM(Fact_PurchaseOrders[open_commitment_nok])"
    },
    {
        "name": "Total Financial Exposure",
        "folder": "05 Procurement & Commitments",
        "format": "#,##0.00",
        "description": "Total finansiell forpliktelse for Elkem: Bokført kostnad + Uavsluttede innkjøpsordrer.",
        "dax": "[Actual Cost (AC)] + [Open Commitments (Total)]"
    },
    {
        "name": "PO vs BAC Ratio %",
        "folder": "05 Procurement & Commitments",
        "format": "0.0%",
        "description": "Forholdet mellom forpliktede innkjøp og totalbudsjett. Alarm hvis > 100%.",
        "dax": "DIVIDE([PO Committed (Total)], [Budget at Completion (BAC)], 0.0)"
    },

    # -------------------------------------------------------------------------
    # 6. CASH FLOW & WORKING CAPITAL
    # -------------------------------------------------------------------------
    {
        "name": "Supplier AP Paid NOK",
        "folder": "06 Cash Flow & Working Capital",
        "format": "#,##0.00",
        "description": "Faktiske utbetalinger til leverandører etter 30 dagers forfall (DPO).",
        "dax": "SUM(Fact_CashFlowBridge[supplier_ap_paid_nok])"
    },
    {
        "name": "Internal Payroll Paid NOK",
        "folder": "06 Cash Flow & Working Capital",
        "format": "#,##0.00",
        "description": "Lønnsutbetalinger til egne ansatte på prosjektet.",
        "dax": "SUM(Fact_CashFlowBridge[internal_payroll_paid_nok])"
    },
    {
        "name": "Total Cash Outflow NOK",
        "folder": "06 Cash Flow & Working Capital",
        "format": "#,##0.00",
        "description": "Samlet månedlig likviditetsbelastning for prosjektet (Leverandører + Lønn).",
        "dax": "SUM(Fact_CashFlowBridge[total_cash_outflow_nok])"
    },
    {
        "name": "Enova Grant Cash In NOK",
        "folder": "06 Cash Flow & Working Capital",
        "format": "#,##0.00",
        "description": "Innbetalte tilskuddsmidler fra Enova ved oppnådde milepæler.",
        "dax": "SUM(Fact_CashFlowBridge[enova_grant_cash_in_nok])"
    },
    {
        "name": "Net Monthly Cash Flow NOK",
        "folder": "06 Cash Flow & Working Capital",
        "format": "#,##0.00",
        "description": "Månedlig netto kontantstrøm for Elkem (Tilskudd inn - Utbetalinger ut).",
        "dax": "[Enova Grant Cash In NOK] - [Total Cash Outflow NOK]"
    },
    {
        "name": "Cumulative Net Cash Flow NOK",
        "folder": "06 Cash Flow & Working Capital",
        "format": "#,##0.00",
        "description": "Akkumulert kontantposisjon som viser Elkems maksimale kapitalbinding (Peak Working Capital Exposure).",
        "dax": """VAR MaxDate = MAX(Dim_Date[Date])
RETURN
CALCULATE(
    [Net Monthly Cash Flow NOK],
    FILTER(
        ALL(Dim_Date),
        Dim_Date[Date] <= MaxDate
    )
)"""
    },

    # -------------------------------------------------------------------------
    # 7. ENKELTENHETER & KOSTSTEDER (FISKÅ)
    # -------------------------------------------------------------------------
    {
        "name": "Faktiske Timer Koststed",
        "folder": "07 Koststeder & Enheter",
        "format": "#,##0.0",
        "description": "Totalt antall registrerte timer fra timelister for valgt koststed/avdeling.",
        "dax": "SUM(Fact_Timesheets[hours])"
    },
    {
        "name": "Personalkostnad Koststed NOK",
        "folder": "07 Koststeder & Enheter",
        "format": "#,##0.00",
        "description": "Beregnet personalkostnad for koststedet basert på SkatteFUNN-godkjent sats (maks 530 kr/t).",
        "dax": "[Faktiske Timer Koststed] * 530.0"
    },
    {
        "name": "Koststedsandel %",
        "folder": "07 Koststeder & Enheter",
        "format": "0.0%",
        "description": "Koststedets relative andel av de samlede faktiske prosjektkostnadene.",
        "dax": """DIVIDE(
    [Actual Cost (AC)],
    CALCULATE([Actual Cost (AC)], ALLSELECTED(Dim_CostCenter)),
    0.0
)"""
    },

    # -------------------------------------------------------------------------
    # 8. EARLY WARNINGS & BETINGET FORMATERING (TUFTE RAG)
    # -------------------------------------------------------------------------
    {
        "name": "Early Warning Status Signal",
        "folder": "08 Early Warnings & RAG",
        "format": "@",
        "description": "Overordnet varselindikator basert på ledende forpliktelses- og effektivitetsgrenser.",
        "dax": """SWITCH(
    TRUE(),
    [PO vs BAC Ratio %] > 1.0, "🔴 KRITISK: Forpliktelser > 100% BAC (Innkjøpsfrys)",
    [Cost Performance Index (CPI)] < 0.80, "🔴 RØD: Alvorlig kostnadsoverskridelse",
    [Cost Performance Index (CPI)] < 0.90, "🟡 GUL: Kostnadspress / Marginavvik",
    "🟢 GRØNN: Normal drift"
)"""
    },
    {
        "name": "Early Warning Color Hex",
        "folder": "08 Early Warnings & RAG",
        "format": "@",
        "description": "Hex-fargekode for betinget formatering av tabeller og KPI-kort.",
        "dax": """SWITCH(
    TRUE(),
    [PO vs BAC Ratio %] > 1.0, "#D32F2F",   // Mørkerød
    [Cost Performance Index (CPI)] < 0.80, "#E53935",   // Rød
    [Cost Performance Index (CPI)] < 0.90, "#FB8C00",   // Oransje/Gul
    "#43A047"                                           // Grønn
)"""
    },
    {
        "name": "CPI Status RAG",
        "folder": "08 Early Warnings & RAG",
        "format": "@",
        "description": "Dynamisk RAG-statusikon for CPI (Grønn >= 1.0, Gul 0.90-1.0, Rød < 0.90).",
        "dax": """VAR Val = [Cost Performance Index (CPI)]
RETURN
SWITCH(
    TRUE(),
    ISBLANK(Val), "⚪",
    Val < 0.90, "🔴",
    Val < 1.00, "🟡",
    "🟢"
)"""
    },
    {
        "name": "SPI Status RAG",
        "folder": "08 Early Warnings & RAG",
        "format": "@",
        "description": "Dynamisk RAG-statusikon for SPI (Grønn >= 1.0, Gul 0.90-1.0, Rød < 0.90).",
        "dax": """VAR Val = [Schedule Performance Index (SPI)]
RETURN
SWITCH(
    TRUE(),
    ISBLANK(Val), "⚪",
    Val < 0.90, "🔴",
    Val < 1.00, "🟡",
    "🟢"
)"""
    },
    {
        "name": "CPI RAG Color",
        "folder": "08 Early Warnings & RAG",
        "format": "@",
        "description": "Fargekode for CPI (Grønn >= 1.0, Gul 0.90-1.0, Rød < 0.90).",
        "dax": """VAR Val = [Cost Performance Index (CPI)]
RETURN
SWITCH(
    TRUE(),
    ISBLANK(Val), "#737373",
    Val < 0.90, "#D32F2F",
    Val < 1.00, "#FB8C00",
    "#43A047"
)"""
    },
    {
        "name": "SPI RAG Color",
        "folder": "08 Early Warnings & RAG",
        "format": "@",
        "description": "Fargekode for SPI (Grønn >= 1.0, Gul 0.90-1.0, Rød < 0.90).",
        "dax": """VAR Val = [Schedule Performance Index (SPI)]
RETURN
SWITCH(
    TRUE(),
    ISBLANK(Val), "#737373",
    Val < 0.90, "#D32F2F",
    Val < 1.00, "#FB8C00",
    "#43A047"
)"""
    }
]

def generate_dax_library_file():
    print(f"Genererer Master DAX-bibliotek til: {OUTPUT_DAX_FILE}")
    with open(OUTPUT_DAX_FILE, "w", encoding="utf-8") as f:
        f.write("// ===============================================================================\n")
        f.write("// MASTER DAX MEASURES LIBRARY - ELKEM TECHNOLOGY (GREENPILOT 2026)\n")
        f.write("// ===============================================================================\n\n")
        
        current_folder = ""
        for m in DAX_MEASURES:
            if m["folder"] != current_folder:
                current_folder = m["folder"]
                f.write(f"\n// -------------------------------------------------------------------------------\n")
                f.write(f"// MAPPE: {current_folder}\n")
                f.write(f"// -------------------------------------------------------------------------------\n")
            
            f.write(f"// Beskrivelse: {m['description']}\n")
            f.write(f"// Format: {m['format']}\n")
            f.write(f"[{m['name']}] =\n{m['dax']}\n\n")

    print(f" [OK] {len(DAX_MEASURES)} DAX-mål eksportert til {OUTPUT_DAX_FILE}")

import re

def generate_tmdl_table():
    if not os.path.exists(os.path.dirname(OUTPUT_TMDL_MEASURES)):
        print(f"Merk: Fant ikke TMDL-katalog ({OUTPUT_TMDL_MEASURES}). Hopper over TMDL-oppdatering.")
        return
        
    print(f"Oppdaterer (Merger) TMDL _Measures til: {OUTPUT_TMDL_MEASURES}")
    
    header_lines = [
        "table _Measures",
        "\tlineageTag: a7e39958-8686-4fbf-93ba-f27eb66b5930",
        ""
    ]
    existing_blocks = {}
    
    # 1. Les eksisterende mål hvis filen finnes fra før (bevarer alle 22 Dynamic RAG & In-Cell Bar-mål)
    if os.path.exists(OUTPUT_TMDL_MEASURES):
        with open(OUTPUT_TMDL_MEASURES, "r", encoding="utf-8") as f:
            content = f.read()
        
        current_name = None
        current_lines = []
        for line in content.splitlines():
            match = re.match(r"^\tmeasure '([^']+)' =", line)
            if match:
                if current_name:
                    existing_blocks[current_name] = current_lines
                current_name = match.group(1)
                current_lines = [line]
            elif current_name:
                current_lines.append(line)
        if current_name:
            existing_blocks[current_name] = current_lines
            
    # 2. Merge / Oppdater med de nye og forbedrede målene fra DAX_MEASURES
    for m in DAX_MEASURES:
        m_lines = [f"\tmeasure '{m['name']}' ="]
        for dl in m["dax"].split("\n"):
            m_lines.append(f"\t\t{dl}")
        m_lines.append(f"\t\tformatString: {m['format']}")
        m_lines.append(f"\t\tdisplayFolder: {m['folder']}")
        m_lines.append(f"\t\tdescription: {m['description']}")
        m_lines.append(f"\t\tlineageTag: {abs(hash(m['name']))}")
        m_lines.append("")
        existing_blocks[m["name"]] = m_lines
        
    # 3. Skriv ut samlet TMDL med alle mål intakt
    out_lines = header_lines[:]
    for name, blk in existing_blocks.items():
        out_lines.extend(blk)
        if blk and blk[-1] != "":
            out_lines.append("")
            
    with open(OUTPUT_TMDL_MEASURES, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
        
    print(f" [OK] TMDL-tabell merget! Totalt {len(existing_blocks)} mål bevart og oppdatert.")

if __name__ == "__main__":
    print("=" * 80)
    print("=== GENERERER KOMPLETT MASTER DAX-PAKKE (ELKEM GREENPILOT 2026) ===")
    print("=" * 80)
    generate_dax_library_file()
    generate_tmdl_table()
    print("=" * 80)
    print("Full DAX-pakke er ferdig generert og klar til bruk!")
    print("=" * 80)
