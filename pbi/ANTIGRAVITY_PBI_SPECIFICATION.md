# ANTIGRAVITY TASK SPECIFICATION: ENTERPRISE POWER BI EVM & ROOT CAUSE SUITE
**Target Repository:** `C:\Users\frank\OneDrive\Elkem`  
**Project:** GreenPilot 2026 (Elkem Industrial Pilot Plant)  
**Format:** Power BI Project (`.pbip` / TMDL / Tabular Model)  
**Architecture:** Deterministic Rule-Based Prescriptive Engine (No external AI API required)

---

## 1. Executive Summary & Objective

Antigravity shall implement a complete, enterprise-grade Earned Value Management (EVM), Root Cause Analysis, and Prescriptive Action reporting platform within `pbi\GreenPilotProject.pbip`.

### Project Baseline Facts (Ground Truth)
* **Project ID:** `GP2026` | **Company Code:** `GP01` | **Reporting Currency:** `NOK`
* **Baseline Period:** `2026-01-01` to `2026-12-31`
* **Data Date (Cut-off):** `2026-11-01` (Last GL posting: `2026-10-31`)
* **Baseline Budget (BAC):** `NOK 20,000,000.00`
* **Actual Cost (AC):** `NOK 57,968,040.98`
* **Earned Value (EV):** `NOK 19,215,686.27` (Physical progress: **96.08%** / 98 of 102 activities)
* **Cost Variance (CV):** `-NOK 38,752,354.71` | **CPI:** `0.33` (Over budget by 190%)
* **Schedule Variance (SV):** `+NOK 2,594,815.17` | **SPI:** `1.16` (5 weeks ahead of plan)
* **Open Purchase Commitments:** `NOK 49,233,751.55` (PO baseline: NOK 106.03M total)
* **Accounting Treatment:** AuC Capitalized (IAS 38 Development): `NOK 43,375,028.38`; P&L Expensed: `NOK 14,593,012.60`

---

## 2. Directory Layout & Pipeline Alignment

Antigravity must adhere to the existing folder structure:
```text
C:\Users\frank\OneDrive\Elkem\
├── data\
│   ├── raw\                         # 22 synthetic ERP/Primavera/HR CSV files
│   ├── staging\
│   └── cleaned\
├── docs\                            # Architectural and business guidelines
├── pbi\
│   ├── GreenPilotProject.pbip       # Main PBIP project entry
│   ├── GreenPilotProject.Report\    # Visual layout definition
│   └── GreenPilotProject.SemanticModel\ # TMDL model files
├── processed\
│   ├── star_schema\                 # Enriched gold dimensional CSVs
│   ├── business_ready\              # Business semantic CSVs
│   └── excel_ready\                 # Denormalized flat cube for Excel
└── scripts\
    ├── 01_raw_to_staging.py
    ├── 02_staging_to_cleaned.py
    └── 03_build_star_schema-v4.py   # Gold layer build script
```

---

## 3. Gold Layer Feature Engineering Requirements

Before updating TMDL / Power BI measures, verify that `scripts\03_build_star_schema-v4.py` outputs the following enriched attributes:

### 3.1 `Dim_WBS`
* `parent_wbs_id`: Guaranteed `GP2026` if null (for clean 2-level hierarchy).
* `ias38_phase`: `Research` (100), `Development` (200, 300, 400, 500), `Closeout` (600).
* `ias38_treatment`: `EXPENSE` (100, 600) vs. `CAPITALIZE` (200, 300, 400, 500).
* `accounting_bucket`: `P&L Operating Expense` vs. `Balance Sheet (AuC)`.
* `eligible_auc`: Boolean (`True` for 200–500).

### 3.2 `Dim_Activity`
* `progress_pct`: Integer `100` (Completed), `50` (In Progress), `0` (Not Started).
* `planned_duration_days`: Datediff between `planned_start` and `planned_finish`.
* `activity_status_group`: Visual sorting order.

### 3.3 `Fact_PurchaseOrders`
* `amount_nok`: Foreign exchange normalized via `03_erp_fx_rates.csv`.
* `invoiced_nok`: Total AP invoices posted against `po_line_id`.
* `open_commitment_nok`: `MAX(0, amount_nok - invoiced_nok)`.
* `po_status`: `Fully Invoiced`, `Partially Invoiced`, `Open Uninvoiced`.

### 3.4 New Config Dimension: `Config_VarianceThresholds.csv`
Generate and import a threshold matrix into the Semantic Model:
| Metric | Yellow_Limit | Red_Limit | Trigger_Type | Controller_Action |
| :--- | :---: | :---: | :--- | :--- |
| **CPI** | 0.90 | 0.80 | Min | Freeze non-critical POs, revise EAC |
| **SPI** | 0.90 | 0.80 | Min | Assess schedule compression / reallocate labor |
| **Open Commitments (MNOK)** | 10.0 | 25.0 | Max | Immediate PO cancellation audit |
| **AuC Capitalization Ratio** | 60% | 80% | Max | Trigger mandatory IAS 36 Impairment Test |

---

## 4. Master DAX Measures Architecture (`_Measures`)

Antigravity shall deploy the complete DAX library inside `GreenPilotProject.SemanticModel\definition\tables\_Measures.tmdl`.

### 4.1 Core EVM Metrics
```dax
[Budget at Completion (BAC)] = 
SUM ( Fact_BudgetBaseline[baseline_budget_nok] )

[Planned Value (PV)] = 
SUM ( Fact_BudgetBaseline[baseline_budget_nok] )

[Planned Value Cumulative (PV S-Curve)] = 
VAR MaxDate = MAX ( Dim_Date[Date] )
RETURN
    CALCULATE (
        [Budget at Completion (BAC)],
        FILTER ( ALL ( Dim_Date ), Dim_Date[Date] <= MaxDate )
    )

[Actual Cost (AC)] = 
SUM ( Fact_GLActuals[amount_nok] )

[Actual Cost Cumulative (AC S-Curve)] = 
VAR MaxDate = MAX ( Dim_Date[Date] )
VAR ProjectDataDate = MAX ( Dim_Project[data_date] )
RETURN
    IF (
        MaxDate <= ProjectDataDate,
        CALCULATE (
            [Actual Cost (AC)],
            FILTER ( ALL ( Dim_Date ), Dim_Date[Date] <= MaxDate )
        ),
        BLANK ()
    )

[Physical Progress % (Current)] = 
AVERAGE ( Dim_Activity[progress_pct] ) / 100

[Physical Progress % Cumulative] = 
VAR MaxSelectedDate = MAX ( Dim_Date[Date] )
VAR TotalActivities = COUNTROWS ( ALL ( Dim_Activity ) )
VAR CompletedToDate = 
    CALCULATE (
        COUNTROWS ( Dim_Activity ),
        Dim_Activity[planned_finish] <= MaxSelectedDate,
        ALL ( Dim_Date )
    )
RETURN
    IF ( ISBLANK ( MaxSelectedDate ), BLANK (), DIVIDE ( CompletedToDate, TotalActivities, 0 ) )

[Earned Value Cumulative (EV S-Curve)] = 
VAR MaxDate = MAX ( Dim_Date[Date] )
VAR ProjectDataDate = MAX ( Dim_Project[data_date] )
VAR TotalBAC = CALCULATE ( [Budget at Completion (BAC)], ALL ( Dim_Date ) )
RETURN
    IF (
        MaxDate <= ProjectDataDate,
        TotalBAC * [Physical Progress % Cumulative],
        BLANK ()
    )

[Cost Variance (CV)] = [Earned Value Cumulative (EV S-Curve)] - [Actual Cost Cumulative (AC S-Curve)]
[Schedule Variance (SV)] = [Earned Value Cumulative (EV S-Curve)] - [Planned Value Cumulative (PV S-Curve)]
[Cost Performance Index (CPI)] = DIVIDE ( [Earned Value Cumulative (EV S-Curve)], [Actual Cost Cumulative (AC S-Curve)], BLANK () )
[Schedule Performance Index (SPI)] = DIVIDE ( [Earned Value Cumulative (EV S-Curve)], [Planned Value Cumulative (PV S-Curve)], BLANK () )
```

### 4.2 Forecasts & Health Checks (EAC / VAC / TCPI)
```dax
[Estimate at Completion (EAC)] = 
// Standard EVM formula based on past cost performance
VAR CurrentCPI = [Cost Performance Index (CPI)]
RETURN
    IF (
        CurrentCPI > 0,
        [Actual Cost (AC)] + DIVIDE ( [Budget at Completion (BAC)] - [Earned Value Cumulative (EV S-Curve)], CurrentCPI ),
        [Actual Cost (AC)]
    )

[Variance at Completion (VAC)] = 
[Budget at Completion (BAC)] - [Estimate at Completion (EAC)]

[To Complete Performance Index (TCPI EAC)] = 
// Calculated against revised EAC because BAC is already breached
VAR RemainingWork = [Budget at Completion (BAC)] - [Earned Value Cumulative (EV S-Curve)]
VAR RemainingFunds = [Estimate at Completion (EAC)] - [Actual Cost (AC)]
RETURN
    IF ( RemainingFunds > 0, DIVIDE ( RemainingWork, RemainingFunds ), BLANK () )
```

### 4.3 Deterministic Root Cause Engine (No AI dependency)
```dax
[Root Cause Primary Diagnosis] = 
VAR CurrentCPI = [Cost Performance Index (CPI)]
VAR CurrentSPI = [Schedule Performance Index (SPI)]
VAR OpenCommitments = SUM ( Fact_PurchaseOrders[open_commitment_nok] )
VAR BAC = CALCULATE ( [Budget at Completion (BAC)], ALL ( Dim_Date ) )
RETURN
SWITCH (
    TRUE (),
    CurrentSPI >= 1.05 && CurrentCPI < 0.70,
        "FAST-TRACKING / PREMATURE FORCING: Schedule is 5 weeks ahead (SPI 1.16), but achieved via excessive premium freight, unbudgeted equipment purchases, and heavy overtime. Work delivered at 3x planned unit cost.",
    CurrentSPI < 0.90 && CurrentCPI < 0.90,
        "PRODUCTIVITY COLLAPSE: Severe execution bottlenecks with compounding delays and budget overruns.",
    OpenCommitments > (BAC * 0.50),
        "PROCUREMENT CONTROL BREACH: Uncontrolled Purchase Orders issued without gate approvals.",
    "STABLE / MINOR VARIANCE: Project progressing within acceptable operational variance."
)

[Root Cause Driver Decomposition] = 
"VARIANCE DRIVERS (Total CV: " & FORMAT([Cost Variance (CV)] / 1e6, "-0.00") & "M NOK):" & UNICHAR(10) &
"1. Technology Development (WBS-500): -13.13M NOK (Overrun +417%)" & UNICHAR(10) &
"2. Equipment & Machinery (CE400):   -10.15M NOK (Overrun +312%)" & UNICHAR(10) &
"3. Pilot Plant Assembly (WBS-300):   -9.90M NOK (Overrun +295%)" & UNICHAR(10) &
"4. Internal Labor / Overtime (CE100): -9.52M NOK (Overrun +263%)" & UNICHAR(10) &
"5. Project Management (WBS-600):     -9.57M NOK (Overrun +282%)"
```

### 4.4 Prescriptive Controller Action Engine
```dax
[Prescriptive Controller Actions] = 
VAR OpenCommitments = SUM ( Fact_PurchaseOrders[open_commitment_nok] )
VAR CapitalizedAuC = 
    CALCULATE (
        SUM ( Fact_GLActuals[amount_nok] ),
        Dim_WBS[ias38_treatment] = "CAPITALIZE"
    )
RETURN
"MANDATORY CONTROLLER ACTIONS (ELKEM PILOT CONTROL):" & UNICHAR(10) &
"1. [IMMEDIATE PO FREEZE] Cancel unfulfilled line items in Fact_PurchaseOrders. Open exposure is currently " & 
    FORMAT(OpenCommitments / 1e6, "0.00") & "M NOK across foreign vendors." & UNICHAR(10) &
"2. [IFRS / IAS 36 IMPAIRMENT REVIEW] Capitalized AuC on balance sheet has reached " & 
    FORMAT(CapitalizedAuC / 1e6, "0.00") & "M NOK. Corporate finance must assess if future commercial cash flows support this asset base." & UNICHAR(10) &
"3. [CHANGE ORDER BASELINE RESET] 14 out of 18 Change Orders remain unapproved or pending. The steering committee must establish an Over-Target Baseline (OTB) of 62.5M NOK." & UNICHAR(10) &
"4. [TIME CONTROL] 96.08% physical completion reached. Close remaining 4 active activities (A097-A100) and demobilize external personnel."
```

---

## 5. Power BI Report Page Architecture (`pbi\GreenPilotProject.Report`)

Configure the `.pbip` report layout into **5 dedicated analytical views**:

### Page 1: "Executive EVM Scorecard & S-Curve"
* **Header / Filter:** Project Slicer (`GP2026`), Cut-off Indicator (`Status Date: 2026-11-01`).
* **KPI Cards (Top):**
  * `BAC` (20.00M), `AC` (57.97M), `EV` (19.22M), `CPI` (0.33, Red), `SPI` (1.16, Green), `Physical Progress %` (96.08%).
* **Visual 1 (Main):** **Line and Clustered Column Chart**
  * X-Axis: `Dim_Date[Period]` (or `Date`)
  * Line Y-Axis: `[Planned Value Cumulative (PV S-Curve)]`, `[Actual Cost Cumulative (AC S-Curve)]`, `[Earned Value Cumulative (EV S-Curve)]`.
  * Column Y-Axis: Dynamic Status Date marker column (`[Status Date Dynamic Line]`).
  * Subtitle (`fx`): `[S-Curve Subtitle KPI]`.
* **Visual 2 (Right):** Summary matrix showing WBS breakdown with `BAC`, `PV`, `AC`, `EV`, `CV`, `CPI`.

### Page 2: "Root Cause & Variance Driver Matrix"
* **Visual 1 (Top Left):** **Decomposition Tree (Nedbrytingstre)**
  * Analyze: `Cost Variance (CV)`
  * Explain by: `Dim_WBS[wbs_name]`, `Dim_CostElement[cost_element_name]`, `Dim_Vendor[vendor_name]`.
* **Visual 2 (Top Right):** **Diagnostic & Action Card**
  * Text Card binding: `[Root Cause Primary Diagnosis]` & `[Root Cause Driver Decomposition]`.
* **Visual 3 (Bottom Left):** **Scatter Plot (CPI vs. SPI by WBS)**
  * X-Axis: `SPI` (Constant reference line at 1.0).
  * Y-Axis: `CPI` (Constant reference line at 1.0).
  * Bubbles: `Dim_WBS[wbs_name]` sized by `Actual Cost (AC)`. Highlights WBS-500, WBS-300 in the "Fast but Ruinous" quadrant.
* **Visual 4 (Bottom Right):** **Waterfall Chart (Variance Bridge)**
  * Category: Cost Elements (`CE100` to `CE600`).
  * Breakdown: Baseline Budget \\(\rightarrow\\) Variances \\(\rightarrow\\) Actual Cost.

### Page 3: "Procurement & Commitment Exposure"
* **Visual 1 (Top Cards):** Total PO Amount (106.03M), Invoiced AP (56.85M), Open Commitments (49.23M).
* **Visual 2:** Table of Top Exposed Vendors (`Dim_Vendor[vendor_name]`, `currency`, `PO Amount NOK`, `Invoiced NOK`, `Open Commitment NOK`, `PO Status`).
* **Visual 3:** Currency exposure donut chart (`NOK`, `EUR`, `USD`).

### Page 4: "IFRS / IAS 38 Accounting & AuC Capitalization"
* **Visual 1:** Split of actual costs: **AuC Capitalized** (NOK 43.38M) vs. **P&L Expensed** (NOK 14.59M).
* **Visual 2:** Matrix by `Dim_WBS[wbs_id]` and `Dim_WBS[accounting_bucket]`.
* **Visual 3:** Callout warning on IAS 36 Impairment Trigger.

### Page 5: "Prescriptive Controller Action Panel"
* **Visual 1:** Large Action Board bound to `[Prescriptive Controller Actions]`.
* **Visual 2:** Open Change Order backlog status (`11_erp_change_orders.csv`).
* **Visual 3:** Remaining Activities Audit (Filter: `Dim_Activity[status] IN {"In Progress", "Not Started"}`).

---

## 6. Antigravity Verification & Quality Gates

Antigravity must execute the following automated validation checks prior to handoff:

```powershell
# 1. Regenerate Star Schema and Gold Layer
python scripts\03_build_star_schema-v4.py

# 2. Verify Generated CSV files exist in processed/star_schema
Test-Path processed\star_schema\Dim_WBS.csv
Test-Path processed\star_schema\Fact_PurchaseOrders.csv
Test-Path processed\excel_ready\Fact_FinancialEVM_Unified_Flat.csv

# 3. Assert EVM Numbers Integrity
# BAC == 20,000,000.00
# AC  == 57,968,040.98
# EV  == 19,215,686.27
# CPI == 0.3315
# SPI == 1.1561
```

### TMDL Integrity Rule
Ensure no hardcoded date literals (`DATE(2026, 11, 1)`) remain in cumulative measures. All cut-offs must dynamically read `MAX(Dim_Project[data_date])`.
