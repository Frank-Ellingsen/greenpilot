import os
import sys
import pandas as pd
import numpy as np

# ==============================================================================
# STEG 4: BUSINESS RULES & EVM ENRICHMENT (SEMANTIC / ACCOUNTING LAYER)
# Prosjekt: GreenPilot 2026 (Elkem Showcase)
# ==============================================================================

CURRENT_DIR = os.getcwd()
if os.path.exists(os.path.join(CURRENT_DIR, "processed", "star_schema")):
    BASE_DIR = CURRENT_DIR
elif os.path.exists(os.path.join(os.path.dirname(CURRENT_DIR), "processed", "star_schema")):
    BASE_DIR = os.path.dirname(CURRENT_DIR)
elif os.path.exists("/workspace/processed/star_schema"):
    BASE_DIR = "/workspace"
else:
    BASE_DIR = CURRENT_DIR

STAR_SCHEMA_DIR = os.path.join(BASE_DIR, "processed", "star_schema")
BUSINESS_READY_DIR = os.path.join(BASE_DIR, "processed", "business_ready")
AUDIT_LOG_DIR = os.path.join(BASE_DIR, "processed", "audit_logs")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")
RAW_DIR = "/workspace/knowledge" if os.path.exists("/workspace/knowledge") else os.path.join(BASE_DIR, "data", "raw")

os.makedirs(BUSINESS_READY_DIR, exist_ok=True)
os.makedirs(AUDIT_LOG_DIR, exist_ok=True)

print("=" * 78)
print("=== STEG 4: BUSINESS RULES & EVM ENRICHMENT (GREENPILOT 2026) ===")
print("=" * 78)
print(f"Kilde for stjernemodell:  {STAR_SCHEMA_DIR}")
print(f"Mål for business ready:   {BUSINESS_READY_DIR}\n")

def read_star(fname: str) -> pd.DataFrame:
    path = os.path.join(STAR_SCHEMA_DIR, fname)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Finner ikke fil i star_schema: {path}")
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    df.columns = [c.strip().strip('"').strip("'").lstrip('\ufeff') for c in df.columns]
    return df

# 1. LAST INN DATA
df_wbs = read_star("Dim_WBS.csv")
df_cost_elem = read_star("Dim_CostElement.csv")
df_gl = read_star("Fact_GLActuals.csv")
df_budget = read_star("Fact_BudgetBaseline.csv")
df_po = read_star("Fact_PurchaseOrders.csv")
df_ap = read_star("Fact_APInvoices.csv")
df_timesheets = read_star("Fact_Timesheets.csv")
df_activities = read_star("Dim_Activity.csv")
df_change_orders = read_star("Fact_ChangeOrders.csv")

# Valutakurser for AP dersom amount_nok ikke allerede finnes
if "amount_nok" not in df_ap.columns:
    fx_path = os.path.join(RAW_DIR, "03_erp_fx_rates.csv")
    if os.path.exists(fx_path):
        df_fx = pd.read_csv(fx_path, sep=";", encoding="utf-8-sig")
        df_fx.columns = [c.strip().strip('"').strip("'").lstrip('\ufeff') for c in df_fx.columns]
        df_ap["period"] = pd.to_datetime(df_ap["invoice_date"]).dt.strftime("%Y-%m")
        df_ap = df_ap.merge(df_fx[["period", "currency", "nok_rate"]], on=["period", "currency"], how="left")
        df_ap["nok_rate"] = df_ap["nok_rate"].fillna(1.0)
        df_ap["amount_nok"] = df_ap["amount_currency"] * df_ap["nok_rate"]
    else:
        df_ap["amount_nok"] = df_ap["amount_currency"]

# ------------------------------------------------------------------------------
# REGELSETT 1: IFRS / IAS 38 KLASSIFISERING (FORSKNING VS. UTVIKLING / AuC)
# ------------------------------------------------------------------------------
ias38_mapping = {
    "WBS-100": {"phase": "Research",    "ias38_treatment": "EXPENSE",   "accounting_bucket": "P&L Operating Expense", "eligible_auc": False},
    "WBS-200": {"phase": "Development", "ias38_treatment": "CAPITALIZE", "accounting_bucket": "Balance Sheet (AuC)",  "eligible_auc": True},
    "WBS-300": {"phase": "Development", "ias38_treatment": "CAPITALIZE", "accounting_bucket": "Balance Sheet (AuC)",  "eligible_auc": True},
    "WBS-400": {"phase": "Development", "ias38_treatment": "CAPITALIZE", "accounting_bucket": "Balance Sheet (AuC)",  "eligible_auc": True},
    "WBS-500": {"phase": "Development", "ias38_treatment": "CAPITALIZE", "accounting_bucket": "Balance Sheet (AuC)",  "eligible_auc": True},
    "WBS-600": {"phase": "Closeout",    "ias38_treatment": "EXPENSE",   "accounting_bucket": "P&L Operating Expense", "eligible_auc": False},
}

print("--- 1. Beriker Dim_WBS med IAS 38 Klassifisering ---")
df_wbs["ias38_phase"] = df_wbs["wbs_id"].map(lambda x: ias38_mapping.get(x, {}).get("phase", "Unknown"))
df_wbs["ias38_treatment"] = df_wbs["wbs_id"].map(lambda x: ias38_mapping.get(x, {}).get("ias38_treatment", "EXPENSE"))
df_wbs["accounting_bucket"] = df_wbs["wbs_id"].map(lambda x: ias38_mapping.get(x, {}).get("accounting_bucket", "P&L Operating Expense"))
df_wbs["eligible_auc"] = df_wbs["wbs_id"].map(lambda x: ias38_mapping.get(x, {}).get("eligible_auc", False))

print("--- 2. Beriker Fact_GLActuals med IAS 38 Behandling ---")
df_gl["ias38_treatment"] = df_gl["wbs_id"].map(lambda x: ias38_mapping.get(x, {}).get("ias38_treatment", "EXPENSE"))
df_gl["accounting_bucket"] = df_gl["wbs_id"].map(lambda x: ias38_mapping.get(x, {}).get("accounting_bucket", "P&L Operating Expense"))

capitalized_actuals = df_gl[df_gl["ias38_treatment"] == "CAPITALIZE"]["amount_nok"].sum()
expensed_actuals = df_gl[df_gl["ias38_treatment"] == "EXPENSE"]["amount_nok"].sum()
total_actuals = df_gl["amount_nok"].sum()

# ------------------------------------------------------------------------------
# REGELSETT 2: OPEN COMMITMENTS & FORPLIKTELSESRESERVE (PO vs AP)
# ------------------------------------------------------------------------------
print("--- 3. Beregner Åpne Forpliktelser (Open Commitments) ---")
matching_file = os.path.join(CLEANED_DIR, "po_3way_matching_summary.csv")
po_invoiced_map = {}

if os.path.exists(matching_file):
    df_match = pd.read_csv(matching_file, sep=";", encoding="utf-8-sig")
    df_match.columns = [c.strip().strip('"').strip("'").lstrip('\ufeff') for c in df_match.columns]
    # Sjekk tilgjengelige kolonner i match-filen (kan hete ap_nok, invoiced_nok osv.)
    inv_col = None
    for cand in ["ap_nok", "invoiced_nok", "amount_nok_ap", "amount_nok"]:
        if cand in df_match.columns:
            inv_col = cand
            break
    if inv_col and "po_line_id" in df_match.columns:
        po_invoiced_map = df_match.set_index("po_line_id")[inv_col].to_dict()

# Fallback til direkte gruppering på df_ap hvis map er tom
if not po_invoiced_map:
    po_invoiced_map = df_ap.groupby("po_line_id")["amount_nok"].sum().to_dict()

df_po["invoiced_nok"] = df_po["po_line_id"].map(lambda x: po_invoiced_map.get(x, 0.0)).fillna(0.0)
df_po["open_commitment_nok"] = np.maximum(0.0, df_po["amount_nok"] - df_po["invoiced_nok"])
total_po_nok = df_po["amount_nok"].sum()
total_invoiced_nok = df_po["invoiced_nok"].sum()
total_open_commitments = df_po["open_commitment_nok"].sum()

# ------------------------------------------------------------------------------
# REGELSETT 3: EVM BASERAPPORT OG ENDRINGSORDRE-JUSTERING
# ------------------------------------------------------------------------------
print("--- 4. Beregner EVM Metrikker og Justert Budsjett (EAC Grunnlag) ---")
bac_initial = df_budget["baseline_budget_nok"].sum()

df_change_orders["approved_amount_nok"] = pd.to_numeric(df_change_orders["approved_amount_nok"], errors="coerce").fillna(0.0)
df_change_orders["requested_amount_nok"] = pd.to_numeric(df_change_orders["requested_amount_nok"], errors="coerce").fillna(0.0)

approved_co = df_change_orders[df_change_orders["status"].isin(["APPROVED", "IMPLEMENTED"])]["approved_amount_nok"].sum()
pending_co = df_change_orders[df_change_orders["status"].isin(["SUBMITTED", "PENDING"])]["requested_amount_nok"].sum()
bac_revised = bac_initial + approved_co

# Fremdriftsberegning basert på aktiviteter i Primavera P6
if "percent_complete" in df_activities.columns:
    df_activities["percent_complete"] = pd.to_numeric(df_activities["percent_complete"], errors="coerce").fillna(0.0)
    avg_progress_pct = df_activities["percent_complete"].mean()
elif "status" in df_activities.columns:
    comp_count = len(df_activities[df_activities["status"] == "Completed"])
    in_prog_count = len(df_activities[df_activities["status"] == "In Progress"])
    avg_progress_pct = ((comp_count * 100.0) + (in_prog_count * 50.0)) / max(1, len(df_activities))
else:
    avg_progress_pct = 75.0

earned_value_initial = bac_initial * (avg_progress_pct / 100.0)
earned_value_revised = bac_revised * (avg_progress_pct / 100.0)

cpi_initial = earned_value_initial / total_actuals if total_actuals > 0 else 1.0
cpi_revised = earned_value_revised / total_actuals if total_actuals > 0 else 1.0

eac_initial = total_actuals + (bac_initial - earned_value_initial)
eac_revised = total_actuals + (bac_revised - earned_value_revised)
vac_initial = bac_initial - eac_initial
vac_revised = bac_revised - eac_revised

# ------------------------------------------------------------------------------
# 5. EKSPORT AV BUSINESS-READY TABELLER
# ------------------------------------------------------------------------------
print("--- 5. Eksporterer Business-Ready Tabeller ---")
df_wbs.to_csv(os.path.join(BUSINESS_READY_DIR, "Dim_WBS_Enriched.csv"), index=False, sep=";")
df_gl.to_csv(os.path.join(BUSINESS_READY_DIR, "Fact_GLActuals_Enriched.csv"), index=False, sep=";")
df_po.to_csv(os.path.join(BUSINESS_READY_DIR, "Fact_PurchaseOrders_Enriched.csv"), index=False, sep=";")

# Bygg sammendragsrapport
summary_data = [
    {"Metric": "Original Budget at Completion (BAC)", "Amount_NOK": bac_initial, "Description": "Opprinnelig godkjent baseline budsjett"},
    {"Metric": "Approved / Implemented Change Orders", "Amount_NOK": approved_co, "Description": "Godkjente endringsordrer som utvider baseline"},
    {"Metric": "Revised Budget at Completion (BAC)", "Amount_NOK": bac_revised, "Description": "Revidert budsjett inkludert godkjente endringer"},
    {"Metric": "Pending / Submitted Change Orders", "Amount_NOK": pending_co, "Description": "Endringsordrer under vurdering"},
    {"Metric": "Total Actual Cost (AC / GL Actuals)", "Amount_NOK": total_actuals, "Description": "Totalt bokført faktisk kostnad"},
    {"Metric": " -> IAS 38 Capitalized to AuC (Development)", "Amount_NOK": capitalized_actuals, "Description": "Aktiveres i balansen som Anlegg under utførelse (WBS 200-500)"},
    {"Metric": " -> IAS 38 Expensed to P&L (Research & Closeout)", "Amount_NOK": expensed_actuals, "Description": "Resultatføres direkte som driftskostnad (WBS 100 & 600)"},
    {"Metric": "Total Purchase Orders Placed", "Amount_NOK": total_po_nok, "Description": "Totalt bestilte innkjøpsordrer omregnet til NOK"},
    {"Metric": "Invoiced Purchase Orders (AP)", "Amount_NOK": total_invoiced_nok, "Description": "Inngående fakturaer registrert mot innkjøp"},
    {"Metric": "Open Commitments (PO Rest)", "Amount_NOK": total_open_commitments, "Description": "Gjenstående forpliktelser under bestilling"},
    {"Metric": "Physical Progress %", "Amount_NOK": avg_progress_pct, "Description": "Gjennomsnittlig fysisk fremdrift i aktiviteter"},
    {"Metric": "Earned Value (EV) - Initial BAC", "Amount_NOK": earned_value_initial, "Description": "Opptjent verdi basert på opprinnelig budsjett"},
    {"Metric": "Cost Performance Index (CPI) - Initial", "Amount_NOK": cpi_initial, "Description": "Kostnadsindeks (EV / AC)"},
    {"Metric": "Estimate at Completion (EAC) - Initial", "Amount_NOK": eac_initial, "Description": "Forventet totalkostnad ved ferdigstillelse"},
    {"Metric": "Variance at Completion (VAC) - Initial", "Amount_NOK": vac_initial, "Description": "Forventet budsjettavvik ved ferdigstillelse"}
]

df_summary = pd.DataFrame(summary_data)
summary_file = os.path.join(AUDIT_LOG_DIR, "business_rules_and_evm_summary.csv")
df_summary.to_csv(summary_file, index=False, sep=";")

print("\n" + "=" * 78)
print("=== BUSINESS RULES & EVM ENRICHMENT SAMMENDRAG ===")
print("=" * 78)
for row in summary_data:
    if "%" in row["Metric"] or "Index" in row["Metric"]:
        print(f" {row['Metric']:<47} : {row['Amount_NOK']:15.2f}")
    else:
        print(f" {row['Metric']:<47} : NOK {row['Amount_NOK']:14,.2f}")
print("=" * 78)
print(f"[OK] Fullført! Business-ready data lagret i: {BUSINESS_READY_DIR}")
print(f"[OK] Ledelsessammendrag lagret i:           {summary_file}")
print("=" * 78 + "\n")
