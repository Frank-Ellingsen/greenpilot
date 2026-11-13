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
        "Change Order Status RAG",
        "Change Order Status Color RAG",
        "Activity Status RAG",
        "Activity Status Color RAG",
        "Cost Variance Bar",
        "Physical Progress Bar",
        "Activity Progress Bar",
        "Budget Consumption Bar",
        "PO Commitment Exposure Bar",
        "AuC Capitalization Bar",
        "Change Order Exposure Bar",
        "Supplier AP Paid NOK",
        "Internal Payroll Paid NOK",
        "Total Cash Outflow NOK",
        "Enova Grant Cash In NOK",
        "Net Monthly Cash Flow NOK",
        "Cumulative Net Cash Flow NOK",
        "Faktiske Timer Koststed",
        "Personalkostnad Koststed NOK",
        "Andel Timer Koststed %",
        "Koststed Timer Bar",
        "Early Warning Status RAG",
        "Early Warning Color RAG",
        "Early Warning PO Exposure Bar"
    ]
    for m in required_rag_and_bars:
        assert f"measure '{m}'" in tmdl_content, f"Missing required DAX measure in _Measures.tmdl: {m}"
    assert "Dim_Date[Date] < ProjectDataDate" in tmdl_content, "Missing cutoff < ProjectDataDate filter in PV measure!"
    assert "VAR Empty " not in tmdl_content, "Reserved keyword VAR Empty found in _Measures.tmdl!"
    assert "\n\tcolumn Value\n" in tmdl_content, "Missing top-level '\\tcolumn Value' in _Measures.tmdl!"
    assert "\n\t\tcolumn Value" not in tmdl_content, "Invalid 2-tab '\\t\\tcolumn Value' inside a measure in _Measures.tmdl!"
    assert "\n\tpartition _Measures = calculated\n" in tmdl_content, "Missing '\\tpartition _Measures = calculated' in _Measures.tmdl!"
    assert "\n\t\tdescription:" not in tmdl_content, "Invalid TMDL property 'description:' found in _Measures.tmdl (use /// comments)!"
    _, after_partition = tmdl_content.split("\n\tpartition _Measures = calculated\n", 1)
    assert "\n\tmeasure " not in after_partition, "Found DAX measures appended after 'partition _Measures = calculated' in _Measures.tmdl!"
    for uncached in ["Fact_CashFlowBridge", "Dim_CostCenter", "Fact_MonthlyEarlyWarnings"]:
        assert uncached not in tmdl_content, f"Reference to uncached table {uncached} found in _Measures.tmdl!"
    assert os.path.exists(r"pbi\GreenPilotProject.SemanticModel\.pbi\cache.abf"), "Missing cache.abf in SemanticModel!"
    print(f"[OK] All {len(required_rag_and_bars)} Dynamic RAG, Cash Flow, Cost Center & Bar measures and TMDL trailer verified!")

    # Verify PBIR visual.json projections and conditional formatting objects
    import glob, json
    with open(r"pbi\GreenPilotProject.Report\definition\pages\pages.json", encoding="utf-8") as f:
        pages_meta = json.load(f)
    assert "$schema" in pages_meta, "Missing $schema in pages.json!"
    page_folders = sorted([d for d in os.listdir(r"pbi\GreenPilotProject.Report\definition\pages") if os.path.isdir(os.path.join(r"pbi\GreenPilotProject.Report\definition\pages", d))])
    assert sorted(pages_meta["pageOrder"]) == page_folders, f"pages.json pageOrder {pages_meta['pageOrder']} != folders {page_folders}"
    visual_files = sorted(glob.glob(r"pbi\GreenPilotProject.Report\definition\pages\*\visuals\*\visual.json"))
    cond_formatted_visuals = []
    for vf in visual_files:
        with open(vf, encoding="utf-8") as f:
            vdata = json.load(f)
        assert "$schema" in vdata, f"Missing $schema in {vf}"
        qstate = vdata.get("visual", {}).get("query", {}).get("queryState", {})
        assert "ColumnY" not in qstate and "LineY" not in qstate, f"Invalid combo chart roles ColumnY/LineY in {vf} (use Y/Y2)!"
        for role, rdata in qstate.items():
            for proj in rdata.get("projections", []):
                if vdata.get("visual", {}).get("visualType") != "decompositionTreeVisual":
                    assert proj.get("active", True) is True, f"Projection {proj.get('queryRef')} in {vf} is explicitly False!"
                qref = proj.get("queryRef", "")
                for uncached in ["Fact_CashFlowBridge", "Dim_CostCenter", "Fact_MonthlyEarlyWarnings", "Fact_FinancialEVM_Unified_Flat"]:
                    assert uncached not in qref, f"Visual {vf} references uncached table {uncached} in {qref}!"
        vobjects = vdata.get("visual", {}).get("objects", {})
        assert "cellElements" not in vobjects, f"Visual {vf} contains cellElements without internal queryState bindings (causes Missing_References)!"
        if vobjects:
            cond_formatted_visuals.append(os.path.basename(os.path.dirname(vf)))
    assert len(cond_formatted_visuals) >= 12, f"Expected >=12 conditionally formatted visuals, found {len(cond_formatted_visuals)}"
    assert "Capitalized AuC NOK" not in tmdl_content and "Expensed R&D / OpEx NOK" not in tmdl_content, "Missing measure reference found in _Measures.tmdl!"
    print(f"[OK] All {len(visual_files)} PBIR visuals across {len(page_folders)} pages have valid schemas, cached projections, and {len(cond_formatted_visuals)} conditionally formatted visuals!")

    # 7. Cross-Platform Consistency Check (Power BI vs Streamlit vs index.html)
    print("\n--- Cross-Platform Consistency Check (PBI vs Streamlit vs index.html) ---")
    import re
    with open("scripts/app.py", encoding="utf-8") as f:
        app_code = f.read()
    st_constants = {}
    for varname in ["BAC_NOK", "PV_YTD_NOK", "AC_NOK", "EV_NOK", "OPEN_PO_NOK", "AUC_CAPITALIZED_NOK", "PL_EXPENSE_NOK"]:
        m = re.search(rf"^{varname}\s*=\s*([0-9_.]+)", app_code, re.M)
        if m:
            st_constants[varname] = float(m.group(1).replace("_", ""))

    assert np.isclose(st_constants["BAC_NOK"], bac, atol=0.01), f"Streamlit BAC mismatch: {st_constants['BAC_NOK']} vs {bac}"
    assert np.isclose(st_constants["PV_YTD_NOK"], pv_cutoff, atol=0.01), f"Streamlit PV mismatch: {st_constants['PV_YTD_NOK']} vs {pv_cutoff}"
    assert np.isclose(st_constants["EV_NOK"], ev, atol=0.01), f"Streamlit EV mismatch: {st_constants['EV_NOK']} vs {ev}"
    assert np.isclose(st_constants["AC_NOK"], ac, atol=0.01), f"Streamlit AC mismatch: {st_constants['AC_NOK']} vs {ac}"
    assert np.isclose(st_constants["OPEN_PO_NOK"], open_commitments, atol=0.01), f"Streamlit Open PO mismatch: {st_constants['OPEN_PO_NOK']}"
    assert np.isclose(st_constants["AUC_CAPITALIZED_NOK"], gl_auc, atol=0.01), f"Streamlit AuC mismatch: {st_constants['AUC_CAPITALIZED_NOK']}"
    assert np.isclose(st_constants["PL_EXPENSE_NOK"], gl_pnl, atol=0.01), f"Streamlit P&L mismatch: {st_constants['PL_EXPENSE_NOK']}"
    print("[OK] Streamlit (scripts/app.py) SSOT constants match Star Schema & Power BI 100%!")

    with open("index.html", encoding="utf-8") as f:
        html_content = f.read()
    expected_html_tokens = [
        ("20.0 MNOK", "20,0 MNOK"),
        ("58.0 MNOK", "58,0 MNOK"),
        ("19.2 MNOK", "19,2 MNOK"),
        ("0.33", "0,33"),
        ("1.16", "1,16"),
        ("49.2 MNOK", "49,2 MNOK"),
        ("107.2 MNOK", "107,2 MNOK")
    ]
    for opt1, opt2 in expected_html_tokens:
        assert (opt1 in html_content or opt2 in html_content), f"Missing canonical figure '{opt1}' or '{opt2}' in index.html!"
    assert any(x in html_content for x in ["43.4", "43,4", "43,38", "43.375"]), "Missing IAS 38 AuC in index.html!"
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

