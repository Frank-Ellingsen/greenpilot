### 1. Datamodell og Relasjoner (Stjernemodell)

Pek Power BI til mappen `C:\Users\frank\OneDrive\Elkem\processed\business_ready` (eller `star_schema`). Sett opp **1-til-mange (1:\*) relasjoner med énveis filterretning (Single)** fra fellesdimensjonene til faktatabellene:

- **`Dim_Date[Date]`** \\(\rightarrow\\) `Fact_BudgetBaseline[period_date]`
- **`Dim_Date[Date]`** \\(\rightarrow\\) `Fact_GLActuals[posting_date]`
- **`Dim_Date[Date]`** \\(\rightarrow\\) `Fact_PurchaseOrders[po_date]`
- **`Dim_Date[Date]`** \\(\rightarrow\\) `Fact_Timesheets[work_date]`
- **`Dim_WBS[wbs_id]`** \\(\rightarrow\\) Kobles til `wbs_id` i `Fact_BudgetBaseline`, `Fact_GLActuals`, `Fact_PurchaseOrders` og `Fact_Timesheets`
- **`Dim_CostElement[cost_element]`** \\(\rightarrow\\) Kobles til `Fact_BudgetBaseline`, `Fact_GLActuals` og `Fact_PurchaseOrders`
- **`Dim_Vendor[vendor_id]`** \\(\rightarrow\\) `Fact_PurchaseOrders[vendor_id]` og `Fact_APInvoices[vendor_id]`
- **`Dim_Activity[activity_id]`** \\(\rightarrow\\) `Fact_Timesheets[activity_id]`

> **Tips**: Opprett en tom tabell `_Measures` for å samle alle de 16 målene fra `docs\dax_measures_library.dax`.

---

### 2. Rapportside 1: Executive EVM & Variance Dashboard

Hensikten er å gi prosjektledelse og ledelse i Elkem umiddelbar status på fremdrift, kostnader og sluttprognose:

- **KPI-Kort (øverst)**:
  - `[Planned Value (PV)]` (NOK 20,00M)
  - `[Earned Value (EV)]` (NOK 19,22M)
  - `[Actual Cost (AC)]` (NOK 57,97M)
  - `[Cost Performance Index (CPI)]` (**0,33** – fargekodet rød for kritisk avvik)
  - `[Schedule Performance Index (SPI)]` (fysisk fremdrift 96,08 %)
  - `[Estimate at Completion (EAC)]` (NOK 58,75M vs. BAC NOK 20,00M)
- **Hovedgraf (Linjediagram / S-kurve)**:
  - **X-akse**: `Dim_Date[Date]` (eller `Period` YYYY-MM)
  - **Linjer**: `[Planned Value (PV)]`, `[Actual Cost Cumulative]` og `[Earned Value (EV)]`.
  - _Tydelig visuelt poeng_: Viser det voldsomme gapet der AC løper fra PV/EV på grunn av ubehandlede endringsordrer og utstyrsleveranser.
- **WBS-Nedbrytning (Matrise)**:
  - **Rader**: `Dim_WBS[wbs_id]` og `Dim_WBS[wbs_name]`
  - **Verdier**: `[Budget at Completion (BAC)]`, `[Actual Cost (AC)]`, `[Cost Variance (CV)]` og `[CPI]`.

---

### 3. Rapportside 2: IFRS / IAS 38 Accounting & AuC Tracking

Denne siden henvender seg spesifikt til Finans og Regnskap:

- **Donut / Ringdiagram**:
  - Fordeling mellom **`[Actual Cost Capitalized (AuC)]`** (NOK 43,38M / 74,8 %) og **`[Actual Cost Expensed (P&L)]`** (NOK 14,59M / 25,2 %).
- **Drill-down Tabell**:
  - Viser hvordan WBS-100 (Forskning) og WBS-600 (Avslutning) resultatføres løpende mot drift, mens WBS 200–500 oppfyller kriteriene i IAS 38 § 57 og balanseføres som anlegg under utførelse.

---

### 4. Rapportside 3: Procurement, 3-Way Match & Commitments

Viser controller-revisjonen og likviditetsrisiko:

- **Stolpediagram / Fossekall (Waterfall)**:
  - `[Total Purchase Orders (PO)]` (NOK 106,17M) \\(\rightarrow\\) `[Invoiced PO Amount (AP)]` (NOK 56,95M) \\(\rightarrow\\) `[Open Commitments]` (NOK 49,23M).
- **Avvikstabell**:
  - Viser de 3 overfakturerte linjene fra DQA-revisjonen samt de 70 uavregnede varemottakene (GR uten faktura) som krever periodisering (Accrual) på NOK 7,39M.
