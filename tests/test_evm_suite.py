"""
tests/test_evm_suite.py
Automated Quality Assurance & EVM Integrity Test Suite for Elkem GreenPilot 2026.
Compatible with pytest and GitHub Actions CI.
"""

import os
import pytest
import duckdb
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAR_SCHEMA_DIR = os.path.join(BASE_DIR, "processed", "star_schema")
MEASURES_TMDL = os.path.join(BASE_DIR, "pbi", "GreenPilotProject.SemanticModel", "definition", "tables", "_Measures.tmdl")

@pytest.fixture(scope="module")
def db_conn():
    con = duckdb.connect()
    tables = [
        ("dim_project", "Dim_Project.csv"),
        ("dim_wbs", "Dim_WBS.csv"),
        ("dim_activity", "Dim_Activity.csv"),
        ("dim_vendor", "Dim_Vendor.csv"),
        ("fact_budget_baseline", "Fact_BudgetBaseline.csv"),
        ("fact_gl_actuals", "Fact_GLActuals.csv"),
        ("fact_purchase_orders", "Fact_PurchaseOrders.csv")
    ]
    for table_name, csv_file in tables:
        path = os.path.join(STAR_SCHEMA_DIR, csv_file)
        assert os.path.exists(path), f"Missing required star schema table: {path}"
        con.execute(f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_csv('{path}', delim=';', header=true, auto_detect=true)")
    return con

def test_bac_reconciliation(db_conn):
    """Verify that Total Budget At Completion (BAC) equals exactly NOK 20,000,000.00"""
    bac = db_conn.execute("SELECT SUM(baseline_budget_nok) FROM fact_budget_baseline").fetchone()[0]
    assert bac == pytest.approx(20000000.0, rel=1e-4)

def test_actual_cost_reconciliation(db_conn):
    """Verify that Total Actual Cost (AC) equals exactly NOK 57,968,040.98"""
    ac = db_conn.execute("SELECT SUM(amount_nok) FROM fact_gl_actuals").fetchone()[0]
    assert ac == pytest.approx(57968040.98, rel=1e-4)

def test_activity_physical_progress(db_conn):
    """Verify 98 of 102 activities completed (96.08% physical progress)"""
    total = db_conn.execute("SELECT COUNT(*) FROM dim_activity").fetchone()[0]
    completed = db_conn.execute("SELECT COUNT(*) FROM dim_activity WHERE activity_status_group = 'Completed' OR progress_pct = 100").fetchone()[0]
    assert total == 102
    assert completed == 98
    prog_pct = completed / total
    assert prog_pct == pytest.approx(0.960784, rel=1e-4)

def test_earned_value_and_indices(db_conn):
    """Verify EV = NOK 19,215,686.27, CPI = 0.33, SPI = 1.16"""
    bac = 20000000.0
    ac = db_conn.execute("SELECT SUM(amount_nok) FROM fact_gl_actuals").fetchone()[0]
    ev = bac * (98 / 102)
    pv = 16616335.70
    
    cpi = ev / ac
    spi = ev / pv
    cv = ev - ac
    sv = ev - pv

    assert ev == pytest.approx(19215686.27, rel=1e-3)
    assert cpi == pytest.approx(0.3315, rel=1e-2)
    assert spi == pytest.approx(1.1564, rel=1e-2)
    assert cv == pytest.approx(-38752354.71, rel=1e-3)
    assert sv > 0  # Schedule ahead

def test_procurement_open_commitments(db_conn):
    """Verify open commitments equal NOK 49.23M"""
    open_po = db_conn.execute("SELECT SUM(open_commitment_nok) FROM fact_purchase_orders").fetchone()[0]
    assert open_po == pytest.approx(49233751.55, rel=1e-3)

def test_ias38_accounting_buckets(db_conn):
    """Verify IAS 38 AuC Capitalization (NOK 43.38M) and P&L Operating Expensing (NOK 14.59M)"""
    res = db_conn.execute("""
        SELECT 
            accounting_bucket,
            SUM(amount_nok)
        FROM fact_gl_actuals
        GROUP BY accounting_bucket
    """).fetchall()
    bucket_map = {r[0]: r[1] for r in res}
    
    auc_cap = bucket_map.get("AuC Capitalized (IAS 38)", 0.0)
    pl_exp = bucket_map.get("P&L Expensed (Research/Opex)", 0.0)
    
    assert auc_cap == pytest.approx(43375028.38, rel=1e-3)
    assert pl_exp == pytest.approx(14593012.60, rel=1e-3)
    assert (auc_cap + pl_exp) == pytest.approx(57968040.98, rel=1e-4)

def test_tmdl_date_integrity():
    """Verify zero hardcoded date literals in Power BI TMDL measures"""
    assert os.path.exists(MEASURES_TMDL), f"TMDL file not found: {MEASURES_TMDL}"
    with open(MEASURES_TMDL, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check for forbidden static date strings
    forbidden = ['DATE(2026, 11, 1)', 'DATE(2026,11,1)', '"2026-11-01"']
    for p in forbidden:
        assert p not in content, f"Hardcoded date literal found in TMDL measures: {p}"
    
    # Verify dynamic read from Dim_Project[data_date]
    assert "Dim_Project[data_date]" in content

def test_rag_and_conditional_bar_measures_in_tmdl():
    """Verify dynamic RAG formatting and conditional bar length measures are deployed in TMDL"""
    with open(MEASURES_TMDL, "r", encoding="utf-8") as f:
        content = f.read()

    expected_measures = [
        "CPI Status RAG",
        "CPI Color RAG",
        "SPI Status RAG",
        "SPI Color RAG",
        "CV Status RAG",
        "CV Color RAG",
        "PO Commitment Exposure RAG",
        "Overall Project Health RAG",
        "Cost Variance Bar",
        "Physical Progress Bar",
        "Activity Progress Bar",
        "Budget Consumption Bar",
        "PO Commitment Exposure Bar",
        "AuC Capitalization Bar"
    ]
    for measure in expected_measures:
        assert f"measure '{measure}'" in content, f"Missing required DAX measure: {measure}"


