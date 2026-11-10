import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import tests.test_evm_suite as t

con = t.db_conn()

tests = [
    ("test_bac_reconciliation", t.test_bac_reconciliation, [con]),
    ("test_actual_cost_reconciliation", t.test_actual_cost_reconciliation, [con]),
    ("test_activity_physical_progress", t.test_activity_physical_progress, [con]),
    ("test_earned_value_and_indices", t.test_earned_value_and_indices, [con]),
    ("test_procurement_open_commitments", t.test_procurement_open_commitments, [con]),
    ("test_ias38_accounting_buckets", t.test_ias38_accounting_buckets, [con]),
    ("test_tmdl_date_integrity", t.test_tmdl_date_integrity, []),
    ("test_rag_and_conditional_bar_measures_in_tmdl", t.test_rag_and_conditional_bar_measures_in_tmdl, [])
]

passed = 0
failed = 0
for name, func, args in tests:
    try:
        func(*args)
        print(f"[PASS] {name}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        failed += 1

print(f"\nSummary: {passed} passed, {failed} failed out of {len(tests)} tests.")
if failed > 0:
    sys.exit(1)
