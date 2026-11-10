# ANTIGRAVITY AGENT TASK SPECIFICATION: EXCEL MODERN ANALYTICS MODEL (POWER QUERY & POWER PIVOT)
**Target File**: `C:\Users\frank\OneDrive\Elkem\docs\ANTIGRAVITY_EXCEL_SPECIFICATION.md`  
**Output Workbook**: `C:\Users\frank\OneDrive\Elkem\GreenPilot_2026_EVM_Model.xlsx`  
**Governing Standards**: FAST Standard (v2.0), ICAEW 20 Principles of Good Spreadsheet Practice, SSRB Financial Modelling Code.  
**Architecture**: Excel Modern Analytics (Power Query M ETL + Power Pivot VertiPaq Data Model + DAX Engine + CUBE Functions / Pivot Presentation).

---

## 1. EXECUTIVE OBJECTIVE & ARCHITECTURAL FOUNDATION

The Antigravity AI Agent must construct an enterprise-grade, **100% dynamic** Earned Value Management (EVM), Root Cause Analysis, and Prescriptive Controller Model in Microsoft Excel for the **Elkem GreenPilot 2026** project (`GP2026`).

### Why Excel Modern Analytics (Power Query + Power Pivot)?
Unlike fragile flat-file workbooks populated with thousands of cell-based `SUMIFS` or volatile arrays, the modern Excel analytics stack leverages the **exact same internal VertiPaq tabular engine and DAX formula language as Power BI**:
1. **Zero Granularity Conflict**: Fact tables (`Fact_GLActuals`, `Fact_BudgetBaseline`, `Fact_PurchaseOrders`) and Dimension tables (`Dim_Activity`, `Dim_WBS`, `Dim_Date`, `Dim_Vendor`) remain in a normalized Star Schema inside the Data Model.
2. **Reusability of DAX**: All 22+ advanced DAX measures developed for Power BI (including dynamic S-curves, root cause diagnosis, and prescriptive recommendations) operate identically inside Excel Power Pivot.
3. **100% Dynamic Presentation**: Dynamic CUBE functions (`CUBEVALUE`, `CUBEMEMBER`) allow pixel-perfect executive scorecards that pull directly from the Data Model without rigid PivotTable layout constraints.
4. **Auditability & Governance**: Separates raw data ingestion (Power Query), business logic (Data Model / DAX), and reporting presentation (Worksheets) strictly in accordance with **ICAEW Principle 5** (*Structure your model clearly*) and **FAST Principle 1** (*Flexible, Appropriate, Structured, Transparent*).

---

## 2. PROJECT RECONCILIATION & BENCHMARK TRUTH (CUT-OFF: 2026-11-01)

The agent must ensure that all queries, measures, and formula outputs match these verified control totals:

| Metric | Source Field / Formula | Benchmark Value (NOK) | Accounting / EVM Interpretation |
| :--- | :--- | :---: | :--- |
| **Project Code / Name** | `Dim_Project[project_id]` | `GP2026` | GreenPilot 2026 R&D / Pilot Plant |
| **Data Date (Cut-off)** | `Dim_Project[data_date]` | **`2026-11-01`** | Dynamic cut-off boundary (GL posts to 2026-10-31) |
| **Budget at Completion (BAC)** | `Fact_BudgetBaseline[baseline_budget_nok]` | **NOK 20,000,000.00** | Approved baseline across 12 periods & 6 WBS |
| **Planned Value (PV at Cut-off)** | Kumulativt budsjett t.o.m. okt 2026 | **NOK 16,620,871.10** | 83.10 % planlagt fremdrift ved statusdato |
| **Actual Cost (AC at Cut-off)** | `Fact_GLActuals[amount_nok]` | **NOK 57,968,040.98** | Påløpte kostnader (AP fakturaer + Journaler) |
| **Physical Progress %** | `AVERAGE(Dim_Activity[progress_pct])/100` | **96.08 %** | 96 Completed, 4 In Progress, 2 Not Started |
| **Earned Value (EV at Cut-off)** | `BAC * Physical Progress %` | **NOK 19,215,686.27** | Opptjent verdi per statusdato (NOK 19.22M) |
| **Cost Variance (CV)** | `EV - AC` | **-NOK 38,752,354.71** | Kritisk overskridelse (-38.75M NOK) |
| **Schedule Variance (SV)** | `EV - PV` | **+NOK 2,594,815.17** | Fysisk foran opprinnelig plan (+2.60M NOK) |
| **Cost Performance Index (CPI)** | `EV / AC` | **0.33** | 33 øre levert per 1 krone brukt |
| **Schedule Performance Index (SPI)**| `EV / PV` | **1.16** | Forsert tempo (16 % foran opprinnelig plan) |
| **Total Committed PO Amount** | `Fact_PurchaseOrders[amount_nok]` | **NOK 106,032,291.88** | Innkjøpsordrer utstedt (>5x budsjett) |
| **Open Purchase Commitments** | `PO Amount - Invoiced Amount` | **NOK 49,183,436.70** | Uoppgjort kontraktsforpliktelse (Likviditetsrisiko) |
| **AuC Capitalization (IAS 38)** | WBS-200, 300, 400, 500 Actuals | **NOK 43,379,909.52** | Balanseført Anlegg under Utførelse |
| **P&L Operating Expense** | WBS-100 (Forskn.) + WBS-600 (PM) | **NOK 14,588,131.46** | Kostnadsført direkte i resultat |

---

## 3. POWER QUERY (M) ETL ARCHITECTURE

All tables must be ingested via Power Query using parameterised relative file paths pointing to `C:\Users\frank\OneDrive\Elkem\processed\star_schema\` (or CSV files in `data\cleaned\`).

### 3.1. Parameter Definition: `pDataFolder`
```powerquery
let
    Source = "C:\Users\frank\OneDrive\Elkem\processed\star_schema" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
in
    Source
```

### 3.2. Extraction & Transformation Pipeline (M Code Templates)

#### A. Ingest Dimension Tables (`Dim_Project`, `Dim_WBS`, `Dim_Date`, `Dim_Vendor`, `Dim_Activity`, `Dim_CostElement`)
```powerquery
// Query: Dim_WBS
let
    Source = Csv.Document(File.Contents(pDataFolder & "\dim_wbs.csv"), [Delimiter=";", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"wbs_id", type text},
        {"wbs_name", type text},
        {"project_id", type text},
        {"ias38_category", type text},
        {"is_capitalizable", type logical}
    })
in
    ChangeTypes
```

```powerquery
// Query: Dim_Project
let
    Source = Csv.Document(File.Contents(pDataFolder & "\dim_project.csv"), [Delimiter=";", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"project_id", type text},
        {"project_name", type text},
        {"currency", type text},
        {"baseline_budget_nok", type number},
        {"baseline_start", type date},
        {"baseline_finish", type date},
        {"data_date", type date}
    })
in
    ChangeTypes
```

#### B. Ingest Fact Tables (`Fact_GLActuals`, `Fact_BudgetBaseline`, `Fact_PurchaseOrders`)
Ensure data types for dates (`type date`), currency keys (`type text`), and financial amounts (`Currency.Type` or `type number`) are explicitly enforced. Set `LoadToDataModel = true` and `CreateDataModelConnection = true` for all queries without loading raw tables into memory-heavy Excel grid sheets.

---

## 4. POWER PIVOT DATA MODEL & DAX MEASURE LIBRARY

Inside the Power Pivot Data Model, configure the relationships as a clean **Star Schema** (1:M, Single Direction from Dimensions to Facts):
* `Dim_Project[project_id]` \\(\longrightarrow\\) `Fact_GLActuals[project_id]`, `Fact_BudgetBaseline[project_id]`, `Fact_PurchaseOrders[project_id]`
* `Dim_WBS[wbs_id]` \\(\longrightarrow\\) `Fact_GLActuals[wbs_id]`, `Fact_BudgetBaseline[wbs_id]`, `Fact_PurchaseOrders[wbs_id]`, `Dim_Activity[wbs_id]`
* `Dim_CostElement[cost_element]` \\(\longrightarrow\\) `Fact_GLActuals[cost_element]`, `Fact_BudgetBaseline[cost_element]`, `Fact_PurchaseOrders[cost_element]`
* `Dim_Vendor[vendor_id]` \\(\longrightarrow\\) `Fact_PurchaseOrders[vendor_id]`
* `Dim_Date[Date]` \\(\longrightarrow\\) `Fact_GLActuals[posting_date]`, `Fact_BudgetBaseline[period_date]`, `Fact_PurchaseOrders[po_date]`

### 4.1. Core DAX Measure Implementation

Create the following measures inside the `_Measures` calculated table (or hosted on `Fact_GLActuals`):

#### 1. Baseline & S-Curve Foundations
```dax
[Project Data Date] := 
MAX ( Dim_Project[data_date] )

[Budget at Completion (BAC)] := 
SUM ( Fact_BudgetBaseline[baseline_budget_nok] )

[Total BAC Unfiltered] := 
CALCULATE ( [Budget at Completion (BAC)], ALL ( Dim_Date ) )

[Planned Value Cumulative (PV S-Curve)] := 
VAR MaxDate = MAX ( Dim_Date[Date] )
RETURN
    CALCULATE (
        [Budget at Completion (BAC)],
        FILTER ( ALL ( Dim_Date ), Dim_Date[Date] <= MaxDate )
    )

[Actual Cost (AC)] := 
SUM ( Fact_GLActuals[amount_nok] )

[Actual Cost Cumulative (AC S-Curve)] := 
VAR MaxDate = MAX ( Dim_Date[Date] )
VAR ProjectDataDate = [Project Data Date]
RETURN
    IF (
        MaxDate <= ProjectDataDate,
        CALCULATE (
            [Actual Cost (AC)],
            FILTER ( ALL ( Dim_Date ), Dim_Date[Date] <= MaxDate )
        ),
        BLANK ()
    )
```

#### 2. Dynamic Progress & Earned Value (Preventing Month-Filter Collapse)
```dax
[Physical Progress % (Current)] := 
AVERAGE ( Dim_Activity[progress_pct] ) / 100

[Physical Progress % Cumulative] := 
VAR MaxSelectedDate = MAX ( Dim_Date[Date] )
VAR TotalActivities = COUNTROWS ( ALL ( Dim_Activity ) )
VAR CompletedToDate = 
    CALCULATE (
        COUNTROWS ( Dim_Activity ),
        Dim_Activity[planned_finish] <= MaxSelectedDate,
        ALL ( Dim_Date )
    )
RETURN
    IF (
        ISBLANK ( MaxSelectedDate ),
        BLANK (),
        DIVIDE ( CompletedToDate, TotalActivities, 0 )
    )

[Earned Value (EV)] := 
[Total BAC Unfiltered] * [Physical Progress % (Current)]

[Earned Value Cumulative (EV S-Curve)] := 
VAR MaxDate = MAX ( Dim_Date[Date] )
VAR ProjectDataDate = [Project Data Date]
RETURN
    IF (
        MaxDate <= ProjectDataDate,
        [Total BAC Unfiltered] * [Physical Progress % Cumulative],
        BLANK ()
    )
```

#### 3. Variances & Indices
```dax
[Cost Variance (CV)] := [Earned Value (EV)] - [Actual Cost (AC)]
[Schedule Variance (SV)] := [Earned Value (EV)] - [Planned Value Cumulative (PV S-Curve)]

[Cost Performance Index (CPI)] := DIVIDE ( [Earned Value (EV)], [Actual Cost (AC)], BLANK () )
[Schedule Performance Index (SPI)] := DIVIDE ( [Earned Value (EV)], [Planned Value Cumulative (PV S-Curve)], BLANK () )

[Estimate at Completion (EAC)] := 
IF ( [CPI] > 0, [Actual Cost (AC)] + DIVIDE ( [Total BAC Unfiltered] - [Earned Value (EV)], [CPI] ), BLANK () )

[Variance at Completion (VAC)] := [Total BAC Unfiltered] - [Estimate at Completion (EAC)]

[To Complete Performance Index (TCPI BAC)] := 
VAR RemainingWork = [Total BAC Unfiltered] - [Earned Value (EV)]
VAR RemainingBudget = [Total BAC Unfiltered] - [Actual Cost (AC)]
RETURN
    IF ( RemainingBudget <= 0, BLANK (), DIVIDE ( RemainingWork, RemainingBudget ) )
```

#### 4. Automated Root Cause Engine & Prescriptive Actions
```dax
[Root Cause Diagnosis] := 
VAR CurrentCPI = [Cost Performance Index (CPI)]
VAR CurrentSPI = [Schedule Performance Index (SPI)]
VAR OpenCommitments = [Open Commitments (NOK)]
VAR BAC = [Total BAC Unfiltered]
RETURN
SWITCH (
    TRUE (),
    CurrentSPI > 1.05 && CurrentCPI < 0.80,
        "FORSERINGSAVVIK (Fast-Tracking): Fremdriften er forsert foran plan (SPI = " & FORMAT(CurrentSPI, "0.00") & 
        "), men enheten leverer med massiv kostnadsoverskridelse (CPI = " & FORMAT(CurrentCPI, "0.00") & 
        "). Prosjektet har pådratt seg kritiske overtids-, haste- og riggkostnader.",
        
    CurrentSPI < 0.95 && CurrentCPI < 0.90,
        "PRODUKTIVITETSSVIKT / FORSINKELSE: Både tid og kostnad svikter (SPI = " & FORMAT(CurrentSPI, "0.00") & 
        ", CPI = " & FORMAT(CurrentCPI, "0.00") & ").",
        
    CurrentCPI >= 0.95 && CurrentSPI >= 0.95,
        "I RUTE: Prosjektet leverer innenfor akseptable toleransegrenser.",
        
    "SAMMENSATT AVVIK: Se WBS-matrise for detaljert kostnadsdriver."
)

[Recommended Controller Actions] := 
VAR WorstWBS = TOPN ( 1, VALUES ( Dim_WBS[wbs_name] ), [Cost Variance (CV)], ASC )
VAR TopVendor = TOPN ( 1, VALUES ( Dim_Vendor[vendor_name] ), [Open Commitments (NOK)], DESC )
VAR OpenPO = [Open Commitments (NOK)]
VAR CapitalizedAuC = [Actual Cost AuC Capitalized]
RETURN
"ANBEFALTE CONTROLLER-TILTAK (AUTOMATISK UTLEDET):" & UNICHAR(10) &
"1. [KOSTNADSKONTROLL] Stans nye rekvisisjoner og reforhandle kontrakter på mest kritiske WBS: " & WorstWBS & 
    " (Akkumulert avvik: " & FORMAT ( [Cost Variance (CV)] / 1e6, "+#,0.00;-#,0.00" ) & "M NOK)." & UNICHAR(10) &
"2. [LIKVIDITET] Sanér åpne PO-forpliktelser (totalt " & FORMAT ( OpenPO / 1e6, "#,0.0" ) & "M NOK). " &
    "Største uoppgjorte enkeltforpliktelse ligger hos: " & TopVendor & "." & UNICHAR(10) &
"3. [REGNSKAP / IFRS] Varsle konsernledelsen om påkrevd nedskrivningstest (IAS 36) for balanseført AuC på " &
    FORMAT ( CapitalizedAuC / 1e6, "#,0.00" ) & "M NOK."
```

---

## 5. WORKBOOK STRUCTURE & FRONTEND WORKSHEET DESIGN

The generated Excel workbook must follow a disciplined, audit-friendly tab structure complying with FAST and ICAEW standards:

```
GreenPilot_2026_EVM_Model.xlsx
├── 00_Control_Index       (Metadata, Cut-off selector, Status indicators, TOC)
├── 01_Executive_Dashboard (KPI Scorecard via CUBEVALUE, Dynamic S-Curve, Diagnosis Card)
├── 02_EVM_Timeline        (Monthly PivotTable: Periods 2026-01 to 2026-12, PV, AC, EV, CV, SV)
├── 03_WBS_Variance_Matrix (Matrix Pivot: WBS × Cost Element with conditional heatmaps)
├── 04_Commitment_Control  (Vendor PO exposure, Invoiced vs Open Commitments, FX breakdown)
└── 05_IFRS_AuC_Asset_Reg  (AuC vs P&L classification, IAS 36 Impairment trigger tracker)
```

### 5.1. Tab 01: `Executive_Dashboard` (CUBE Formula Architecture)
Instead of an unstable standard PivotTable on the dashboard, Antigravity must use **Excel CUBE Functions** connected to the Data Model (`"ThisWorkbookDataModel"`). This guarantees that cells stay locked in place and never shift when filters change:

* **Project Name**:
  `=CUBEVALUE("ThisWorkbookDataModel"; "[Measures].[Project Name]")`
* **Cut-Off Date Display**:
  `=TEXT(CUBEVALUE("ThisWorkbookDataModel"; "[Measures].[Project Data Date]"); "YYYY-MM-DD")`
* **BAC Tile (Cell C4)**:
  `=CUBEVALUE("ThisWorkbookDataModel"; "[Measures].[Total BAC Unfiltered]")`
* **Actual Cost Tile (Cell E4)**:
  `=CUBEVALUE("ThisWorkbookDataModel"; "[Measures].[Actual Cost (AC)]")`
* **Earned Value Tile (Cell G4)**:
  `=CUBEVALUE("ThisWorkbookDataModel"; "[Measures].[Earned Value (EV)]")`
* **CPI Tile (Cell C6)**:
  `=CUBEVALUE("ThisWorkbookDataModel"; "[Measures].[Cost Performance Index (CPI)]")`
* **SPI Tile (Cell E6)**:
  `=CUBEVALUE("ThisWorkbookDataModel"; "[Measures].[Schedule Performance Index (SPI)]")`
* **Cost Variance Tile (Cell G6)**:
  `=CUBEVALUE("ThisWorkbookDataModel"; "[Measures].[Cost Variance (CV)]")`
* **Dynamic Diagnosis Textbox (Merged C9:I11)**:
  `=CUBEVALUE("ThisWorkbookDataModel"; "[Measures].[Root Cause Diagnosis]")`
* **Dynamic Controller Action Plan (Merged C13:I16)**:
  `=CUBEVALUE("ThisWorkbookDataModel"; "[Measures].[Recommended Controller Actions]")`

### 5.2. Tab 01 S-Curve Chart (PivotChart)
* **Underlying Source**: PivotTable in `02_EVM_Timeline`.
* **X-Axis**: `Dim_Date[Period]` (`2026-01` to `2026-12`).
* **Series 1**: `[Planned Value Cumulative (PV S-Curve)]` (Dark Blue Line, marker dots, smoothly curves to 20.00M in Dec).
* **Series 2**: `[Actual Cost Cumulative (AC S-Curve)]` (Solid Crimson Red Line, stops abruptly at 2026-10 / 2026-11 at 57.97M).
* **Series 3**: `[Earned Value Cumulative (EV S-Curve)]` (Forest Green Dashed Line, stops at 2026-11 at 19.22M).
* **Chart Styling**: Clean white background, no horizontal gridline clutter, Legend positioned top-center.

---

## 6. PYTHON AUTOMATION SCRIPT (`build_excel_model.py`)

Antigravity should generate and execute a Python automation script in `scripts\build_excel_model.py` utilizing `openpyxl` (or PowerShell COM automation) to build the workbook scaffolding, inject standard formulas, format ranges, and apply corporate styling.

### Script Specification:
```python
"""
build_excel_model.py
Constructs the FAST-compliant GreenPilot 2026 EVM Excel Model.
Applies typography, column widths, number formatting, and formula scaffolding.
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
# Setup sheets: 00_Control_Index, 01_Executive_Dashboard, 02_EVM_Timeline, etc.
# Inject CUBEVALUE formulas, corporate navy headers (#002060), and MNOK formatting.
wb.save("C:/Users/frank/OneDrive/Elkem/GreenPilot_2026_EVM_Model.xlsx")
```

---

## 7. QUALITY ASSURANCE GATES & RECONCILIATION PROTOCOL

Before signaling completion, the Antigravity Agent must verify the following automated checklist:

- [ ] **Data Model Connectivity**: Power Query queries refresh with zero errors when pointed to local CSV files.
- [ ] **No Month-Filter Collapse**: Verifying that `[Earned Value (EV)]` and `[Total BAC Unfiltered]` do not drop to 1.4M when filtered on October 2026.
- [ ] **S-Curve Truncation Check**: Verifying that `[Actual Cost Cumulative]` and `[Earned Value Cumulative]` return `#N/A` or `BLANK()` for periods `2026-11` and `2026-12` (post cut-off).
- [ ] **Fast Standard Formatting**: All inputs formatted in Blue font (`#0000FF`), formulas in Black font (`#000000`), and headers with muted slate fills. All currency figures formatted as `#,##0.00 "M NOK"` or `#,##0 "NOK"`.
- [ ] **Cross-Tool Parity**: Figures in `GreenPilot_2026_EVM_Model.xlsx` reconcile to the penny against `ANTIGRAVITY_PBI_SPECIFICATION.md` and the Gold Layer facts.
