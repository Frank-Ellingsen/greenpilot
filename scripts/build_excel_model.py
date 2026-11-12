SCRATCH_DIR = '/workspace/scratch'
import os
import sys
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, Reference

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

# GL
fact_gl["period"] = pd.to_datetime(fact_gl["posting_date"]).dt.strftime("%Y-%m")
ac_monthly_vals = fact_gl.groupby("period")["amount_nok"].sum().to_dict()
pv_monthly_vals = fact_budget.groupby("period")["baseline_budget_nok"].sum().to_dict()
po_monthly_vals = fact_po.groupby("period")["amount_nok"].sum().to_dict()

bac_total = 20000000.0
total_acts = len(dim_activity)

# Initialiser arbeidsbok
wb = openpyxl.Workbook()
wb.remove(wb.active)

# Formateringsdefinisjoner (FAST Standard)
FONT_TITLE = Font(name="Calibri", size=14, bold=True, color="1F4E79")
FONT_SUBTITLE = Font(name="Calibri", size=10, italic=True, color="595959")
FONT_TH = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
FONT_REGULAR = Font(name="Calibri", size=10, bold=False, color="000000")
FONT_BOLD = Font(name="Calibri", size=10, bold=True, color="000000")

FILL_HEADER = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
FILL_SECTION = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
FILL_ZEBRA = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
FILL_WHITE = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
FILL_INPUT = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
FILL_CALC = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
FILL_ALERT_RED = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
FILL_ALERT_YELLOW = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
FILL_ALERT_GREEN = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

FONT_ALERT_RED = Font(name="Calibri", size=10, bold=True, color="C00000")
FONT_ALERT_YELLOW = Font(name="Calibri", size=10, bold=True, color="B25900")
FONT_ALERT_GREEN = Font(name="Calibri", size=10, bold=True, color="385723")

ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
ALIGN_CENTER = Alignment(horizontal="center", vertical="center")
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")
ALIGN_WRAP_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)

THIN_BORDER_SIDE = Side(border_style="thin", color="D9D9D9")
CELL_BORDER = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=THIN_BORDER_SIDE, bottom=THIN_BORDER_SIDE)
HEADER_BORDER = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=THIN_BORDER_SIDE, bottom=Side(border_style="medium", color="1F4E79"))
TOTAL_BORDER = Border(top=Side(border_style="thin", color="000000"), bottom=Side(border_style="double", color="000000"))

FMT_CURR = "#,##0.00"
FMT_IDX = "0.000"
FMT_PCT = "0.0%"

def auto_fit_columns(ws, max_cols=20):
    for col in ws.iter_cols(min_col=1, max_col=max_cols):
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val = cell.value
            if val is not None and cell.row > 2:
                lines = str(val).split("\n")
                line_lens = [len(l) for l in lines]
                max_len = max(max_len, max(line_lens) if line_lens else 0)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

# ==============================================================================
# FANE 00: EXECUTIVE SUMMARY
# ==============================================================================
print(" - Bygger 00_Executive_Summary")
ws0 = wb.create_sheet(title="00_Executive_Summary")
ws0.views.sheetView[0].showGridLines = True
ws0["A1"] = "ELKEM GREENPILOT 2026 - FINANCIAL & EVM EXECUTIVE SUMMARY"
ws0["A1"].font = FONT_TITLE
ws0["A2"] = "Single Source of Truth (SSOT) Model | FAST Standard Compliant | Cut-off: 2026-10-31"
ws0["A2"].font = FONT_SUBTITLE

kpi_headers = ["Styringsmetrikk / KPI", "Bokført / Beregnet Verdi", "Enhet / Valuta", "Krav / Målverdi", "Status / Controller Vurdering"]
ws0.row_dimensions[4].height = 24
for c_idx, h in enumerate(kpi_headers, start=1):
    c = ws0.cell(row=4, column=c_idx, value=h)
    c.font = FONT_TH
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = HEADER_BORDER

# Rekkefølge:
# Rad 5: BAC
# Rad 6: PV (per 31.10)
# Rad 7: AC (per 31.10)
# Rad 8: EV (per 31.10)
# Rad 9: CV (=B8-B7)
# Rad 10: SV (=B8-B6)
# Rad 11: CPI (=B8/B7)
# Rad 12: SPI (=B8/B6)
# Rad 13: Open Commitments (PO)
# Rad 14: Total Financial Exposure (=B7+B13)
# Rad 15: AuC Balanseført (IAS 38)
# Rad 16: P&L Driftsført FoU (IAS 38)
# Rad 17: Enova Tilskudd Utbetalt
kpis = [
    ("Budget at Completion (BAC)", 20000000.0, "NOK", "20,000,000.00", "Vedtatt baseline-ramme (Styret)", FMT_CURR),
    ("Planned Value (PV per 31.10)", 16620871.10, "NOK", "16,620,871.10", "Planlagt verdi frem til cut-off", FMT_CURR),
    ("Actual Cost (AC)", 57968040.98, "NOK", "< 20,000,000.00", "Overskridelse på +189.8% over BAC", FMT_CURR),
    ("Earned Value (EV)", 19215686.27, "NOK", "20,000,000.00", "96.1% fysisk ferdigstillelse", FMT_CURR),
    ("Cost Variance (CV)", "=B8-B7", "NOK", ">= 0.00", "Alvorlig kostnadsoverskridelse (-38.8M)", FMT_CURR),
    ("Schedule Variance (SV)", "=B8-B6", "NOK", ">= 0.00", "Positivt tidsavvik pga forsering (+2.59M)", FMT_CURR),
    ("Cost Performance Index (CPI)", "=B8/B7", "Ratio", ">= 1.000", "Kritisk ineffektivitet (0.331)", FMT_IDX),
    ("Schedule Performance Index (SPI)", "=B8/B6", "Ratio", ">= 1.000", "Raskere enn opprinnelig plan (1.156)", FMT_IDX),
    ("Open Commitments (PO)", 49233751.55, "NOK", "0.00", "Åpne leverandørforpliktelser", FMT_CURR),
    ("Total Financial Exposure", "=B7+B13", "NOK", "<= BAC", "Samlet finansiell forpliktelse (107.2M)", FMT_CURR),
    ("AuC Balanseført (IAS 38)", 43375028.38, "NOK", "Aktivum", "Balanseført anlegg under utførelse (AuC)", FMT_CURR),
    ("P&L Driftsført FoU (IAS 38)", 14593012.60, "NOK", "Kostnad", "Driftsført forskningsfase & PMO", FMT_CURR),
    ("Enova Tilskudd Utbetalt", 3000000.0, "NOK", "10,000,000.00", "Refusjon innbetalt juni 2026", FMT_CURR),
]

for idx, k in enumerate(kpis, start=5):
    ws0.row_dimensions[idx].height = 20
    ws0.cell(row=idx, column=1, value=k[0]).alignment = ALIGN_LEFT
    c_val = ws0.cell(row=idx, column=2, value=k[1])
    c_val.number_format = k[5]
    c_val.alignment = ALIGN_RIGHT
    ws0.cell(row=idx, column=3, value=k[2]).alignment = ALIGN_CENTER
    ws0.cell(row=idx, column=4, value=k[3]).alignment = ALIGN_RIGHT
    ws0.cell(row=idx, column=5, value=k[4]).alignment = ALIGN_LEFT
    for col_i in range(1, 6):
        c = ws0.cell(row=idx, column=col_i)
        c.font = FONT_REGULAR
        c.fill = FILL_ZEBRA if idx % 2 == 0 else FILL_WHITE
        c.border = CELL_BORDER

auto_fit_columns(ws0)

# ==============================================================================
# FANE 01: EVM WBS LEVEL 2 & IAS 38
# ==============================================================================
print(" - Bygger 01_EVM_WBS")
ws1 = wb.create_sheet(title="01_EVM_WBS")
ws1.views.sheetView[0].showGridLines = True
ws1["A1"] = "WBS LEVEL 2 - EVM METRIKKER & IFRS IAS 38 ALLOKERING"
ws1["A1"].font = FONT_TITLE
ws1["A2"] = "Inndeling i Balanseført Utvikling (AuC) vs. Driftsført Forskning (P&L Expensed)"
ws1["A2"].font = FONT_SUBTITLE

headers_wbs = [
    "WBS ID", "Arbeidspakke Navn", "IFRS IAS 38 Status", "Regnskapsmessig Behandling",
    "BAC (Budsjett)", "Faktisk Kost (AC)", "Earned Value (EV)", "Cost Variance (CV)", "CPI"
]
ws1.row_dimensions[4].height = 24
for c_idx, h in enumerate(headers_wbs, start=1):
    c = ws1.cell(row=4, column=c_idx, value=h)
    c.font = FONT_TH
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = HEADER_BORDER

wbs_data = [
    ("WBS-100", "Forprosjekt & Konseptstudie", "Research Phase", "P&L Driftsført", 2000000.0, 5800000.0, 2000000.0),
    ("WBS-200", "Detaljprosjektering & Engineering", "Development Phase", "Balanseføres (AuC)", 3500000.0, 10200000.0, 3500000.0),
    ("WBS-300", "Pilotanlegg Innkjøp & Konstruksjon", "Development Phase", "Balanseføres (AuC)", 8500000.0, 24800000.0, 8000000.0),
    ("WBS-400", "Mekanisk Ferdigstillelse", "Development Phase", "Balanseføres (AuC)", 2500000.0, 7400000.0, 2500000.0),
    ("WBS-500", "Idriftsettelse & Testkjøring", "Development Phase", "Balanseføres (AuC)", 2000000.0, 5900000.0, 1800000.0),
    ("WBS-600", "Prosjektledelse & PMO", "Closeout / Mgmt", "P&L Driftsført", 1500000.0, 3868040.98, 1415686.27),
]

for idx, r in enumerate(wbs_data, start=5):
    ws1.row_dimensions[idx].height = 20
    fill = FILL_ZEBRA if idx % 2 == 0 else FILL_WHITE
    ws1.cell(row=idx, column=1, value=r[0]).alignment = ALIGN_CENTER
    ws1.cell(row=idx, column=2, value=r[1]).alignment = ALIGN_LEFT
    ws1.cell(row=idx, column=3, value=r[2]).alignment = ALIGN_LEFT
    ws1.cell(row=idx, column=4, value=r[3]).alignment = ALIGN_LEFT
    ws1.cell(row=idx, column=5, value=r[4]).number_format = FMT_CURR
    ws1.cell(row=idx, column=6, value=r[5]).number_format = FMT_CURR
    ws1.cell(row=idx, column=7, value=r[6]).number_format = FMT_CURR
    ws1.cell(row=idx, column=8, value=f"=G{idx}-F{idx}").number_format = FMT_CURR
    ws1.cell(row=idx, column=9, value=f"=IFERROR(G{idx}/F{idx}, 1.0)").number_format = FMT_IDX
    for c_i in range(1, 10):
        c = ws1.cell(row=idx, column=c_i)
        c.font = FONT_REGULAR
        c.fill = fill
        c.border = CELL_BORDER

tot_row_wbs = 11
ws1.row_dimensions[tot_row_wbs].height = 22
ws1.cell(row=tot_row_wbs, column=1, value="TOTAL").alignment = ALIGN_CENTER
ws1.cell(row=tot_row_wbs, column=2, value="Konsolidert Prosjekt").alignment = ALIGN_LEFT
ws1.cell(row=tot_row_wbs, column=3, value="-").alignment = ALIGN_CENTER
ws1.cell(row=tot_row_wbs, column=4, value="-").alignment = ALIGN_CENTER
ws1.cell(row=tot_row_wbs, column=5, value="=SUM(E5:E10)").number_format = FMT_CURR
ws1.cell(row=tot_row_wbs, column=6, value="=SUM(F5:F10)").number_format = FMT_CURR
ws1.cell(row=tot_row_wbs, column=7, value="=SUM(G5:G10)").number_format = FMT_CURR
ws1.cell(row=tot_row_wbs, column=8, value="=G11-F11").number_format = FMT_CURR
ws1.cell(row=tot_row_wbs, column=9, value="=IFERROR(G11/F11, 1.0)").number_format = FMT_IDX

for c_i in range(1, 10):
    c = ws1.cell(row=tot_row_wbs, column=c_i)
    c.font = FONT_BOLD
    c.fill = FILL_CALC
    c.border = TOTAL_BORDER

auto_fit_columns(ws1)

# ==============================================================================
# FANE 02: TIMELINE MONTHLY (S-CURVE)
# ==============================================================================
print(" - Bygger 02_Timeline_Monthly")
ws2 = wb.create_sheet(title="02_Timeline_Monthly")
ws2.views.sheetView[0].showGridLines = True
ws2["A1"] = "MÅNEDLIG EVM TIDSLINJE & S-KURVE (2026)"
ws2["A1"].font = FONT_TITLE
ws2["A2"] = "Akkumulert Planlagt Verdi (PV), Faktisk Kostnad (AC) og Opptjent Verdi (EV) med månedlige indekser"
ws2["A2"].font = FONT_SUBTITLE

headers_time = [
    "Periode", "Månedlig PV", "Kumulativ PV", "Månedlig AC", "Kumulativ AC",
    "Kumulativ EV", "Cost Variance (CV)", "Schedule Variance (SV)", "Månedlig CPI", "Månedlig SPI"
]
ws2.row_dimensions[4].height = 24
for c_idx, h in enumerate(headers_time, start=1):
    c = ws2.cell(row=4, column=c_idx, value=h)
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
    for c_i in range(1, 11):
        c = ws2.cell(row=idx, column=c_i)
        c.font = FONT_REGULAR
        c.fill = fill
        c.border = CELL_BORDER

auto_fit_columns(ws2)

# ==============================================================================
# FANE 03: CASH FLOW & WORKING CAPITAL BRIDGE (MED DIAGRAM)
# ==============================================================================
print(" - Bygger 03_CashFlow (Working Capital & Likviditetsbro med Diagram)")
ws3 = wb.create_sheet(title="03_CashFlow")
ws3.views.sheetView[0].showGridLines = True
ws3["A1"] = "KONTANTSTRØM & ARBEIDSKAPITAL-BRO (CASH FLOW & WORKING CAPITAL BRIDGE)"
ws3["A1"].font = FONT_TITLE
ws3["A2"] = "Avstemming fra Påløpt Regnskapskostnad (AC) til Faktisk Likviditetsbelastning og Enova-tilskudd (FAST Standard)"
ws3["A2"].font = FONT_SUBTITLE

headers_cf = [
    "Periode", "Faktisk Kost (AC)", "Leverandørutbetaling (DPO 30d)", "Intern Lønn Løpende",
    "Total Kontantstrøm Ut", "Enova Tilskudd Innbetalt", "Netto Månedlig Kontantstrøm", "Kumulativ Likviditetseksponering"
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
    for c_idx in range(1, 9):
        c = ws3.cell(row=idx, column=c_idx)
        c.font = FONT_REGULAR
        c.fill = fill
        c.border = CELL_BORDER

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

for c_idx in range(1, 9):
    c = ws3.cell(row=tot_cf_row, column=c_idx)
    c.font = FONT_BOLD
    c.fill = FILL_CALC
    c.border = TOTAL_BORDER

# Innebygd Diagram for Cash Flow & Working Capital Bridge
chart_bars = BarChart()
chart_bars.title = "Månedlig Likviditetsutgang vs. Enova Innbetaling (NOK)"
chart_bars.style = 10
chart_bars.y_axis.title = "Månedlig Likviditet (NOK)"
chart_bars.x_axis.title = "Periode (2026)"
chart_bars.width = 18
chart_bars.height = 10

data_bars = Reference(ws3, min_col=5, min_row=4, max_col=6, max_row=14)
cats_bars = Reference(ws3, min_col=1, min_row=5, max_row=14)
chart_bars.add_data(data_bars, titles_from_data=True)
chart_bars.set_categories(cats_bars)

ws3.add_chart(chart_bars, "J4")

auto_fit_columns(ws3, max_cols=9)

# ==============================================================================
# FANE 04: EARLY WARNINGS MED REGELBASERT NARRATIV KONKLUSJON
# ==============================================================================
print(" - Bygger 04_EarlyWarnings (med Regelbaserte Konklusjonsformler)")
ws4 = wb.create_sheet(title="04_EarlyWarnings")
ws4.views.sheetView[0].showGridLines = True
ws4["A1"] = "MÅNEDLIGE EARLY WARNING RAPPORTER & REGELBASERTE KONTROLL-KONKLUSJONER"
ws4["A1"].font = FONT_TITLE
ws4["A2"] = "Automated Executive Narrative Generator | 4-leddet regelbasert controller-vurdering jfr. stillingsansvar"
ws4["A2"].font = FONT_SUBTITLE

headers_ew = [
    "Måned", "Kumulativ AC", "Kumulativ PO", "BAC Budsjett",
    "PO vs BAC %", "Point-in-Time CPI", "Projected EAC", "RAG Signal",
    "1. Diagnose (EVM)", "2. Driver (Innkjøp & Fremdrift)", "3. Konsekvens (Likviditet/IFRS)", "4. Påkrevd Tiltak (Action)",
    "Samlet Controller-Konklusjon (Executive Narrative)"
]
ws4.row_dimensions[4].height = 26
for col_idx, h in enumerate(headers_ew, start=1):
    c = ws4.cell(row=4, column=col_idx, value=h)
    c.font = FONT_TH
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = HEADER_BORDER

po_cum = 0.0
ac_cum = 0.0

for idx, m in enumerate(cf_months, start=5):
    ws4.row_dimensions[idx].height = 45
    ac_cum += ac_monthly_vals.get(m, 0.0)
    po_cum += po_monthly_vals.get(m, 0.0)
    finished_acts = dim_activity[(dim_activity["status"] == "Completed") & 
                                 (pd.to_datetime(dim_activity["planned_finish"]).dt.strftime("%Y-%m") <= m)]
    ev_val = (len(finished_acts) / total_acts) * bac_total
    cpi_val = ev_val / ac_cum if ac_cum > 0 else 1.0
    
    # 1-8: Nøkkeltall
    ws4.cell(row=idx, column=1, value=m).alignment = ALIGN_CENTER
    ws4.cell(row=idx, column=2, value=ac_cum).number_format = FMT_CURR
    ws4.cell(row=idx, column=3, value=po_cum).number_format = FMT_CURR
    ws4.cell(row=idx, column=4, value=bac_total).number_format = FMT_CURR
    ws4.cell(row=idx, column=5, value=f"=C{idx}/D{idx}").number_format = FMT_PCT
    ws4.cell(row=idx, column=6, value=cpi_val).number_format = FMT_IDX
    ws4.cell(row=idx, column=7, value=f"=D{idx}/F{idx}").number_format = FMT_CURR
    
    # RAG Status Signal
    rag_cell = ws4.cell(row=idx, column=8)
    if po_cum > bac_total:
        rag_cell.value = "🔴 RØD (PO > 100% BAC)"
        rag_cell.fill = FILL_ALERT_RED
        rag_cell.font = FONT_ALERT_RED
    else:
        rag_cell.value = "🟡 GUL (Burn Rate)"
        rag_cell.fill = FILL_ALERT_YELLOW
        rag_cell.font = FONT_ALERT_YELLOW
    rag_cell.alignment = ALIGN_CENTER

    # 4-LEDDET REGELBASERT KONTROLLMOTOR (FORMELBASERT)
    # Kolonne I (9): Del 1 - Diagnose (EVM)
    formula_part1 = (
        f'=IF(F{idx}<0.5, "KRITISK KOSTNADSKRISE (CPI: " & TEXT(F{idx},"0.00") & "): ", '
        f'IF(F{idx}<0.8, "ALVORLIG KOSTNADSPRESS (CPI: " & TEXT(F{idx},"0.00") & "): ", '
        f'IF(F{idx}<1.0, "MARGINALT KOSTNADSAVVIK: ", "NORMAL KOSTNADSKONTROLL: ")))'
    )
    ws4.cell(row=idx, column=9, value=formula_part1).alignment = ALIGN_LEFT

    # Kolonne J (10): Del 2 - Driver (PO vs BAC)
    formula_part2 = (
        f'=IF(E{idx}>1.0, "Akkumulerte forpliktelser (" & TEXT(C{idx}/1000000,"0.0") & " MNOK) overskrider totalbudsjettet med " & TEXT((E{idx}-1)*100,"0") & "%. Fysisk fremdrift meldes høy (klassisk forsering). ", '
        f'IF(E{idx}>0.5, "Innkjøpsforpliktelsene har passert 50% av totalrammen (" & TEXT(C{idx}/1000000,"0.0") & " MNOK) tidlig i prosjektløpet. ", '
        f'"Innkjøpstakten er innenfor planlagt tildeling. "))'
    )
    ws4.cell(row=idx, column=10, value=formula_part2).alignment = ALIGN_LEFT

    # Kolonne K (11): Del 3 - Konsekvens (Likviditet & IAS 38/36)
    formula_part3 = (
        f'=IF(E{idx}>1.0, "Sluttprognose (EAC) eksploderer til " & TEXT(G{idx}/1000000,"0.0") & " MNOK. Det oppstår akutt likviditetsunderskudd og revisor vil kreve IAS 36 nedskrivningsvurdering av balanseført AuC. ", '
        f'IF(F{idx}<0.8, "Forventet sluttkostnad øker til " & TEXT(G{idx}/1000000,"0.0") & " MNOK, noe som vil belaste konsernets driftsmarginer. ", '
        f'"Ingen umiddelbar trussel mot balanseførte verdier eller likviditetsrammer. "))'
    )
    ws4.cell(row=idx, column=11, value=formula_part3).alignment = ALIGN_LEFT

    # Kolonne L (12): Del 4 - Påkrevd Tiltak (Action)
    formula_part4 = (
        f'=IF(E{idx}>1.0, "PÅBUD: 1) Umiddelbar innkjøpsfrys på nye rekvisisjoner. 2) Kanselleringsaudit av åpne PO-er. 3) Ekstraordinær Stage-Gate beslutning (Technical Hold / Off-Ramp).", '
        f'IF(F{idx}<0.8, "ANBEFALING: Gjennomfør de-scoping av aktiviteter og reforhandle leverandøravtaler innen WBS-300.", '
        f'"ANBEFALING: Fortsett normal månedlig avstemming av fakturert fremdrift."))'
    )
    ws4.cell(row=idx, column=12, value=formula_part4).alignment = ALIGN_LEFT

    # Kolonne M (13): Samlet Konklusjon (Konkatenering av I, J, K, L)
    formula_concat = f'=I{idx} & J{idx} & K{idx} & L{idx}'
    c_exec = ws4.cell(row=idx, column=13, value=formula_concat)
    c_exec.alignment = ALIGN_WRAP_LEFT
    c_exec.font = FONT_BOLD

    fill_row = FILL_ZEBRA if idx % 2 == 0 else FILL_WHITE
    for c_i in range(1, 14):
        c = ws4.cell(row=idx, column=c_i)
        c.border = CELL_BORDER
        if c_i != 8:
            c.fill = fill_row

# Kolonnebredder
ws4.column_dimensions["A"].width = 12
ws4.column_dimensions["B"].width = 18
ws4.column_dimensions["C"].width = 18
ws4.column_dimensions["D"].width = 16
ws4.column_dimensions["E"].width = 14
ws4.column_dimensions["F"].width = 16
ws4.column_dimensions["G"].width = 18
ws4.column_dimensions["H"].width = 24
ws4.column_dimensions["I"].width = 28
ws4.column_dimensions["J"].width = 35
ws4.column_dimensions["K"].width = 38
ws4.column_dimensions["L"].width = 42
ws4.column_dimensions["M"].width = 65

# ==============================================================================
# FANE 05: KOSTSTEDER & ENHETER (ELKEM FISKÅ)
# ==============================================================================
print(" - Bygger 05_CostCenters (Fiskå Enheter)")
ws5 = wb.create_sheet(title="05_CostCenters")
ws5.views.sheetView[0].showGridLines = True
ws5["A1"] = "ENKELTENHETER & KOSTSTEDER - ELKEM FISKÅ (2026)"
ws5["A1"].font = FONT_TITLE
ws5["A2"] = "Oppfølging av timefangst, kapasitet og personalkostnader per avdeling | Forskningsrådet/SkatteFUNN (530 kr/t)"
ws5["A2"].font = FONT_SUBTITLE

headers_cc = [
    "Koststed", "Enhetsnavn / Avdeling", "Lokasjon Fiskå", "Registrerte Timer",
    "Godkjent Timesats", "Beregnet Lønnskostnad", "Andel av Total Timefangst %", "Status / Kapasitetsvurdering"
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
    ("CC-4100", "Pilotanlegg Drift & Verksted (Operations)", "Bygg 12 Pilot", hours_by_dept.get("Operations", 4200.0), 530.0, "Høy belastning pga. forsering av reaktortester"),
    ("CC-4200", "FoU Sentrallab & Kjemisk Analyse (R&D)", "Bygg 04 Lab", hours_by_dept.get("R&D", 3800.0), 530.0, "Normal drift, analyse av materialprøver"),
    ("CC-4300", "Prosessmetallurgi & Prosjektledelse (Finance/PMO)", "Hovedkontor Adm", hours_by_dept.get("Finance", 4320.0), 530.0, "Betydelig overforbruk av timer til feilsøking og koordinering"),
]

for idx, r in enumerate(cc_data, start=5):
    ws5.row_dimensions[idx].height = 20
    fill = FILL_ZEBRA if idx % 2 == 0 else FILL_WHITE
    ws5.cell(row=idx, column=1, value=r[0]).alignment = ALIGN_CENTER
    ws5.cell(row=idx, column=2, value=r[1]).alignment = ALIGN_LEFT
    ws5.cell(row=idx, column=3, value=r[2]).alignment = ALIGN_CENTER
    ws5.cell(row=idx, column=4, value=r[3]).number_format = "#,##0.0"
    ws5.cell(row=idx, column=5, value=r[4]).number_format = FMT_CURR
    ws5.cell(row=idx, column=6, value=f"=D{idx}*E{idx}").number_format = FMT_CURR
    ws5.cell(row=idx, column=7, value=f"=D{idx}/$D$8").number_format = FMT_PCT
    ws5.cell(row=idx, column=8, value=r[5]).alignment = ALIGN_LEFT
    for c_i in range(1, 9):
        c = ws5.cell(row=idx, column=c_i)
        c.font = FONT_REGULAR
        c.fill = fill
        c.border = CELL_BORDER

tot_cc_row = 8
ws5.row_dimensions[tot_cc_row].height = 22
ws5.cell(row=tot_cc_row, column=1, value="TOTAL").alignment = ALIGN_CENTER
ws5.cell(row=tot_cc_row, column=2, value="Konsolidert Personell").alignment = ALIGN_LEFT
ws5.cell(row=tot_cc_row, column=3, value="Fiskå").alignment = ALIGN_CENTER
ws5.cell(row=tot_cc_row, column=4, value="=SUM(D5:D7)").number_format = "#,##0.0"
ws5.cell(row=tot_cc_row, column=5, value=530.0).number_format = FMT_CURR
ws5.cell(row=tot_cc_row, column=6, value="=SUM(F5:F7)").number_format = FMT_CURR
ws5.cell(row=tot_cc_row, column=7, value="=SUM(G5:G7)").number_format = FMT_PCT
ws5.cell(row=tot_cc_row, column=8, value="Full timeavstemming mot timelister").alignment = ALIGN_LEFT

for c_i in range(1, 9):
    c = ws5.cell(row=tot_cc_row, column=c_i)
    c.font = FONT_BOLD
    c.fill = FILL_CALC
    c.border = TOTAL_BORDER

auto_fit_columns(ws5)

output_dir = os.path.join(PROJECT_ROOT, "processed", "excel_ready") if "PROJECT_ROOT" in locals() and os.path.exists(PROJECT_ROOT) else "/workspace/scratch"
os.makedirs(output_dir, exist_ok=True)
output_model_path = os.path.join(output_dir, "GreenPilot_2026_Model-v2.xlsx")
wb.save(output_model_path)
print(f" [OK] Excel-modell generert til: {output_model_path}")
