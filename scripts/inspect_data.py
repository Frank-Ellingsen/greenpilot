import os
import glob
import duckdb
import pandas as pd

con = duckdb.connect()

csv_files = glob.glob('processed/star_schema/*.csv')
for f in csv_files:
    raw_name = os.path.splitext(os.path.basename(f))[0]
    # Standardize table name cleanly:
    # e.g. Fact_GLActuals -> fact_gl_actuals, Fact_BudgetBaseline -> fact_budget_baseline
    mapping = {
        'Config_VarianceThresholds': 'config_variance_thresholds',
        'Dim_Activity': 'dim_activity',
        'Dim_CostElement': 'dim_cost_element',
        'Dim_Date': 'dim_date',
        'Dim_Employee': 'dim_employee',
        'Dim_Project': 'dim_project',
        'Dim_Resource': 'dim_resource',
        'Dim_Vendor': 'dim_vendor',
        'Dim_WBS': 'dim_wbs',
        'Fact_APInvoices': 'fact_ap_invoices',
        'Fact_BudgetBaseline': 'fact_budget_baseline',
        'Fact_CapacityCalendar': 'fact_capacity_calendar',
        'Fact_ChangeOrders': 'fact_change_orders',
        'Fact_GLActuals': 'fact_gl_actuals',
        'Fact_GoodsReceipts': 'fact_goods_receipts',
        'Fact_Journals': 'fact_journals',
        'Fact_PurchaseOrders': 'fact_purchase_orders',
        'Fact_ResourceAssignments': 'fact_resource_assignments',
        'Fact_Timesheets': 'fact_timesheets'
    }
    snake_name = mapping.get(raw_name, raw_name.lower())
    
    df = pd.read_csv(f, sep=';', encoding='utf-8-sig')
    # Save to parquet as well
    parquet_path = f"processed/star_schema/{snake_name}.parquet"
    df.to_parquet(parquet_path, index=False)
    # Also save with original name
    df.to_parquet(f"processed/star_schema/{raw_name}.parquet", index=False)
    
    con.register(snake_name, df)
    print(f"Loaded {raw_name} -> {snake_name} ({len(df)} rows)")

print("\n--- BENCHMARK EVM CHECKS ---")
bac = con.execute("SELECT SUM(baseline_budget_nok) FROM fact_budget_baseline").fetchone()[0]
ac = con.execute("SELECT SUM(amount_nok) FROM fact_gl_actuals").fetchone()[0]
po_tot = con.execute("SELECT SUM(amount_nok) FROM fact_purchase_orders").fetchone()[0]
open_po = con.execute("SELECT SUM(open_amount_nok) FROM fact_purchase_orders").fetchone()[0] if 'open_amount_nok' in df.columns else None

# Check columns of tables
for t in ['dim_date', 'fact_gl_actuals', 'dim_wbs', 'fact_purchase_orders']:
    cols = [c[0] for c in con.execute(f"DESCRIBE {t}").fetchall()]
    print(f"{t} cols:", cols)

open_po = con.execute("SELECT SUM(open_commitment_nok) FROM fact_purchase_orders").fetchone()[0]
print(f"BAC: {bac:,.2f}")
print(f"AC:  {ac:,.2f}")
print(f"PO Total: {po_tot:,.2f}")
print(f"Open PO Commitments: {open_po:,.2f}")

print("\n--- MONTHLY BREAKDOWN (Posting Month) ---")
res = con.execute("""
    SELECT 
        SUBSTR(posting_date, 1, 7) as period,
        SUM(amount_nok) as ac_monthly
    FROM fact_gl_actuals
    GROUP BY SUBSTR(posting_date, 1, 7)
    ORDER BY period
""").fetchall()
for r in res:
    print(r)

print("\n--- WBS ACTUALS ---")
wbs_res = con.execute("""
    SELECT 
        w.wbs_id,
        w.wbs_name,
        SUM(g.amount_nok) as ac
    FROM dim_wbs w
    LEFT JOIN fact_gl_actuals g ON w.wbs_id = g.wbs_id
    GROUP BY w.wbs_id, w.wbs_name
    ORDER BY w.wbs_id
""").fetchall()
for r in wbs_res:
    print(r)

print("\n--- WBS BUDGET ---")
wbs_b = con.execute("""
    SELECT 
        w.wbs_id,
        w.wbs_name,
        SUM(b.baseline_budget_nok) as bac
    FROM dim_wbs w
    LEFT JOIN fact_budget_baseline b ON w.wbs_id = b.wbs_id
    GROUP BY w.wbs_id, w.wbs_name
    ORDER BY w.wbs_id
""").fetchall()
for r in wbs_b:
    print(r)

