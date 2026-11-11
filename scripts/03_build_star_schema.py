import os
import sys
import pandas as pd
import numpy as np

# ==============================================================================
# STEG 3 (v5): ENRICHED STAR SCHEMA & DUAL EXCEL ENGINE (GREENPILOT 2026)
#
# Formål:
#  1. Bevarer Power BI-kompatibilitet 100% uendret i processed/star_schema/
#  2. Optimaliserer stjerneskjemaet for Excels Data Model (Power Pivot)
#  3. Genererer "Fact_FinancialEVM_Analytics_Flat.csv" for Python i Excel (=PY())
#     og Excel Analysis ToolPak (Dataanalyse-tillegget)
#  4. Eksporterer 3 kuraterte sammendragstabeller til processed/excel_ready/
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
print("=== STEG 3 (v5): STAR SCHEMA & DUAL EXCEL ENGINE (GREENPILOT 2026) ===")
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

def save_csv_sig(df: pd.DataFrame, path: str):
    """Sikrer semikolon og utf-8-sig (BOM) så norsk Excel viser æ, ø, å korrekt uten konvertering."""
    df.to_csv(path, index=False, sep=";", encoding="utf-8-sig")

# ------------------------------------------------------------------------------
# 1. HENT MASTERDATA OG TRANSAKSJONER
# ------------------------------------------------------------------------------
print("--- 1. Leser kildedata ---")
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
# 2. BERIKELSER FOR DIMENSJONER (BEVARER ALLE PBI-FELTER)
# ------------------------------------------------------------------------------
print("--- 2. Beriker Dimensjoner ---")

# A. Dim_WBS: parent_wbs_id og IAS 38
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

# B. Dim_Activity: progress_pct, duration og finish_period
status_progress_map = {"Completed": 100, "In Progress": 50, "Not Started": 0}
status_order_map = {"Completed": "1 - Completed", "In Progress": "2 - In Progress", "Not Started": "3 - Not Started"}
dim_activity["progress_pct"] = dim_activity["status"].map(lambda s: status_progress_map.get(s, 0)).astype(int)
dim_activity["activity_status_group"] = dim_activity["status"].map(lambda s: status_order_map.get(s, "4 - Other"))
dim_activity["planned_start_dt"] = pd.to_datetime(dim_activity["planned_start"])
dim_activity["planned_finish_dt"] = pd.to_datetime(dim_activity["planned_finish"])
dim_activity["planned_duration_days"] = ((dim_activity["planned_finish_dt"] - dim_activity["planned_start_dt"]).dt.days + 1).astype(int)
dim_activity["finish_period"] = dim_activity["planned_finish_dt"].dt.strftime("%Y-%m")
dim_activity.drop(columns=["planned_start_dt", "planned_finish_dt"], inplace=True)

# Beregn Earned Value per aktivitet (vektet likt mot BAC 20M)
total_bac = fact_budget["baseline_budget_nok"].sum()
act_weight = total_bac / len(dim_activity)
dim_activity["ev_nok"] = (dim_activity["progress_pct"] / 100.0) * act_weight

# C. Dim_Date (med DateKey for ren 1:Mange-relasjon i både PBI og Power Pivot)
dates = pd.date_range(start="2026-01-01", end="2026-12-31", freq="D")
dim_date = pd.DataFrame({"Date": dates.strftime("%Y-%m-%d")})
dim_date["DateKey"] = dates.strftime("%Y%m%d").astype(int)
dim_date["Year"] = dates.year
dim_date["Quarter"] = "Q" + dates.quarter.astype(str)
dim_date["Month"] = dates.month
dim_date["MonthName"] = dates.strftime("%B")
dim_date["Period"] = dates.strftime("%Y-%m")
dim_date["WeekNumber"] = dates.isocalendar().week
dim_date["WeekStart"] = dates.to_period("W").start_time.strftime("%Y-%m-%d")
dim_date["DayOfWeek"] = dates.day_name()
dim_date["IsWorkingDay"] = dates.dayofweek.isin(range(0, 5))

# ------------------------------------------------------------------------------
# 3. BERIKELSER FOR FAKTATABELLER & NØKLER TIL POWER PIVOT / PBI
# ------------------------------------------------------------------------------
print("--- 3. Beriker Faktatabeller og Nøkler ---")

fx_lookup = {"NOK": 1.0, "EUR": 11.45, "USD": 10.50}

# A. Fact_PurchaseOrders & Fact_APInvoices med NOK
if "amount_nok" not in fact_po.columns:
    fact_po["period"] = pd.to_datetime(fact_po["po_date"]).dt.strftime("%Y-%m")
    fact_po = fact_po.merge(df_fx[["period", "currency", "nok_rate"]], on=["period", "currency"], how="left")
    fact_po["nok_rate"] = fact_po["nok_rate"].fillna(fact_po["currency"].map(fx_lookup)).fillna(1.0)
    fact_po["amount_nok"] = (fact_po["amount_currency"] * fact_po["nok_rate"]).round(2)

if "amount_nok" not in fact_ap.columns:
    fact_ap["period"] = pd.to_datetime(fact_ap["invoice_date"]).dt.strftime("%Y-%m")
    fact_ap = fact_ap.merge(df_fx[["period", "currency", "nok_rate"]], on=["period", "currency"], how="left")
    fact_ap["nok_rate"] = fact_ap["nok_rate"].fillna(fact_ap["currency"].map(fx_lookup)).fillna(1.0)
    fact_ap["amount_nok"] = (fact_ap["amount_currency"] * fact_ap["nok_rate"]).round(2)

# Beregn forpliktelser og status på PO
ap_by_po = fact_ap.groupby("po_line_id")["amount_nok"].sum().to_dict()
fact_po["invoiced_nok"] = fact_po["po_line_id"].map(lambda x: ap_by_po.get(x, 0.0)).fillna(0.0).round(2)
fact_po["open_commitment_nok"] = np.maximum(0.0, fact_po["amount_nok"] - fact_po["invoiced_nok"]).round(2)
fact_po["po_status"] = np.where(
    fact_po["invoiced_nok"] >= fact_po["amount_nok"] - 1.0, "Fully Invoiced",
    np.where(fact_po["invoiced_nok"] > 0, "Partially Invoiced", "Open Uninvoiced")
)
fact_po["DateKey"] = pd.to_datetime(fact_po["po_date"]).dt.strftime("%Y%m%d").astype(int)

# B. Fact_GLActuals med DateKey og IAS 38
fact_gl["DateKey"] = pd.to_datetime(fact_gl["posting_date"]).dt.strftime("%Y%m%d").astype(int)
fact_gl["period"] = pd.to_datetime(fact_gl["posting_date"]).dt.strftime("%Y-%m")
fact_gl["ias38_treatment"] = fact_gl["wbs_id"].map(lambda x: ias38_meta.get(x, ("", "EXPENSE", "", ""))[1])
fact_gl["accounting_bucket"] = fact_gl["wbs_id"].map(lambda x: ias38_meta.get(x, ("", "", "P&L Operating Expense", ""))[2])

# C. Fact_BudgetBaseline med DateKey (knyttet til 1. i måneden for Power Pivot relasjon)
fact_budget["period_date"] = fact_budget["period"] + "-01"
fact_budget["DateKey"] = pd.to_datetime(fact_budget["period_date"]).dt.strftime("%Y%m%d").astype(int)

# ------------------------------------------------------------------------------
# 4. EKSPORT TIL BÅDE STAR_SCHEMA OG BUSINESS_READY (FOR POWER BI & DATA MODEL)
# ------------------------------------------------------------------------------
print("--- 4. Eksporterer tabeller til star_schema og business_ready ---")
for target_dir in [STAR_SCHEMA_DIR, BUSINESS_READY_DIR]:
    save_csv_sig(dim_project, os.path.join(target_dir, "Dim_Project.csv"))
    save_csv_sig(dim_wbs, os.path.join(target_dir, "Dim_WBS.csv"))
    save_csv_sig(dim_cost_element, os.path.join(target_dir, "Dim_CostElement.csv"))
    save_csv_sig(dim_vendor, os.path.join(target_dir, "Dim_Vendor.csv"))
    save_csv_sig(dim_employee, os.path.join(target_dir, "Dim_Employee.csv"))
    save_csv_sig(dim_activity, os.path.join(target_dir, "Dim_Activity.csv"))
    save_csv_sig(dim_resource, os.path.join(target_dir, "Dim_Resource.csv"))
    save_csv_sig(dim_date, os.path.join(target_dir, "Dim_Date.csv"))

    save_csv_sig(fact_budget, os.path.join(target_dir, "Fact_BudgetBaseline.csv"))
    save_csv_sig(fact_gl, os.path.join(target_dir, "Fact_GLActuals.csv"))
    save_csv_sig(fact_timesheets, os.path.join(target_dir, "Fact_Timesheets.csv"))
    save_csv_sig(fact_po, os.path.join(target_dir, "Fact_PurchaseOrders.csv"))
    save_csv_sig(fact_gr, os.path.join(target_dir, "Fact_GoodsReceipts.csv"))
    save_csv_sig(fact_ap, os.path.join(target_dir, "Fact_APInvoices.csv"))
    save_csv_sig(fact_journals, os.path.join(target_dir, "Fact_Journals.csv"))
    save_csv_sig(fact_change_orders, os.path.join(target_dir, "Fact_ChangeOrders.csv"))
    save_csv_sig(fact_capacity, os.path.join(target_dir, "Fact_CapacityCalendar.csv"))
    save_csv_sig(fact_resource_assignments, os.path.join(target_dir, "Fact_ResourceAssignments.csv"))

    # Terskelverdier med numeriske grenser for Power Query / DAX (5 kolonner som matcher Config_VarianceThresholds.tmdl)
    df_thresholds = pd.DataFrame([
        {"Metric": "CPI", "Yellow_Limit": 0.90, "Red_Limit": 0.80, "Trigger_Type": "Min", "Controller_Action": "Freeze non-critical POs, revise EAC"},
        {"Metric": "SPI", "Yellow_Limit": 0.90, "Red_Limit": 0.80, "Trigger_Type": "Min", "Controller_Action": "Assess schedule compression / reallocate labor"},
        {"Metric": "Open Commitments (MNOK)", "Yellow_Limit": 10.0, "Red_Limit": 25.0, "Trigger_Type": "Max", "Controller_Action": "Immediate PO cancellation audit"},
        {"Metric": "AuC Capitalization Ratio", "Yellow_Limit": 0.60, "Red_Limit": 0.80, "Trigger_Type": "Max", "Controller_Action": "Trigger mandatory IAS 36 Impairment Test"}
    ])
    save_csv_sig(df_thresholds, os.path.join(target_dir, "Config_VarianceThresholds.csv"))

# ------------------------------------------------------------------------------
# 5. GENERER DEN FLATE ANALYSE-KUBEN FOR PYTHON I EXCEL (=PY()) OG ANALYSIS TOOLPAK
# ------------------------------------------------------------------------------
print("--- 5. Bygger Fact_FinancialEVM_Analytics_Flat for Python i Excel & ToolPak ---")

# A. Aggregering av budsjett (PV)
b_agg = fact_budget.groupby(["wbs_id", "cost_element", "period"])["baseline_budget_nok"].sum().reset_index()

# B. Aggregering av faktiske kostnader (AC) og IAS 38
gl_agg = fact_gl.groupby(["wbs_id", "cost_element", "period"]).agg(
    actual_cost_nok=("amount_nok", "sum"),
    capitalized_auc_nok=("amount_nok", lambda s: s[fact_gl.loc[s.index, "ias38_treatment"] == "CAPITALIZE"].sum()),
    expensed_pnl_nok=("amount_nok", lambda s: s[fact_gl.loc[s.index, "ias38_treatment"] == "EXPENSE"].sum()),
).reset_index()

# C. Aggregering av forpliktelser (PO)
po_agg = fact_po.groupby(["wbs_id", "cost_element", "period"]).agg(
    po_committed_nok=("amount_nok", "sum"),
    po_invoiced_nok=("invoiced_nok", "sum"),
    open_commitment_nok=("open_commitment_nok", "sum")
).reset_index()

# D. Aggregering av Earned Value (EV) per måned og WBS
ev_agg = dim_activity.groupby(["wbs_id", "finish_period"])["ev_nok"].sum().reset_index()
ev_agg.rename(columns={"finish_period": "period", "ev_nok": "earned_value_nok"}, inplace=True)

# E. Slå sammen kuben
flat_df = pd.merge(b_agg, gl_agg, on=["wbs_id", "cost_element", "period"], how="outer").fillna(0.0)
flat_df = pd.merge(flat_df, po_agg, on=["wbs_id", "cost_element", "period"], how="outer").fillna(0.0)
flat_df = pd.merge(flat_df, ev_agg, on=["wbs_id", "period"], how="left").fillna(0.0)

# F. Beregn eksplisitte matematiske avvik per rad (for ToolPak regresjon og korrelasjon)
flat_df["cost_variance_cv"] = (flat_df["earned_value_nok"] - flat_df["actual_cost_nok"]).round(2)
flat_df["schedule_variance_sv"] = (flat_df["earned_value_nok"] - flat_df["baseline_budget_nok"]).round(2)
flat_df["cpi"] = np.where(flat_df["actual_cost_nok"] > 0, (flat_df["earned_value_nok"] / flat_df["actual_cost_nok"]).round(3), np.nan)
flat_df["spi"] = np.where(flat_df["baseline_budget_nok"] > 0, (flat_df["earned_value_nok"] / flat_df["baseline_budget_nok"]).round(3), np.nan)

# G. Berik med tekstnavn og regnskapsklassifisering
wbs_dict = dim_wbs.set_index("wbs_id")[["wbs_name", "parent_wbs_id", "ias38_phase", "ias38_treatment", "accounting_bucket", "eligible_auc"]].to_dict("index")
ce_dict = dim_cost_element.set_index("cost_element")["cost_element_name"].to_dict()

flat_df["project_id"] = "GP2026"
flat_df["month_num"] = flat_df["period"].apply(lambda p: int(p.split("-")[1]))
flat_df["wbs_name"] = flat_df["wbs_id"].map(lambda x: wbs_dict.get(x, {}).get("wbs_name", x))
flat_df["parent_wbs_id"] = flat_df["wbs_id"].map(lambda x: wbs_dict.get(x, {}).get("parent_wbs_id", "GP2026"))
flat_df["cost_element_name"] = flat_df["cost_element"].map(lambda x: ce_dict.get(x, x))
flat_df["ias38_phase"] = flat_df["wbs_id"].map(lambda x: wbs_dict.get(x, {}).get("ias38_phase", "Research"))
flat_df["ias38_treatment"] = flat_df["wbs_id"].map(lambda x: wbs_dict.get(x, {}).get("ias38_treatment", "EXPENSE"))
flat_df["accounting_bucket"] = flat_df["wbs_id"].map(lambda x: wbs_dict.get(x, {}).get("accounting_bucket", "P&L"))
flat_df["eligible_auc"] = flat_df["wbs_id"].map(lambda x: wbs_dict.get(x, {}).get("eligible_auc", False))

col_order = [
    "project_id", "period", "month_num", "wbs_id", "wbs_name", "parent_wbs_id",
    "ias38_phase", "ias38_treatment", "accounting_bucket", "eligible_auc",
    "cost_element", "cost_element_name",
    "baseline_budget_nok", "actual_cost_nok", "earned_value_nok",
    "cost_variance_cv", "schedule_variance_sv", "cpi", "spi",
    "capitalized_auc_nok", "expensed_pnl_nok",
    "po_committed_nok", "po_invoiced_nok", "open_commitment_nok"
]
flat_df = flat_df[col_order].sort_values(["period", "wbs_id", "cost_element"])

# Lagre primært til excel_ready som Fact_FinancialEVM_Analytics_Flat.csv
flat_csv_path = os.path.join(EXCEL_READY_DIR, "Fact_FinancialEVM_Analytics_Flat.csv")
save_csv_sig(flat_df, flat_csv_path)

# Bevar også filnavnet fra v4 for bakoverkompatibilitet
legacy_csv_path = os.path.join(EXCEL_READY_DIR, "Fact_FinancialEVM_Unified_Flat.csv")
save_csv_sig(flat_df, legacy_csv_path)

# ------------------------------------------------------------------------------
# 6. GENERER KURATERTE UTTRREKK FOR RAPPORTERING (EXCEL_READY)
# ------------------------------------------------------------------------------
print("--- 6. Bygger formålstjenlige sammendragstabeller for Excel-arkene ---")

# UTTREKK 1: 01_EVM_Monthly_Timeline.csv (Kilde til Dashboard & S-kurve)
pv_monthly = fact_budget.groupby("period")["baseline_budget_nok"].sum().rename("pv_monthly_nok")
ac_monthly = fact_gl.groupby("period")["amount_nok"].sum().rename("ac_monthly_nok")
ev_monthly = dim_activity.groupby("finish_period")["ev_nok"].sum().rename("ev_monthly_nok")

evm_timeline = pd.DataFrame(index=dim_date["Period"].unique()).rename_axis("period")
evm_timeline = evm_timeline.join([pv_monthly, ac_monthly, ev_monthly]).fillna(0.0)

# Kutt AC og EV ved statusdato (2026-11-01 -> tom period 2026-10)
evm_timeline["ac_monthly_nok"] = np.where(evm_timeline.index > "2026-10", 0.0, evm_timeline["ac_monthly_nok"])
evm_timeline["ev_monthly_nok"] = np.where(evm_timeline.index > "2026-10", 0.0, evm_timeline["ev_monthly_nok"])

evm_timeline["pv_cum_nok"] = evm_timeline["pv_monthly_nok"].cumsum()
evm_timeline["ac_cum_nok"] = np.where(evm_timeline.index > "2026-10", np.nan, evm_timeline["ac_monthly_nok"].cumsum())
evm_timeline["ev_cum_nok"] = np.where(evm_timeline.index > "2026-10", np.nan, evm_timeline["ev_monthly_nok"].cumsum())

evm_timeline["cost_variance_cv"] = evm_timeline["ev_cum_nok"] - evm_timeline["ac_cum_nok"]
evm_timeline["schedule_variance_sv"] = evm_timeline["ev_cum_nok"] - evm_timeline["pv_cum_nok"]
evm_timeline["cpi"] = (evm_timeline["ev_cum_nok"] / evm_timeline["ac_cum_nok"]).round(2)
evm_timeline["spi"] = (evm_timeline["ev_cum_nok"] / evm_timeline["pv_cum_nok"]).round(2)

save_csv_sig(evm_timeline.reset_index(), os.path.join(EXCEL_READY_DIR, "01_EVM_Monthly_Timeline.csv"))

# UTTREKK 2: 02_WBS_Executive_Summary.csv (Kilde til WBS Avviksmatrise og IAS 38 AuC)
wbs_b = fact_budget.groupby("wbs_id")["baseline_budget_nok"].sum()
wbs_ac = fact_gl.groupby("wbs_id")["amount_nok"].sum()
wbs_auc = fact_gl[fact_gl["ias38_treatment"] == "CAPITALIZE"].groupby("wbs_id")["amount_nok"].sum()
wbs_pnl = fact_gl[fact_gl["ias38_treatment"] == "EXPENSE"].groupby("wbs_id")["amount_nok"].sum()
wbs_ev = dim_activity.groupby("wbs_id")["ev_nok"].sum()

wbs_summary = dim_wbs[["wbs_id", "wbs_name", "parent_wbs_id", "ias38_phase", "accounting_bucket", "eligible_auc"]].set_index("wbs_id")
wbs_summary["bac_nok"] = wbs_b
wbs_summary["ac_nok"] = wbs_ac
wbs_summary["ev_nok"] = wbs_ev
wbs_summary["cost_variance_nok"] = wbs_summary["ev_nok"] - wbs_summary["ac_nok"]
wbs_summary["cpi"] = (wbs_summary["ev_nok"] / wbs_summary["ac_nok"]).round(2)
wbs_summary["capitalized_auc_nok"] = wbs_auc.fillna(0.0)
wbs_summary["expensed_pnl_nok"] = wbs_pnl.fillna(0.0)

save_csv_sig(wbs_summary.reset_index(), os.path.join(EXCEL_READY_DIR, "02_WBS_Executive_Summary.csv"))

# UTTREKK 3: 03_Top_Open_Commitments.csv (Kilde til Topp 20 Innkjøpseksponeringer)
vendor_names = dim_vendor.set_index("vendor_id")["vendor_name"].to_dict()
top_po = fact_po[fact_po["open_commitment_nok"] > 0].copy()
top_po["vendor_name"] = top_po["vendor_id"].map(vendor_names)
top_po_cols = [
    "po_id", "po_line_id", "vendor_id", "vendor_name", "wbs_id", "cost_element",
    "currency", "amount_currency", "amount_nok", "invoiced_nok", "open_commitment_nok", "po_status"
]
top_po = top_po[top_po_cols].sort_values("open_commitment_nok", ascending=False).head(20)

save_csv_sig(top_po, os.path.join(EXCEL_READY_DIR, "03_Top_Open_Commitments.csv"))

print("=" * 80)
print("=== STEG 3 (v5) FULLFØRT MED DOBBEL EXCEL-MOTOR OG BEVART PBI-STRUKTUR ===")
print("=" * 80)
print(f" - star_schema:      {len(os.listdir(STAR_SCHEMA_DIR))} tabeller (100% PBI-kompatibel + DateKey for Power Pivot)")
print(f" - Flat Analytics:   {flat_csv_path} ({len(flat_df)} rader for =PY() & ToolPak)")
print(f" - 01_EVM_Timeline:  12 mnd S-kurve, CPI, SPI ferdig avskåret ved cut-off")
print(f" - 02_WBS_Summary:   6 rader WBS EVM og IAS 38 AuC")
print(f" - 03_Top_Open_POs:  Topp 20 uavsluttede innkjøpsordrer")
print("=" * 80)
