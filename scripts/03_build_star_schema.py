# Full Pipeline Script: 03_build_star_schema.py (v5)


import os
import sys
import pandas as pd
import numpy as np

# ==============================================================================
# STEG 3 (v5): STAR SCHEMA & ENRICHED GOLD LAYER (GREENPILOT 2026 / ELKEM)
# Inkluderer:
#  1. Dim_WBS: parent_wbs_id og IFRS IAS 38 metadata (AuC vs. Drift)
#  2. Dim_CostCenter & Dim_Employee: Enkeltenheter ved Elkem Fiskå (CC-4100, CC-4200, CC-4300)
#  3. Dim_Activity: progress_pct, duration og statusgruppering
#  4. Fact_PurchaseOrders: invoiced_nok, open_commitment_nok og status
#  5. Fact_GLActuals: Valutajustering til NOK og direkte IAS 38-allokering
#  6. tbl_CashFlow_Bridge: Arbeidskapital, DPO (30 dager), lønn og Enova-tilskudd
#  7. tbl_Monthly_EarlyWarnings: 10 månedlige rapporter uten bakspeil (PoV Jan-Okt)
#  8. Fact_FinancialEVM_Unified_Flat: Flat konsolidert kube for Power BI og Excel
# ==============================================================================

CURRENT_DIR = os.getcwd()
if os.path.exists(os.path.join(CURRENT_DIR, "data")):
    BASE_DIR = CURRENT_DIR
elif os.path.exists(os.path.join(os.path.dirname(CURRENT_DIR), "data")):
    BASE_DIR = os.path.dirname(CURRENT_DIR)
elif os.path.exists(r"C:\Users\frank\OneDrive\Elkem\data"):
    BASE_DIR = r"C:\Users\frank\OneDrive\Elkem"
elif os.path.exists("/workspace/knowledge"):
    BASE_DIR = "/workspace"
else:
    BASE_DIR = CURRENT_DIR

CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")
STAGING_DIR = os.path.join(BASE_DIR, "data", "staging")
RAW_DIR = "/workspace/knowledge" if os.path.exists("/workspace/knowledge") else os.path.join(BASE_DIR, "data", "raw")
STAR_SCHEMA_DIR = os.path.join(BASE_DIR, "processed", "star_schema")
BUSINESS_READY_DIR = os.path.join(BASE_DIR, "processed", "business_ready")
EXCEL_READY_DIR = os.path.join(BASE_DIR, "processed", "excel_ready")

os.makedirs(STAR_SCHEMA_DIR, exist_ok=True)
os.makedirs(BUSINESS_READY_DIR, exist_ok=True)
os.makedirs(EXCEL_READY_DIR, exist_ok=True)

print("=" * 80)
print("=== STEG 3 (v5): STAR SCHEMA & ENRICHED GOLD LAYER (GREENPILOT 2026) ===")
print("=" * 80)

def read_source(fname: str) -> pd.DataFrame:
    for folder in [CLEANED_DIR, STAGING_DIR, RAW_DIR]:
        path = os.path.join(folder, fname)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8-sig") as f:
                first_line = f.readline()
                delimiter = ";" if ";" in first_line else ","
            df = pd.read_csv(path, sep=delimiter, encoding="utf-8-sig")
            df.columns = [c.strip().strip('"').strip("'").lstrip('\ufeff') for c in df.columns]
            return df
    raise FileNotFoundError(f"Finner ikke tabell verken i cleaned, staging eller raw: {fname}")

# ------------------------------------------------------------------------------
# 1. HENT MASTERDATA OG TRANSAKSJONER (KILDER A)
# ------------------------------------------------------------------------------
print("--- 1. Leser kildedata fra forsystemer ---")
dim_project = read_source("00_project_master.csv")
dim_wbs = read_source("01_master_wbs.csv")
dim_cost_element = read_source("02_master_cost_elements.csv")
dim_vendor = read_source("04_erp_vendor_master.csv")
dim_employee = read_source("16_hr_employee_master.csv")
dim_activity = read_source("12_primavera_activities.csv")
dim_resource = read_source("14_primavera_resources.csv")

fact_budget = read_source("05_erp_budget_baseline.csv")
fact_gl = read_source("10_erp_gl_actuals.csv")
fact_timesheets = read_source("18_hr_timesheets.csv")
fact_po = read_source("06_erp_purchase_orders.csv")
fact_gr = read_source("07_erp_goods_receipts.csv")
fact_ap = read_source("08_erp_ap_invoices.csv")
fact_journals = read_source("09_erp_journals.csv")
fact_change_orders = read_source("11_erp_change_orders.csv")
fact_capacity = read_source("17_hr_capacity_calendar.csv")
fact_resource_assignments = read_source("15_primavera_resource_assignments.csv")
df_fx = read_source("03_erp_fx_rates.csv")

# ------------------------------------------------------------------------------
# 2. BERIKELSER FOR DIMENSJONER
# ------------------------------------------------------------------------------
print("--- 2. Beriker Dimensjoner ---")

# A. Dim_WBS: parent_wbs_id og IFRS IAS 38 klassifisering
if "parent_wbs_id" not in dim_wbs.columns:
    dim_wbs["parent_wbs_id"] = dim_wbs["project_id"]
else:
    dim_wbs["parent_wbs_id"] = dim_wbs["parent_wbs_id"].fillna("").astype(str).str.strip()
    dim_wbs["parent_wbs_id"] = dim_wbs.apply(
        lambda r: r["project_id"] if r["parent_wbs_id"] in ["", "nan", "None"] else r["parent_wbs_id"], 
        axis=1
    )

ias38_meta = {
    "WBS-100": ("Research",    "EXPENSE",    "P&L Operating Expense", False),
    "WBS-200": ("Development", "CAPITALIZE", "Balance Sheet (AuC)",  True),
    "WBS-300": ("Development", "CAPITALIZE", "Balance Sheet (AuC)",  True),
    "WBS-400": ("Development", "CAPITALIZE", "Balance Sheet (AuC)",  True),
    "WBS-500": ("Development", "CAPITALIZE", "Balance Sheet (AuC)",  True),
    "WBS-600": ("Closeout",    "EXPENSE",    "P&L Operating Expense", False),
}

dim_wbs["ias38_phase"] = dim_wbs["wbs_id"].map(lambda x: ias38_meta.get(x, ("Unknown", "", "", ""))[0])
dim_wbs["ias38_treatment"] = dim_wbs["wbs_id"].map(lambda x: ias38_meta.get(x, ("", "EXPENSE", "", ""))[1])
dim_wbs["accounting_bucket"] = dim_wbs["wbs_id"].map(lambda x: ias38_meta.get(x, ("", "", "P&L Operating Expense", ""))[2])
dim_wbs["eligible_auc"] = dim_wbs["wbs_id"].map(lambda x: ias38_meta.get(x, ("", "", "", False))[3])

# B. Dim_Activity: progress_pct, duration, activity_status_group
status_progress_map = {"Completed": 100, "In Progress": 50, "Not Started": 0}
status_order_map = {"Completed": "1 - Completed", "In Progress": "2 - In Progress", "Not Started": "3 - Not Started"}
dim_activity["progress_pct"] = dim_activity["status"].map(lambda s: status_progress_map.get(s, 0)).astype(int)
dim_activity["activity_status_group"] = dim_activity["status"].map(lambda s: status_order_map.get(s, "4 - Other"))
dim_activity["planned_start_dt"] = pd.to_datetime(dim_activity["planned_start"])
dim_activity["planned_finish_dt"] = pd.to_datetime(dim_activity["planned_finish"])
dim_activity["planned_duration_days"] = ((dim_activity["planned_finish_dt"] - dim_activity["planned_start_dt"]).dt.days + 1).astype(int)
dim_activity.drop(columns=["planned_start_dt", "planned_finish_dt"], inplace=True)

# C. Dim_Date (Master Tidstabell)
dates = pd.date_range(start="2026-01-01", end="2026-12-31", freq="D")
dim_date = pd.DataFrame({"Date": dates})
dim_date["DateKey"] = dim_date["Date"].dt.strftime("%Y%m%d").astype(int)
dim_date["Year"] = dim_date["Date"].dt.year
dim_date["Quarter"] = "Q" + dim_date["Date"].dt.quarter.astype(str)
dim_date["Month"] = dim_date["Date"].dt.month
dim_date["MonthName"] = dim_date["Date"].dt.strftime("%B")
dim_date["Period"] = dim_date["Date"].dt.strftime("%Y-%m")
dim_date["WeekNumber"] = dim_date["Date"].dt.isocalendar().week
dim_date["WeekStart"] = dim_date["Date"].dt.to_period("W").dt.start_time.dt.strftime("%Y-%m-%d")
dim_date["DayOfWeek"] = dim_date["Date"].dt.day_name()
dim_date["IsWorkingDay"] = dim_date["Date"].dt.day_of_week.isin(range(0, 5))

# D. Dim_CostCenter & Berikelse av Dim_Employee (Enkeltenheter ved Elkem Fiskå)
dept_cc_map = {
    "Operations": ("CC-4100", "Pilotanlegg Drift & Mekanisk Verksted", "Fiskå Bygg 12"),
    "R&D":        ("CC-4200", "FoU Sentrallab & Kjemisk Analyse",     "Fiskå Bygg 04"),
    "Finance":    ("CC-4300", "Prosessmetallurgi & Prosjektledelse",  "Fiskå Adm Hovedbygg")
}

df_cost_centers = pd.DataFrame([
    {
        "cost_center_id": v[0],
        "cost_center_name": v[1],
        "location": v[2],
        "department": k
    }
    for k, v in dept_cc_map.items()
])

dim_employee["cost_center_id"] = dim_employee["department"].map(lambda d: dept_cc_map.get(d, ("CC-4300", "", ""))[0])

# ------------------------------------------------------------------------------
# 3. BERIKELSER FOR FAKTATABELLER
# ------------------------------------------------------------------------------
print("--- 3. Beriker Faktatabeller ---")

# A. Fact_PurchaseOrders & Fact_APInvoices med NOK
if "amount_nok" not in fact_po.columns:
    fact_po["period"] = pd.to_datetime(fact_po["po_date"]).dt.strftime("%Y-%m")
    fact_po = fact_po.merge(df_fx[["period", "currency", "nok_rate"]], on=["period", "currency"], how="left")
    fact_po["nok_rate"] = fact_po["nok_rate"].fillna(1.0)
    fact_po["amount_nok"] = fact_po["amount_currency"] * fact_po["nok_rate"]

if "amount_nok" not in fact_ap.columns:
    fact_ap["period"] = pd.to_datetime(fact_ap["invoice_date"]).dt.strftime("%Y-%m")
    fact_ap = fact_ap.merge(df_fx[["period", "currency", "nok_rate"]], on=["period", "currency"], how="left")
    fact_ap["nok_rate"] = fact_ap["nok_rate"].fillna(1.0)
    fact_ap["amount_nok"] = fact_ap["amount_currency"] * fact_ap["nok_rate"]

# B. Open Commitments på Fact_PurchaseOrders
ap_by_po = fact_ap.groupby("po_line_id")["amount_nok"].sum().to_dict()
fact_po["invoiced_nok"] = fact_po["po_line_id"].map(lambda x: ap_by_po.get(x, 0.0)).fillna(0.0)
fact_po["open_commitment_nok"] = np.maximum(0.0, fact_po["amount_nok"] - fact_po["invoiced_nok"])
fact_po["po_status"] = np.where(
    fact_po["invoiced_nok"] >= fact_po["amount_nok"] - 1.0, "Fully Invoiced",
    np.where(fact_po["invoiced_nok"] > 0, "Partially Invoiced", "Open Uninvoiced")
)

# C. Fact_GLActuals med IAS 38
fact_gl["period"] = pd.to_datetime(fact_gl["posting_date"]).dt.strftime("%Y-%m")
fact_gl["ias38_treatment"] = fact_gl["wbs_id"].map(lambda x: ias38_meta.get(x, ("", "EXPENSE"))[1])
fact_gl["accounting_bucket"] = fact_gl["wbs_id"].map(lambda x: ias38_meta.get(x, ("", "", "P&L Operating Expense"))[2])

# ------------------------------------------------------------------------------
# 4. KONTANTSTRØM (CASH FLOW BRIDGE) & MÅNEDLIGE EARLY WARNINGS (JAN - OKT 2026)
# ------------------------------------------------------------------------------
print("--- 4. Beregner Kontantstrøm & Månedlige Early Warnings ---")

# A. Likviditetsutgang leverandører (DPO 30 dager)
fact_ap["payment_due_date"] = pd.to_datetime(fact_ap["invoice_date"]) + pd.Timedelta(days=30)
fact_ap["cash_out_period"] = fact_ap["payment_due_date"].dt.strftime("%Y-%m")
ap_cash_monthly = fact_ap.groupby("cash_out_period")["amount_nok"].sum().to_dict()

# B. Interne lønnsutbetalinger per måned
fact_timesheets["period"] = pd.to_datetime(fact_timesheets["work_date"]).dt.strftime("%Y-%m")
payroll_cash_monthly = (fact_timesheets.groupby("period")["hours"].sum() * 530.0).to_dict()

# C. Månedlig simulering uten bakspeil
bac_total = 20000000.0
total_activities = len(dim_activity)
months_all = sorted(fact_gl["period"].unique())

early_warning_records = []
cash_bridge_records = []

po_cum = 0.0
ac_cum = 0.0
pv_cum = 0.0

for m in months_all:
    pv_m = fact_budget[fact_budget["period"] == m]["baseline_budget_nok"].sum()
    pv_cum += pv_m
    
    ac_m = fact_gl[fact_gl["period"] == m]["amount_nok"].sum()
    ac_cum += ac_m
    
    po_m = fact_po[fact_po["period"] == m]["amount_nok"].sum()
    po_cum += po_m
    
    finished_m = dim_activity[(dim_activity["status"] == "Completed") & 
                              (pd.to_datetime(dim_activity["planned_finish"]).dt.strftime("%Y-%m") <= m)]
    ev_cum = (len(finished_m) / total_activities) * bac_total
    
    cpi = ev_cum / ac_cum if ac_cum > 0 else 1.0
    spi = ev_cum / pv_cum if pv_cum > 0 else 1.0
    po_ratio_pct = (po_cum / bac_total) * 100.0
    projected_eac = bac_total / cpi if cpi > 0 else bac_total
    
    if po_cum > bac_total:
        rag = "RED: PO > 100% BAC"
        signal_level = "CRITICAL"
        action = "Krav om Stage-Gate Freeze og formell styrebehandlet OTB."
    elif ac_cum > (pv_cum * 1.5):
        rag = "YELLOW: Burn-rate > 1.5x"
        signal_level = "WARNING"
        action = "Avstemming av åpne PO-er og de-scoping av lab-tester."
    else:
        rag = "GREEN: Normal"
        signal_level = "NORMAL"
        action = "Løpende drift og kostnadskontroll."
        
    early_warning_records.append({
        "period": m,
        "pv_monthly_nok": round(pv_m, 2),
        "pv_cum_nok": round(pv_cum, 2),
        "ac_monthly_nok": round(ac_m, 2),
        "ac_cum_nok": round(ac_cum, 2),
        "ev_cum_nok": round(ev_cum, 2),
        "po_committed_monthly_nok": round(po_m, 2),
        "po_committed_cum_nok": round(po_cum, 2),
        "po_vs_bac_ratio_pct": round(po_ratio_pct, 1),
        "cpi": round(cpi, 3),
        "spi": round(spi, 3),
        "projected_eac_nok": round(projected_eac, 2),
        "rag_status": rag,
        "signal_level": signal_level,
        "controller_action_required": action
    })
    
    ap_payout = ap_cash_monthly.get(m, 0.0)
    payroll_payout = payroll_cash_monthly.get(m, 0.0)
    total_cash_out = ap_payout + payroll_payout
    
    enova_cash_in = 3000000.0 if m == "2026-06" else 0.0
    net_cash_flow = enova_cash_in - total_cash_out
    
    cash_bridge_records.append({
        "period": m,
        "actual_cost_ac_nok": round(ac_m, 2),
        "supplier_ap_paid_nok": round(ap_payout, 2),
        "internal_payroll_paid_nok": round(payroll_payout, 2),
        "total_cash_outflow_nok": round(total_cash_out, 2),
        "enova_grant_cash_in_nok": round(enova_cash_in, 2),
        "net_monthly_cash_flow_nok": round(net_cash_flow, 2)
    })

df_early_warnings = pd.DataFrame(early_warning_records)
df_cash_flow = pd.DataFrame(cash_bridge_records)

# ------------------------------------------------------------------------------
# 5. GENERER FLAT KONSOLIDERT EXCEL-TABELL (EXCEL READY)
# ------------------------------------------------------------------------------
print("--- 5. Bygger Flat Financial EVM Cube for Excel (excel_ready) ---")
b_agg = fact_budget.groupby(["wbs_id", "cost_element", "period"])["baseline_budget_nok"].sum().reset_index()

gl_agg = fact_gl.groupby(["wbs_id", "cost_element", "period"]).agg(
    actual_cost_nok=("amount_nok", "sum"),
    capitalized_auc_nok=("amount_nok", lambda s: s[fact_gl.loc[s.index, "ias38_treatment"] == "CAPITALIZE"].sum()),
    expensed_pnl_nok=("amount_nok", lambda s: s[fact_gl.loc[s.index, "ias38_treatment"] == "EXPENSE"].sum()),
).reset_index()

po_agg = fact_po.groupby(["wbs_id", "cost_element", "period"]).agg(
    po_committed_nok=("amount_nok", "sum"),
    po_invoiced_nok=("invoiced_nok", "sum"),
    open_commitment_nok=("open_commitment_nok", "sum")
).reset_index()

flat_df = pd.merge(b_agg, gl_agg, on=["wbs_id", "cost_element", "period"], how="outer").fillna(0.0)
flat_df = pd.merge(flat_df, po_agg, on=["wbs_id", "cost_element", "period"], how="outer").fillna(0.0)

wbs_dict = dim_wbs.set_index("wbs_id")[["wbs_name", "parent_wbs_id", "ias38_phase", "ias38_treatment", "accounting_bucket"]].to_dict("index")
ce_dict = dim_cost_element.set_index("cost_element")["cost_element_name"].to_dict()

flat_df["project_id"] = "GP2026"
flat_df["wbs_name"] = flat_df["wbs_id"].map(lambda x: wbs_dict.get(x, {}).get("wbs_name", x))
flat_df["parent_wbs_id"] = flat_df["wbs_id"].map(lambda x: wbs_dict.get(x, {}).get("parent_wbs_id", "GP2026"))
flat_df["cost_element_name"] = flat_df["cost_element"].map(lambda x: ce_dict.get(x, x))
flat_df["ias38_treatment"] = flat_df["wbs_id"].map(lambda x: wbs_dict.get(x, {}).get("ias38_treatment", "EXPENSE"))
flat_df["ias38_phase"] = flat_df["wbs_id"].map(lambda x: wbs_dict.get(x, {}).get("ias38_phase", "Research"))
flat_df["accounting_bucket"] = flat_df["wbs_id"].map(lambda x: wbs_dict.get(x, {}).get("accounting_bucket", "P&L"))

col_order = [
    "project_id", "period", "wbs_id", "wbs_name", "parent_wbs_id", "ias38_phase", "ias38_treatment", "accounting_bucket",
    "cost_element", "cost_element_name",
    "baseline_budget_nok", "actual_cost_nok", "capitalized_auc_nok", "expensed_pnl_nok",
    "po_committed_nok", "po_invoiced_nok", "open_commitment_nok"
]
flat_df = flat_df[col_order].sort_values(["period", "wbs_id", "cost_element"])

# ------------------------------------------------------------------------------
# 6. EKSPORT TIL DISK (STAR_SCHEMA, BUSINESS_READY OG EXCEL_READY)
# ------------------------------------------------------------------------------
print("--- 6. Eksporterer tabeller til star_schema, business_ready og excel_ready ---")
for target_dir in [STAR_SCHEMA_DIR, BUSINESS_READY_DIR]:
    dim_project.to_csv(os.path.join(target_dir, "Dim_Project.csv"), index=False, sep=";")
    dim_wbs.to_csv(os.path.join(target_dir, "Dim_WBS.csv"), index=False, sep=";")
    dim_cost_element.to_csv(os.path.join(target_dir, "Dim_CostElement.csv"), index=False, sep=";")
    dim_vendor.to_csv(os.path.join(target_dir, "Dim_Vendor.csv"), index=False, sep=";")
    dim_employee.to_csv(os.path.join(target_dir, "Dim_Employee.csv"), index=False, sep=";")
    dim_activity.to_csv(os.path.join(target_dir, "Dim_Activity.csv"), index=False, sep=";")
    dim_resource.to_csv(os.path.join(target_dir, "Dim_Resource.csv"), index=False, sep=";")
    dim_date.to_csv(os.path.join(target_dir, "Dim_Date.csv"), index=False, sep=";")
    df_cost_centers.to_csv(os.path.join(target_dir, "Dim_CostCenter.csv"), index=False, sep=";")

    fact_budget.to_csv(os.path.join(target_dir, "Fact_BudgetBaseline.csv"), index=False, sep=";")
    fact_gl.to_csv(os.path.join(target_dir, "Fact_GLActuals.csv"), index=False, sep=";")
    fact_timesheets.to_csv(os.path.join(target_dir, "Fact_Timesheets.csv"), index=False, sep=";")
    fact_po.to_csv(os.path.join(target_dir, "Fact_PurchaseOrders.csv"), index=False, sep=";")
    fact_gr.to_csv(os.path.join(target_dir, "Fact_GoodsReceipts.csv"), index=False, sep=";")
    fact_ap.to_csv(os.path.join(target_dir, "Fact_APInvoices.csv"), index=False, sep=";")
    fact_journals.to_csv(os.path.join(target_dir, "Fact_Journals.csv"), index=False, sep=";")
    fact_change_orders.to_csv(os.path.join(target_dir, "Fact_ChangeOrders.csv"), index=False, sep=";")
    fact_capacity.to_csv(os.path.join(target_dir, "Fact_CapacityCalendar.csv"), index=False, sep=";")
    fact_resource_assignments.to_csv(os.path.join(target_dir, "Fact_ResourceAssignments.csv"), index=False, sep=";")
    
    df_early_warnings.to_csv(os.path.join(target_dir, "Fact_MonthlyEarlyWarnings.csv"), index=False, sep=";")
    df_cash_flow.to_csv(os.path.join(target_dir, "Fact_CashFlowBridge.csv"), index=False, sep=";")

    df_thresholds = pd.DataFrame([
        {"Metric": "CPI", "Yellow_Limit": "0.90", "Red_Limit": "0.80", "Trigger_Type": "Min", "Controller_Action": "Freeze non-critical POs, revise EAC"},
        {"Metric": "SPI", "Yellow_Limit": "0.90", "Red_Limit": "0.80", "Trigger_Type": "Min", "Controller_Action": "Assess schedule compression / reallocate labor"},
        {"Metric": "Open Commitments (MNOK)", "Yellow_Limit": "10.0", "Red_Limit": "25.0", "Trigger_Type": "Max", "Controller_Action": "Immediate PO cancellation audit"},
        {"Metric": "AuC Capitalization Ratio", "Yellow_Limit": "60%", "Red_Limit": "80%", "Trigger_Type": "Max", "Controller_Action": "Trigger mandatory IAS 36 Impairment Test"}
    ])
    df_thresholds.to_csv(os.path.join(target_dir, "Config_VarianceThresholds.csv"), index=False, sep=";")

# Eksport til Excel Ready
flat_csv_path = os.path.join(EXCEL_READY_DIR, "Fact_FinancialEVM_Unified_Flat.csv")
flat_df.to_csv(flat_csv_path, index=False, sep=";")
df_early_warnings.to_csv(os.path.join(EXCEL_READY_DIR, "tbl_Monthly_EarlyWarnings.csv"), index=False, sep=";")
df_cash_flow.to_csv(os.path.join(EXCEL_READY_DIR, "tbl_CashFlow_Bridge.csv"), index=False, sep=";")

print("=" * 80)
print("=== STEG 3 (v5) FULLFØRT MED ALLE BERIKELSER ===")
print("=" * 80)
print(f" - Dim_Activity progress_pct: Vektet snitt = {dim_activity['progress_pct'].mean():.2f}%")
print(f" - Fact_PurchaseOrders Open Commitments: NOK {fact_po['open_commitment_nok'].sum():,.2f}")
print(f" - Fact_GLActuals AuC Capitalized:        NOK {fact_gl[fact_gl['ias38_treatment'] == 'CAPITALIZE']['amount_nok'].sum():,.2f}")
print(f" - Fact_GLActuals P&L Expensed:          NOK {fact_gl[fact_gl['ias38_treatment'] == 'EXPENSE']['amount_nok'].sum():,.2f}")
print(f" - Dim_CostCenter: 3 enheter etablert (CC-4100, CC-4200, CC-4300)")
print(f" - tbl_CashFlow_Bridge: {len(df_cash_flow)} måneder med leverandør- og lønnsutbetalinger")
print(f" - tbl_Monthly_EarlyWarnings: 10 månedsrapporter generert")
critical_month = df_early_warnings[df_early_warnings['signal_level']=='CRITICAL']['period'].iloc[0]
critical_po = df_early_warnings[df_early_warnings['signal_level']=='CRITICAL']['po_committed_cum_nok'].iloc[0]
print(f"   * Første RØDE alarm utløst i {critical_month} (PO = NOK {critical_po:,.0f})")
print(f" - Flat Cube for Excel lagret: {flat_csv_path} ({len(flat_df)} rader)")
print("=" * 80)

