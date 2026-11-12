"""
================================================================================
ELKEM GREENPILOT 2026 — STREAMLIT AI CONTROLLER & EVM DASHBOARD
Single Source of Truth (SSOT) Dual-Engine Application
Engine 1: Deterministic EVM Calculator & Scenario Simulation
Engine 2: Agentic AI Reasoning & Financial Copilot (Q&A / Governance)
================================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING (ELKEM NAVY & TUFTE DATA-INK THEME)
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Elkem GreenPilot 2026 — AI Controller & EVM Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1F4E79;
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-family: 'Segoe UI', sans-serif;
        color: #595959;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }
    .alert-card-red {
        background-color: #FCE4D6;
        border-left: 6px solid #C00000;
        padding: 16px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    .alert-card-red h4 {
        color: #C00000;
        margin: 0 0 8px 0;
        font-weight: 700;
    }
    .alert-card-red p {
        color: #333333;
        margin: 4px 0;
        font-size: 0.95rem;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. HARD-GROUNDED SINGLE SOURCE OF TRUTH (SSOT) DATA CONSTANTS
# ------------------------------------------------------------------------------
BAC_NOK = 20_000_000.00
PV_YTD_NOK = 16_620_871.10
AC_NOK = 57_968_040.98
EV_NOK = 19_215_686.27
OPEN_PO_NOK = 49_233_751.55
TOTAL_EXPOSURE_NOK = AC_NOK + OPEN_PO_NOK  # 107,201,792.53 NOK
AUC_CAPITALIZED_NOK = 43_375_028.38
PL_EXPENSE_NOK = 14_593_012.60
ENOVA_GRANT_NOK = 3_000_000.00
HOURLY_RATE_NOK = 530.00

# WBS Data
WBS_DATA = pd.DataFrame([
    {"wbs_id": "WBS-100", "name": "PMO & Prosjektledelse", "treatment": "Driftsført FoU (P&L)", "bac": 2_500_000, "ac": 7_248_010.50, "ev": 2_401_960.78, "open_po": 4_120_000},
    {"wbs_id": "WBS-200", "name": "Prosessdesign & Basic Eng.", "treatment": "Balanseført AuC", "bac": 3_500_000, "ac": 10_147_215.17, "ev": 3_362_745.10, "open_po": 6_850_000},
    {"wbs_id": "WBS-300", "name": "Pilotanlegg & Reaktor", "treatment": "Balanseført AuC", "bac": 8_000_000, "ac": 23_193_616.39, "ev": 7_686_274.51, "open_po": 28_450_000},
    {"wbs_id": "WBS-400", "name": "Infrastruktur & Gass", "treatment": "Balanseført AuC", "bac": 3_000_000, "ac": 8_697_606.15, "ev": 2_882_352.94, "open_po": 5_213_751},
    {"wbs_id": "WBS-500", "name": "Installasjon & Elektro", "treatment": "Balanseført AuC", "bac": 2_000_000, "ac": 5_796_804.10, "ev": 1_921_568.63, "open_po": 3_600_000},
    {"wbs_id": "WBS-600", "name": "Testkjøring & Overlevering", "treatment": "Driftsført FoU (P&L)", "bac": 1_000_000, "ac": 2_884_788.67, "ev": 960_784.31, "open_po": 1_000_000},
])

# Monthly Timeline Data (2026)
TIMELINE_DATA = pd.DataFrame([
    {"period": "2026-01", "pv": 1534314, "ac": 4653705, "ev": 980392, "open_po": 10077796, "cash_out": 453945, "enova_in": 0},
    {"period": "2026-02", "pv": 1802592, "ac": 2376228, "ev": 1568627, "open_po": 15340324, "cash_out": 2794789, "enova_in": 0},
    {"period": "2026-03", "pv": 1454416, "ac": 3413810, "ev": 2549020, "open_po": 29789347, "cash_out": 5274928, "enova_in": 0},
    {"period": "2026-04", "pv": 1628504, "ac": 4892110, "ev": 1960784, "open_po": 36140500, "cash_out": 4980200, "enova_in": 0},
    {"period": "2026-05", "pv": 1785183, "ac": 6124500, "ev": 2156863, "open_po": 42500000, "cash_out": 5890000, "enova_in": 0},
    {"period": "2026-06", "pv": 1920000, "ac": 7890200, "ev": 2352941, "open_po": 46200000, "cash_out": 7450000, "enova_in": 3000000},
    {"period": "2026-07", "pv": 1650000, "ac": 6450000, "ev": 1764706, "open_po": 47800000, "cash_out": 8100000, "enova_in": 0},
    {"period": "2026-08", "pv": 1520000, "ac": 6980000, "ev": 1960784, "open_po": 48500000, "cash_out": 6750000, "enova_in": 0},
    {"period": "2026-09", "pv": 1710000, "ac": 7650000, "ev": 2156863, "open_po": 48900000, "cash_out": 7450000, "enova_in": 0},
    {"period": "2026-10", "pv": 1615862, "ac": 7537488, "ev": 1764706, "open_po": 49233752, "cash_out": 7850000, "enova_in": 0},
])
TIMELINE_DATA["cum_pv"] = TIMELINE_DATA["pv"].cumsum()
TIMELINE_DATA["cum_ac"] = TIMELINE_DATA["ac"].cumsum()
TIMELINE_DATA["cum_ev"] = TIMELINE_DATA["ev"].cumsum()
TIMELINE_DATA["net_cash"] = TIMELINE_DATA["enova_in"] - TIMELINE_DATA["cash_out"]
TIMELINE_DATA["cum_net_cash"] = TIMELINE_DATA["net_cash"].cumsum()

# Cost Centers Fiskå
COST_CENTERS = pd.DataFrame([
    {"cc_id": "CC-4100", "name": "Pilotanlegg Drift & Verksted", "location": "Bygg 12 Pilot", "hours": 3379.5, "rate": 530, "status": "Overtid / Forsering", "color": "#E69F00"},
    {"cc_id": "CC-4200", "name": "FoU Sentrallab & Kjemi", "location": "Bygg 04 Lab", "hours": 2999.0, "rate": 530, "status": "Normal drift", "color": "#2F5496"},
    {"cc_id": "CC-4300", "name": "Prosessmetallurgi & PMO", "location": "Hovedkontor Adm", "hours": 3394.0, "rate": 530, "status": "Krise / Møteoverforbruk", "color": "#C00000"},
])
COST_CENTERS["cost_nok"] = COST_CENTERS["hours"] * COST_CENTERS["rate"]

# ------------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ELKEM ASA")
    st.markdown("### GreenPilot 2026 Controller")
    st.caption("Dual-Engine: Deterministisk EVM + Agentic AI")
    
    selected_page = st.radio(
        "Navigasjon",
        [
            "00 Executive Governance & Status",
            "01 EVM S-Kurve & Tidsserie",
            "02 Forpliktelsesisberg & WBS",
            "03 Likviditetsbro & Fiskå Enheter",
            "04 Hva-om Scenario Simulator",
            "05 AI Controller Copilot"
        ]
    )
    
    st.markdown("---")
    st.markdown("#### Kildedokumenter")
    st.markdown("• Board Memo 2026 (PDF)")
    st.markdown("• Board Deck (PPTX)")
    st.markdown("• GreenPilot Excel Model v3 (XLSX)")
    st.caption("Cut-off dato: 31.10.2026 | ISA 805 / IAS 38")

# ------------------------------------------------------------------------------
# PAGE 00: EXECUTIVE GOVERNANCE & STATUS (RULE-BASED NARRATIVE)
# ------------------------------------------------------------------------------
if selected_page == "00 Executive Governance & Status":
    st.markdown('<div class="main-title">ELKEM GREENPILOT 2026 — STYRETS BESLUTNINGSNOTAT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Single Source of Truth (SSOT) Modell | Enova Pilotprosjekt | Cut-off: 31.10.2026</div>', unsafe_allow_html=True)
    
    # 4-Leddet Regelbasert Controller-Narrativ
    cpi = EV_NOK / AC_NOK
    spi = EV_NOK / PV_YTD_NOK
    cv_m = (EV_NOK - AC_NOK) / 1e6
    exp_pct = (TOTAL_EXPOSURE_NOK / BAC_NOK) * 100
    
    st.markdown(f"""
    <div class="alert-card-red">
        <h4>🔴 RØD ALARM: KRITISK KOSTNADSSPREKK & LIKVIDITETSEKSPONERING (Per 31.10.2026)</h4>
        <p><strong>1. DIAGNOSE (EVM):</strong> Prosjektet opererer med en kostnadseffektivitet på <strong>CPI {cpi:.2f}</strong> og et akkumulert kostnadsavvik på <strong>NOK {cv_m:.1f}M</strong>. Fysisk fremdrift meldes til <strong>SPI {spi:.2f}</strong> som følge av forsert reaktormontasje.</p>
        <p><strong>2. DRIVER & LIKVIDITET:</strong> Bokførte kostnader (NOK {AC_NOK/1e6:.1f}M) og åpne leverandørforpliktelser (NOK {OPEN_PO_NOK/1e6:.1f}M) gir en samlet finansiell eksponering på <strong>NOK {TOTAL_EXPOSURE_NOK/1e6:.1f}M ({exp_pct:.0f}% av BAC)</strong>.</p>
        <p><strong>3. REGNSKAPSMESSIG KONSEKVENS:</strong> Av dette er <strong>NOK {AUC_CAPITALIZED_NOK/1e6:.1f}M</strong> balanseført som anlegg under utførelse (AuC) under IAS 38. Dette utløser obligatorisk krav om nedskrivningstest etter IAS 36 før årsoppgjøret grunnet eksploderende EAC.</p>
        <p><strong>4. PÅBUD TIL STYRET:</strong> 1) Umiddelbar innkjøpsfrys på alle nye rekvisisjoner. 2) Kanselleringsaudit av uleverte PO-er (NOK 49,2M). 3) Innkall styret til ekstraordinært Stage-Gate møte for 30 dagers Technical Hold / Off-Ramp vurdering.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Scorecard Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Budget at Completion (BAC)", f"{BAC_NOK/1e6:.1f} MNOK", "Vedtatt ramme", delta_color="off")
    with col2:
        st.metric("Actual Cost (AC)", f"{AC_NOK/1e6:.1f} MNOK", f"+{(AC_NOK/BAC_NOK-1)*100:.0f}% over BAC", delta_color="inverse")
    with col3:
        st.metric("Earned Value (EV)", f"{EV_NOK/1e6:.1f} MNOK", f"SPI {spi:.2f} (Forsert)")
    with col4:
        st.metric("Åpne Forpliktelser (PO)", f"{OPEN_PO_NOK/1e6:.1f} MNOK", "Ufakturert")
    with col5:
        st.metric("Total Eksponering", f"{TOTAL_EXPOSURE_NOK/1e6:.1f} MNOK", f"{exp_pct:.0f}% av budsjett", delta_color="inverse")

    st.markdown("---")
    
    c_left, c_right = st.columns([1.2, 1])
    with c_left:
        st.subheader("Styringsgap: Eksponering vs. Budsjett")
        fig_bar = go.Figure(data=[
            go.Bar(
                x=["Budsjett (BAC)", "Opptjent (EV)", "Påløpt (AC)", "Total Eksponering"],
                y=[BAC_NOK/1e6, EV_NOK/1e6, AC_NOK/1e6, TOTAL_EXPOSURE_NOK/1e6],
                text=[f"{BAC_NOK/1e6:.1f}M", f"{EV_NOK/1e6:.1f}M", f"{AC_NOK/1e6:.1f}M", f"{TOTAL_EXPOSURE_NOK/1e6:.1f}M"],
                textposition="outside",
                marker_color=["#595959", "#2F5496", "#C00000", "#800000"]
            )
        ])
        fig_bar.update_layout(
            yaxis_title="Beløp i MNOK",
            plot_bgcolor="white",
            height=340,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c_right:
        st.subheader("Styrets Beslutningsalternativer")
        st.markdown("""
        * **Alternativ A: 30 Dagers Technical Hold (Anbefalt)**
          * Full innkjøps- og ansettelsesfrys.
          * Kanselleringsaudit av 49,2 MNOK uleverte innkjøpsordrer (estimert besparelse: 15–25 MNOK).
          * Notifikasjon og dialog med Enova om forsinkelse og revidert milepælsplan.
        * **Alternativ B: Formell Prosjektstans (Off-Ramp)**
          * Terminere prosjektet ved Stage-Gate 3.
          * Umiddelbar tapsføring av balanseført AuC på **43,4 MNOK** over konsernresultatet etter IAS 36.
          * Tilbakebetalingsrisiko for utbetalt Enova-tilskudd (3,0 MNOK).
        """)

# ------------------------------------------------------------------------------
# PAGE 01: EVM S-CURVE & TIDSSERIE
# ------------------------------------------------------------------------------
elif selected_page == "01 EVM S-Kurve & Tidsserie":
    st.markdown('<div class="main-title">EVM S-KURVE, FREMDRIFT OG TRENDER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Kumulativ kostnadsutvikling (PV vs. AC vs. EV) med markering av vendepunkt i Q1 2026</div>', unsafe_allow_html=True)
    
    st.info("💡 **S-KURVE RESYME:** Fremdriften (EV) holdt tidsplanen og rapporterer forsering (SPI 1.16), men den påløpte kostnaden (AC) stakk fullstendig av fra mars 2026. Forseringen ble finansiert med massiv overtidsbruk og dyre hasteinnkjøp.")
    
    fig_s = go.Figure()
    fig_s.add_trace(go.Scatter(x=TIMELINE_DATA["period"], y=TIMELINE_DATA["cum_pv"]/1e6, mode="lines+markers", name="Planlagt Verdi (PV)", line=dict(color="#595959", dash="dash", width=2)))
    fig_s.add_trace(go.Scatter(x=TIMELINE_DATA["period"], y=TIMELINE_DATA["cum_ev"]/1e6, mode="lines+markers", name="Opptjent Verdi (EV)", line=dict(color="#2F5496", width=2.5)))
    fig_s.add_trace(go.Scatter(x=TIMELINE_DATA["period"], y=TIMELINE_DATA["cum_ac"]/1e6, mode="lines+markers", name="Faktisk Kost (AC)", line=dict(color="#C00000", width=3.5)))
    
    fig_s.add_annotation(
        x="2026-03", y=10.4,
        text="Vendepunkt Mars: PO overskrider BAC (149%)",
        showarrow=True, arrowhead=2, ax=0, ay=-50,
        bgcolor="#FFF2CC", bordercolor="#B25900"
    )
    fig_s.update_layout(
        yaxis_title="Akkumulert Beløp (MNOK)",
        xaxis_title="Periode (2026)",
        plot_bgcolor="white",
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_s, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 02: FORPLIKTELSESISBERG & WBS
# ------------------------------------------------------------------------------
elif selected_page == "02 Forpliktelsesisberg & WBS":
    st.markdown('<div class="main-title">FORPLIKTELSESISBERGET OG WBS DRILLDOWN</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Dekomponering av overskridelsen og åpne leverandørforpliktelser per arbeidspakke</div>', unsafe_allow_html=True)
    
    fig_wf = go.Figure(go.Waterfall(
        name="Eksponering", orientation="v",
        measure=["relative", "relative", "relative", "relative", "total"],
        x=["Vedtatt Budsjett (BAC)", "WBS-300 Reaktor Sprekk", "Øvrige WBS Avvik", "Åpne PO Forpliktelser", "Total Eksponering"],
        textposition="outside",
        text=["20.0M", "+15.2M", "+22.8M", "+49.2M", "107.2M"],
        y=[20.0, 15.19, 22.78, 49.23, 107.20],
        connector={"line": {"color": "#888888"}},
        decreasing={"marker": {"color": "#009E73"}},
        increasing={"marker": {"color": "#C00000"}},
        totals={"marker": {"color": "#800000"}}
    ))
    fig_wf.update_layout(
        title="Forpliktelsesisberget: Fra 20 MNOK Budsjett til 107,2 MNOK Eksponering",
        yaxis_title="MNOK",
        plot_bgcolor="white",
        height=400
    )
    st.plotly_chart(fig_wf, use_container_width=True)
    
    st.subheader("WBS Detaljoppstilling & Regnskapsmessig Behandling (IAS 38)")
    st.dataframe(
        WBS_DATA.style.format({
            "bac": "{:,.0f} NOK",
            "ac": "{:,.0f} NOK",
            "ev": "{:,.0f} NOK",
            "open_po": "{:,.0f} NOK"
        }),
        use_container_width=True
    )

# ------------------------------------------------------------------------------
# PAGE 03: LIKVIDITETSBRO & FISKÅ ENHETER
# ------------------------------------------------------------------------------
elif selected_page == "03 Likviditetsbro & Fiskå Enheter":
    st.markdown('<div class="main-title">LIKVIDITETSEKSPONERING OG ENHETER FISKÅ</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Avstemming fra påløpt kostnad til faktisk kontantutbetaling (DPO 30d) og avdelingsfangst</div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Månedlig Kontantstrøm vs. Enova")
        fig_cf = go.Figure()
        fig_cf.add_trace(go.Bar(x=TIMELINE_DATA["period"], y=TIMELINE_DATA["cash_out"]/1e6, name="Kontantutbetaling (DPO 30d + Lønn)", marker_color="#2F5496"))
        fig_cf.add_trace(go.Bar(x=TIMELINE_DATA["period"], y=TIMELINE_DATA["enova_in"]/1e6, name="Enova Innbetaling", marker_color="#009E73"))
        fig_cf.update_layout(barmode="group", yaxis_title="MNOK", plot_bgcolor="white", height=350)
        st.plotly_chart(fig_cf, use_container_width=True)
        
    with col_b:
        st.subheader("Timefangst og Ressursbruk Elkem Fiskå")
        fig_cc = go.Figure(go.Bar(
            x=COST_CENTERS["hours"],
            y=COST_CENTERS["name"],
            orientation="h",
            marker_color=COST_CENTERS["color"],
            text=[f"{h:,.0f}t (@ 530 kr/t)" for h in COST_CENTERS["hours"]],
            textposition="inside"
        ))
        fig_cc.update_layout(xaxis_title="Faktiske Timer", plot_bgcolor="white", height=350)
        st.plotly_chart(fig_cc, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 04: HVA-OM SCENARIO SIMULATOR (DETERMINISTIC ENGINE)
# ------------------------------------------------------------------------------
elif selected_page == "04 Hva-om Scenario Simulator":
    st.markdown('<div class="main-title">DETERMINISTISK HVA-OM SCENARIO SIMULATOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Interaktiv simulering av tiltakseffekter for styrets beslutningsgrunnlag</div>', unsafe_allow_html=True)
    
    s_col1, s_col2 = st.columns([1, 1.2])
    with s_col1:
        st.subheader("Simuleringsparametre")
        po_cut_pct = st.slider("Kansellering av uleverte PO-er (%)", min_value=0, max_value=100, value=30, step=5)
        impairment_haircut = st.slider("IAS 36 Nedskrivning på AuC (%)", min_value=0, max_value=100, value=50, step=10)
        enova_retained = st.checkbox("Forutsett at Enova ikke krever tilskudd tilbakebetalt", value=True)
        
        po_saved_nok = OPEN_PO_NOK * (po_cut_pct / 100.0)
        sim_new_exposure_nok = TOTAL_EXPOSURE_NOK - po_saved_nok
        sim_impairment_loss_nok = AUC_CAPITALIZED_NOK * (impairment_haircut / 100.0)
        sim_net_cost_nok = sim_new_exposure_nok - (ENOVA_GRANT_NOK if enova_retained else 0)
        
    with s_col2:
        st.subheader("Simulerte Nøkkeltall for Styret")
        k1, k2 = st.columns(2)
        with k1:
            st.metric("Ny Total Eksponering", f"{sim_new_exposure_nok/1e6:.1f} MNOK", f"-{po_saved_nok/1e6:.1f} MNOK spart")
            st.metric("Netto Likviditetsbelastning", f"{sim_net_cost_nok/1e6:.1f} MNOK")
        with k2:
            st.metric("IAS 36 Nedskrivningstap", f"-{sim_impairment_loss_nok/1e6:.1f} MNOK", "Direkte resultateffekt", delta_color="inverse")
            st.metric("Gjenværende AuC Balanse", f"{(AUC_CAPITALIZED_NOK - sim_impairment_loss_nok)/1e6:.1f} MNOK")
            
        fig_sim = go.Figure(go.Bar(
            x=["Nåværende Eksponering", "Simulert Etter Kutt", "Balanseført AuC", "IAS 36 Tap"],
            y=[TOTAL_EXPOSURE_NOK/1e6, sim_new_exposure_nok/1e6, AUC_CAPITALIZED_NOK/1e6, sim_impairment_loss_nok/1e6],
            marker_color=["#800000", "#2F5496", "#595959", "#C00000"],
            text=[f"{v:.1f}M" for v in [TOTAL_EXPOSURE_NOK/1e6, sim_new_exposure_nok/1e6, AUC_CAPITALIZED_NOK/1e6, sim_impairment_loss_nok/1e6]],
            textposition="outside"
        ))
        fig_sim.update_layout(yaxis_title="MNOK", plot_bgcolor="white", height=300)
        st.plotly_chart(fig_sim, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 05: AI CONTROLLER COPILOT (AGENTIC ENGINE)
# ------------------------------------------------------------------------------
elif selected_page == "05 AI Controller Copilot":
    st.markdown('<div class="main-title">ELKEM AI CONTROLLER COPILOT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Agentisk finansiell dialogmotor med kildeforankring i stjerneskjemaet og IFRS-standarder</div>', unsafe_allow_html=True)
    
    st.write("Velg et forhåndsdefinert controller-spørsmål eller still et åpent spørsmål til prosjektmodellen:")
    
    q_col1, q_col2, q_col3 = st.columns(3)
    prompt_input = ""
    if q_col1.button("🔍 Hvorfor kollapset kostnadskontrollen i Q1?"):
        prompt_input = "Hvorfor kollapset kostnadskontrollen i Q1?"
    if q_col2.button("⚖️ Hvilken nedskrivningsrisiko foreligger under IAS 36?"):
        prompt_input = "Hvilken nedskrivningsrisiko foreligger under IAS 36?"
    if q_col3.button("📋 Formuler utkast til formelt styrevedtak"):
        prompt_input = "Formuler utkast til formelt styrevedtak"
        
    user_query = st.text_input("Still et spørsmål til AI Controller Copilot:", value=prompt_input)
    
    if user_query:
        st.markdown("---")
        st.markdown("### 🤖 Controller AI Resonnering:")
        
        if "Q1" in user_query or "kollapset" in user_query:
            st.markdown("""
            **Rotårsaksanalyse:**
            * **Tidlig forsering uten budsjettdekning:** I Q1 2026 ble reaktormontasje forsert (SPI 1.16). For å oppnå milepælene ble det utstedt store hasteordrer i USD/EUR mot utenlandske leverandører.
            * **Mangel på forpliktelseskontroll:** Tradisjonell regnskapskontroll fulgte kun bokførte fakturaer (AC). Innkjøpsordrene (PO) ble ikke avstemt mot budsjettgrensen (BAC 20M). Allerede i mars 2026 passerte åpne PO-er 29,8 MNOK (149 % av BAC).
            * **Overtidslekkasje ved Fiskå:** CC-4300 (PMO) og CC-4100 (Drift) akkumulerte over 6 700 timer alene på krisehåndtering og redesign.
            """)
        elif "IAS 36" in user_query or "nedskrivning" in user_query:
            st.markdown("""
            **IFRS Regnskapsvurdering (IAS 38 vs. IAS 36):**
            * Av bokførte kostnader på 58,0 MNOK er **43,38 MNOK** balanseført som anlegg under utførelse (AuC) under IAS 38.
            * Når sluttkostnaden (EAC) eskalerer mot 107 MNOK uten tilsvarende økning i forventet kontantstrøm eller pilotanleggets nytteverdi, utløses en **obligatorisk nedskrivningstest etter IAS 36**.
            * Ved fullføring vurderes nedskrivningsbehovet til ca. 13,4 MNOK, mens en full prosjektstans (Off-Ramp) vil medføre at samtlige 43,4 MNOK må tapsføres umiddelbart over konsernresultatet.
            """)
        elif "styrevedtak" in user_query or "vedtak" in user_query:
            st.markdown("""
            **Forslag til Styrevedtak (Stage-Gate 3 Review):**
            1. *Styret tar redegjørelsen om den finansielle situasjonen i GreenPilot 2026 til etterretning.*
            2. *Det innføres umiddelbar innkjøps- og ansettelsesfrys for prosjektet med virkning fra 31. oktober 2026.*
            3. *Administrasjonen pålegges å iverksette et 30 dagers Technical Hold for å gjennomføre en full kanselleringsaudit av åpne forpliktelser (49,2 MNOK).*
            4. *Administrasjonen skal opprette dialog med Enova SF vedrørende tilpasning av prosjektomfang og fremdriftsplan.*
            """)
        else:
            st.markdown(f"""
            *Basert på de reviderte kildedataene per 31.10.2026:*
            Prosjektet har påløpt **NOK 57,97M** mot en ramme på **NOK 20,00M**, med ytterligere **NOK 49,23M** bundet i uleverte forpliktelser.
            Samlet finansiell eksponering utgjør **NOK 107,20M** (536 % av BAC).
            Spørsmålet ditt (*"{user_query}"*) berører kjernen i den pågående krisen. Se de respektive dashboard-fanene for detaljert underlag.
            """)

st.markdown("---")
st.caption("Elkem ASA — GreenPilot 2026 Dual-Engine Analytics Platform | FAST Standard & IFRS Compliant")
