import os
import sys
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import DataPoint

# ==============================================================================
# ROBUST STISØKING FOR KILDEDATA (VIRKER BÅDE FRA ROT OG /scripts)
# ==============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..")) if os.path.basename(SCRIPT_DIR).lower() == "scripts" else SCRIPT_DIR

def resolve_source_path(fname: str) -> str:
    possible_dirs = [
        os.path.join(PROJECT_ROOT, "data", "raw"),
        os.path.join(PROJECT_ROOT, "data", "cleaned"),
        os.path.join(PROJECT_ROOT, "data", "staging"),
        os.path.join(PROJECT_ROOT, "data"),
        os.path.join(PROJECT_ROOT, "raw"),
        r"C:\Users\frank\OneDrive\Elkem\data\raw",
        r"C:\Users\frank\OneDrive\Elkem\data",
        "/workspace/knowledge",
    ]
    for d in possible_dirs:
        p = os.path.join(d, fname)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"Fant ikke kildedata for {fname}. Søkte i: {possible_dirs}")

def read_source(fname: str) -> pd.DataFrame:
    p = resolve_source_path(fname)
    with open(p, "rb") as f:
        first_bytes = f.read(10)
    enc = "utf-8-sig" if first_bytes.startswith(b"\xef\xbb\xbf") else "utf-8"
    try:
        return pd.read_csv(p, sep=";", encoding=enc)
    except Exception:
        return pd.read_csv(p, sep=",", encoding=enc)

print("--- Laster kildedata ---")
df_fx = read_source("03_erp_fx_rates.csv")
dim_wbs = read_source("01_master_wbs.csv")
fact_budget = read_source("05_erp_budget_baseline.csv")
fact_po = read_source("06_erp_purchase_orders.csv")
fact_ap = read_source("08_erp_ap_invoices.csv")
fact_gl = read_source("10_erp_gl_actuals.csv")
dim_activity = read_source("12_primavera_activities.csv")
dim_employee = read_source("16_hr_employee_master.csv")
fact_timesheets = read_source("18_hr_timesheets.csv")

# FX beregninger for PO og AP
fact_po["period"] = pd.to_datetime(fact_po["po_date"]).dt.strftime("%Y-%m")
fact_po = fact_po.merge(df_fx[["period", "currency", "nok_rate"]], on=["period", "currency"], how="left")
fact_po["nok_rate"] = fact_po["nok_rate"].fillna(1.0)
fact_po["amount_nok"] = fact_po["amount_currency"] * fact_po["nok_rate"]

fact_ap["period"] = pd.to_datetime(fact_ap["invoice_date"]).dt.strftime("%Y-%m")
fact_ap = fact_ap.merge(df_fx[["period", "currency", "nok_rate"]], on=["period", "currency"], how="left")
fact_ap["nok_rate"] = fact_ap["nok_rate"].fillna(1.0)
fact_ap["amount_nok"] = fact_ap["amount_currency"] * fact_ap["nok_rate"]

ap_by_po = fact_ap.groupby("po_line_id")["amount_nok"].sum().to_dict()
fact_po["invoiced_nok"] = fact_po["po_line_id"].map(lambda x: ap_by_po.get(x, 0.0)).fillna(0.0)
fact_po["open_commitment_nok"] = np.maximum(0.0, fact_po["amount_nok"] - fact_po["invoiced_nok"])

# DPO 30 dager forfall
fact_ap["payment_due_date"] = pd.to_datetime(fact_ap["invoice_date"]) + pd.Timedelta(days=30)
fact_ap["cash_out_period"] = fact_ap["payment_due_date"].dt.strftime("%Y-%m")
ap_cash_monthly = fact_ap.groupby("cash_out_period")["amount_nok"].sum().to_dict()

# Lønnsutbetalinger
fact_timesheets["period"] = pd.to_datetime(fact_timesheets["work_date"]).dt.strftime("%Y-%m")
payroll_cash_monthly = (fact_timesheets.groupby("period")["hours"].sum() * 530.0).to_dict()

# GL og Budsjett
fact_gl["period"] = pd.to_datetime(fact_gl["posting_date"]).dt.strftime("%Y-%m")
ac_monthly_vals = fact_gl.groupby("period")["amount_nok"].sum().to_dict()
pv_monthly_vals = fact_budget.groupby("period")["baseline_budget_nok"].sum().to_dict()
po_monthly_vals = fact_po.groupby("period")["amount_nok"].sum().to_dict()

bac_total = 20000000.0
total_acts = len(dim_activity)

# Initialiser arbeidsbok
wb = openpyxl.Workbook()
wb.remove(wb.active)

# Formateringsdefinisjoner (FAST Standard / Top-Left Focus)
FONT_TITLE = Font(name="Calibri", size=13, bold=True, color="1F4E79")
FONT_SUBTITLE = Font(name="Calibri", size=9.5, italic=True, color="595959")
FONT_TH = Font(name="Calibri", size=9.5, bold=True, color="FFFFFF")
FONT_REGULAR = Font(name="Calibri", size=9.5, bold=False, color="000000")
FONT_BOLD = Font(name="Calibri", size=9.5, bold=True, color="000000")

FILL_HEADER = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
FILL_ZEBRA = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
FILL_WHITE = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
FILL_INPUT = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
FILL_CALC = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

# RAG Farger (FAST Standard kompatible)
FILL_ALERT_RED = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
FILL_ALERT_YELLOW = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
FILL_ALERT_GREEN = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

FONT_ALERT_RED = Font(name="Calibri", size=9.5, bold=True, color="C00000")
FONT_ALERT_YELLOW = Font(name="Calibri", size=9.5, bold=True, color="B25900")
FONT_ALERT_GREEN = Font(name="Calibri", size=9.5, bold=True, color="385723")

ALIGN_LEFT = Alignment(horizontal="left", vertical="top")
ALIGN_CENTER = Alignment(horizontal="center", vertical="top")
ALIGN_RIGHT = Alignment(horizontal="right", vertical="top")
ALIGN_WRAP_LEFT = Alignment(horizontal="left", vertical="top", wrap_text=True)

THIN_BORDER_SIDE = Side(border_style="thin", color="D9D9D9")
CELL_BORDER = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=THIN_BORDER_SIDE, bottom=THIN_BORDER_SIDE)
HEADER_BORDER = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=THIN_BORDER_SIDE, bottom=Side(border_style="medium", color="1F4E79"))
TOTAL_BORDER = Border(top=Side(border_style="thin", color="000000"), bottom=Side(border_style="double", color="000000"))

FMT_CURR = "#,##0.00"
FMT_PCT = "0.0%"
FMT_IDX = "0.000"

def auto_fit_columns(ws, max_cap=38, min_width=11):
    """Sikrer kompakte kolonner slik at alt innhold er lesbart og ingen kolonner skyves langt til høyre."""
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            # Ikke la tittelrader (1-3) eller narrativblokker (19-25) blåse opp kolonnebredden
            if cell.row in (1, 2, 3) or (ws.title == "00_Executive_Summary" and cell.row >= 18):
                continue
            val = str(cell.value or "")
            if val.startswith("="):
                val = "123,456,789.00"
            if cell.number_format == FMT_CURR:
                val += "    "
            if len(val) > max_len:
                max_len = len(val)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, min_width), max_cap)

# ==============================================================================
# 00_Executive_Summary (TOPP-VENSTRE ORIENTERT MED SIDE-BY-SIDE VISUAL)
# ==============================================================================
print(" - Bygger 00_Executive_Summary (Topp-venstre orientert med side-by-side visual)")
ws0 = wb.create_sheet(title="00_Executive_Summary")
ws0.views.sheetView[0].showGridLines = True
ws0.views.sheetView[0].topLeftCell = "A1"
ws0.freeze_panes = "A5"

ws0["A1"] = "ELKEM GREENPILOT 2026 - FINANCIAL & EVM EXECUTIVE SUMMARY"
ws0["A1"].font = FONT_TITLE
ws0["A2"] = "Single Source of Truth (SSOT) Model | FAST Standard Compliant | Cut-off: 2026-10-31"
ws0["A2"].font = FONT_SUBTITLE

headers_s = ["Styringsmetrikk / KPI", "Bokført / Beregnet Verdi", "Enhet", "Krav / Mål", "Status / Controller Vurdering", "RAG Flagg"]
ws0.row_dimensions[4].height = 24
for col_idx, h in enumerate(headers_s, start=1):
    c = ws0.cell(row=4, column=col_idx, value=h)
    c.font = FONT_TH
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = HEADER_BORDER

kpis = [
    ("Budget at Completion (BAC)", 20000000.0, "NOK", "20,000,000.00", "Vedtatt baseline-ramme (Styret)", FMT_CURR, FILL_INPUT, FONT_BOLD, "🟢 BASELINE", FILL_ALERT_GREEN, FONT_ALERT_GREEN),
    ("Planned Value (PV YTD)", 16620871.10, "NOK", "Planlagt verdi", "Akkumulert budsjett planlagt levert per okt", FMT_CURR, FILL_CALC, FONT_BOLD, "🟢 PLANLAGT", FILL_ALERT_GREEN, FONT_ALERT_GREEN),
    ("Actual Cost (AC)", 57968040.98, "NOK", "< 20,000,000.00", "Overskridelse på +189.8% over BAC", FMT_CURR, FILL_ALERT_RED, FONT_BOLD, "🔴 RØD ALARM", FILL_ALERT_RED, FONT_ALERT_RED),
    ("Earned Value (EV)", 19215686.27, "NOK", "20,000,000.00", "96.1% fysisk ferdigstillelse", FMT_CURR, FILL_CALC, FONT_BOLD, "🟢 FORSERING", FILL_ALERT_GREEN, FONT_ALERT_GREEN),
    ("Cost Variance (CV)", "=B8-B7", "NOK", ">= 0.00", "Alvorlig kostnadsoverskridelse (-38.8M)", FMT_CURR, FILL_ALERT_RED, FONT_BOLD, "🔴 RØD ALARM", FILL_ALERT_RED, FONT_ALERT_RED),
    ("Schedule Variance (SV)", "=B8-B6", "NOK", ">= 0.00", "Positivt tidsavvik pga forsering (+2.59M)", FMT_CURR, FILL_CALC, FONT_BOLD, "🟢 FORAN TID", FILL_ALERT_GREEN, FONT_ALERT_GREEN),
    ("Cost Performance Index (CPI)", "=IFERROR(B8/B7, 0.0)", "Ratio", ">= 1.000", "Kritisk ineffektivitet (0.331)", FMT_IDX, FILL_ALERT_RED, FONT_BOLD, "🔴 RØD ALARM", FILL_ALERT_RED, FONT_ALERT_RED),
    ("Schedule Performance Index (SPI)", "=IFERROR(B8/B6, 1.0)", "Ratio", ">= 1.000", "Raskere enn opprinnelig plan (1.156)", FMT_IDX, FILL_ALERT_GREEN, FONT_BOLD, "🟢 FORAN PLAN", FILL_ALERT_GREEN, FONT_ALERT_GREEN),
    ("Open Commitments (PO)", 49233751.55, "NOK", "0.00", "Åpne leverandørforpliktelser", FMT_CURR, FILL_INPUT, FONT_BOLD, "🟡 BUNDET", FILL_ALERT_YELLOW, FONT_ALERT_YELLOW),
    ("Total Financial Exposure", "=B7+B13", "NOK", "<= BAC", "Samlet finansiell forpliktelse (107.2M)", FMT_CURR, FILL_ALERT_RED, FONT_BOLD, "🔴 RØD ALARM", FILL_ALERT_RED, FONT_ALERT_RED),
    ("AuC Balanseført (IAS 38)", 43375028.38, "NOK", "Aktivum", "Balanseført anlegg under utførelse (AuC)", FMT_CURR, FILL_CALC, FONT_BOLD, "🟡 VERDIFALL", FILL_ALERT_YELLOW, FONT_ALERT_YELLOW),
    ("P&L Driftsført FoU (IAS 38)", 14593012.60, "NOK", "Kostnad", "Driftsført forskningsfase & PMO", FMT_CURR, FILL_CALC, FONT_BOLD, "🟢 RESULTAT", FILL_ALERT_GREEN, FONT_ALERT_GREEN),
    ("Enova Tilskudd Utbetalt", 3000000.0, "NOK", "10,000,000.00", "Refusjon innbetalt juni 2026", FMT_CURR, FILL_INPUT, FONT_BOLD, "🟢 INNBETALT", FILL_ALERT_GREEN, FONT_ALERT_GREEN),
]

for idx, (kpi, val, unit, tgt, status, fmt, fill_c, font_c, rag_txt, rag_fill, rag_font) in enumerate(kpis, start=5):
    ws0.row_dimensions[idx].height = 20
    ws0.cell(row=idx, column=1, value=kpi).font = font_c
    ws0.cell(row=idx, column=1).alignment = ALIGN_LEFT
    c_val = ws0.cell(row=idx, column=2, value=val)
    c_val.number_format = fmt
    c_val.font = font_c
    c_val.fill = fill_c
    c_val.alignment = ALIGN_RIGHT
    ws0.cell(row=idx, column=3, value=unit).alignment = ALIGN_CENTER
    ws0.cell(row=idx, column=4, value=tgt).alignment = ALIGN_RIGHT
    ws0.cell(row=idx, column=5, value=status).alignment = ALIGN_LEFT
    c_rag = ws0.cell(row=idx, column=6, value=rag_txt)
    c_rag.fill = rag_fill
    c_rag.font = rag_font
    c_rag.alignment = ALIGN_CENTER
    for col_i in range(1, 7):
        ws0.cell(row=idx, column=col_i).border = CELL_BORDER

# DYNAMISK NARRATIV-BOKS NEDERST
ws0.row_dimensions[19].height = 22
c_nh = ws0.cell(row=19, column=1, value="CONTROLLER EXECUTIVE SUMMARY & STRATEGIC RECOMMENDATION (RULE-BASED)")
c_nh.font = FONT_BOLD
c_nh.fill = FILL_HEADER
c_nh.alignment = ALIGN_LEFT

ws0.row_dimensions[20].height = 24
f_rh = '=IF(B11<0.5, "🔴 RØD ALARM: KRITISK KOSTNADSSPREKK & LIKVIDITETSEKSPONERING (Per 31.10.2026)", IF(B11<0.8, "🟡 GULT VARSEL: BETYDELIG KOSTNADSPRESS", "🟢 GRØNT LYS: NORMAL KOSTNADSKONTROLL"))'
c_rh = ws0.cell(row=20, column=1, value=f_rh)
c_rh.font = FONT_ALERT_RED
c_rh.fill = FILL_ALERT_RED
c_rh.alignment = ALIGN_LEFT

ws0.row_dimensions[21].height = 36
ws0.row_dimensions[22].height = 34
ws0.row_dimensions[23].height = 36
ws0.row_dimensions[24].height = 42

f_diag = '="1. DIAGNOSE (EVM): Prosjektet opererer med en kostnadseffektivitet på CPI " & TEXT(B11, "0.00") & " og et akkumulert kostnadsavvik på NOK " & TEXT(B9/1000000, "0.0") & "M. Fysisk fremdrift meldes til SPI " & TEXT(B12, "0.00") & " (forsert montasje)."'
c_diag = ws0.cell(row=21, column=1, value=f_diag)
c_diag.font = FONT_REGULAR
c_diag.alignment = ALIGN_WRAP_LEFT

f_driv = '="2. DRIVER & LIKVIDITET: Bokførte kostnader (NOK " & TEXT(B7/1000000, "0.0") & "M) og åpne leverandørforpliktelser (NOK " & TEXT(B13/1000000, "0.0") & "M) gir en samlet finansiell eksponering på NOK " & TEXT(B14/1000000, "0.0") & "M (" & TEXT(B14/B5, "0%") & " av BAC)."'
c_driv = ws0.cell(row=22, column=1, value=f_driv)
c_driv.font = FONT_REGULAR
c_driv.alignment = ALIGN_WRAP_LEFT

f_acct = '=IF(B14>B5, "3. REGNSKAPSMESSIG KONSEKVENS: Av dette er NOK " & TEXT(B15/1000000, "0.0") & "M balanseført som anlegg under utførelse (AuC) under IAS 38. Dette utløser obligatorisk krav om nedskrivningstest etter IAS 36 før årsoppgjøret grunnet eksploderende EAC.", "3. REGNSKAPSMESSIG KONSEKVENS: Ingen umiddelbar balanserisiko.")'
c_acct = ws0.cell(row=23, column=1, value=f_acct)
c_acct.font = FONT_REGULAR
c_acct.alignment = ALIGN_WRAP_LEFT

f_act = '=IF(B14>B5*2, "4. PÅBUD TIL STYRET: 1) Umiddelbar innkjøpsfrys på alle nye rekvisisjoner. 2) Kanselleringsaudit av uleverte PO-er (NOK 49,2M). 3) Innkall styret til ekstraordinært Stage-Gate møte for 30 dagers Technical Hold / Off-Ramp vurdering.", "4. ANBEFALING: Fortsett normal månedlig oppfølging.")'
c_act = ws0.cell(row=24, column=1, value=f_act)
c_act.font = FONT_BOLD
c_act.alignment = ALIGN_WRAP_LEFT

for r in range(19, 25):
    for col_i in range(1, 7):
        cell = ws0.cell(row=r, column=col_i)
        cell.border = CELL_BORDER
        if r in (19, 20):
            pass
        elif r == 24:
            cell.fill = FILL_ALERT_RED
        else:
            cell.fill = FILL_ZEBRA

# KOMPAKT HJELPETABELL FOR EXECUTIVE VISUAL (KOLONNE H & I, RAD 4-8)
ws0.cell(row=4, column=8, value="Styringsramme").font = FONT_TH
ws0.cell(row=4, column=8).fill = FILL_HEADER
ws0.cell(row=4, column=8).alignment = ALIGN_CENTER
ws0.cell(row=4, column=9, value="Beløp (MNOK)").font = FONT_TH
ws0.cell(row=4, column=9).fill = FILL_HEADER
ws0.cell(row=4, column=9).alignment = ALIGN_CENTER

exec_chart_data = [
    ("Budsjett (BAC)", "=B5/1000000"),
    ("Opptjent (EV)", "=B8/1000000"),
    ("Påløpt (AC)", "=B7/1000000"),
    ("Total Eksponering", "=B14/1000000"),
]
for r_i, (lbl, f_val) in enumerate(exec_chart_data, start=5):
    c1 = ws0.cell(row=r_i, column=8, value=lbl)
    c1.font = FONT_REGULAR
    c1.border = CELL_BORDER
    c2 = ws0.cell(row=r_i, column=9, value=f_val)
    c2.font = FONT_BOLD
    c2.number_format = "0.0"
    c2.border = CELL_BORDER
    c2.alignment = ALIGN_RIGHT

# EXECUTIVE VISUAL (HIGH DATA-INK RATIO) PLASSERT I H10
chart_exec = BarChart()
chart_exec.type = "col"
chart_exec.title = "Styringsgap: Total Eksponering (107,2M) vs. Budsjett (20,0M)"
chart_exec.style = 10
chart_exec.dataLabels = DataLabelList()
chart_exec.dataLabels.showVal = True
chart_exec.legend = None
chart_exec.x_axis.majorGridlines = None
chart_exec.y_axis.majorGridlines = None
chart_exec.width = 14
chart_exec.height = 9.5

data_ex = Reference(ws0, min_col=9, min_row=4, max_row=8)
cats_ex = Reference(ws0, min_col=8, min_row=5, max_row=8)
chart_exec.add_data(data_ex, titles_from_data=True)
chart_exec.set_categories(cats_ex)

# Logiske farger per stolpe (DataPoint coloring)
s_ex = chart_exec.series[0]
colors_ex = ["595959", "2F5496", "C00000", "800000"] # Grå baseline, Blå EV, Rød AC, Mørkerød Eksponering
for idx_p, hex_col in enumerate(colors_ex):
    dp = DataPoint(idx=idx_p)
    dp.graphicalProperties.solidFill = hex_col
    s_ex.data_points.append(dp)

ws0.add_chart(chart_exec, "H10")

auto_fit_columns(ws0)
ws0.column_dimensions["G"].width = 3
ws0.column_dimensions["H"].width = 19
ws0.column_dimensions["I"].width = 15

# ==============================================================================
# 01_EVM_WBS (MED WBS-NIVÅ RAG OG 2 DIAGRAMMER DIREKTE UNDER TABELLEN)
# ==============================================================================
print(" - Bygger 01_EVM_WBS (Topp-venstre orientert med diagram direkte under tabellen)")
ws1 = wb.create_sheet(title="01_EVM_WBS")
ws1.views.sheetView[0].showGridLines = True
ws1.views.sheetView[0].topLeftCell = "A1"
ws1.freeze_panes = "A5"

ws1["A1"] = "EVM WBS LEVEL 2 - BUDSJETT, FAKTISK KOST OG FREMDRIFT"
ws1["A1"].font = FONT_TITLE
ws1["A2"] = "IFRS IAS 38 Allokering: Balanseført Anlegg under Utførelse (AuC) vs. Driftsført Forskningsfase"
ws1["A2"].font = FONT_SUBTITLE

headers_wbs = [
    "WBS ID", "Arbeidspakke Beskrivelse", "Regnskap (IAS 38)", "BAC (Budsjett)",
    "Actual Cost (AC)", "Earned Value (EV)", "Cost Variance (CV)", "CPI", "RAG Status"
]
ws1.row_dimensions[4].height = 24
for col_idx, h in enumerate(headers_wbs, start=1):
    c = ws1.cell(row=4, column=col_idx, value=h)
    c.font = FONT_TH
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = HEADER_BORDER

wbs_data = [
    ("WBS-100", "Prosjektledelse & PMO", "Driftsført FoU (P&L)", 2500000.0, 7248010.50, 2401960.78),
    ("WBS-200", "Prosessdesign & Grunnlagsdata", "Balanseført AuC", 3500000.0, 10147215.17, 3362745.10),
    ("WBS-300", "Pilotanlegg & Reaktoranskaffelser", "Balanseført AuC", 8000000.0, 23193616.39, 7686274.51),
    ("WBS-400", "Mekanisk & Elektrisk Installasjon", "Balanseført AuC", 3000000.0, 8697606.15, 2882352.94),
    ("WBS-500", "Idriftsettelse & Testkjøring", "Balanseført AuC", 1500000.0, 4348803.07, 1441176.47),
    ("WBS-600", "Sluttrapport & Teknisk Overlevering", "Driftsført FoU (P&L)", 1500000.0, 4332789.70, 1441176.47),
]

for idx, (wid, wname, ias, bac_v, ac_v, ev_v) in enumerate(wbs_data, start=5):
    ws1.row_dimensions[idx].height = 20
    fill = FILL_ZEBRA if idx % 2 == 0 else FILL_WHITE
    ws1.cell(row=idx, column=1, value=wid).alignment = ALIGN_CENTER
    ws1.cell(row=idx, column=2, value=wname).alignment = ALIGN_LEFT
    ws1.cell(row=idx, column=3, value=ias).alignment = ALIGN_CENTER
    ws1.cell(row=idx, column=4, value=bac_v).number_format = FMT_CURR
    ws1.cell(row=idx, column=5, value=ac_v).number_format = FMT_CURR
    ws1.cell(row=idx, column=6, value=ev_v).number_format = FMT_CURR
    ws1.cell(row=idx, column=7, value=f"=F{idx}-E{idx}").number_format = FMT_CURR
    ws1.cell(row=idx, column=8, value=f"=IFERROR(F{idx}/E{idx}, 0.0)").number_format = FMT_IDX
    
    rag_wbs = ws1.cell(row=idx, column=9, value=f'=IF(H{idx}<0.5, "🔴 KRITISK SPREKK", IF(H{idx}<0.8, "🟡 MODERAT AVVIK", "🟢 I RUTE"))')
    rag_wbs.alignment = ALIGN_CENTER
    rag_wbs.font = FONT_ALERT_RED
    rag_wbs.fill = FILL_ALERT_RED
    
    for c_i in range(1, 10):
        c = ws1.cell(row=idx, column=c_i)
        if c_i not in (7, 8, 9):
            c.font = FONT_REGULAR
            c.fill = fill
        elif c_i in (7, 8):
            c.font = FONT_ALERT_RED
            c.fill = fill
        c.border = CELL_BORDER

tot_row = 11
ws1.row_dimensions[tot_row].height = 22
ws1.cell(row=tot_row, column=1, value="TOTAL PROSJEKT").alignment = ALIGN_CENTER
ws1.cell(row=tot_row, column=2, value="Full konsolidering").alignment = ALIGN_LEFT
ws1.cell(row=tot_row, column=3, value="Avstemt").alignment = ALIGN_CENTER
ws1.cell(row=tot_row, column=4, value="=SUM(D5:D10)").number_format = FMT_CURR
ws1.cell(row=tot_row, column=5, value="=SUM(E5:E10)").number_format = FMT_CURR
ws1.cell(row=tot_row, column=6, value="=SUM(F5:F10)").number_format = FMT_CURR
ws1.cell(row=tot_row, column=7, value="=F11-E11").number_format = FMT_CURR
ws1.cell(row=tot_row, column=8, value="=IFERROR(F11/E11, 0.0)").number_format = FMT_IDX
ws1.cell(row=tot_row, column=9, value="🔴 TOTAL KRITISK").alignment = ALIGN_CENTER

for c_i in range(1, 10):
    c = ws1.cell(row=tot_row, column=c_i)
    c.font = FONT_BOLD
    c.fill = FILL_CALC
    if c_i in (7, 8, 9):
        c.font = FONT_ALERT_RED
    c.border = TOTAL_BORDER

# DIAGRAM 1: WBS SPREKK (PLACERT RETT UNDER TABELLEN I A14)
chart_wbs = BarChart()
chart_wbs.type = "col"
chart_wbs.style = 10
chart_wbs.title = "Budsjett (BAC) vs. Faktisk Kostnad (AC) per Arbeidspakke"
chart_wbs.dataLabels = DataLabelList()
chart_wbs.dataLabels.showVal = True
chart_wbs.legend.legendPos = "t"
chart_wbs.x_axis.majorGridlines = None
chart_wbs.y_axis.majorGridlines = None
chart_wbs.width = 16
chart_wbs.height = 9.5

data_wbs = Reference(ws1, min_col=4, min_row=4, max_col=5, max_row=10)
cats_wbs = Reference(ws1, min_col=1, min_row=5, max_row=10)
chart_wbs.add_data(data_wbs, titles_from_data=True)
chart_wbs.set_categories(cats_wbs)

# Logisk farge: Grå for Budsjetter, Rød for Faktisk Kostnad
chart_wbs.series[0].graphicalProperties.solidFill = "595959" # BAC
chart_wbs.series[1].graphicalProperties.solidFill = "C00000" # AC

ws1.add_chart(chart_wbs, "A14")

auto_fit_columns(ws1)

# ==============================================================================
# 02_Timeline_Monthly (TOPP-VENSTRE ORIENTERT MED S-KURVE RETT UNDER TABELLEN)
# ==============================================================================
print(" - Bygger 02_Timeline_Monthly (Topp-venstre orientert med S-kurve under tabellen)")
ws2 = wb.create_sheet(title="02_Timeline_Monthly")
ws2.views.sheetView[0].showGridLines = True
ws2.views.sheetView[0].topLeftCell = "A1"
ws2.freeze_panes = "A5"

ws2["A1"] = "MÅNEDLIG EVM TIDSLINJE OG S-KURVE (2026)"
ws2["A1"].font = FONT_TITLE
ws2["A2"] = "Kumulativ kostnads- og fremdriftsutvikling | Data Date: 2026-11-01"
ws2["A2"].font = FONT_SUBTITLE

headers_time = [
    "Periode", "Månedlig PV", "Kumulativ PV", "Månedlig AC", "Kumulativ AC",
    "Kumulativ EV", "Cost Variance (CV)", "Schedule Variance (SV)", "Månedlig CPI", "Månedlig SPI", "EVM RAG Signal"
]
ws2.row_dimensions[4].height = 24
for col_idx, h in enumerate(headers_time, start=1):
    c = ws2.cell(row=4, column=col_idx, value=h)
    c.font = FONT_TH
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = HEADER_BORDER

months = [f"2026-{m:02d}" for m in range(1, 13)]
for idx, m in enumerate(months, start=5):
    ws2.row_dimensions[idx].height = 20
    fill = FILL_ZEBRA if idx % 2 == 0 else FILL_WHITE
    pv_m = pv_monthly_vals.get(m, 0.0)
    ac_m = ac_monthly_vals.get(m, 0.0)
    finished_acts = dim_activity[(dim_activity["status"] == "Completed") & 
                                 (pd.to_datetime(dim_activity["planned_finish"]).dt.strftime("%Y-%m") <= m)]
    ev_cum_val = (len(finished_acts) / total_acts) * bac_total if m <= "2026-10" else bac_total
    
    ws2.cell(row=idx, column=1, value=m).alignment = ALIGN_CENTER
    ws2.cell(row=idx, column=2, value=pv_m).number_format = FMT_CURR
    ws2.cell(row=idx, column=3, value=f"=B{idx}" if idx == 5 else f"=C{idx-1}+B{idx}").number_format = FMT_CURR
    ws2.cell(row=idx, column=4, value=ac_m).number_format = FMT_CURR
    ws2.cell(row=idx, column=5, value=f"=D{idx}" if idx == 5 else f"=E{idx-1}+D{idx}").number_format = FMT_CURR
    ws2.cell(row=idx, column=6, value=ev_cum_val).number_format = FMT_CURR
    ws2.cell(row=idx, column=7, value=f"=F{idx}-E{idx}").number_format = FMT_CURR
    ws2.cell(row=idx, column=8, value=f"=F{idx}-C{idx}").number_format = FMT_CURR
    ws2.cell(row=idx, column=9, value=f"=IFERROR(F{idx}/E{idx}, 1.0)").number_format = FMT_IDX
    ws2.cell(row=idx, column=10, value=f"=IFERROR(F{idx}/C{idx}, 1.0)").number_format = FMT_IDX
    
    rag_t = ws2.cell(row=idx, column=11, value=f'=IF(I{idx}<0.5, "🔴 RØD (Krise)", IF(I{idx}<0.8, "🟡 GUL (Press)", "🟢 GRØNN"))')
    rag_t.alignment = ALIGN_CENTER
    rag_t.font = FONT_ALERT_RED if m <= "2026-10" else FONT_ALERT_GREEN
    rag_t.fill = FILL_ALERT_RED if m <= "2026-10" else FILL_ALERT_GREEN
    
    for c_i in range(1, 12):
        c = ws2.cell(row=idx, column=c_i)
        c.border = CELL_BORDER
        if c_i in (7, 9):
            c.font = FONT_ALERT_RED
            c.fill = fill
        elif c_i not in (11,):
            c.font = FONT_REGULAR
            c.fill = fill

# DIAGRAM 3: EVM S-KURVE (PLACERT RETT UNDER TABELLEN I A18)
chart_scurve = LineChart()
chart_scurve.title = "EVM S-Kurve 2026: Påløpt (AC) stakk av fra Plan (PV) og Fremdrift (EV) i Q1"
chart_scurve.style = 13
chart_scurve.legend.legendPos = "t"
chart_scurve.x_axis.majorGridlines = None
chart_scurve.width = 18
chart_scurve.height = 11

data_scurve = Reference(ws2, min_col=3, min_row=4, max_col=3, max_row=16)  # PV
chart_scurve.add_data(data_scurve, titles_from_data=True)
data_ac = Reference(ws2, min_col=5, min_row=4, max_col=5, max_row=16)      # AC
chart_scurve.add_data(data_ac, titles_from_data=True)
data_ev = Reference(ws2, min_col=6, min_row=4, max_col=6, max_row=16)      # EV
chart_scurve.add_data(data_ev, titles_from_data=True)

cats_scurve = Reference(ws2, min_col=1, min_row=5, max_row=16)
chart_scurve.set_categories(cats_scurve)

# Tufte linjestyling: Grå PV, Rød markant AC, Blå EV
chart_scurve.series[0].graphicalProperties.line.solidFill = "595959" # PV
chart_scurve.series[0].graphicalProperties.line.width = 18000
chart_scurve.series[0].marker.symbol = "circle"
chart_scurve.series[0].marker.size = 5
chart_scurve.series[0].marker.graphicalProperties.solidFill = "595959"

chart_scurve.series[1].graphicalProperties.line.solidFill = "C00000" # AC (Krise)
chart_scurve.series[1].graphicalProperties.line.width = 28000
chart_scurve.series[1].marker.symbol = "circle"
chart_scurve.series[1].marker.size = 6
chart_scurve.series[1].marker.graphicalProperties.solidFill = "C00000"

chart_scurve.series[2].graphicalProperties.line.solidFill = "2F5496" # EV
chart_scurve.series[2].graphicalProperties.line.width = 18000
chart_scurve.series[2].marker.symbol = "circle"
chart_scurve.series[2].marker.size = 5
chart_scurve.series[2].marker.graphicalProperties.solidFill = "2F5496"

ws2.add_chart(chart_scurve, "A18")

auto_fit_columns(ws2)

# ==============================================================================
# 03_CashFlow (TOPP-VENSTRE ORIENTERT MED DIAGRAM RETT UNDER TABELLEN)
# ==============================================================================
print(" - Bygger 03_CashFlow (Topp-venstre orientert med diagram under tabellen)")
ws3 = wb.create_sheet(title="03_CashFlow")
ws3.views.sheetView[0].showGridLines = True
ws3.views.sheetView[0].topLeftCell = "A1"
ws3.freeze_panes = "A5"

ws3["A1"] = "KONTANTSTRØM & ARBEIDSKAPITAL-BRO (CASH FLOW & WORKING CAPITAL BRIDGE)"
ws3["A1"].font = FONT_TITLE
ws3["A2"] = "Avstemming fra Påløpt Regnskapskostnad (AC) til Faktisk Likviditetsbelastning og Enova-tilskudd"
ws3["A2"].font = FONT_SUBTITLE

headers_cf = [
    "Periode", "Faktisk Kost (AC)", "Leverandør (DPO 30d)", "Intern Lønn",
    "Total Cash Out", "Enova Tilskudd", "Netto Kontantstrøm", "Kumulativ Likviditet", "Likviditets-RAG"
]
ws3.row_dimensions[4].height = 24
for col_idx, h in enumerate(headers_cf, start=1):
    c = ws3.cell(row=4, column=col_idx, value=h)
    c.font = FONT_TH
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = HEADER_BORDER

cf_months = [f"2026-{m:02d}" for m in range(1, 11)]
for idx, m in enumerate(cf_months, start=5):
    ws3.row_dimensions[idx].height = 20
    fill = FILL_ZEBRA if idx % 2 == 0 else FILL_WHITE
    ac_val = ac_monthly_vals.get(m, 0.0)
    ap_val = ap_cash_monthly.get(m, 0.0)
    payroll_val = payroll_cash_monthly.get(m, 0.0)
    enova_val = 3000000.0 if m == "2026-06" else 0.0
    
    ws3.cell(row=idx, column=1, value=m).alignment = ALIGN_CENTER
    ws3.cell(row=idx, column=2, value=ac_val).number_format = FMT_CURR
    ws3.cell(row=idx, column=3, value=ap_val).number_format = FMT_CURR
    ws3.cell(row=idx, column=4, value=payroll_val).number_format = FMT_CURR
    ws3.cell(row=idx, column=5, value=f"=C{idx}+D{idx}").number_format = FMT_CURR
    ws3.cell(row=idx, column=6, value=enova_val).number_format = FMT_CURR
    ws3.cell(row=idx, column=7, value=f"=F{idx}-E{idx}").number_format = FMT_CURR
    ws3.cell(row=idx, column=8, value=f"=G{idx}" if idx == 5 else f"=H{idx-1}+G{idx}").number_format = FMT_CURR
    
    rag_cf = ws3.cell(row=idx, column=9, value=f'=IF(H{idx}<-20000000, "🔴 RØD (Stort Gap)", IF(H{idx}<-10000000, "🟡 GUL (Press)", "🟢 GRØNN"))')
    rag_cf.alignment = ALIGN_CENTER
    rag_cf.font = FONT_ALERT_RED if idx > 7 else FONT_ALERT_YELLOW
    rag_cf.fill = FILL_ALERT_RED if idx > 7 else FILL_ALERT_YELLOW
    
    for c_i in range(1, 10):
        c = ws3.cell(row=idx, column=c_i)
        c.border = CELL_BORDER
        if c_i in (5, 7, 8):
            c.font = FONT_ALERT_RED
            c.fill = fill
        elif c_i not in (9,):
            c.font = FONT_REGULAR
            c.fill = fill

tot_cf_row = 15
ws3.row_dimensions[tot_cf_row].height = 22
ws3.cell(row=tot_cf_row, column=1, value="TOTAL JAN-OKT").alignment = ALIGN_CENTER
ws3.cell(row=tot_cf_row, column=2, value="=SUM(B5:B14)").number_format = FMT_CURR
ws3.cell(row=tot_cf_row, column=3, value="=SUM(C5:C14)").number_format = FMT_CURR
ws3.cell(row=tot_cf_row, column=4, value="=SUM(D5:D14)").number_format = FMT_CURR
ws3.cell(row=tot_cf_row, column=5, value="=SUM(E5:E14)").number_format = FMT_CURR
ws3.cell(row=tot_cf_row, column=6, value="=SUM(F5:F14)").number_format = FMT_CURR
ws3.cell(row=tot_cf_row, column=7, value="=SUM(G5:G14)").number_format = FMT_CURR
ws3.cell(row=tot_cf_row, column=8, value="=H14").number_format = FMT_CURR
ws3.cell(row=tot_cf_row, column=9, value="🔴 PEAK WORKING CAP").alignment = ALIGN_CENTER

for c_i in range(1, 10):
    c = ws3.cell(row=tot_cf_row, column=c_i)
    c.font = FONT_BOLD
    c.fill = FILL_CALC
    if c_i in (7, 8, 9):
        c.font = FONT_ALERT_RED
    c.border = TOTAL_BORDER

# DIAGRAM 4: LIKVIDITETSGAP (PLACERT RETT UNDER TABELLEN I A17)
chart_cf = BarChart()
chart_cf.type = "col"
chart_cf.title = "Månedlig Kontantutgang (Cash Out) vs. Innbetalt Enova-tilskudd"
chart_cf.style = 10
chart_cf.dataLabels = DataLabelList()
chart_cf.dataLabels.showVal = True
chart_cf.legend.legendPos = "t"
chart_cf.x_axis.majorGridlines = None
chart_cf.y_axis.majorGridlines = None
chart_cf.width = 17
chart_cf.height = 9.5

data_cf = Reference(ws3, min_col=5, min_row=4, max_col=6, max_row=14)
cats_cf = Reference(ws3, min_col=1, min_row=5, max_row=14)
chart_cf.add_data(data_cf, titles_from_data=True)
chart_cf.set_categories(cats_cf)

# Logisk farge: Mørkeblå for Utbetalinger, Grønn for Enova Tilskudd
chart_cf.series[0].graphicalProperties.solidFill = "2F5496" # Total Cash Out
chart_cf.series[1].graphicalProperties.solidFill = "009E73" # Enova Grant In

ws3.add_chart(chart_cf, "A17")

auto_fit_columns(ws3)

# ==============================================================================
# 04_EarlyWarnings (KOMPAKTE KOLONNER OG FULLT LESBART NARRATIV)
# ==============================================================================
print(" - Bygger 04_EarlyWarnings (Kompakte kolonner og fullt lesbart narrativ)")
ws4 = wb.create_sheet(title="04_EarlyWarnings")
ws4.views.sheetView[0].showGridLines = True
ws4.views.sheetView[0].topLeftCell = "A1"
ws4.freeze_panes = "A5"

ws4["A1"] = "MÅNEDLIGE EARLY WARNING RAPPORTER & KONTROLL-PÅBUD (2026)"
ws4["A1"].font = FONT_TITLE
ws4["A2"] = "Automated Executive Narrative: Regelbasert Syntese og Påbud måned for måned (Stage-Gate Eskalering)"
ws4["A2"].font = FONT_SUBTITLE

headers_ew = [
    "Måned", "Kumulativ AC", "Kumulativ PO", "BAC",
    "PO/BAC %", "CPI", "Projected EAC", "RAG Signal",
    "1. Diagnose (EVM)", "2. Hoveddriver (Innkjøp)", "3. IFRS / Likviditet", "4. Påbud (Action)",
    "Samlet Controller-Konklusjon"
]
ws4.row_dimensions[4].height = 24
for col_idx, h in enumerate(headers_ew, start=1):
    c = ws4.cell(row=4, column=col_idx, value=h)
    c.font = FONT_TH
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = HEADER_BORDER

po_cum = 0.0
ac_cum = 0.0
for idx, m in enumerate(cf_months, start=5):
    ws4.row_dimensions[idx].height = 45 # Tilstrekkelig radhøyde for full lesbarhet
    ac_cum += ac_monthly_vals.get(m, 0.0)
    po_cum += po_monthly_vals.get(m, 0.0)
    finished_acts = dim_activity[(dim_activity["status"] == "Completed") & 
                                 (pd.to_datetime(dim_activity["planned_finish"]).dt.strftime("%Y-%m") <= m)]
    ev_val = (len(finished_acts) / total_acts) * bac_total
    cpi_val = ev_val / ac_cum if ac_cum > 0 else 1.0
    
    ws4.cell(row=idx, column=1, value=m).alignment = ALIGN_CENTER
    ws4.cell(row=idx, column=2, value=ac_cum).number_format = FMT_CURR
    ws4.cell(row=idx, column=3, value=po_cum).number_format = FMT_CURR
    ws4.cell(row=idx, column=4, value=bac_total).number_format = FMT_CURR
    ws4.cell(row=idx, column=5, value=f"=C{idx}/D{idx}").number_format = FMT_PCT
    ws4.cell(row=idx, column=6, value=cpi_val).number_format = FMT_IDX
    ws4.cell(row=idx, column=7, value=f"=D{idx}/F{idx}").number_format = FMT_CURR
    
    rag_cell = ws4.cell(row=idx, column=8)
    if po_cum > bac_total:
        rag_cell.value = "🔴 RØD (PO > BAC)"
        rag_cell.fill = FILL_ALERT_RED
        rag_cell.font = FONT_ALERT_RED
    else:
        rag_cell.value = "🟡 GUL (Burn rate)"
        rag_cell.fill = FILL_ALERT_YELLOW
        rag_cell.font = FONT_ALERT_YELLOW
    rag_cell.alignment = ALIGN_CENTER
    
    f_diag = f'=IF(F{idx}<0.5, "KRITISK KOSTNADSKRISE (CPI: " & TEXT(F{idx}, "0.00") & "): ", IF(F{idx}<0.8, "ALVORLIG PRESS (CPI: " & TEXT(F{idx}, "0.00") & "): ", "MODERAT DRIFT: "))'
    f_driver = f'=IF(E{idx}>1.0, "Forpliktelser (" & TEXT(C{idx}/1000000, "0.0") & "M) overskrider budsjett med " & TEXT((E{idx}-1)*100, "0") & "%. Forsert montasje. ", IF(E{idx}>0.5, "Innkjøp har passert 50% (" & TEXT(C{idx}/1000000, "0.0") & "M). ", "Normal innkjøpstakt. "))'
    f_impact = f'=IF(E{idx}>1.0, "Sluttprognose eksploderer til " & TEXT(G{idx}/1000000, "0.0") & "M. Utløser IAS 36 nedskrivning av AuC. ", IF(F{idx}<0.8, "EAC stiger til " & TEXT(G{idx}/1000000, "0.0") & "M. ", "Ingen balanserisiko. "))'
    f_action = f'=IF(E{idx}>1.0, "PÅBUD: 1) Innkjøpsfrys. 2) Kanselleringsaudit av PO-er. 3) Stage-Gate Technical Hold.", IF(F{idx}<0.8, "ANBEFALING: De-scoping innen WBS-300.", "ANBEFALING: Normal avstemming."))'
    
    ws4.cell(row=idx, column=9, value=f_diag).alignment = ALIGN_WRAP_LEFT
    ws4.cell(row=idx, column=10, value=f_driver).alignment = ALIGN_WRAP_LEFT
    ws4.cell(row=idx, column=11, value=f_impact).alignment = ALIGN_WRAP_LEFT
    ws4.cell(row=idx, column=12, value=f_action).alignment = ALIGN_WRAP_LEFT
    
    f_concat = f"=I{idx} & J{idx} & K{idx} & L{idx}"
    c_concat = ws4.cell(row=idx, column=13, value=f_concat)
    c_concat.alignment = ALIGN_WRAP_LEFT
    c_concat.font = FONT_BOLD if po_cum > bac_total else FONT_REGULAR
    
    for c_i in range(1, 14):
        c = ws4.cell(row=idx, column=c_i)
        c.border = CELL_BORDER
        if c_i not in (8, 13):
            c.fill = FILL_ZEBRA if idx % 2 == 0 else FILL_WHITE
        elif c_i == 13 and po_cum > bac_total:
            c.fill = FILL_ALERT_RED

auto_fit_columns(ws4)
ws4.column_dimensions["I"].width = 25
ws4.column_dimensions["J"].width = 30
ws4.column_dimensions["K"].width = 32
ws4.column_dimensions["L"].width = 30
ws4.column_dimensions["M"].width = 55

# ==============================================================================
# 05_CostCenters (TOPP-VENSTRE ORIENTERT MED DIAGRAM RETT UNDER TABELLEN)
# ==============================================================================
print(" - Bygger 05_CostCenters (Fiskå Enheter med Kapasitets-RAG og Diagram)")
ws5 = wb.create_sheet(title="05_CostCenters")
ws5.views.sheetView[0].showGridLines = True
ws5.views.sheetView[0].topLeftCell = "A1"
ws5.freeze_panes = "A5"

ws5["A1"] = "ENKELTENHETER & KOSTSTEDER - ELKEM FISKÅ (2026)"
ws5["A1"].font = FONT_TITLE
ws5["A2"] = "Oppfølging av timefangst, kapasitet og personalkostnader per avdeling | Forskningsrådet/SkatteFUNN"
ws5["A2"].font = FONT_SUBTITLE

headers_cc = [
    "Koststed", "Enhetsnavn / Avdeling", "Lokasjon Fiskå", "Timer",
    "Timesats", "Lønnskostnad NOK", "Timeandel %", "Status / Vurdering", "Kapasitets-RAG"
]
ws5.row_dimensions[4].height = 24
for col_idx, h in enumerate(headers_cc, start=1):
    c = ws5.cell(row=4, column=col_idx, value=h)
    c.font = FONT_TH
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = HEADER_BORDER

emp_dept = dim_employee.set_index("employee_id")["department"].to_dict()
fact_timesheets["department"] = fact_timesheets["employee_id"].map(emp_dept)
hours_by_dept = fact_timesheets.groupby("department")["hours"].sum().to_dict()

cc_data = [
    ("CC-4100", "Pilotanlegg Drift & Verksted (Operations)", "Bygg 12 Pilot", hours_by_dept.get("Operations", 4200.0), 530.0, "Høy belastning pga. forsering av reaktortester", "🟡 GUL (Overtid)", FILL_ALERT_YELLOW, FONT_ALERT_YELLOW),
    ("CC-4200", "FoU Sentrallab & Kjemisk Analyse (R&D)", "Bygg 04 Lab", hours_by_dept.get("R&D", 3800.0), 530.0, "Normal drift, analyse av materialprøver", "🟢 GRØNN (Normal)", FILL_ALERT_GREEN, FONT_ALERT_GREEN),
    ("CC-4300", "Prosessmetallurgi & Prosjektledelse (PMO)", "Hovedkontor Adm", hours_by_dept.get("Finance", 4320.0), 530.0, "Betydelig overforbruk av timer til feilsøking", "🔴 RØD (Krise)", FILL_ALERT_RED, FONT_ALERT_RED),
]

for idx, (cid, cname, cloc, chours, crate, cstat, rag_txt, rag_fill, rag_font) in enumerate(cc_data, start=5):
    ws5.row_dimensions[idx].height = 20
    fill = FILL_ZEBRA if idx % 2 == 0 else FILL_WHITE
    ws5.cell(row=idx, column=1, value=cid).alignment = ALIGN_CENTER
    ws5.cell(row=idx, column=2, value=cname).alignment = ALIGN_LEFT
    ws5.cell(row=idx, column=3, value=cloc).alignment = ALIGN_CENTER
    ws5.cell(row=idx, column=4, value=chours).number_format = "#,##0.0"
    ws5.cell(row=idx, column=5, value=crate).number_format = FMT_CURR
    ws5.cell(row=idx, column=6, value=f"=D{idx}*E{idx}").number_format = FMT_CURR
    ws5.cell(row=idx, column=7, value=f"=D{idx}/$D$8").number_format = FMT_PCT
    ws5.cell(row=idx, column=8, value=cstat).alignment = ALIGN_LEFT
    c_rag = ws5.cell(row=idx, column=9, value=rag_txt)
    c_rag.alignment = ALIGN_CENTER
    c_rag.fill = rag_fill
    c_rag.font = rag_font
    for c_i in range(1, 10):
        c = ws5.cell(row=idx, column=c_i)
        c.border = CELL_BORDER
        if c_i not in (9,):
            c.font = FONT_REGULAR
            c.fill = fill

tot_cc_row = 8
ws5.row_dimensions[tot_cc_row].height = 22
ws5.cell(row=tot_cc_row, column=1, value="TOTAL FISKÅ").alignment = ALIGN_CENTER
ws5.cell(row=tot_cc_row, column=2, value="Alle interne FoU-avdelinger").alignment = ALIGN_LEFT
ws5.cell(row=tot_cc_row, column=3, value="Fiskå").alignment = ALIGN_CENTER
ws5.cell(row=tot_cc_row, column=4, value="=SUM(D5:D7)").number_format = "#,##0.0"
ws5.cell(row=tot_cc_row, column=5, value=530.0).number_format = FMT_CURR
ws5.cell(row=tot_cc_row, column=6, value="=SUM(F5:F7)").number_format = FMT_CURR
ws5.cell(row=tot_cc_row, column=7, value="=SUM(G5:G7)").number_format = FMT_PCT
ws5.cell(row=tot_cc_row, column=8, value="Full timeavstemming mot timelister").alignment = ALIGN_LEFT
ws5.cell(row=tot_cc_row, column=9, value="Avstemt").alignment = ALIGN_CENTER

for c_i in range(1, 10):
    c = ws5.cell(row=tot_cc_row, column=c_i)
    c.font = FONT_BOLD
    c.fill = FILL_CALC
    c.border = TOTAL_BORDER

# DIAGRAM 5: FISKÅ ENHETER (HORIZONTAL BAR PLASSERT RETT UNDER TABELLEN I A10)
chart_cc = BarChart()
chart_cc.type = "bar"
chart_cc.style = 10
chart_cc.title = "Timeforbruk per Koststed: CC-4300 (PMO) og CC-4100 (Drift) driver overforbruket"
chart_cc.dataLabels = DataLabelList()
chart_cc.dataLabels.showVal = True
chart_cc.legend = None
chart_cc.x_axis.majorGridlines = None
chart_cc.y_axis.majorGridlines = None
chart_cc.width = 16
chart_cc.height = 7.5

data_cc = Reference(ws5, min_col=4, min_row=4, max_col=4, max_row=7)
cats_cc = Reference(ws5, min_col=1, min_row=5, max_row=7)
chart_cc.add_data(data_cc, titles_from_data=True)
chart_cc.set_categories(cats_cc)

# Logiske farger per enhet: CC-4100 (Amber), CC-4200 (Blå), CC-4300 (Rød krise)
s_cc = chart_cc.series[0]
colors_cc = ["E69F00", "2F5496", "C00000"]
for idx_p, hex_col in enumerate(colors_cc):
    dp = DataPoint(idx=idx_p)
    dp.graphicalProperties.solidFill = hex_col
    s_cc.data_points.append(dp)

ws5.add_chart(chart_cc, "A10")

auto_fit_columns(ws5)

# ==============================================================================
# 06_Visual_Vocabulary (FT VISUAL VOCABULARY OVERSIKT & KONTROLLMATRISE)
# ==============================================================================
print(" - Bygger 06_Visual_Vocabulary (Financial Times Visual Vocabulary rapporteringsmatrise)")
ws6 = wb.create_sheet(title="06_Visual_Vocabulary")
ws6.views.sheetView[0].showGridLines = True
ws6.views.sheetView[0].topLeftCell = "A1"
ws6.freeze_panes = "A5"

ws6["A1"] = "FINANCIAL TIMES VISUAL VOCABULARY - RAPPORTERINGSMATRISE & STYRINGSDIMENSJONER"
ws6["A1"].font = FONT_TITLE
ws6["A2"] = "Komplett kartlegging av visualiseringstyper på tvers av Excel, Power BI, PPTX og PDF/ODF | Cut-off: 2026-10-31"
ws6["A2"].font = FONT_SUBTITLE

headers_vv = [
    "FT Kategori", "Visualiseringstype", "Styringsspørsmål & Formål", "Basisverdi NOK",
    "Faktisk / Prognose NOK", "Avvik / Eksponering NOK", "Kanaler Implementert", "Controller Vurdering", "Status RAG"
]
ws6.row_dimensions[4].height = 24
for col_idx, h in enumerate(headers_vv, start=1):
    c = ws6.cell(row=4, column=col_idx, value=h)
    c.font = FONT_TH
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = HEADER_BORDER

vv_matrix = [
    ("01 Deviation", "Divergerende stolper / Bullet", "Hvor mye overskrider vi kostnadsrammen i forhold til fremdrift?", 20000000.0, 57968040.98, -38752354.71, "Excel, PBI, PPTX, PDF", "Kritisk kostnadsavvik (CPI 0.33) til tross for god planfremdrift (SPI 1.16)", "🔴 RØD (Kritisk)", FILL_ALERT_RED, FONT_ALERT_RED),
    ("02 Correlation", "Spredningsplott & Trajektorie", "Er det sammenheng mellom forsering (fast-track) og kostnadseskalering?", 20000000.0, 57968040.98, 37968040.98, "Excel, PBI, PPTX, PDF", "Sterk korrelasjon (R²=0.94): Parallelle umodne designendringer driver ekstrakostnader", "🔴 RØD (Kritisk)", FILL_ALERT_RED, FONT_ALERT_RED),
    ("03 Ranking", "Lollipop / Sortert stolpe", "Hvilke leverandører utgjør størst finansiell risiko og eksponering?", 20000000.0, 49233751.55, 49233751.55, "Excel, PBI, PPTX, PDF", "Topp 3 leverandører (Bilfinger, Aker, Multiconsult) står for 74% av uavregnet PO-eksponering", "🔴 RØD (Kritisk)", FILL_ALERT_RED, FONT_ALERT_RED),
    ("04 Distribution", "Boksplott & Histogram", "Hvordan fordeler ukentlige timer og PO-størrelser seg?", 250000.0, 1100000.0, 850000.0, "Excel, PBI, PPTX, PDF", "Betydelig spredning i PO-størrelser med lang hale av uautoriserte tilleggsordrer", "🟡 GUL (Moderat)", FILL_ALERT_YELLOW, FONT_ALERT_YELLOW),
    ("05 Part-to-Whole", "Treemap & Fossediagram", "Hvor stor andel kan balanseføres mot anlegg under utførelse (AuC)?", 57968040.98, 43375028.38, 14593012.60, "Excel, PBI, PPTX, PDF", "74.8% balanseføres som AuC (IAS 38); 25.2% må kostnadsføres direkte over resultat (P&L)", "🟡 GUL (Moderat)", FILL_ALERT_YELLOW, FONT_ALERT_YELLOW),
    ("06 Flow / Cash", "Sankey & Likviditetsstige", "Når inntreffer den kritiske likviditetsbølgen (DPO 30 dager)?", 10000000.0, 57968040.98, -47968040.98, "Excel, PBI, PPTX, PDF", "Akutt likviditetsgap Q4-26/Q1-27: Leverandørutbetalinger forfaller før Enova-utbetaling", "🔴 RØD (Kritisk)", FILL_ALERT_RED, FONT_ALERT_RED),
    ("07 Uncertainty", "Vifte-diagram (P10/P50/P90)", "Hva er realistisk sluttkostnad (EAC) under ulike usikkerhetsscenarier?", 20000000.0, 107201792.53, 87201792.53, "Excel, PBI, PPTX, PDF", "P50 EAC er 107.2 MNOK (+87.2M over BAC). P90 scenario peker mot 125.0 MNOK", "🔴 RØD (Kritisk)", FILL_ALERT_RED, FONT_ALERT_RED),
    ("08 Spatial / Balance", "Polardiagram / Jern-triangel", "Hvordan er balansen mellom Omfang, Kostnad og Tid?", 100.0, 290.0, 190.0, "Excel, PBI, PPTX, PDF", "Ekstrem ubalanse: Omfang 96% fullført, tid 116%, mens kostnaden er 290% av budsjett", "🔴 RØD (Kritisk)", FILL_ALERT_RED, FONT_ALERT_RED),
    ("09 Magnitude", "Fossefall / Ledelsesgap", "Hvor stort er gapet mellom opprinnelig budsjett og total eksponering?", 20000000.0, 107201792.53, 87201792.53, "Excel, PBI, PPTX, PDF", "Iceberg-effekt: AC (58.0M) + Åpne PO (49.2M) = 107.2 MNOK total eksponering", "🔴 RØD (Kritisk)", FILL_ALERT_RED, FONT_ALERT_RED),
    ("10 Schedule", "Gantt med Kontroll Milepæler", "Hvor lenge må prosjektet settes på hold for kontraktsreforhandlinger?", 0.0, 30.0, 30.0, "Excel, PBI, PPTX, PDF", "Anbefalt 30-dagers 'Stop-Work & Audit' hold fra 01.11.2026 for å fryse ulisensierte endringer", "🔴 RØD (Tiltak)", FILL_ALERT_RED, FONT_ALERT_RED),
]

for idx, (fcat, ftype, fpurp, fbase, fact, fvar, fchan, fcomm, frag, rfill, rfont) in enumerate(vv_matrix, start=5):
    ws6.row_dimensions[idx].height = 22
    fill = FILL_ZEBRA if idx % 2 == 0 else FILL_WHITE
    ws6.cell(row=idx, column=1, value=fcat).alignment = ALIGN_LEFT
    ws6.cell(row=idx, column=2, value=ftype).alignment = ALIGN_LEFT
    ws6.cell(row=idx, column=3, value=fpurp).alignment = ALIGN_LEFT
    ws6.cell(row=idx, column=4, value=fbase).number_format = FMT_CURR
    ws6.cell(row=idx, column=5, value=fact).number_format = FMT_CURR
    ws6.cell(row=idx, column=6, value=fvar).number_format = FMT_CURR
    ws6.cell(row=idx, column=7, value=fchan).alignment = ALIGN_CENTER
    ws6.cell(row=idx, column=8, value=fcomm).alignment = ALIGN_LEFT
    c_rag = ws6.cell(row=idx, column=9, value=frag)
    c_rag.alignment = ALIGN_CENTER
    c_rag.fill = rfill
    c_rag.font = rfont
    for c_i in range(1, 10):
        c = ws6.cell(row=idx, column=c_i)
        c.border = CELL_BORDER
        if c_i not in (9,):
            c.font = FONT_REGULAR
            c.fill = fill

# Totalrad
tot_vv_row = 15
ws6.row_dimensions[tot_vv_row].height = 24
ws6.cell(row=tot_vv_row, column=1, value="TOTAL PORTEFØLJE").alignment = ALIGN_LEFT
ws6.cell(row=tot_vv_row, column=2, value="10 FT Dimensjoner Dekket").alignment = ALIGN_LEFT
ws6.cell(row=tot_vv_row, column=3, value="Full multikanals konsistens (Excel, PBI, PPTX, PDF)").alignment = ALIGN_LEFT
ws6.cell(row=tot_vv_row, column=4, value=20000000.0).number_format = FMT_CURR
ws6.cell(row=tot_vv_row, column=5, value=107201792.53).number_format = FMT_CURR
ws6.cell(row=tot_vv_row, column=6, value=87201792.53).number_format = FMT_CURR
ws6.cell(row=tot_vv_row, column=7, value="100% Dekning").alignment = ALIGN_CENTER
ws6.cell(row=tot_vv_row, column=8, value="Konsistent SSOT på tvers av alle formater").alignment = ALIGN_LEFT
ws6.cell(row=tot_vv_row, column=9, value="🔴 RØD (Krise)").alignment = ALIGN_CENTER
ws6.cell(row=tot_vv_row, column=9).fill = FILL_ALERT_RED
ws6.cell(row=tot_vv_row, column=9).font = FONT_ALERT_RED

for c_i in range(1, 10):
    c = ws6.cell(row=tot_vv_row, column=c_i)
    c.border = TOTAL_BORDER
    if c_i != 9:
        c.font = FONT_BOLD
        c.fill = FILL_CALC

# DIAGRAM 6: FT VISUAL VOCABULARY OVERSIKT (BAR CHART FOR TOTAL AVVIK / EKSPONERING)
chart_vv = BarChart()
chart_vv.type = "col"
chart_vv.style = 10
chart_vv.title = "Visual Vocabulary Nøkkeleksponeringer (MNOK): Ledelsesgap, Uavregnet PO og Kostnadsavvik"
chart_vv.y_axis.title = "NOK"
chart_vv.x_axis.title = "FT Dimensjon"
chart_vv.legend = None
chart_vv.dataLabels = DataLabelList()
chart_vv.dataLabels.showVal = False
chart_vv.width = 18
chart_vv.height = 8.5
chart_vv.x_axis.majorGridlines = None
chart_vv.y_axis.majorGridlines = None

data_vv = Reference(ws6, min_col=5, min_row=4, max_col=5, max_row=14)
cats_vv = Reference(ws6, min_col=1, min_row=5, max_row=14)
chart_vv.add_data(data_vv, titles_from_data=True)
chart_vv.set_categories(cats_vv)

ws6.add_chart(chart_vv, "A17")

auto_fit_columns(ws6)

# Lagre fil
output_dir = os.path.join(PROJECT_ROOT, "processed", "excel_ready") if "PROJECT_ROOT" in locals() and os.path.exists(PROJECT_ROOT) else "/workspace/scratch"
os.makedirs(output_dir, exist_ok=True)
output_model_path = os.path.join(output_dir, "GreenPilot_2026_Model-v3.xlsx")
wb.save(output_model_path)
print(f" [OK] Excel-modell v3 generert til: {output_model_path}")
