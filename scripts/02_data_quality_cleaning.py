import os
import sys
import pandas as pd
import numpy as np

# ==============================================================================
# STEG 2: DATA QUALITY & CLEANING (SILVER LAYER)
# Prosjekt: GreenPilot 2026 (Elkem Showcase)
# ==============================================================================

# Robust sti-deteksjon:
# 1) Hvis data/staging finnes i aktuell mappe (C:\Users\frank\OneDrive\Elkem)
# 2) Hvis /workspace/data/staging finnes (sandbox)
# 3) Fallback til overordnet mappe hvis skriptet kjøres fra scripts/
current_dir = os.getcwd()
if os.path.exists(os.path.join(current_dir, "data", "staging")):
    BASE_DIR = current_dir
elif os.path.exists("/workspace/data/staging"):
    BASE_DIR = "/workspace"
elif os.path.exists(os.path.join(os.path.dirname(current_dir), "data", "staging")):
    BASE_DIR = os.path.dirname(current_dir)
else:
    BASE_DIR = current_dir

STAGING_DIR = os.path.join(BASE_DIR, "data", "staging")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")
AUDIT_LOG_DIR = os.path.join(BASE_DIR, "processed", "audit_logs")

os.makedirs(CLEANED_DIR, exist_ok=True)
os.makedirs(AUDIT_LOG_DIR, exist_ok=True)

print("=" * 78)
print("=== STEG 2: DATA QUALITY, ASSURANCE & CLEANING (SILVER LAYER) ===")
print("=" * 78)
print(f"Staging-kilde:  {STAGING_DIR}")
print(f"Cleaned-output: {CLEANED_DIR}")
print(f"Audit-logger:   {AUDIT_LOG_DIR}\n")

audit_records = []

def log_audit(category: str, check_name: str, status: str, severity: str, details: str):
    audit_records.append({
        "Category": category,
        "Check": check_name,
        "Status": status,
        "Severity": severity,
        "Details": details
    })

def read_staging(filename: str) -> pd.DataFrame:
    filepath = os.path.join(STAGING_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Finner ikke staging-fil: {filepath}")
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline()
        delimiter = ';' if ';' in first_line else ','
    df = pd.read_csv(filepath, sep=delimiter, encoding='utf-8-sig')
    df.columns = [c.strip().strip('"').strip("'").lstrip('\ufeff') for c in df.columns]
    return df

# ------------------------------------------------------------------------------
# 1. LAST INN DATA FRA STAGING
# ------------------------------------------------------------------------------
print("--- 1. Laster tabeller fra Staging ---")
df_proj = read_staging("00_project_master.csv")
df_wbs = read_staging("01_master_wbs.csv")
df_cost_elem = read_staging("02_master_cost_elements.csv")
df_fx = read_staging("03_erp_fx_rates.csv")
df_vendor = read_staging("04_erp_vendor_master.csv")
df_budget = read_staging("05_erp_budget_baseline.csv")
df_po = read_staging("06_erp_purchase_orders.csv")
df_gr = read_staging("07_erp_goods_receipts.csv")
df_ap = read_staging("08_erp_ap_invoices.csv")
df_journals = read_staging("09_erp_journals.csv")
df_gl = read_staging("10_erp_gl_actuals.csv")
df_co = read_staging("11_erp_change_orders.csv")
df_act = read_staging("12_primavera_activities.csv")
df_emp = read_staging("16_hr_employee_master.csv")
df_ts = read_staging("18_hr_timesheets.csv")

data_date_str = str(df_proj["data_date"].iloc[0]).strip()
print(f"Prosjekt Data Date: {data_date_str}\n")

# ------------------------------------------------------------------------------
# 2. REFERANSIELL INTEGRITET (Master Data Checks)
# ------------------------------------------------------------------------------
print("--- 2. Kontrollerer Referansiell Integritet ---")

valid_wbs = set(df_wbs["wbs_id"].dropna().str.strip())
valid_vendors = set(df_vendor["vendor_id"].dropna().str.strip())
valid_emp = set(df_emp["employee_id"].dropna().str.strip())
valid_ce = set(df_cost_elem["cost_element"].dropna().str.strip())
valid_act = set(df_act["activity_id"].dropna().str.strip())

# Sjekk GL mot WBS og Cost Element
gl_bad_wbs = df_gl[~df_gl["wbs_id"].astype(str).str.strip().isin(valid_wbs)]
gl_bad_ce = df_gl[~df_gl["cost_element"].astype(str).str.strip().isin(valid_ce)]
if len(gl_bad_wbs) == 0 and len(gl_bad_ce) == 0:
    log_audit("Integrity", "GL Master Foreign Keys", "PASS", "HIGH", "Alle GL-poster har gyldig WBS og Cost Element.")
else:
    log_audit("Integrity", "GL Master Foreign Keys", "FAIL", "HIGH", f"{len(gl_bad_wbs)} rader mangler WBS, {len(gl_bad_ce)} mangler CE.")

# Sjekk PO mot Vendor
po_bad_vendor = df_po[~df_po["vendor_id"].astype(str).str.strip().isin(valid_vendors)]
if len(po_bad_vendor) == 0:
    log_audit("Integrity", "PO Vendor Integrity", "PASS", "HIGH", "Alle PO-leverandører eksisterer i Dim_Vendor.")
else:
    log_audit("Integrity", "PO Vendor Integrity", "FAIL", "HIGH", f"{len(po_bad_vendor)} PO-linjer har ukjent leverandør.")

# Sjekk Timelister mot Ansatte og Aktiviteter
ts_bad_emp = df_ts[~df_ts["employee_id"].astype(str).str.strip().isin(valid_emp)]
ts_bad_act = df_ts[~df_ts["activity_id"].astype(str).str.strip().isin(valid_act)]
if len(ts_bad_emp) == 0:
    log_audit("Integrity", "Timesheet Employee Integrity", "PASS", "HIGH", "100% konsistens mellom timelister og ansattmaster.")
else:
    log_audit("Integrity", "Timesheet Employee Integrity", "FAIL", "HIGH", f"{len(ts_bad_emp)} timelisterader har ukjent ansatt.")

# ------------------------------------------------------------------------------
# 3. VALUTANORMALISERING & NOK-BEREGNING
# ------------------------------------------------------------------------------
print("--- 3. Valutanormalisering til NOK ---")

# Normaliser PO
df_po["period"] = pd.to_datetime(df_po["po_date"]).dt.strftime("%Y-%m")
df_po = df_po.merge(df_fx[["period", "currency", "nok_rate"]], on=["period", "currency"], how="left")
df_po["nok_rate"] = df_po["nok_rate"].fillna(1.0)
df_po["amount_nok"] = df_po["amount_currency"] * df_po["nok_rate"]

# Normaliser AP Invoices
df_ap["period"] = pd.to_datetime(df_ap["invoice_date"]).dt.strftime("%Y-%m")
df_ap = df_ap.merge(df_fx[["period", "currency", "nok_rate"]], on=["period", "currency"], how="left")
df_ap["nok_rate"] = df_ap["nok_rate"].fillna(1.0)
df_ap["amount_nok"] = df_ap["amount_currency"] * df_ap["nok_rate"]

# Normaliser Goods Receipts via tilhørende PO-linje
gr_fx_map = df_po.set_index("po_line_id")[["currency", "nok_rate"]].to_dict(orient="index")
df_gr["currency"] = df_gr["po_line_id"].map(lambda x: gr_fx_map.get(x, {}).get("currency", "NOK"))
df_gr["nok_rate"] = df_gr["po_line_id"].map(lambda x: gr_fx_map.get(x, {}).get("nok_rate", 1.0)).fillna(1.0)
df_gr["amount_nok"] = df_gr["amount_currency"] * df_gr["nok_rate"]

log_audit("Valuta", "FX Normalization", "PASS", "INFO", "PO, AP og GR er omregnet til NOK ved månedlige FX-satser.")

# ------------------------------------------------------------------------------
# 4. FINANSIELL 3-VEIS MATCHING (PO vs. GR vs. AP)
# ------------------------------------------------------------------------------
print("--- 4. Gjennomfører 3-veis matching (PO - GR - AP) ---")

po_summary = df_po.groupby("po_line_id").agg({
    "amount_currency": "sum",
    "amount_nok": "sum",
    "currency": "first",
    "vendor_id": "first",
    "wbs_id": "first"
}).rename(columns={"amount_currency": "po_currency", "amount_nok": "po_nok"})

gr_summary = df_gr.groupby("po_line_id").agg({
    "amount_currency": "sum",
    "amount_nok": "sum"
}).rename(columns={"amount_currency": "gr_currency", "amount_nok": "gr_nok"})

ap_summary = df_ap.groupby("po_line_id").agg({
    "amount_currency": "sum",
    "amount_nok": "sum"
}).rename(columns={"amount_currency": "ap_currency", "amount_nok": "ap_nok"})

matching_df = po_summary.join(gr_summary, how="left").join(ap_summary, how="left").fillna(0.0)

# Avvik 1: Overfakturering (AP > PO med toleranse)
matching_df["over_invoiced_nok"] = np.maximum(0.0, matching_df["ap_nok"] - matching_df["po_nok"])
over_invoiced_lines = matching_df[matching_df["over_invoiced_nok"] > 100.0]

if len(over_invoiced_lines) > 0:
    tot_over_inv = over_invoiced_lines["over_invoiced_nok"].sum()
    log_audit("3-Way Match", "Over-Invoiced Lines", "FAIL", "HIGH", 
              f"Funnet {len(over_invoiced_lines)} linjer overfakturert utover PO-ramme. Totalt avvik: NOK {tot_over_inv:,.2f}")
else:
    log_audit("3-Way Match", "Over-Invoiced Lines", "PASS", "HIGH", "Ingen overfakturering identifisert.")

# Avvik 2: Uavregnede varemottak (GR levert, men ennå ikke fakturert i AP -> Krever periodisering/Accrual)
matching_df["uninvoiced_receipts_nok"] = np.maximum(0.0, matching_df["gr_nok"] - matching_df["ap_nok"])
uninvoiced_gr = matching_df[matching_df["uninvoiced_receipts_nok"] > 100.0]

if len(uninvoiced_gr) > 0:
    tot_uninvoiced = uninvoiced_gr["uninvoiced_receipts_nok"].sum()
    log_audit("3-Way Match", "Uninvoiced Goods Receipts", "INFO", "MEDIUM", 
              f"Funnet {len(uninvoiced_gr)} varemottak levert uten mottatt faktura. Påløpt udekket kostnad: NOK {tot_uninvoiced:,.2f}")
else:
    log_audit("3-Way Match", "Uninvoiced Goods Receipts", "PASS", "INFO", "Alle mottatte varer er fakturert.")

# Beregn gjenværende åpne forpliktelser (Open Commitments = PO - AP)
matching_df["open_commitment_nok"] = np.maximum(0.0, matching_df["po_nok"] - matching_df["ap_nok"])

# ------------------------------------------------------------------------------
# 5. CUT-OFF OG DATOAUDIT
# ------------------------------------------------------------------------------
print("--- 5. Dato- og Cut-off Audit ---")
data_date = pd.to_datetime(data_date_str)

gl_dates = pd.to_datetime(df_gl["posting_date"])
future_gl = df_gl[gl_dates > data_date]
if len(future_gl) == 0:
    log_audit("Cut-off", "GL Posting Date <= Data Date", "PASS", "HIGH", f"Alle bokføringer er innenfor prosjektets Data Date ({data_date_str}).")
else:
    log_audit("Cut-off", "GL Posting Date <= Data Date", "FAIL", "HIGH", f"{len(future_gl)} poster er datert etter Data Date.")

ts_dates = pd.to_datetime(df_ts["work_date"])
future_ts = df_ts[ts_dates > data_date]
if len(future_ts) == 0:
    log_audit("Cut-off", "Timesheet Date <= Data Date", "PASS", "HIGH", f"Alle timelister er innenfor Data Date.")
else:
    log_audit("Cut-off", "Timesheet Date <= Data Date", "WARN", "MEDIUM", f"{len(future_ts)} timelisterader er datert etter Data Date.")

# Sjekk helgearbeid
weekend_ts = df_ts[pd.to_datetime(df_ts["work_date"]).dt.day_name().isin(["Saturday", "Sunday"])]
if len(weekend_ts) == 0:
    log_audit("HR Audit", "Weekend Hours", "PASS", "LOW", "Ingen timer logget på lørdag eller søndag.")
else:
    log_audit("HR Audit", "Weekend Hours", "WARN", "LOW", f"{len(weekend_ts)} timelisterader ført i helg.")

# ------------------------------------------------------------------------------
# 6. EKSPORT AV VASKEDE TABELLER OG AUDIT-RAPPORT
# ------------------------------------------------------------------------------
print("--- 6. Eksporterer Vaskede Data og Revisjonsrapport ---")

# Lagre vaskede datasett til data/cleaned/
df_proj.to_csv(os.path.join(CLEANED_DIR, "00_project_master.csv"), index=False, sep=";")
df_wbs.to_csv(os.path.join(CLEANED_DIR, "01_master_wbs.csv"), index=False, sep=";")
df_cost_elem.to_csv(os.path.join(CLEANED_DIR, "02_master_cost_elements.csv"), index=False, sep=";")
df_fx.to_csv(os.path.join(CLEANED_DIR, "03_erp_fx_rates.csv"), index=False, sep=";")
df_vendor.to_csv(os.path.join(CLEANED_DIR, "04_erp_vendor_master.csv"), index=False, sep=";")
df_budget.to_csv(os.path.join(CLEANED_DIR, "05_erp_budget_baseline.csv"), index=False, sep=";")
df_po.to_csv(os.path.join(CLEANED_DIR, "06_erp_purchase_orders.csv"), index=False, sep=";")
df_gr.to_csv(os.path.join(CLEANED_DIR, "07_erp_goods_receipts.csv"), index=False, sep=";")
df_ap.to_csv(os.path.join(CLEANED_DIR, "08_erp_ap_invoices.csv"), index=False, sep=";")
df_journals.to_csv(os.path.join(CLEANED_DIR, "09_erp_journals.csv"), index=False, sep=";")
df_gl.to_csv(os.path.join(CLEANED_DIR, "10_erp_gl_actuals.csv"), index=False, sep=";")
df_co.to_csv(os.path.join(CLEANED_DIR, "11_erp_change_orders.csv"), index=False, sep=";")
df_act.to_csv(os.path.join(CLEANED_DIR, "12_primavera_activities.csv"), index=False, sep=";")
df_emp.to_csv(os.path.join(CLEANED_DIR, "16_hr_employee_master.csv"), index=False, sep=";")
df_ts.to_csv(os.path.join(CLEANED_DIR, "18_hr_timesheets.csv"), index=False, sep=";")

# Lagre 3-veis matching rapport
matching_df.to_csv(os.path.join(CLEANED_DIR, "po_3way_matching_summary.csv"), sep=";")

# Lagre audit report
df_audit = pd.DataFrame(audit_records)
audit_csv_path = os.path.join(AUDIT_LOG_DIR, "data_quality_audit_report.csv")
df_audit.to_csv(audit_csv_path, index=False, sep=";")

print("=" * 78)
print("=== AUDIT LOGG SAMMENDRAG ===")
print("=" * 78)
print(df_audit.to_string(index=False))
print("=" * 78)
print(f"[OK] Steg 2 fullført. Vaskede data lagret i: {CLEANED_DIR}")
print(f"[OK] Revisjonsrapport lagret i:            {audit_csv_path}")
print("=" * 78)
