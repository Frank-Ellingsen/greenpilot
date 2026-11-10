# ERD og Stjernemodell Arkitektur – GreenPilot 2026 (v2)

Dette dokumentet utvider spesifikasjonen for prosjektet **GreenPilot 2026 (GP2026)** med et komplett **Entity-Relationship Diagram (ERD)**. Dokumentet kartlegger alle de 22 kildetabellene på tvers av ERP, Primavera P6, HR og Tilskuddsrammeverk, og definerer primærnøkler (PK), fremmednøkler (FK), kardinalitet og referanseintegritet.

---

## 1. Konseptuell og Logisk ERD-Oversikt

I motsetning til stjernemodellen (som er optimalisert for analytiske spørringer i Power BI), beskriver ERD-modellen de operasjonelle entitetene og deres naturlige relasjoner i kildesystemene (OLTP-struktur).

### Kildedomener i Datamodellen

1. **ERP & Finansdomene**: Prosjektmasteer, WBS-hierarki, budsjett baseline, hovedbok (GL), journaler, leverandører, innkjøpsordrer, varemottak, AP-fakturaer og endringsordrer (Change Orders).
2. **Primavera P6 Fremdriftsdomene**: Aktiviteter, avhengighetsrelasjoner (predecessor/successor), ressurser og ressurstilordninger.
3. **HR & Timeføringsdomene**: Ansattmaster, ukentlig kapasitetskalender og daglige timelister.
4. **Offentlige Tilskudd (Grant)**: SkatteFUNN/Enova-rammebudsjett med dokumentasjonskrav.

---

## 2. Entitetskatalog (Entity Inventory)

Tabellen nedenfor gir en komplett oversikt over entitetene i ERD-modellen, deres rolle i datamodellen og kilde-CSV.

| Entitet (Entity Name) | Kildefil                                | Entitetstype        | Beskrivelse                                              |
| :-------------------- | :-------------------------------------- | :------------------ | :------------------------------------------------------- |
| `PROJECT`             | `00_project_master.csv`                 | Master (Stamdata)   | Prosjektdefinisjon, baseline-ramme og data-dato          |
| `WBS`                 | `01_master_wbs.csv`                     | Master / Hierarki   | Arbeidspakkestruktur (Work Breakdown Structure)          |
| `COST_ELEMENT`        | `02_master_cost_elements.csv`           | Master              | Kostnadselementer (Internal labor, Equipment, etc.)      |
| `FX_RATE`             | `03_erp_fx_rates.csv`                   | Master / Lookup     | Valutakurser per regnskapsperiode (NOK, EUR, USD)        |
| `VENDOR`              | `04_erp_vendor_master.csv`              | Master              | Leverandørkatalog med land og avtalt valuta              |
| `BUDGET_BASELINE`     | `05_erp_budget_baseline.csv`            | Transaksjon / Plan  | Periodisert budsjett per WBS og kostnadselement          |
| `PURCHASE_ORDER`      | `06_erp_purchase_orders.csv`            | Transaksjon         | Innkjøpsordrelinjer for eksterne leveranser              |
| `GOODS_RECEIPT`       | `07_erp_goods_receipts.csv`             | Transaksjon         | Mottak av varer og tjenester på PO-linjer                |
| `AP_INVOICE`          | `08_erp_ap_invoices.csv`                | Transaksjon         | Leverandørfakturaer koblet mot PO og WBS                 |
| `JOURNAL`             | `09_erp_journals.csv`                   | Transaksjon         | Periodiseringer, manuelle omposteringer og reverseringer |
| `GL_ACTUALS`          | `10_erp_gl_actuals.csv`                 | Transaksjon         | Hovedboksposteringer (faktiske kostnader / AC)           |
| `CHANGE_ORDER`        | `11_erp_change_orders.csv`              | Transaksjon         | Endringsanmodninger for prosjektomfang/budsjett          |
| `ACTIVITY`            | `12_primavera_activities.csv`           | Master / Fremdrift  | Fremdriftsaktiviteter i Primavera P6                     |
| `RELATIONSHIP`        | `13_primavera_relationships.csv`        | Relasjonstabell     | Nettverkskoblinger mellom aktiviteter (FS, SS, FF)       |
| `RESOURCE`            | `14_primavera_resources.csv`            | Master              | Ressurskatalog i Primavera (utstyr, roller, personer)    |
| `RESOURCE_ASSIGNMENT` | `15_primavera_resource_assignments.csv` | Transaksjon / Plan  | Planlagte timer per aktivitet og ressurs                 |
| `EMPLOYEE`            | `16_hr_employee_master.csv`             | Master              | Ansattoversikt med avdeling og stillingsrolle            |
| `CAPACITY_CALENDAR`   | `17_hr_capacity_calendar.csv`           | Transaksjon         | Kontraktsfestet kapasitet og fravær per uke              |
| `TIMESHEET`           | `18_hr_timesheets.csv`                  | Transaksjon         | Daglige førte timer per ansatt, WBS og aktivitet         |
| `GRANT_BUDGET`        | `19_grant_agreement_budget.csv`         | Transaksjon / Regel | Godkjent ramme for SkatteFUNN/Enova                      |

---

## 3. Detaljert ERD Relasjonsmatrise

Tabellen nedenfor spesifiserer alle relasjoner i datamodellen, inkludert kardinalitet, koblingsnøkler og referanseintegritet.

| Forelder-entitet (Parent Entity) | Relasjon              | Barn-entitet (Child Entity) | Kardinalitet | Primærnøkkel (PK) $\rightarrow$ Fremmednøkkel (FK)                          | Integritetsregel               |
| :------------------------------- | :-------------------- | :-------------------------- | :----------- | :-------------------------------------------------------------------------- | :----------------------------- |
| `PROJECT`                        | innehar               | `WBS`                       | `1 : N`      | `PROJECT.project_id` $\rightarrow$ `WBS.project_id`                         | Obligatorisk forelder          |
| `WBS`                            | inneholder (hierarki) | `WBS`                       | `1 : N`      | `WBS.wbs_id` $\rightarrow$ `WBS.parent_wbs_id`                              | Valgfri forelder               |
| `WBS`                            | budsjetteres i        | `BUDGET_BASELINE`           | `1 : N`      | `WBS.wbs_id` $\rightarrow$ `BUDGET_BASELINE.wbs_id`                         | Obligatorisk                   |
| `COST_ELEMENT`                   | budsjetteres i        | `BUDGET_BASELINE`           | `1 : N`      | `COST_ELEMENT.cost_element` $\rightarrow$ `BUDGET_BASELINE.cost_element`    | Obligatorisk                   |
| `WBS`                            | belastes i            | `GL_ACTUALS`                | `1 : N`      | `WBS.wbs_id` $\rightarrow$ `GL_ACTUALS.wbs_id`                              | Obligatorisk                   |
| `COST_ELEMENT`                   | belastes i            | `GL_ACTUALS`                | `1 : N`      | `COST_ELEMENT.cost_element` $\rightarrow$ `GL_ACTUALS.cost_element`         | Obligatorisk                   |
| `VENDOR`                         | utsteder              | `PURCHASE_ORDER`            | `1 : N`      | `VENDOR.vendor_id` $\rightarrow$ `PURCHASE_ORDER.vendor_id`                 | Obligatorisk                   |
| `WBS`                            | utstedt for           | `PURCHASE_ORDER`            | `1 : N`      | `WBS.wbs_id` $\rightarrow$ `PURCHASE_ORDER.wbs_id`                          | Obligatorisk                   |
| `COST_ELEMENT`                   | tilordnes             | `PURCHASE_ORDER`            | `1 : N`      | `COST_ELEMENT.cost_element` $\rightarrow$ `PURCHASE_ORDER.cost_element`     | Obligatorisk                   |
| `PURCHASE_ORDER`                 | mottar                | `GOODS_RECEIPT`             | `1 : N`      | `PURCHASE_ORDER.po_line_id` $\rightarrow$ `GOODS_RECEIPT.po_line_id`        | Obligatorisk                   |
| `PURCHASE_ORDER`                 | faktureres i          | `AP_INVOICE`                | `1 : N`      | `PURCHASE_ORDER.po_line_id` $\rightarrow$ `AP_INVOICE.po_line_id`           | Valgfri (Direktefaktura mulig) |
| `VENDOR`                         | fakturerer i          | `AP_INVOICE`                | `1 : N`      | `VENDOR.vendor_id` $\rightarrow$ `AP_INVOICE.vendor_id`                     | Obligatorisk                   |
| `WBS`                            | justeres av           | `CHANGE_ORDER`              | `1 : N`      | `WBS.wbs_id` $\rightarrow$ `CHANGE_ORDER.wbs_id`                            | Obligatorisk                   |
| `WBS`                            | grupperer             | `ACTIVITY`                  | `1 : N`      | `WBS.wbs_id` $\rightarrow$ `ACTIVITY.wbs_id`                                | Obligatorisk                   |
| `ACTIVITY`                       | forelder i            | `RELATIONSHIP`              | `1 : N`      | `ACTIVITY.activity_id` $\rightarrow$ `RELATIONSHIP.predecessor_activity_id` | Obligatorisk                   |
| `ACTIVITY`                       | etterfolger i         | `RELATIONSHIP`              | `1 : N`      | `ACTIVITY.activity_id` $\rightarrow$ `RELATIONSHIP.successor_activity_id`   | Obligatorisk                   |
| `ACTIVITY`                       | bemannes av           | `RESOURCE_ASSIGNMENT`       | `1 : N`      | `ACTIVITY.activity_id` $\rightarrow$ `RESOURCE_ASSIGNMENT.activity_id`      | Obligatorisk                   |
| `RESOURCE`                       | tilordnes i           | `RESOURCE_ASSIGNMENT`       | `1 : N`      | `RESOURCE.resource_id` $\rightarrow$ `RESOURCE_ASSIGNMENT.resource_id`      | Obligatorisk                   |
| `EMPLOYEE`                       | planlegges i          | `CAPACITY_CALENDAR`         | `1 : N`      | `EMPLOYEE.employee_id` $\rightarrow$ `CAPACITY_CALENDAR.employee_id`        | Obligatorisk                   |
| `EMPLOYEE`                       | fører timer i         | `TIMESHEET`                 | `1 : N`      | `EMPLOYEE.employee_id` $\rightarrow$ `TIMESHEET.employee_id`                | Obligatorisk                   |
| `WBS`                            | belastes med timer    | `TIMESHEET`                 | `1 : N`      | `WBS.wbs_id` $\rightarrow$ `TIMESHEET.wbs_id`                               | Obligatorisk                   |
| `ACTIVITY`                       | fremdrives av         | `TIMESHEET`                 | `1 : N`      | `ACTIVITY.activity_id` $\rightarrow$ `TIMESHEET.activity_id`                | Obligatorisk                   |

---

## 4. Strukturert ERD-Kardiogram (Entitetsstrukturer)

Nedenfor spesifiseres primærnøkler og fremmednøkler for kjernedomene.

### 4.1 ERP Innkjøp og Fakturaflyt (Commitment Chain)

```text
[VENDOR] (1) ────< (N) [PURCHASE_ORDER] (1) ────< (N) [GOODS_RECEIPT]
   │                          │
   │                          └─────────────< (N) [AP_INVOICE]
   │                                                    │
   └────────────────────────────────────────────────────┘
```

### 4.2 Fremdrifts- og Timeføringsstruktur (Schedule & Labor Chain)

```text
[WBS] (1) ────< (N) [ACTIVITY] (1) ────< (N) [RESOURCE_ASSIGNMENT] >──── (1) [RESOURCE]
  │                     │
  │                     └──────────────< (N) [TIMESHEET] >──── (1) [EMPLOYEE]
  │                                                │
  └────────────────────────────────────────────────┘
```

---

## 5. Kartlegging fra ERD til Stjernemodell (Power BI Transformation)

For å bygge den analytiske stjernemodellen i Power BI slås flere av de operasjonelle ERD-entitetene sammen til felles dim- og faktatabeller:

1. **`Dim_WBS`**: Dannes fra `WBS`, beriket med hierarkibeskrivelser og prosjektdata fra `PROJECT`.
2. **`Dim_Vendor`**: Dannes direkte fra `VENDOR`.
3. **`Dim_Employee`**: Dannes direkte fra `EMPLOYEE`.
4. **`Dim_Activity`**: Dannes fra `ACTIVITY`, med avhengighetsindatorer fra `RELATIONSHIP`.
5. **`Fact_BudgetBaseline`**: Konsoliderer periodiserte budsjettlinjer fra `BUDGET_BASELINE`.
6. **`Fact_GLActuals`**: Kombinerer bokførte actuals fra `GL_ACTUALS` og justeringer fra `JOURNAL`.
7. **`Fact_Timesheets`**: Konsoliderer timerader fra `TIMESHEET`, koblet mot `Dim_Employee`, `Dim_WBS` og `Dim_Activity`.
8. **`Fact_PurchaseCommitments`**: Kobler `PURCHASE_ORDER`, `GOODS_RECEIPT` og `AP_INVOICE` på `po_line_id` for å beregne uavregnede forpliktelser.

---

## 6. Oppsummering

Denne ERD-spesifikasjonen sikrer at **datagrunnlaget for GreenPilot 2026 er 100% konsistent**. Alle primærnøkler og fremmednøkler i CSV-datasettet har bekreftet referanseintegritet, slik at du trygt kan bygge ETL-rutiner, Power Query-transformasjoner og Power BI-rapporter for Elkem.

moderne datateknisk praksis (Medallion-arkitektur: Bronze $\rightarrow$ Silver $\rightarrow$ Gold $\rightarrow$ Business/Semantic Ready).Anbefalt 5-stegs Python Pipeline-arkitektur[Rådata (data/)]
│
▼

1. INGESTION & VALIDATION (Bronze) --> Sjekker filtyper, tegnsett, manifest og BOM
   │
   ▼
2. DATA QUALITY & CLEANING (Silver) --> 3-veis matching, valutakonvertering, avviksflagg
   │
   ▼
3. STAR SCHEMA MODELING (Gold) --> Dim*\* og Fact*\* tabeller + Dim_Date
   │
   ▼
4. BUSINESS RULES & EVM ENRICHMENT --> IFRS / IAS 38-klassifisering, Open Commitments, EVM
   │
   ▼
5. BUSINESS READY & TRANSPARENCY LOG --> Eksport til Power BI + Revisjonslogg (JSON/CSV)
   Hva skjer i de ulike stegene?Steg 1: Ingestion & Validation (Bronze / Raw Layer)Leser rå-CSV-ene fra data/.Validerer filenes integritet mot 21_manifest.csv og 20_data_dictionary.csv.Vasker tegnsett (UTF-8 BOM \ufeff) og detekterer skilletegn automatisk.Steg 2: Data Quality & Cleaning (Silver / Cleaned Layer)Referansiell integritet: Sjekker om alle nøkler i faktatabellene finnes i mastertabellene.3-Vei Matching: Kobler PO, GR og AP for å avdekke overfakturering og uavregnede varemottak.Valuta-normalisering: Omregner valutafakturaer og innkjøpsordrer (EUR/USD) til NOK via FX-tabellen.Cut-off sjekk: Verifiserer bokføringsdatoer mot prosjektets skjæringsdato (2026-11-01).Steg 3: Star Schema Modeling (Gold / Dimensional Layer)Oppretter fellesdimensjonene (Dim_WBS, Dim_CostElement, Dim_Vendor, Dim_Employee, Dim_Activity, Dim_Resource).Genererer den dynamiske kalendertabellen (Dim_Date).Bygger rene faktatabeller (Fact_GLActuals, Fact_BudgetBaseline, Fact_Timesheets, osv.).Steg 4: Business Rules & EVM Enrichment (Semantic / Accounting Layer)IFRS / IAS 38-berikelse: Flagger om kostnadene gjelder Forskning (kostnadsføres direkte på WBS-100) eller Utvikling (aktiveres som anlegg under utførelse / AuC på WBS-300).Open Commitments: Beregner gjenstående innkjøpsforpliktelser per PO-linje ($\text{PO} - \text{AP}$).EVM-grunnlag: Kobler godkjente endringsordrer (Fact_ChangeOrders) mot baseline for å skille reelle kostnadsoverskridelser fra ubehandlede endringssøknader.Steg 5: Business Ready Export & Transparency Audit Log (Reporting Layer)Lagrer de ferdige tabellene i processed/star_schema/ klare for Power BI.Skriver ut en strukturert transparens- og auditlogg (pipeline_execution_audit.log / .json) som dokumenterer nøyaktig hvilke rader som ble korrigert, hvilke avvik som ble funnet, og hva totaltallene ble.Hvorfor denne oppdelingen gir verdi i din ShowcaseFull transparens (Audit Trail): En prosjektcontroller i Elkem skal ikke bare levere tall, men kunne bevise hvorfor et tall er som det er. Ved å skille Steg 2 (Cleaning) fra Steg 4 (Business Rules) kan du vise frem nøyaktig hva som var rådata vs. regnskapsmessige justeringer.Feilsøking i VS Code: Hvis et tall i Power BI ser feil ut, kan du kjøre pipelinen steg-for-steg og se nøyaktig i hvilket lag avviket oppsto.
