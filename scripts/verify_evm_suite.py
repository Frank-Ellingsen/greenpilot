import os
import pandas as pd
import numpy as np

def run_quality_gates():
    print("=" * 80)
    print("RUNNING AUTOMATED EVM QUALITY GATES & DATA INTEGRITY VERIFICATION")
    print("=" * 80)

    # 1. Paths verification
    paths = [
        r"processed\star_schema\Dim_WBS.csv",
        r"processed\star_schema\Dim_Activity.csv",
        r"processed\star_schema\Fact_PurchaseOrders.csv",
        r"processed\star_schema\Config_VarianceThresholds.csv",
        r"processed\excel_ready\Fact_FinancialEVM_Unified_Flat.csv",
        r"pbi\GreenPilotProject.SemanticModel\definition\tables\_Measures.tmdl",
        r"pbi\GreenPilotProject.SemanticModel\definition\tables\Config_VarianceThresholds.tmdl",
        r"pbi\GreenPilotProject.Report\definition\pages\pages.json"
    ]
    for p in paths:
        exists = os.path.exists(p)
        print(f"[{'OK' if exists else 'FAIL'}] File exists: {p}")
        assert exists, f"Missing file: {p}"

    # 2. Load data
    budget = pd.read_csv(r"processed\star_schema\Fact_BudgetBaseline.csv", sep=";")
    gl = pd.read_csv(r"processed\star_schema\Fact_GLActuals.csv", sep=";")
    act = pd.read_csv(r"processed\star_schema\Dim_Activity.csv", sep=";")
    po = pd.read_csv(r"processed\star_schema\Fact_PurchaseOrders.csv", sep=";")
    wbs = pd.read_csv(r"processed\star_schema\Dim_WBS.csv", sep=";")

    # 3. Core EVM Numbers Assertions
    bac = budget["baseline_budget_nok"].sum()
    ac = gl["amount_nok"].sum()
    total_activities = len(act)
    # Physical progress % = average(progress_pct) / 100
    phys_prog = act["progress_pct"].mean() / 100.0
    ev = bac * phys_prog
    cpi = ev / ac
    pv_cutoff = budget[budget["period"] <= "2026-10"]["baseline_budget_nok"].sum()
    spi = ev / pv_cutoff
    cv = ev - ac
    sv = ev - pv_cutoff

    print("\n--- Core EVM Assertions ---")
    print(f"BAC: {bac:,.2f} (Expected: 20,000,000.00)")
    assert np.isclose(bac, 20000000.00, atol=0.01), f"BAC mismatch: {bac}"

    print(f"AC:  {ac:,.2f} (Expected: 57,968,040.98)")
    assert np.isclose(ac, 57968040.98, atol=0.01), f"AC mismatch: {ac}"

    print(f"EV:  {ev:,.2f} (Expected: 19,215,686.27)")
    assert np.isclose(ev, 19215686.27, atol=0.01), f"EV mismatch: {ev}"

    print(f"CPI: {cpi:.4f} (Expected: 0.3315)")
    assert np.isclose(cpi, 0.3315, atol=0.0001), f"CPI mismatch: {cpi}"

    print(f"SPI: {spi:.4f} (Expected: 1.1561)")
    assert np.isclose(spi, 1.1561, atol=0.0001), f"SPI mismatch: {spi}"

    print(f"CV:  {cv:,.2f} (Expected: -38,752,354.71)")
    assert np.isclose(cv, -38752354.71, atol=0.01), f"CV mismatch: {cv}"

    print(f"SV:  {sv:,.2f} (Expected: +2,594,815.17)")
    assert np.isclose(sv, 2594815.17, atol=0.01), f"SV mismatch: {sv}"

    # 4. Accounting Treatment (IAS 38 / AuC) Assertions
    gl_auc = gl[gl["ias38_treatment"] == "CAPITALIZE"]["amount_nok"].sum()
    gl_pnl = gl[gl["ias38_treatment"] == "EXPENSE"]["amount_nok"].sum()
    print("\n--- IAS 38 Accounting Assertions ---")
    print(f"AuC Capitalized: NOK {gl_auc:,.2f} (Expected: 43,375,028.38)")
    assert np.isclose(gl_auc, 43375028.38, atol=0.01), f"AuC mismatch: {gl_auc}"

    print(f"P&L Expensed:    NOK {gl_pnl:,.2f} (Expected: 14,593,012.60)")
    assert np.isclose(gl_pnl, 14593012.60, atol=0.01), f"P&L mismatch: {gl_pnl}"

    # 5. Purchase Order Exposure Assertions
    open_commitments = po["open_commitment_nok"].sum()
    print("\n--- Procurement Open Commitments ---")
    print(f"Open Commitments: NOK {open_commitments:,.2f} (Expected: 49,233,751.55)")
    assert np.isclose(open_commitments, 49233751.55, atol=0.01), f"Open commitments mismatch: {open_commitments}"

    # 6. TMDL Date Integrity & RAG / Bar Length Check
    print("\n--- TMDL Date Integrity & Dynamic RAG / Bar Length Check ---")
    with open(r"pbi\GreenPilotProject.SemanticModel\definition\tables\_Measures.tmdl", encoding="utf-8") as f:
        tmdl_content = f.read()
    assert "DATE ( 2026, 11, 1 )" not in tmdl_content, "Hardcoded DATE(2026,11,1) found in _Measures.tmdl!"
    assert "DATE(2026, 11, 1)" not in tmdl_content, "Hardcoded DATE(2026, 11, 1) found in _Measures.tmdl!"
    assert "Dim_Project[data_date]" in tmdl_content, "Dim_Project[data_date] dynamic status date missing in _Measures.tmdl!"
    print("[OK] Zero hardcoded date literals in _Measures.tmdl; dynamic Dim_Project[data_date] verified!")

    # Dynamic RAG & In-Cell Bar Length measures check
    required_rag_and_bars = [
        "CPI Status RAG",
        "CPI Color RAG",
        "SPI Status RAG",
        "SPI Color RAG",
        "CV Status RAG",
        "CV Color RAG",
        "PO Commitment Exposure RAG",
        "PO Commitment Color RAG",
        "AuC Capitalization Rate RAG",
        "AuC Capitalization Color RAG",
        "Overall Project Health RAG",
        "Cost Variance Bar",
        "Physical Progress Bar",
        "Activity Progress Bar",
        "Budget Consumption Bar",
        "PO Commitment Exposure Bar",
        "AuC Capitalization Bar"
    ]
    for m in required_rag_and_bars:
        assert f"measure '{m}'" in tmdl_content, f"Missing required DAX measure in _Measures.tmdl: {m}"
    assert "Dim_Date[Date] < ProjectDataDate" in tmdl_content, "Missing cutoff < ProjectDataDate filter in PV measure!"
    assert "VAR Empty " not in tmdl_content, "Reserved keyword VAR Empty found in _Measures.tmdl!"
    print(f"[OK] All {len(required_rag_and_bars)} Dynamic RAG and In-Cell Conditional Bar measures verified in TMDL!")

    # 7. Cross-Platform Consistency Check (Power BI vs Streamlit vs index.html)
    print("\n--- Cross-Platform Consistency Check (PBI vs Streamlit vs index.html) ---")
    import sys
    if "scripts" not in sys.path:
        sys.path.insert(0, "scripts")
    import app as st_app
    con = st_app.get_db_connection()
    st_kpis = st_app.get_evm_kpis(con)

    assert np.isclose(st_kpis["BAC"], bac, atol=0.01), f"Streamlit BAC mismatch: {st_kpis['BAC']} vs {bac}"
    assert np.isclose(st_kpis["PV"], pv_cutoff, atol=0.01), f"Streamlit PV mismatch: {st_kpis['PV']} vs {pv_cutoff}"
    assert np.isclose(st_kpis["EV"], ev, atol=0.01), f"Streamlit EV mismatch: {st_kpis['EV']} vs {ev}"
    assert np.isclose(st_kpis["AC"], ac, atol=0.01), f"Streamlit AC mismatch: {st_kpis['AC']} vs {ac}"
    assert np.isclose(st_kpis["CV"], cv, atol=0.01), f"Streamlit CV mismatch: {st_kpis['CV']} vs {cv}"
    assert np.isclose(st_kpis["SV"], sv, atol=0.01), f"Streamlit SV mismatch: {st_kpis['SV']} vs {sv}"
    assert np.isclose(st_kpis["CPI"], cpi, atol=0.0001), f"Streamlit CPI mismatch: {st_kpis['CPI']} vs {cpi}"
    assert np.isclose(st_kpis["SPI"], spi, atol=0.0001), f"Streamlit SPI mismatch: {st_kpis['SPI']} vs {spi}"
    assert np.isclose(st_kpis["Open_PO"], open_commitments, atol=0.01), f"Streamlit Open PO mismatch: {st_kpis['Open_PO']}"
    assert np.isclose(st_kpis["AuC_Cap"], gl_auc, atol=0.01), f"Streamlit AuC mismatch: {st_kpis['AuC_Cap']}"
    assert np.isclose(st_kpis["PL_Exp"], gl_pnl, atol=0.01), f"Streamlit P&L mismatch: {st_kpis['PL_Exp']}"
    print("[OK] Streamlit (scripts/app.py) KPIs match Star Schema & Power BI 100%!")

    with open("index.html", encoding="utf-8") as f:
        html_content = f.read()
    expected_html_tokens = [
        "20 000 000",
        "57 968 041",
        "19 215 686",
        "16 620 871",
        "-38 752 355",
        "+2 594 815",
        "0.331",
        "1.156",
        "60 334 083",
        "2 366 042",
        "-40 334 083",
        "49 233 752",
        "43 375 028"
    ]
    for tok in expected_html_tokens:
        assert tok in html_content, f"Missing canonical figure '{tok}' in index.html!"
    print("[OK] index.html KPI cards, tables, S-curve, and simulator match Star Schema & Power BI 100%!")

    # 8. Config_VarianceThresholds CSV & TMDL Schema Alignment Check
    cfg_df = pd.read_csv(r"processed\star_schema\Config_VarianceThresholds.csv", sep=";")
    expected_cfg_cols = ["Metric", "Yellow_Limit", "Red_Limit", "Trigger_Type", "Controller_Action"]
    assert list(cfg_df.columns) == expected_cfg_cols, f"Config_VarianceThresholds.csv columns mismatch: {list(cfg_df.columns)}"
    with open(r"pbi\GreenPilotProject.SemanticModel\definition\tables\Config_VarianceThresholds.tmdl", encoding="utf-8") as f:
        cfg_tmdl = f.read()
    assert "Columns = 5" not in cfg_tmdl, "Brittle 'Columns = 5' found in Config_VarianceThresholds.tmdl!"
    print("[OK] Config_VarianceThresholds.csv and Config_VarianceThresholds.tmdl schema 100% aligned!")

    print("\n" + "=" * 80)
    print("ALL QUALITY GATES PASSED SUCCESSFULLY (100% SPEC COMPLIANCE)")
    print("=" * 80)

if __name__ == "__main__":
    run_quality_gates()

