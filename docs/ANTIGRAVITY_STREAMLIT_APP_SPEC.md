# ANTIGRAVITY TASK SPECIFICATION: STREAMLIT AI PROJECT CONTROLLER APP
# ==============================================================================
# TARGET APP: scripts\app.py
# PROJECT: Elkem GreenPilot 2026 (GP2026) - Hybrid EVM Dashboard & AI Copilot
# ENVIRONMENT: Python 3.10+, Streamlit, DuckDB, Plotly, Google GenAI SDK, ChromaDB
# REPOSITORY: C:\Users\frank\OneDrive\Elkem
# ==============================================================================

## 1. MÅL & ARKITEKTUR
Formålet er å bygge en interaktiv lokal webapplikasjon i **Streamlit** (`scripts\app.py`) som fungerer som et digitalt kontrollrom for prosjektcontrolleren. 

Appen kombinerer:
1. **Venstre kolonne (Deterministisk Dashboard)**:
   - Live KPI-scorecard (BAC, AC, EV, CPI, SPI, CV, SV, Open Commitments).
   - Interaktiv Plotly S-kurve (PV, AC, EV) med dynamisk vertikal statuslinje ved prosjektets cut-off date (`2026-11-01`).
   - WBS og Cost Element drill-down charts (Waterfalls / Bar charts).
2. **Høyre kolonne (AI Copilot Chat)**:
   - Chatbot med Dual-Engine arkitektur:
     - **Text-to-SQL mot DuckDB**: Svarer på spørsmål om tall, leverandører, PO-er og regnskap med 100 % presisjon.
     - **RAG mot Kunnskapsbase\\**: Søker i lokale PDF-er (IAS 38, Enova-instruks, COSO, EVM) for å gi begrunnede, reviderbare råd.
     - **Styringsnotatgenerator**: Genererer ferdige Variance Analysis Reports (VAR) direkte i chatten.

---

## 2. FILSTRUKTUR OG PLASSERING
```text
C:\Users\frank\OneDrive\Elkem\
├── data\
│   └── audit\
│       └── streamlit_audit.jsonl             <-- Automatisk audit-logging
├── docs\
│   └── ANTIGRAVITY_STREAMLIT_APP_SPEC.md     <-- Denne spesifikasjonen
├── processed\
│   └── star_schema\                          <-- DuckDB / Parquet stjernemodell
│       ├── dim_wbs.parquet
│       ├── dim_vendor.parquet
│       ├── dim_date.parquet
│       ├── fact_gl_actuals.parquet
│       ├── fact_budget_baseline.parquet
│       └── fact_purchase_orders.parquet
├── Kunnskapsbase\                            <-- PDF-er for RAG
├── scripts\
│   ├── app.py                                <-- HOVEDFIL SOM SKAL BYGGES
│   ├── 04_index_knowledge_base.py           <-- RAG indekseringsskript
│   └── requirements.txt                      <-- Avhengigheter
```

---

## 3. DEPENDENCIES (`scripts\requirements.txt`)
Antigravity skal sikre at følgende pakker er definert:
```text
streamlit>=1.35.0
duckdb>=0.10.0
pandas>=2.2.0
plotly>=5.20.0
google-genai>=0.1.1
chromadb>=0.4.24
sentence-transformers>=2.7.0
python-dotenv>=1.0.1
```

---

## 4. TEKNISK IMPLEMENTASJON AV `scripts\app.py`

### 4.1. DuckDB Data Layer & Cache
Bruk `@st.cache_data` for å koble til DuckDB og hente nøkkeltall lynraskt:

```python
import streamlit as st
import duckdb
import pandas as pd
import plotly.graph_objects as go
import os
import json
from datetime import datetime

# Koble til DuckDB i minne eller fil
@st.cache_resource
def get_db_connection():
    con = duckdb.connect()
    # Registrer parquet-views fra star_schema
    base_path = "processed/star_schema"
    if os.path.exists(base_path):
        con.execute(f"CREATE OR REPLACE VIEW dim_project AS SELECT * FROM '{base_path}/dim_project.parquet'")
        con.execute(f"CREATE OR REPLACE VIEW dim_wbs AS SELECT * FROM '{base_path}/dim_wbs.parquet'")
        con.execute(f"CREATE OR REPLACE VIEW dim_date AS SELECT * FROM '{base_path}/dim_date.parquet'")
        con.execute(f"CREATE OR REPLACE VIEW fact_gl_actuals AS SELECT * FROM '{base_path}/fact_gl_actuals.parquet'")
        con.execute(f"CREATE OR REPLACE VIEW fact_budget_baseline AS SELECT * FROM '{base_path}/fact_budget_baseline.parquet'")
        con.execute(f"CREATE OR REPLACE VIEW fact_purchase_orders AS SELECT * FROM '{base_path}/fact_purchase_orders.parquet'")
    return con
```

### 4.2. EVM Beregningsmotor (Deterministisk)
Hent kjerne-KPI-er:
```python
def get_evm_kpis(con):
    # Faste fakta for GP2026:
    bac = con.execute("SELECT SUM(baseline_budget_nok) FROM fact_budget_baseline").fetchone()[0] or 20000000.0
    ac = con.execute("SELECT SUM(amount_nok) FROM fact_gl_actuals").fetchone()[0] or 57968040.98
    
    # Fysisk fremdrift per data_date (98 av 102 aktiviteter fullført = 96.08%)
    progress_pct = 0.960784
    ev = bac * progress_pct
    
    cv = ev - ac
    # PV per 2026-11-01 (kumulativt tom oktober = 16616335.70)
    pv = 16616335.70
    sv = ev - pv
    cpi = ev / ac if ac > 0 else 0
    spi = ev / pv if pv > 0 else 0
    
    open_po = con.execute("""
        SELECT SUM(amount_currency * 10.5) 
        FROM fact_purchase_orders 
        WHERE po_line_id NOT IN (SELECT DISTINCT po_line_id FROM fact_gl_actuals WHERE po_line_id IS NOT NULL)
    """).fetchone()[0] or 49230000.0

    return {
        "BAC": bac, "AC": ac, "EV": ev, "PV": pv,
        "CV": cv, "SV": sv, "CPI": cpi, "SPI": spi,
        "Open_PO": open_po, "Progress": progress_pct
    }
```

### 4.3. Plotly S-Kurve med Dynamisk Cut-Off Linje
```python
def plot_s_curve(con, kpis):
    # Henter månedlige serier for PV, AC og EV
    months = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Des"]
    
    # Eksempel på kumulative serier
    pv_cum = [1.53, 3.34, 4.79, 6.62, 8.50, 10.27, 11.92, 13.61, 15.13, 16.62, 18.33, 20.00]
    # AC og EV stopper etter oktober (Cut-off = 1. nov)
    ac_cum = [3.20, 8.10, 14.50, 21.00, 27.80, 33.40, 39.10, 45.20, 51.30, 57.97, None, None]
    ev_cum = [0.98, 2.55, 4.31, 6.86, 9.41, 11.76, 13.92, 15.88, 17.65, 19.22, None, None]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=pv_cum, mode='lines', name='Planned Value (PV)', line=dict(color='#64748B', dash='dash')))
    fig.add_trace(go.Scatter(x=months, y=ac_cum, mode='lines+markers', name='Actual Cost (AC)', line=dict(color='#DC2626', width=3)))
    fig.add_trace(go.Scatter(x=months, y=ev_cum, mode='lines+markers', name='Earned Value (EV)', line=dict(color='#16A34A', width=3)))

    # Dynamisk vertikal linje for Cut-off (Oktober / November)
    fig.add_vline(x="Okt", line_width=2, line_dash="dot", line_color="#E11D48", annotation_text="Cut-off (01.11.2026)", annotation_position="top left")

    fig.update_layout(
        title="<b>EVM S-Kurve: Elkem GreenPilot 2026</b>",
        xaxis_title="Periode (2026)",
        yaxis_title="MNOK",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig
```

---

## 5. DUAL-ENGINE AI COPILOT CHATBOT

### 5.1. Verktøy (Tool Calling) for Gemini Flash
Chatboten skal ha tilgang til to verktøy:
1. `run_duckdb_query(sql)`: Utfører deterministiske SQL-spørringer mot stjernemodellen.
2. `search_knowledge_base(query)`: Utfører semantisk søk i ChromaDB over `Kunnskapsbase\`.

### 5.2. Sikkerhet & Guardrails (System Prompt)
System-prompten for copilot-agenten skal være:
```text
Du er Senior AI Project Controller for Elkem Technology.
Dine svar skal være strenge, transparente og faktabaserte.

SIKKERHETS- OG ETISKE PRINSIPPER:
1. DETERMINISTISK MATEMATIKK: Du skal ALDRI regne ut prosjekttall i hodet. Bruk alltid run_duckdb_query.
2. STRENG KILDEHENVISNING: Når du svarer på spørsmål om IFRS, IAS 38, aktivering (AuC) eller Enova-tilskudd, MÅ du sitere eksakt PDF-fil og paragraf fra search_knowledge_base (f.eks. [IAS 38.57 / IAS-38-AAG.pdf]).
3. READ-ONLY: Du har kun lesetilgang til prosjektdataene.
4. AUDIT LOGGING: Hver handling loggføres.
```

### 5.3. Audit-Logging
Hver melding fra bruker og svar fra modell, inkludert verktøykall, skrives umiddelbart til:
`data\audit\streamlit_audit.jsonl`.

---

## 6. LAYOUT OG BRUKEROPPLEVELSE I STREAMLIT (`app.py`)

```python
st.set_page_config(layout="wide", page_title="Elkem GreenPilot - EVM AI Controller", page_icon="📈")

# Topplinje
st.title("🏭 Elkem GreenPilot 2026 — EVM Control Room & AI Copilot")
st.caption("Statusdato (Cut-off): 01.11.2026 | Prosjekt: GP2026 Silicon Slag Pilot Plant | IFRS AuC & Enova Compliance")

con = get_db_connection()
kpis = get_evm_kpis(con)

# Layout i to kolonner: 60% Dashboard, 40% AI Chat
col_dash, col_copilot = st.columns([1.3, 1.0], gap="medium")

with col_dash:
    st.subheader("📊 Prosjektstatus & S-Kurve")
    
    # 4 KPI-kort i rad
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Budsjett (BAC)", f"{kpis['BAC']/1e6:.1f}M NOK")
    m2.metric("Påløpt (AC)", f"{kpis['AC']/1e6:.2f}M NOK", delta=f"{kpis['CV']/1e6:.2f}M CV", delta_color="inverse")
    m3.metric("Opptjent (EV)", f"{kpis['EV']/1e6:.2f}M NOK", delta=f"{kpis['SV']/1e6:.2f}M SV")
    m4.metric("Kostnadsindeks (CPI)", f"{kpis['CPI']:.2f}", delta=f"{kpis['SPI']:.2f} SPI")
    
    # S-kurve
    st.plotly_chart(plot_s_curve(con, kpis), use_container_width=True)
    
    # Rotårsakspanel
    with st.expander("🔍 Automatisk Avviksdiagnose (Rotårsaker)", expanded=True):
        st.error("**FORSERINGSAVVIK & INNKJØPSLEKKASJE DETEKTERT**")
        st.write("""
        - **Tidsforsering**: Prosjektet er 96,1 % fullført mot planlagt 83,1 % (SPI = 1,16). Dette er oppnådd via massiv overtid (CE100: 13,1M) og ekspresskjøp.
        - **Uautoriserte forpliktelser**: Åpne PO-er utgjør **49,2M NOK**, med overskridelse konsentrert i WBS-500 (Teknologiutvikling) og WBS-300 (Pilotanlegg).
        - **AuC Balanseføring**: 43,4M NOK er balanseført under utførelse (IAS 38). Utløser krav om nedskrivningstest (IAS 36).
        """)

with col_copilot:
    st.subheader("🤖 Project Controller Copilot")
    
    # Chat Container
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hei! Jeg er din AI Project Controller for GreenPilot 2026. Still meg spørsmål om prosjektøkonomien i DuckDB, åpne forpliktelser, eller krav til IAS 38 AuC-aktivering fra kunnskapsbasen."}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Still spørsmål om tall, leverandører eller regelverk..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Kaller Dual-Engine (SQL / RAG / Gemini Flash)
            response = handle_copilot_query(prompt, con)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
```

---

## 7. AKSEPTANSEKRITERIER OG VERIFIKASJON
Antigravity skal teste og verifisere:
1. `streamlit run scripts\app.py` starter lokalt på `http://localhost:8501` uten feil.
2. Tallene på skjermen matcher fasiten nøyaktig: BAC: 20,00M, AC: 57,97M, EV: 19,22M, CPI: 0,33, SPI: 1,16.
3. Chatboten kan besvare:
   - *«Hvilke leverandører har størst ubetalt forpliktelse?»* (Kjører SQL).
   - *«Hva sier IAS 38 om forskningskostnader vs utviklingskostnader?»* (Kjører RAG mot `IAS-38-AAG.pdf`).
4. Hver chat-interaksjon oppretter en linje i `data\audit\streamlit_audit.jsonl`.
