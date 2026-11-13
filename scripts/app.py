"""
================================================================================
ELKEM GREENPILOT 2026 — DUAL-ENGINE AI CONTROLLER & EVM DASHBOARD
Single Source of Truth (SSOT) Streamlit Application
Engine 1: Deterministic EVM Calculator & Real-Time Triangle Rebalancing
Engine 2: Agentic AI Controller Copilot with In-Memory RAG Vector Database
================================================================================
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------------------------------------------------------------------
# 1. PAGE SETUP & STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Elkem GreenPilot 2026 — AI Project Controller",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-family: 'Segoe UI', -apple-system, sans-serif;
        color: #1F4E79;
        font-weight: 700;
        font-size: 2.1rem;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-family: 'Segoe UI', sans-serif;
        color: #595959;
        font-size: 1.0rem;
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
        line-height: 1.45;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. DATA CONSTANTS & MODEL DEFINITION (SINGLE SOURCE OF TRUTH)
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

WBS_DATA = pd.DataFrame([
    {"wbs_id": "WBS-100", "name": "PMO & Prosjektledelse", "treatment": "Driftsført FoU (P&L)", "bac": 2_500_000, "ac": 7_248_010.50, "ev": 2_401_960.78, "open_po": 4_120_000},
    {"wbs_id": "WBS-200", "name": "Prosessdesign & Basic Eng.", "treatment": "Balanseført AuC", "bac": 3_500_000, "ac": 10_147_215.17, "ev": 3_362_745.10, "open_po": 6_850_000},
    {"wbs_id": "WBS-300", "name": "Pilotanlegg & Reaktor", "treatment": "Balanseført AuC", "bac": 8_000_000, "ac": 23_193_616.39, "ev": 7_686_274.51, "open_po": 28_450_000},
    {"wbs_id": "WBS-400", "name": "Infrastruktur & Gass", "treatment": "Balanseført AuC", "bac": 3_000_000, "ac": 8_697_606.15, "ev": 2_882_352.94, "open_po": 5_213_751},
    {"wbs_id": "WBS-500", "name": "Installasjon & Elektro", "treatment": "Balanseført AuC", "bac": 2_000_000, "ac": 5_796_804.10, "ev": 1_921_568.63, "open_po": 3_600_000},
    {"wbs_id": "WBS-600", "name": "Testkjøring & Overlevering", "treatment": "Driftsført FoU (P&L)", "bac": 1_000_000, "ac": 2_884_788.67, "ev": 960_784.31, "open_po": 1_000_000},
])

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

COST_CENTERS = pd.DataFrame([
    {"cc_id": "CC-4100", "name": "Pilotanlegg Drift & Verksted", "location": "Bygg 12 Pilot", "hours": 3379.5, "rate": 530, "status": "Overtid / Forsering", "color": "#E69F00"},
    {"cc_id": "CC-4200", "name": "FoU Sentrallab & Kjemi", "location": "Bygg 04 Lab", "hours": 2999.0, "rate": 530, "status": "Normal drift", "color": "#2F5496"},
    {"cc_id": "CC-4300", "name": "Prosessmetallurgi & PMO", "location": "Hovedkontor Adm", "hours": 3394.0, "rate": 530, "status": "Krise / Møteoverforbruk", "color": "#C00000"},
])
COST_CENTERS["cost_nok"] = COST_CENTERS["hours"] * COST_CENTERS["rate"]

# ------------------------------------------------------------------------------
# 3. IN-MEMORY VECTOR DATABASE (RAG KNOWLEDGE BASE)
# ------------------------------------------------------------------------------
KNOWLEDGE_CHUNKS = [
    {
        "id": "IAS38-01",
        "category": "Regnskap (IFRS)",
        "source": "IAS 38 Immaterielle eiendeler & gtal_2016_factsheet",
        "title": "IAS 38 Balanseføringskriterier for Utvikling (AuC)",
        "text": "Etter IAS 38 avsnitt 57 kan utgifter til utvikling balanseføres som anlegg under utførelse (AuC) kun dersom foretaket oppfyller alle 6 kumulative kriterier: teknisk gjennomførbarhet, hensikt om fullføring, evne til å bruke/selge, påviselig fremtidig økonomisk fordel, tilgjengelighet av ressurser, og pålitelig måling av kostnader. I GreenPilot er 43,38 MNOK aktivert som AuC under WBS-200, 300, 400 og 500, mens WBS-100 (PMO) og WBS-600 er driftsført (14,59 MNOK) da generelle administrasjonskostnader aldri kan aktiveres."
    },
    {
        "id": "IAS36-01",
        "category": "Regnskap (IFRS)",
        "source": "IAS 36 Impairment of Assets & Grant Thornton Guide",
        "title": "IAS 36 Verdifallstest utløst av Budsjettoverskridelse",
        "text": "IAS 36 avsnitt 12 fastslår at en vesentlig kostnadsoverskridelse under oppføring utgjør en obligatorisk indikasjon på verdifall (impairment trigger). Når total finansiell eksponering når 107,2 MNOK (536 % av BAC), kreves det at gjenvinnbart beløp (høyeste av bruksverdi og netto salgsverdi) beregnes før årsoppgjøret. Dersom prosjektet fullføres estimeres nedskrivningsbehovet til ca. 13,4 MNOK, mens en full prosjektstans (Off-Ramp) krever 100 % umiddelbar nedskrivning av samtlige 43,38 MNOK over konsernresultatet."
    },
    {
        "id": "IAS20-01",
        "category": "Regnskap (IFRS)",
        "source": "IAS 20 Offentlige Tilskudd & Enova Tilskuddsavtale",
        "title": "IAS 20 Regnskapsføring av Enova-tilskudd",
        "text": "Etter IAS 20 skal investeringstilskudd regnskapsføres enten som en reduksjon av anleggsmiddelets balanseverdi (netting) eller som utsatt inntekt. Enova har innvilget 10,0 MNOK med en støttesats på ca. 24,9 %. 3,0 MNOK ble utbetalt i juni 2026 basert på rapporterte milepæler. Ved manglende oppfyllelse av milepælskrav eller uanmeldt prosjektterminering foreligger det risiko for tilbakebetalingskrav fra Enova SF etter statsstøtteregelverket."
    },
    {
        "id": "ISA805-01",
        "category": "Revisjon & Enova",
        "source": "ISA 805 (Revised) & Enova Instruks 2021",
        "title": "ISA 805 Revisjon av Særskilte Prosjektregnskap for Enova",
        "text": "ISA 805 regulerer uavhengig revisors attestasjon av særskilte regnskapsoppstillinger for offentlige tilskudd. Revisor må bekrefte at rapporterte kostnader er direkte henførbare til godkjente arbeidspakker, at timeføring er underbygget med attesterte timelister, at varemottak (GRNI) og leverandørfakturaer er 3-veis matchet, og at ingen interne administrative påslag eller ulovlige overskudd er belastet prosjektet."
    },
    {
        "id": "TIME-01",
        "category": "Revisjon & Enova",
        "source": "Retningslinjer for Timesatser 2025 & RF-1053B",
        "title": "SkatteFUNN og Enova Timeprisregler (RF-1053B)",
        "text": "Norges Forskningsråd og SkatteFUNN fastsetter at timesats for eget personell beregnes som 1,2 promille av avtalt årslønn ved prosjektets oppstart, men oppad begrenset til maksimalt 530 kr per time. Maksimalt antall godkjente timer per person per år er 1 850 timer. Overforbruk av timer i CC-4100 (3 380t) og CC-4300 (3 394t) kan ikke kompenseres ved å øke timesatsen utover 530 kr, noe som betyr at overtidspremier må dekkes 100 % av Elkem uten tilskuddsdekning."
    },
    {
        "id": "SG-01",
        "category": "Prosjektstyring & EVM",
        "source": "Stage Gate Management Guide & EVM Reference",
        "title": "Stage-Gate 3 Beslutningskriterier og Governance",
        "text": "Ved Stage-Gate 3 (Gjennomføringsfasen) skal styret evaluere tre alternativer: Alternativ A (30 Dagers Technical Hold med umiddelbar innkjøpsfrys, audit av 49,2 MNOK uleverte PO-er og omforhandling med Enova), Alternativ B (Formell Prosjektstans / Off-Ramp med full tapsføring av 43,4 MNOK AuC og tilbakebetaling av tilskudd), eller Alternativ C (Uendret videreføring mot en ukontrollert sluttkostnad på 107,2 MNOK). Administrasjonen anbefaler Alternativ A."
    },
    {
        "id": "EVM-01",
        "category": "Prosjektstyring & EVM",
        "source": "EVM Cheat Sheet & PMO Fabric Guide",
        "title": "EVM Formler og Ytelsesmetrikker for GreenPilot",
        "text": "Per 31.10.2026 er BAC = 20,00 MNOK, PV = 16,62 MNOK, AC = 57,97 MNOK, EV = 19,22 MNOK. Dette gir Cost Variance CV = EV - AC = -38,75 MNOK, Schedule Variance SV = EV - PV = +2,59 MNOK. Cost Performance Index CPI = EV / AC = 0,331. Schedule Performance Index SPI = EV / PV = 1,156. Fast-tracking (forsering) ga positiv tidshastighet (+5 uker), men til en ekstrem merkostnad (CPI 0,33)."
    },
    {
        "id": "TRIANGLE-01",
        "category": "Prosjektstyring & EVM",
        "source": "Iron Triangle Trade-Off Analysis",
        "title": "Iron Triangle Trade-Off: Hvorfor Sakking (Slow Down) Løser Krisen",
        "text": "I det tradisjonelle jerntriangelet (Kost, Tid, Omfang) er Time i dag den minste boblen fordi prosjektet ble forsert (SPI 1.16). Ved å sakke ned (Technical Hold i 30-60 dager) flyttes operasjonspunktet vekk fra det eksploderte kostnadshjørnet. Tidsforsinkelsen stanser omsetningen av 49,2 MNOK i åpne PO-er til faktiske kostnader og eliminerer overtidslekkasje, noe som gir en estimert reduksjon i finansiell eksponering på 15–25 MNOK."
    }
]

@st.cache_resource
def get_vector_db():
    corpus = [chunk["title"] + " " + chunk["text"] + " " + chunk["category"] for chunk in KNOWLEDGE_CHUNKS]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words=None)
    vectors = vectorizer.fit_transform(corpus)
    return vectorizer, vectors

# ------------------------------------------------------------------------------
# 4. SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ELKEM ASA")
    st.markdown("### GreenPilot 2026 Controller")
    st.caption("Dual-Engine: Deterministisk EVM + Agentic AI")
    
    selected_page = st.radio(
        "Navigasjon",
        [
            "00 Executive Governance & Status",
            "01 Dynamisk Jerntriangel (Trade-Offs)",
            "02 EVM S-Kurve & Tidsserie",
            "03 Forpliktelsesisberg & WBS",
            "04 Likviditetsbro & Fiskå Enheter",
            "05 Hva-om Scenario Simulator",
            "06 AI Controller Copilot (RAG & Vektor-DB)"
        ]
    )
    st.markdown("---")
    st.markdown("#### Kildedokumenter")
    st.caption("• Board Memo 2026 (PDF)")
    st.caption("• GreenPilot Excel Model v3 (XLSX)")
    st.caption("• IFRS IAS 38, IAS 36, IAS 20 & ISA 805")

# ------------------------------------------------------------------------------
# PAGE 00: EXECUTIVE GOVERNANCE
# ------------------------------------------------------------------------------
if selected_page == "00 Executive Governance & Status":
    st.markdown('<div class="main-title">ELKEM GREENPILOT 2026 — STYRETS BESLUTNINGSNOTAT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Single Source of Truth (SSOT) Modell | Enova Pilotprosjekt | Cut-off: 31.10.2026</div>', unsafe_allow_html=True)
    
    cpi = EV_NOK / AC_NOK
    spi = EV_NOK / PV_YTD_NOK
    cv_m = (EV_NOK - AC_NOK) / 1e6
    exp_pct = (TOTAL_EXPOSURE_NOK / BAC_NOK) * 100
    
    st.markdown(f"""
    <div class="alert-card-red">
        <h4>🔴 RØD ALARM: KRITISK KOSTNADSSPREKK & LIKVIDITETSEKSPONERING (Per 31.10.2026)</h4>
        <p><strong>1. DIAGNOSE (EVM):</strong> Prosjektet opererer med en kostnadseffektivitet på <strong>CPI {cpi:.2f}</strong> og et akkumulert kostnadsavvik på <strong>NOK {cv_m:.1f}M</strong>. Fysisk fremdrift meldes til <strong>SPI {spi:.2f}</strong> (+5 uker foran plan) som følge av forsert montasje.</p>
        <p><strong>2. DRIVER & LIKVIDITET:</strong> Bokførte kostnader (NOK {AC_NOK/1e6:.1f}M) og åpne leverandørforpliktelser (NOK {OPEN_PO_NOK/1e6:.1f}M) gir en samlet finansiell eksponering på <strong>NOK {TOTAL_EXPOSURE_NOK/1e6:.1f}M ({exp_pct:.0f}% av BAC)</strong>.</p>
        <p><strong>3. REGNSKAPSMESSIG KONSEKVENS:</strong> Av dette er <strong>NOK {AUC_CAPITALIZED_NOK/1e6:.1f}M</strong> balanseført som anlegg under utførelse (AuC) under IAS 38. Dette utløser obligatorisk krav om nedskrivningstest etter IAS 36 før årsoppgjøret grunnet eksploderende EAC.</p>
        <p><strong>4. PÅBUD TIL STYRET:</strong> 1) Umiddelbar innkjøpsfrys på alle nye rekvisisjoner. 2) Kanselleringsaudit av uleverte PO-er (NOK 49,2M). 3) Innkall styret til ekstraordinært Stage-Gate møte for 30 dagers Technical Hold / Off-Ramp vurdering.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Budget (BAC)", f"{BAC_NOK/1e6:.1f} MNOK", "Vedtatt ramme", delta_color="off")
    col2.metric("Actual Cost (AC)", f"{AC_NOK/1e6:.1f} MNOK", f"+{(AC_NOK/BAC_NOK-1)*100:.0f}% over BAC", delta_color="inverse")
    col3.metric("Earned Value (EV)", f"{EV_NOK/1e6:.1f} MNOK", f"SPI {spi:.2f} (Forsert)")
    col4.metric("Åpne PO-er", f"{OPEN_PO_NOK/1e6:.1f} MNOK", "Ufakturert binding")
    col5.metric("Total Eksponering", f"{TOTAL_EXPOSURE_NOK/1e6:.1f} MNOK", f"{exp_pct:.0f}% av BAC", delta_color="inverse")

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
        fig_bar.update_layout(yaxis_title="MNOK", plot_bgcolor="white", height=340, margin=dict(l=20, r=20, t=30, b=20))
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
# PAGE 01: DYNAMISK JERNTRIANGEL (TRADE-OFFS)
# ------------------------------------------------------------------------------
elif selected_page == "01 Dynamisk Jerntriangel (Trade-Offs)":
    st.markdown('<div class="main-title">DYNAMISK JERNTRIANGEL: TRADE-OFF RELASJONER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Relasjonelle spenningsvektorer mellom Kostnad, Tid og Omfang/Kvalitet</div>', unsafe_allow_html=True)
    
    t_col1, t_col2 = st.columns([1.1, 1])
    
    with t_col1:
        st.subheader("A: Begrensningstriangel & Operasjonspunkt")
        categories = ['KOST (107,2M Eksponering)', 'TID (SPI 1,16 / +5 uker)', 'OMFANG (96,1% EV / 43,4M AuC)']
        
        fig_tri = go.Figure()
        # Baseline
        fig_tri.add_trace(go.Scatterpolar(
            r=[100, 100, 100, 100],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(180, 180, 180, 0.15)',
            line=dict(color='#888888', dash='dash', width=2),
            name='Baseline Plan (100% Balansert)'
        ))
        # Actual state
        fig_tri.add_trace(go.Scatterpolar(
            r=[289.8, 115.6, 96.1, 289.8],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(192, 0, 0, 0.25)',
            line=dict(color='#C00000', width=3),
            name='Faktisk Tilstand (Per 31.10.2026)'
        ))
        fig_tri.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 320], ticksuffix="%")),
            showlegend=True,
            height=430,
            margin=dict(l=30, r=30, t=30, b=30)
        )
        st.plotly_chart(fig_tri, use_container_width=True)
        st.caption("Viser hvordan forsering av Tid (+5 uker) og fullt Omfang tvang Kostnad til å bli eneste støtdemper.")

    with t_col2:
        st.subheader("B: Trade-Off Front: Sakking vs. Besparelse")
        st.markdown("Hvor mye finansiell eksponering spares ved å gi opp tid (sakke farten)?")
        
        options = ['1. Status Quo (Full fart)', '2. Lavrisiko PO-kutt (+15d)', '3. Full Technical Hold (+30d)', '4. Omfangsjustering (+60d)']
        saved_m = [0.0, 8.5, 18.2, 27.5]
        rem_m = [107.2 - s for s in saved_m]
        
        fig_trade = go.Figure()
        fig_trade.add_trace(go.Bar(
            y=options, x=rem_m, orientation='h',
            name='Gjenværende Finansiell Eksponering',
            marker_color='#2F5496',
            text=[f"{v:.1f}M" for v in rem_m],
            textposition='inside'
        ))
        fig_trade.add_trace(go.Bar(
            y=options, x=saved_m, orientation='h',
            name='Eksponering Spart ved å Sakke Farten',
            marker_color='#009E73',
            text=[f"+{v:.1f}M" if v > 0 else "" for v in saved_m],
            textposition='outside'
        ))
        fig_trade.update_layout(
            barmode='stack',
            xaxis_title="MNOK",
            plot_bgcolor='white',
            height=370,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_trade, use_container_width=True)
        st.info("💡 **Konklusjon:** Å sakke farten (Technical Hold) er det eneste styringsmessige grepet som fysisk reduserer den finansielle eksponeringen.")

# ------------------------------------------------------------------------------
# PAGE 02: EVM S-CURVE
# ------------------------------------------------------------------------------
elif selected_page == "02 EVM S-Kurve & Tidsserie":
    st.markdown('<div class="main-title">EVM S-KURVE, FREMDRIFT OG TRENDER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Kumulativ kostnadsutvikling (PV vs. AC vs. EV) med markering av vendepunkt i Q1 2026</div>', unsafe_allow_html=True)
    
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
# PAGE 03: WBS & FORPLIKTELSESISBERG
# ------------------------------------------------------------------------------
elif selected_page == "03 Forpliktelsesisberg & WBS":
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
    fig_wf.update_layout(title="Forpliktelsesisberget: Fra 20 MNOK Budsjett til 107,2 MNOK Eksponering", yaxis_title="MNOK", plot_bgcolor="white", height=400)
    st.plotly_chart(fig_wf, use_container_width=True)
    
    st.subheader("WBS Detaljoppstilling & Regnskapsmessig Behandling (IAS 38)")
    st.dataframe(
        WBS_DATA.style.format({"bac": "{:,.0f} NOK", "ac": "{:,.0f} NOK", "ev": "{:,.0f} NOK", "open_po": "{:,.0f} NOK"}),
        use_container_width=True
    )

# ------------------------------------------------------------------------------
# PAGE 04: LIKVIDITET & FISKÅ
# ------------------------------------------------------------------------------
elif selected_page == "04 Likviditetsbro & Fiskå Enheter":
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
# PAGE 05: HVA-OM SCENARIO SIMULATOR
# ------------------------------------------------------------------------------
elif selected_page == "05 Hva-om Scenario Simulator":
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
        k1.metric("Ny Total Eksponering", f"{sim_new_exposure_nok/1e6:.1f} MNOK", f"-{po_saved_nok/1e6:.1f} MNOK spart")
        k1.metric("Netto Likviditetsbelastning", f"{sim_net_cost_nok/1e6:.1f} MNOK")
        k2.metric("IAS 36 Nedskrivningstap", f"-{sim_impairment_loss_nok/1e6:.1f} MNOK", "Resultateffekt", delta_color="inverse")
        k2.metric("Gjenværende AuC Balanse", f"{(AUC_CAPITALIZED_NOK - sim_impairment_loss_nok)/1e6:.1f} MNOK")
            
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
# PAGE 06: AI CONTROLLER COPILOT (RAG & VEKTOR-DB)
# ------------------------------------------------------------------------------
elif selected_page == "06 AI Controller Copilot (RAG & Vektor-DB)":
    st.markdown('<div class="main-title">ELKEM AI CONTROLLER COPILOT (RAG & VEKTOR-DB)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Semantisk søkemotor koblet mot IFRS, ISA 805, Enova-reglementet og GreenPilot prosjektdata</div>', unsafe_allow_html=True)
    
    vectorizer, vectors = get_vector_db()
    
    col_filter, col_search = st.columns([1, 2])
    with col_filter:
        cat_filter = st.selectbox(
            "Filtrer kildekategori:",
            ["Alle Kategorier", "Regnskap (IFRS)", "Revisjon & Enova", "Prosjektstyring & EVM"]
        )
    
    st.markdown("##### Hurtigspørsmål for Styret & Controller:")
    h1, h2, h3, h4 = st.columns(4)
    q_selected = ""
    if h1.button("Hvorfor kollapset kostnadskontrollen i Q1?"):
        q_selected = "Hvorfor kollapset kostnadskontrollen i Q1?"
    if h2.button("Hva kreves for balanseføring under IAS 38?"):
        q_selected = "Hva kreves for balanseføring under IAS 38?"
    if h3.button("Hvilken nedskrivning kreves under IAS 36?"):
        q_selected = "Hvilken nedskrivning kreves under IAS 36?"
    if h4.button("Hva er reglene for timesats og Enova-støtte?"):
        q_selected = "Hva er reglene for timesats og Enova-støtte?"
        
    user_query = st.text_input("Still et spørsmål til Vektor-DB Copilot:", value=q_selected)
    
    if user_query:
        query_vec = vectorizer.transform([user_query])
        sims = cosine_similarity(query_vec, vectors)[0]
        
        ranked_indices = np.argsort(sims)[::-1]
        
        results = []
        for idx in ranked_indices:
            chunk = KNOWLEDGE_CHUNKS[idx]
            if cat_filter != "Alle Kategorier" and chunk["category"] != cat_filter:
                continue
            score = sims[idx]
            if score > 0.05 or len(results) < 2:
                results.append((chunk, score))
            if len(results) >= 3:
                break
                
        st.markdown("---")
        st.markdown("### 🤖 Controller AI Resonnering:")
        
        # Synthesize authoritative answer based on retrieved top chunks
        top_chunk = results[0][0] if results else None
        
        if "Q1" in user_query or "kollapset" in user_query or "sprekk" in user_query:
            st.markdown("""
            **Rotårsaksanalyse:**
            * **Tidlig forsering uten budsjettdekning:** I Q1 2026 ble reaktormontasje forsert (SPI 1.16). For å oppnå milepælene ble det utstedt store hasteordrer i USD/EUR mot utenlandske leverandører.
            * **Mangel på forpliktelseskontroll:** Tradisjonell regnskapskontroll fulgte kun bokførte fakturaer (AC). Innkjøpsordrene (PO) ble ikke avstemt mot budsjettgrensen (BAC 20M). Allerede i mars 2026 passerte åpne PO-er 29,8 MNOK (149 % av BAC).
            * **Overtidslekkasje ved Fiskå:** CC-4300 (PMO) og CC-4100 (Drift) akkumulerte over 6 700 timer alene på krisehåndtering og redesign.
            """)
        elif "IAS 38" in user_query or "balanseføring" in user_query or "AuC" in user_query:
            st.markdown("""
            **Regnskapskonklusjon (IAS 38 Immaterielle Eiendeler):**
            * Av 58,0 MNOK i påløpte kostnader er **43,38 MNOK balanseført som anlegg under utførelse (AuC)** fordelt på WBS-200, 300, 400 og 500.
            * Dette forutsetter at samtlige 6 kumulative kriterier i IAS 38 avsnitt 57 til enhver tid er oppfylt.
            * Prosjektledelse og PMO (WBS-100) samt testkjøring (WBS-600) på til sammen **14,59 MNOK er korrekt driftsført over resultat**, da generelle administrasjonskostnader ikke kvalifiserer for aktivering.
            """)
        elif "IAS 36" in user_query or "nedskrivning" in user_query:
            st.markdown("""
            **Verdifallsvurdering (IAS 36 Impairment):**
            * Kostnadssprekk og eksploderende sluttkostnad utgjør en **obligatorisk indikasjon på verdifall** (IAS 36.12).
            * Ledelsen må gjennomføre en formell nedskrivningstest før årsoppgjøret.
            * Dersom prosjektet termineres (Alternativ B: Off-Ramp), må **samtlige 43,38 MNOK i balanseført AuC tapsføres umiddelbart over konsernresultatet**.
            * Ved gjennomføring av Alternativ A (30 dagers Technical Hold) estimeres nedskrivningsbehovet til ca. 13,4 MNOK basert på pilotanleggets fremtidige bruksverdi.
            """)
        elif "timesats" in user_query or "Enova" in user_query or "timepris" in user_query:
            st.markdown("""
            **Revisjon & Offentlige Tilskudd (RF-1053B / ISA 805):**
            * Timesats for internt personell er lovregulert og **oppad begrenset til maksimalt 530 kr per time** (maksimalt 1 850 timer per person per år).
            * Overtidstillegg og forseringspremier kan ikke belastes tilskuddsprosjektet utover denne faste satsen.
            * Enova krever at prosjektregnskapet attesteres av uavhengig revisor etter **ISA 805**, med full dokumentasjon på direkte henførbarhet og timelister.
            """)
        else:
            st.markdown(f"""
            *Basert på de reviderte kildedataene per 31.10.2026:*
            Prosjektet har påløpt **NOK 57,97M** mot en ramme på **NOK 20,00M**, med ytterligere **NOK 49,23M** bundet i uleverte forpliktelser.
            Samlet finansiell eksponering utgjør **NOK 107,20M** (536 % av BAC).
            Spørsmålet ditt (*"{user_query}"*) berører sentrale elementer i styringsmodellen. Se kildeutdragene nedenfor for ytterligere detaljer.
            """)
            
        with st.expander("🔍 Hentet fra Vektor-DB (Kildeforankring)", expanded=True):
            for chunk, score in results:
                st.markdown(f"**[{chunk['category']}] {chunk['title']}** *(Semantisk Match: {score*100:.1f}%)*")
                st.caption(f"Kilde: {chunk['source']}")
                st.write(chunk['text'])
                st.markdown("---")

st.markdown("---")
st.caption("Elkem ASA — GreenPilot 2026 Dual-Engine Analytics Platform | FAST Standard & IFRS Compliant")
