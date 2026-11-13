"""
ELKEM ASA — GREENPILOT 2026 CONTROLLER DASHBOARD & EVM PORTAL
Dual-Engine Architecture: Deterministic EVM + Agentic RAG Copilot
Full Visual Vocabulary Suite:
- 00 Executive Governance & Status
- 01 Avvik & Diverging Bars (Deviation)
- 02 Dynamisk Jerntriangel (Constraints & Trade-Offs)
- 03 Tidsplan & Governance Gantt (Schedule)
- 04 Korrelasjon: Bubble & Connected Scatter (Correlation)
- 05 Rangering & Leverandøreksponering (Ranking / Lollipop)
- 06 Fordeling & Revisjonsrisiko (Distribution / Box Plot & Histogram)
- 07 Del til Helhet & Balanse (Part-to-Whole / Treemap & 100% Stacked)
- 08 Kapital- & Forpliktelsesflyt (Flow / Sankey)
- 09 Usikkerhet & EAC Utfallsrom (Uncertainty / Fan Chart)
- 10 Forpliktelsesisberg & WBS (Waterfall)
- 11 Likviditetsbro & Fiskå Enheter (Cash & Timesheets @ 530 kr/t)
- 12 Hva-om Scenario Simulator (Interactive Sliders)
- 13 AI Controller Copilot (RAG & Vektor-DB)
"""

import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------------------------------------------------------------------
# 1. PAGE SETUP & THEME
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Elkem GreenPilot 2026 Controller Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Elkem Deep Blue #1F4E79, Slate #2F5496, Warning #C00000)
st.markdown("""
<style>
    .main-title { font-size: 26px; font-weight: 800; color: #1F4E79; margin-bottom: 2px; }
    .sub-title { font-size: 14px; color: #595959; margin-bottom: 15px; }
    .alert-card-red {
        background-color: #FDEDEC;
        border-left: 6px solid #C00000;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    .alert-card-green {
        background-color: #EAFAF1;
        border-left: 6px solid #009E73;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    .alert-card-blue {
        background-color: #EBF5FB;
        border-left: 6px solid #2F5496;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. DYNAMIC DATA LOADER (SINGLE SOURCE OF TRUTH)
# ------------------------------------------------------------------------------
# SSOT Baseline Financial EVM & Accounting Constants per 31.10.2026
BAC_NOK = 20_000_000.00
AC_NOK = 57_968_040.98
EV_NOK = 19_215_686.27
PV_YTD_NOK = 16_620_871.10
OPEN_PO_NOK = 49_233_751.55
AUC_CAPITALIZED_NOK = 43_375_028.38
PL_EXPENSE_NOK = 14_593_012.60

CURRENT_DIR = os.getcwd()
SEARCH_PATHS = [
    os.path.join(CURRENT_DIR, "processed", "star_schema"),
    os.path.join(CURRENT_DIR, "data", "cleaned"),
    os.path.join(CURRENT_DIR, "data", "raw"),
    os.path.join(CURRENT_DIR, "data"),
    os.path.join(CURRENT_DIR, "..", "data"),
    r"C:\Users\frank\OneDrive\Elkem\data",
    "/workspace/knowledge"
]

def find_file(fname):
    for sp in SEARCH_PATHS:
        p = os.path.join(sp, fname)
        if os.path.exists(p):
            return p
    return None

@st.cache_data(ttl=60)
def load_dynamic_data():
    # Fallback Baseline SSOT Data
    bac_val = BAC_NOK
    ac_val = AC_NOK
    ev_val = EV_NOK
    pv_val = PV_YTD_NOK
    open_po_val = OPEN_PO_NOK
    auc_val = AUC_CAPITALIZED_NOK
    
    # Try dynamic reading
    p_budget = find_file("05_erp_budget_baseline.csv")
    p_gl = find_file("10_erp_gl_actuals.csv")
    p_po = find_file("06_erp_purchase_orders.csv")
    
    if p_budget and p_gl:
        try:
            sep = ";" if ";" in open(p_budget).readline() else ","
            df_b = pd.read_csv(p_budget, sep=sep)
            bac_val = float(df_b["budget_amount_nok"].sum())
        except Exception:
            pass
        try:
            sep = ";" if ";" in open(p_gl).readline() else ","
            df_g = pd.read_csv(p_gl, sep=sep)
            ac_val = float(df_g["amount_nok"].sum())
            if "ias38_treatment" in df_g.columns:
                auc_val = float(df_g[df_g["ias38_treatment"] == "CAPITALIZE"]["amount_nok"].sum())
        except Exception:
            pass
    if p_po:
        try:
            sep = ";" if ";" in open(p_po).readline() else ","
            df_p = pd.read_csv(p_po, sep=sep)
            if "open_commitment_nok" in df_p.columns:
                open_po_val = float(df_p[df_p["po_status"] != "CANCELLED"]["open_commitment_nok"].sum())
        except Exception:
            pass

    return {
        "BAC": bac_val,
        "AC": ac_val,
        "EV": ev_val,
        "PV": pv_val,
        "OPEN_PO": open_po_val,
        "TOTAL_EXPOSURE": ac_val + open_po_val,
        "AUC": auc_val,
        "PL": ac_val - auc_val,
        "CPI": ev_val / ac_val if ac_val > 0 else 1.0,
        "SPI": ev_val / pv_val if pv_val > 0 else 1.0,
        "CV": ev_val - ac_val,
        "SV": ev_val - pv_val
    }

DATA = load_dynamic_data()

# WBS Dataset
WBS_DF = pd.DataFrame([
    {"wbs_id": "WBS-100", "name": "PMO & Prosjektledelse", "treatment": "Driftsført FoU (P&L)", "bac": 2_500_000, "ac": 7_248_010.50, "ev": 2_401_960.78, "open_po": 4_120_000, "pv": 2_150_000},
    {"wbs_id": "WBS-200", "name": "Prosessdesign & Basic Eng.", "treatment": "Balanseført AuC", "bac": 3_500_000, "ac": 10_147_215.17, "ev": 3_362_745.10, "open_po": 6_850_000, "pv": 2_950_000},
    {"wbs_id": "WBS-300", "name": "Pilotanlegg & Reaktor", "treatment": "Balanseført AuC", "bac": 8_000_000, "ac": 23_193_616.39, "ev": 7_686_274.51, "open_po": 28_450_000, "pv": 6_550_000},
    {"wbs_id": "WBS-400", "name": "Infrastruktur & Gass", "treatment": "Balanseført AuC", "bac": 3_000_000, "ac": 8_697_606.15, "ev": 2_882_352.94, "open_po": 5_213_751, "pv": 2_620_000},
    {"wbs_id": "WBS-500", "name": "Installasjon & Elektro", "treatment": "Balanseført AuC", "bac": 2_000_000, "ac": 5_796_804.10, "ev": 1_921_568.63, "open_po": 3_600_000, "pv": 1_550_000},
    {"wbs_id": "WBS-600", "name": "Testkjøring & Overlevering", "treatment": "Driftsført FoU (P&L)", "bac": 1_000_000, "ac": 2_884_788.67, "ev": 960_784.31, "open_po": 1_000_000, "pv": 800_871.10},
])
WBS_DF["cpi"] = WBS_DF["ev"] / WBS_DF["ac"]
WBS_DF["spi"] = WBS_DF["ev"] / WBS_DF["pv"]
WBS_DF["cv"] = WBS_DF["ev"] - WBS_DF["ac"]
WBS_DF["sv"] = WBS_DF["ev"] - WBS_DF["pv"]
WBS_DF["total_exposure"] = WBS_DF["ac"] + WBS_DF["open_po"]

# Timeline Data (Jan - Okt 2026)
TIMELINE_DF = pd.DataFrame([
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
TIMELINE_DF["cum_pv"] = TIMELINE_DF["pv"].cumsum()
TIMELINE_DF["cum_ac"] = TIMELINE_DF["ac"].cumsum()
TIMELINE_DF["cum_ev"] = TIMELINE_DF["ev"].cumsum()
TIMELINE_DF["cum_cpi"] = TIMELINE_DF["cum_ev"] / TIMELINE_DF["cum_ac"]
TIMELINE_DF["cum_spi"] = TIMELINE_DF["cum_ev"] / TIMELINE_DF["cum_pv"]

# Vendor Top 8 Data
VENDOR_DF = pd.DataFrame([
    {"vendor_id": "V006", "name": "Synthetic Vendor 06 (DE)", "po": 7.22, "ac": 2.86, "open_po": 4.36, "priority": "Kritisk"},
    {"vendor_id": "V020", "name": "Synthetic Vendor 20 (NO)", "po": 7.38, "ac": 3.22, "open_po": 4.16, "priority": "Kritisk"},
    {"vendor_id": "V007", "name": "Synthetic Vendor 07 (US)", "po": 8.60, "ac": 4.82, "open_po": 3.78, "priority": "Kritisk"},
    {"vendor_id": "V016", "name": "Synthetic Vendor 16 (NO)", "po": 5.02, "ac": 1.54, "open_po": 3.48, "priority": "Høy"},
    {"vendor_id": "V002", "name": "Synthetic Vendor 02 (DE)", "po": 6.45, "ac": 3.17, "open_po": 3.28, "priority": "Høy"},
    {"vendor_id": "V017", "name": "Synthetic Vendor 17 (SE)", "po": 5.06, "ac": 2.10, "open_po": 2.96, "priority": "Medium"},
    {"vendor_id": "V003", "name": "Synthetic Vendor 03 (US)", "po": 5.86, "ac": 2.98, "open_po": 2.88, "priority": "Medium"},
    {"vendor_id": "V010", "name": "Synthetic Vendor 10 (DE)", "po": 5.83, "ac": 3.69, "open_po": 2.14, "priority": "Medium"},
])

# ------------------------------------------------------------------------------
# 3. KNOWLEDGE BASE & RAG COPILOT CORPUS
# ------------------------------------------------------------------------------
KNOWLEDGE_CHUNKS = [
    {
        "id": "IAS38-01",
        "category": "Regnskap (IFRS)",
        "source": "IAS 38 Immaterielle Eiendeler & Factsheet",
        "title": "IAS 38: Skille mellom Forskningsfase og Utviklingsfase",
        "text": "Kostnader i forskningsfasen skal alltid kostnadsføres løpende over resultatregnskapet (P&L). Utviklingskostnader kan kun balanseføres som anlegg under utførelse (AuC) dersom samtlige seks kriterier i IAS 38.57 er oppfylt: teknisk gjennomførbarhet, intensjon om fullføring, evne til bruk/salg, påvisbare fremtidige økonomiske fordeler, tilgjengelige ressurser og pålitelig måling av utgifter."
    },
    {
        "id": "IAS36-01",
        "category": "Regnskap (IFRS)",
        "source": "IAS 36 Impairment of Assets Guide",
        "title": "IAS 36: Nedskrivningstest for Anlegg under Utførelse (AuC)",
        "text": "Eiendeler under tilvirkning som ennå ikke er klare til bruk skal testes for verdifall minst årlig, eller umiddelbart ved indikasjon på verdifall (IAS 36.12f). En budsjettsprekk på over 100 % (EAC vesentlig over opprinnelig ramme) er en lovpålagt trigger. Ved terminering (Off-Ramp) må gjenvinnbart beløp fastsettes til netto salgsverdi (ofte lik skrapverdi), og balanseført AuC tapsføres umiddelbart i driftsresultatet."
    },
    {
        "id": "ISA805-01",
        "category": "Revisjon & Tilskudd",
        "source": "Retningslinjer for Timesatser 2025 & ISA 805",
        "title": "ISA 805 & Enova: Revisjon av Prosjektregnskap og Timesats 530 kr",
        "text": "Under Enovas regelverk og SkatteFUNN (RF-1053B) er personalkostnader strengt regulert til en fast timesats på 530 kr per time, med et tak på maksimalt 1 850 timer per år per person. Revisor skal etter ISA 805 avgi en særskilt attestasjon på at timelister er direkte knyttet til prosjektets WBS og aktiviteter. Overtidstillegg utover 530 kr/t kan ikke belastes prosjektet."
    },
    {
        "id": "HOLD-01",
        "category": "Styringstiltak",
        "source": "GreenPilot 2026 Board Memo",
        "title": "30 Dagers Technical Hold: Den Strategiske Løsningen",
        "text": "Ved å innføre et 30 dagers Technical Hold ved Gate 3 pauses montasjen. Dette gir kontrollteamet tid til å gjennomføre en kanselleringsaudit på de 49,2 MNOK i åpne innkjøpsordrer (estimert besparelse: 18,2 MNOK) og stanse overtidslekkasje ved Fiskå, mot en kontrollert 4–6 ukers utsettelse av ferdigstillelse."
    }
]

@st.cache_resource
def get_vector_db():
    corpus = [c["title"] + " " + c["text"] + " " + c["category"] for c in KNOWLEDGE_CHUNKS]
    vec = TfidfVectorizer(ngram_range=(1, 2))
    mat = vec.fit_transform(corpus)
    return vec, mat

# ------------------------------------------------------------------------------
# 4. SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚡ ELKEM ASA")
    st.markdown("### GreenPilot 2026 Controller Portal")
    st.caption("Dual-Engine: Deterministisk EVM + Agentic AI")
    
    pages = [
        "00 Executive Governance & Status",
        "01 Avvik & Diverging Bars (Deviation)",
        "02 Dynamisk Jerntriangel (Trade-Offs)",
        "03 Tidsplan & Governance Gantt (Schedule)",
        "04 Korrelasjon: Bubble & Connected (Correlation)",
        "05 Rangering & Leverandører (Ranking)",
        "06 Fordeling & Revisjonsrisiko (Distribution)",
        "07 Del til Helhet & Balanse (Part-to-Whole)",
        "08 Kapital- & Forpliktelsesflyt (Flow / Sankey)",
        "09 Usikkerhet & EAC Vifte (Uncertainty)",
        "10 Forpliktelsesisberg & WBS (Waterfall)",
        "11 Likviditetsbro & Fiskå Enheter (Cash)",
        "12 Hva-om Scenario Simulator",
        "13 AI Controller Copilot (RAG)"
    ]
    selected_page = st.radio("Navigasjon", pages)
    
    st.markdown("---")
    st.markdown("**Prosjektstatus:** 🔴 RØD ALARM")
    st.markdown(f"**Total Eksponering:** {DATA['TOTAL_EXPOSURE']/1e6:.1f} MNOK")
    st.markdown(f"**Budsjettramme (BAC):** {DATA['BAC']/1e6:.1f} MNOK")
    st.markdown(f"**CPI:** {DATA['CPI']:.2f} | **SPI:** {DATA['SPI']:.2f}")

# ------------------------------------------------------------------------------
# PAGE 00: EXECUTIVE GOVERNANCE & STATUS
# ------------------------------------------------------------------------------
if selected_page == "00 Executive Governance & Status":
    st.markdown('<div class="main-title">ELKEM GREENPILOT 2026 — STYRETS BESLUTNINGSNOTAT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Single Source of Truth Modell | Enova Pilotprosjekt | Data Cut-off: 31.10.2026</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="alert-card-red">
        <h4>🔴 KRITISK STYRINGSSVIKT & LIKVIDITETSEKSPONERING (Per 31.10.2026)</h4>
        <p><strong>1. DIAGNOSE (EVM):</strong> Prosjektet opererer med kostnadseffektivitet <strong>CPI {DATA['CPI']:.2f}</strong> og et akkumulert kostnadsavvik på <strong>NOK {DATA['CV']/1e6:.1f}M</strong>. Fremdriften meldes likevel til <strong>SPI {DATA['SPI']:.2f}</strong> (+5 uker foran plan) grunnet aggressiv forsering.</p>
        <p><strong>2. FORPLIKTELSER & EKSPONERING:</strong> Bokførte kostnader (NOK {DATA['AC']/1e6:.1f}M) og uleverte innkjøpsordrer (NOK {DATA['OPEN_PO']/1e6:.1f}M) gir en samlet eksponering på <strong>NOK {DATA['TOTAL_EXPOSURE']/1e6:.1f}M ({DATA['TOTAL_EXPOSURE']/DATA['BAC']*100:.0f}% av budsjett)</strong>.</p>
        <p><strong>3. IFRS BALANSERISIKO:</strong> Av dette er <strong>NOK {DATA['AUC']/1e6:.1f}M</strong> balanseført som anlegg under utførelse (AuC) etter IAS 38. Dette utløser obligatorisk krav om nedskrivningstest etter IAS 36 før årsoppgjøret.</p>
        <p><strong>4. ANBEFALT STYREVEDTAK:</strong> Vedta umiddelbar <strong>30 dagers Technical Hold & Innkjøpsfrys</strong> for å kansellere uleverte PO-er (sparer 18,2 MNOK) og forskyve ferdigstillelse til januar 2027.</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Budsjett (BAC)", f"{DATA['BAC']/1e6:.1f} MNOK", "Vedtatt ramme", delta_color="off")
    c2.metric("Påløpt Kostnad (AC)", f"{DATA['AC']/1e6:.1f} MNOK", f"+{(DATA['AC']/DATA['BAC']-1)*100:.0f}% over BAC", delta_color="inverse")
    c3.metric("Opptjent Verdi (EV)", f"{DATA['EV']/1e6:.1f} MNOK", f"SPI {DATA['SPI']:.2f} (Forsert)")
    c4.metric("Åpne PO-er", f"{DATA['OPEN_PO']/1e6:.1f} MNOK", "Ufakturert binding")
    c5.metric("Total Eksponering", f"{DATA['TOTAL_EXPOSURE']/1e6:.1f} MNOK", f"{DATA['TOTAL_EXPOSURE']/DATA['BAC']*100:.0f}% av BAC", delta_color="inverse")
    
    st.markdown("---")
    col_l, col_r = st.columns([1.2, 1])
    with col_l:
        st.subheader("Styringsgap: Eksponering vs. Budsjett")
        fig = go.Figure([go.Bar(
            x=["Budsjett (BAC)", "Opptjent (EV)", "Påløpt (AC)", "Total Eksponering"],
            y=[DATA["BAC"]/1e6, DATA["EV"]/1e6, DATA["AC"]/1e6, DATA["TOTAL_EXPOSURE"]/1e6],
            text=[f"{DATA['BAC']/1e6:.1f}M", f"{DATA['EV']/1e6:.1f}M", f"{DATA['AC']/1e6:.1f}M", f"{DATA['TOTAL_EXPOSURE']/1e6:.1f}M"],
            textposition="outside",
            marker_color=["#595959", "#2F5496", "#C00000", "#800000"]
        )])
        fig.update_layout(yaxis_title="MNOK", plot_bgcolor="white", height=320, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        st.subheader("Styrets Beslutningsalternativer")
        st.markdown("""
        * **Alternativ A: 30 Dagers Technical Hold (Anbefalt)**
          * Full innkjøpsfrys og kanselleringsaudit av uleverte PO-er (sparer **18,2 MNOK**).
          * Capper samlet eksponering på **89,0 MNOK** mot 4–6 ukers tidsforskyvning.
        * **Alternativ B: Formell Prosjektstans (Off-Ramp)**
          * Terminere prosjektet ved Stage-Gate 3.
          * Umiddelbar tapsføring av **43,4 MNOK** i balanseført AuC rett i konsernresultatet etter IAS 36.
          * Tilbakebetalingsrisiko for 3,0 MNOK i utbetalt Enova-tilskudd.
        """)

# ------------------------------------------------------------------------------
# PAGE 01: AVVIK & DIVERGING BARS (DEVIATION)
# ------------------------------------------------------------------------------
elif selected_page == "01 Avvik & Diverging Bars (Deviation)":
    st.title("01 Avviksanalyse: Diverging Bars (Visual Vocabulary: Deviation)")
    st.markdown("""
    Visual Vocabulary definerer **Diverging Bar Charts** som den overlegne metoden for å vise variasjoner (+/-) 
    rundt et fast referansepunkt (0-linjen). Her ser vi GreenPilot-paradokset:
    * **Kostnadsavvik (CV = EV - AC):** Dyp kollaps mot venstre (rødt) pga. ekstreme overskridelser.
    * **Tidsplanavvik (SV = EV - PV):** Positiv fremdrift mot høyre (grønt) pga. forsering.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("A: Kostnadsavvik per WBS (CV = EV - AC)")
        fig_cv = go.Figure([go.Bar(
            y=WBS_DF["wbs_id"] + " " + WBS_DF["name"].str.slice(0, 15),
            x=WBS_DF["cv"]/1e6,
            orientation='h',
            marker_color="#C00000",
            text=[f"{v/1e6:.2f}M" for v in WBS_DF["cv"]],
            textposition="inside"
        )])
        fig_cv.update_layout(xaxis_title="MNOK (Negativt = Budsjettsprekk)", plot_bgcolor="white", height=320, margin=dict(l=10, r=20, t=20, b=20))
        st.plotly_chart(fig_cv, use_container_width=True)
    with col2:
        st.subheader("B: Tidsplanavvik per WBS (SV = EV - PV)")
        fig_sv = go.Figure([go.Bar(
            y=WBS_DF["wbs_id"] + " " + WBS_DF["name"].str.slice(0, 15),
            x=WBS_DF["sv"]/1e6,
            orientation='h',
            marker_color="#009E73",
            text=[f"+{v/1e6:.2f}M" for v in WBS_DF["sv"]],
            textposition="inside"
        )])
        fig_sv.update_layout(xaxis_title="MNOK (Positivt = Foran Plan)", plot_bgcolor="white", height=320, margin=dict(l=10, r=20, t=20, b=20))
        st.plotly_chart(fig_sv, use_container_width=True)
        
    st.dataframe(WBS_DF[["wbs_id", "name", "bac", "ac", "ev", "cv", "sv", "cpi", "spi"]], use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 02: DYNAMISK JERNTRIANGEL (TRADE-OFFS)
# ------------------------------------------------------------------------------
elif selected_page == "02 Dynamisk Jerntriangel (Trade-Offs)":
    st.title("02 Jerntriangel: Avveininger & Rebalanseringsvektor")
    st.markdown("""
    I stedet for å fokusere på størrelser, visualiserer dette diagrammet de **strukturelle spenningene og avveiningene** 
    mellom prosjektets tre klassiske skranker.
    """)
    
    col1, col2 = st.columns([1.1, 1])
    with col1:
        st.subheader("A: Jerntriangelet med Sanntids Operasjonspunkt")
        cats = ['KOST (107,2M Exp)', 'TID (SPI 1,16 / +5u)', 'OMFANG (96% EV / 43,4M AuC)']
        fig_tri = go.Figure()
        fig_tri.add_trace(go.Scatterpolar(
            r=[100, 100, 100, 100],
            theta=cats + [cats[0]],
            fill='toself',
            fillcolor='rgba(180, 180, 180, 0.15)',
            line=dict(color='#888888', dash='dash', width=2),
            name='Baseline Plan (100% Balansert)'
        ))
        cost_ratio = (DATA["AC"] / DATA["BAC"]) * 100
        time_ratio = DATA["SPI"] * 100
        scope_ratio = (DATA["EV"] / DATA["BAC"]) * 100
        fig_tri.add_trace(go.Scatterpolar(
            r=[cost_ratio, time_ratio, scope_ratio, cost_ratio],
            theta=cats + [cats[0]],
            fill='toself',
            fillcolor='rgba(192, 0, 0, 0.25)',
            line=dict(color='#C00000', width=3),
            name='Faktisk Tilstand (Fast-Tracked)'
        ))
        fig_tri.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 320], ticksuffix='%')),
            legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.15),
            height=380, margin=dict(l=30, r=30, t=20, b=40)
        )
        st.plotly_chart(fig_tri, use_container_width=True)
    with col2:
        st.subheader("B: Beslutningsfront ved Oppbremsing (Slow Down)")
        opts = ['1. Status Quo (Full Fart)', '2. Lavrisiko PO-kutt (+15d)', '3. Technical Hold (+30d)', '4. Omfangsreduksjon (+60d)']
        rem = [107.2, 98.7, 89.0, 79.7]
        sav = [0.0, 8.5, 18.2, 27.5]
        fig_front = go.Figure([
            go.Bar(y=opts, x=rem, orientation='h', name='Gjenværende Eksponering (MNOK)', marker_color='#2F5496', text=[f"{v:.1f}M" for v in rem], textposition='inside'),
            go.Bar(y=opts, x=sav, orientation='h', name='Spart Likviditet ved Hold', marker_color='#009E73', text=[f"+{v:.1f}M" if v>0 else "" for v in sav], textposition='outside')
        ])
        fig_front.update_layout(barmode='stack', plot_bgcolor='white', height=380, legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.15), margin=dict(l=20, r=20, t=20, b=40))
        st.plotly_chart(fig_front, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 03: TIDSPLAN & GOVERNANCE GANTT (SCHEDULE)
# ------------------------------------------------------------------------------
elif selected_page == "03 Tidsplan & Governance Gantt (Schedule)":
    st.title("03 Tidsplan & Governance Gantt (Stage-Gates & 30d Hold)")
    st.markdown("""
    Gantt-diagrammet over de 6 WBS-pakkene (aggregert fra 102 Primavera-aktiviteter) 
    synliggjør hvordan en kontrollert oppbremsing i november (30 dagers Technical Hold) forskyver Gate 4 til januar 2027.
    """)
    
    gantt_df = pd.DataFrame([
        {"Task": "WBS-100 PMO & Ledelse", "Start": "2026-01-05", "Finish": "2026-11-03", "Status": "Fullført"},
        {"Task": "WBS-200 Prosessdesign", "Start": "2026-01-08", "Finish": "2026-11-14", "Status": "Fullført"},
        {"Task": "WBS-300 Reaktor & Pilot", "Start": "2026-01-11", "Finish": "2026-11-17", "Status": "Kritisk (51,6M Exp)"},
        {"Task": "WBS-400 Infrastruktur", "Start": "2026-01-14", "Finish": "2026-11-06", "Status": "Fullført"},
        {"Task": "WBS-500 Elektro & Montasje", "Start": "2026-01-17", "Finish": "2026-11-23", "Status": "Venter på Gate 3"},
        {"Task": "WBS-600 Test & Overlevering", "Start": "2026-01-20", "Finish": "2026-11-11", "Status": "Venter på Gate 3"},
        {"Task": "ANBEFALT: 30d Technical Hold", "Start": "2026-11-01", "Finish": "2026-11-30", "Status": "Innkjøpsfrys (Sparer 18,2M)"},
    ])
    fig_gantt = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Task", color="Status",
                            color_discrete_map={"Fullført": "#2F5496", "Kritisk (51,6M Exp)": "#C00000", "Venter på Gate 3": "#E69F00", "Innkjøpsfrys (Sparer 18,2M)": "#009E73"})
    fig_gantt.update_yaxes(autorange="reversed")
    fig_gantt.add_vline(x="2026-10-31", line_width=2, line_dash="dash", line_color="#C00000")
    fig_gantt.add_annotation(
        x="2026-10-31", y=1, yref="paper",
        text="Status per i dag (31.10.2026)",
        showarrow=False, xanchor="left", yanchor="top",
        font=dict(color="#C00000", size=11)
    )
    fig_gantt.update_layout(plot_bgcolor="white", height=380, margin=dict(l=20, r=20, t=30, b=30))
    st.plotly_chart(fig_gantt, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 04: KORRELASJON: BUBBLE & CONNECTED SCATTER (CORRELATION)
# ------------------------------------------------------------------------------
elif selected_page == "04 Korrelasjon: Bubble & Connected (Correlation)":
    st.title("04 Korrelasjon: Fast-Track Fellen & Dødsspiralen")
    st.markdown("""
    Visual Vocabulary: **Correlation**. Viser samspillet mellom forsering (SPI), kostnadskollaps (CPI) og kontraktseksponering.
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("A: WBS Boblediagram (Eksponering)")
        fig_bub = go.Figure()
        for idx, row in WBS_DF.iterrows():
            col = "#C00000" if "AuC" in row["treatment"] else "#2F5496"
            fig_bub.add_trace(go.Scatter(
                x=[row["spi"]], y=[row["cpi"]],
                mode='markers+text',
                marker=dict(size=row["total_exposure"]/1.5e6 + 12, color=col, opacity=0.75, line=dict(width=1.5, color='black')),
                text=[f"{row['wbs_id']}<br>{row['total_exposure']/1e6:.1f}M"],
                textposition="top center",
                name=row["wbs_id"]
            ))
        fig_bub.update_layout(xaxis_title="Fremdriftsindeks (SPI)", yaxis_title="Kostnadsindeks (CPI)", plot_bgcolor="white", height=360, showlegend=False)
        st.plotly_chart(fig_bub, use_container_width=True)
    with col2:
        st.subheader("B: Månedlig Connected Trajectory (Jan-Okt)")
        fig_conn = go.Figure([go.Scatter(
            x=TIMELINE_DF["cum_spi"], y=TIMELINE_DF["cum_cpi"],
            mode='lines+markers+text',
            line=dict(color='#C00000', width=2.5),
            marker=dict(size=8, color='#2F5496'),
            text=[p.split("-")[1] for p in TIMELINE_DF["period"]],
            textposition="top right"
        )])
        fig_conn.update_layout(xaxis_title="Akkumulert SPI", yaxis_title="Akkumulert CPI", plot_bgcolor="white", height=360)
        st.plotly_chart(fig_conn, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 05: RANGERING & LEVERANDØRER (RANKING)
# ------------------------------------------------------------------------------
elif selected_page == "05 Rangering & Leverandører (Ranking)":
    st.title("05 Rangering & Forhandlingsliste (Visual Vocabulary: Ranking)")
    st.markdown("Horisontal **Lollipop & Bar-ordered** rangering av leverandøreksponering og uleverte PO-kutt.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("A: Topp 8 Leverandører etter Åpen PO (Kanselleringsmål)")
        fig_v = go.Figure([go.Bar(
            y=VENDOR_DF["name"], x=VENDOR_DF["open_po"], orientation='h',
            marker_color=["#C00000" if p=="Kritisk" else "#E69F00" for p in VENDOR_DF["priority"]],
            text=[f"{v:.2f} MNOK" for v in VENDOR_DF["open_po"]],
            textposition="inside"
        )])
        fig_v.update_layout(xaxis_title="Åpen Ulevert PO (MNOK)", plot_bgcolor="white", height=350)
        st.plotly_chart(fig_v, use_container_width=True)
    with col2:
        st.subheader("B: Forhandlingsmandat for 30d Technical Hold")
        st.markdown("""
        * **Mål 1 (V006 - Tyskland):** 4,36 MNOK åpen PO på reaktorkomponenter. Krever umiddelbar produksjonsstans.
        * **Mål 2 (V020 - Norge):** 4,16 MNOK åpen PO på elektro. Utsettelse av leveranse til januar 2027.
        * **Mål 3 (V007 - USA):** 3,78 MNOK i USD. Sikring mot ytterligere kronesvekkelse.
        * **Samlet besparelse ved topp 3:** **12,30 MNOK** (25% av hele forpliktelsesisberget).
        """)

# ------------------------------------------------------------------------------
# PAGE 06: FORDELING & REVISJONSRISIKO (DISTRIBUTION)
# ------------------------------------------------------------------------------
elif selected_page == "06 Fordeling & Revisjonsrisiko (Distribution)":
    st.title("06 Fordeling & Revisjonsrisiko (Visual Vocabulary: Distribution)")
    st.markdown("Statistisk spredning i timeregistreringer (ISA 805 tak på 530 kr/t) og bimodal fordeling i PO-størrelser.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("A: Ukentlig Timefordeling per Koststed (1 537 Linjer)")
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(y=[8, 8, 8, 7.5, 8, 12, 14, 16], name="CC-4100 Verksted", marker_color="#E69F00"))
        fig_box.add_trace(go.Box(y=[7.5, 7.5, 8, 8, 7.5, 7.5, 10, 11], name="CC-4200 Lab", marker_color="#2F5496"))
        fig_box.add_trace(go.Box(y=[8, 8, 8.5, 8, 12, 14, 15, 16], name="CC-4300 PMO", marker_color="#C00000"))
        fig_box.add_hline(y=12.0, line_dash="dash", line_color="#C00000", annotation_text="Overtidsterskel")
        fig_box.update_layout(yaxis_title="Timer / Uke", plot_bgcolor="white", height=350)
        st.plotly_chart(fig_box, use_container_width=True)
    with col2:
        st.subheader("B: Bimodal Innkjøpsstørrelse (150 PO-er)")
        fig_hist = go.Figure([go.Histogram(
            x=[0.1]*50 + [1.2]*35 + [1.6]*35 + [1.9]*30,
            nbinsx=15, marker_color="#2F5496"
        )])
        fig_hist.update_layout(xaxis_title="PO Beløp (MNOK)", yaxis_title="Antall Ordrer", plot_bgcolor="white", height=350)
        st.plotly_chart(fig_hist, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 07: DEL TIL HELHET & BALANSE (PART-TO-WHOLE)
# ------------------------------------------------------------------------------
elif selected_page == "07 Del til Helhet & Balanse (Part-to-Whole)":
    st.title("07 Del til Helhet & IFRS Balanse (Visual Vocabulary: Part-to-Whole)")
    st.markdown("Hierarkisk **Treemap** over samlet eksponering og **100% Proportional Stacked Bars** for AuC balanseforskyvning.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("A: Treemap over Total Eksponering (107,2 MNOK)")
        fig_tree = go.Figure(go.Treemap(
            labels=WBS_DF["wbs_id"] + "<br>" + WBS_DF["name"].str.slice(0, 14),
            parents=["GreenPilot 2026"] * len(WBS_DF),
            values=WBS_DF["total_exposure"],
            textinfo="label+value+percent parent",
            marker=dict(colors=["#C00000" if "AuC" in t else "#2F5496" for t in WBS_DF["treatment"]])
        ))
        fig_tree.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=360)
        st.plotly_chart(fig_tree, use_container_width=True)
    with col2:
        st.subheader("B: 100% Stacked Bar (AuC vs. P&L Forskyvning)")
        fig_stk = go.Figure([
            go.Bar(name='Balanseført AuC (IAS 38)', x=['BAC (20M)', 'AC (58M)', 'Eksponering (107M)'], y=[70.0, 74.8, 85.8], marker_color='#2F5496', text=['70.0%', '74.8% (43.4M)', '85.8% (91.9M)'], textposition='inside'),
            go.Bar(name='Resultatført FoU (P&L)', x=['BAC (20M)', 'AC (58M)', 'Eksponering (107M)'], y=[30.0, 25.2, 14.2], marker_color='#595959', text=['30.0%', '25.2%', '14.2%'], textposition='inside')
        ])
        fig_stk.update_layout(barmode='stack', yaxis=dict(ticksuffix='%', range=[0, 100]), plot_bgcolor='white', height=360, legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig_stk, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 08: KAPITAL- & FORPLIKTELSESFLYT (FLOW / SANKEY)
# ------------------------------------------------------------------------------
elif selected_page == "08 Kapital- & Forpliktelsesflyt (Flow / Sankey)":
    st.title("08 Kapital- & Forpliktelsesflyt (Visual Vocabulary: Flow)")
    st.markdown("Sankey-diagram som sporer kapitalen fra arbeidspakker gjennom ERP-systemet til balanseført AuC og kansellerbare ordrer.")
    
    labels = [
        "WBS-100 PMO (11.4M)", "WBS-200 Prosess (17.0M)", "WBS-300 Reaktor (51.6M)",
        "WBS-400 Infra (13.9M)", "WBS-500 Elektro (9.4M)", "WBS-600 Test (3.9M)",
        "Bokført AC (58.0M)", "Åpne PO-er (49.2M)",
        "Balanseført AuC (43.4M)", "Resultatført FoU (14.6M)",
        "Kansellerbar PO (18.2M)", "Låst PO (31.0M)"
    ]
    sources = [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5, 6, 6, 7, 7]
    targets = [6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 8, 9, 10, 11]
    values =  [7.25, 10.15, 23.19, 8.70, 5.80, 2.88, 4.12, 6.85, 28.45, 5.21, 3.60, 1.00, 43.38, 14.59, 18.20, 31.03]
    node_colors = ["#2F5496"]*6 + ["#C00000", "#E69F00"] + ["#C00000", "#595959", "#009E73", "#800000"]
    
    fig_sankey = go.Figure(go.Sankey(
        node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels, color=node_colors),
        link=dict(source=sources, target=targets, value=values, color="rgba(200, 200, 200, 0.45)")
    ))
    fig_sankey.update_layout(height=480, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_sankey, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 09: USIKKERHET & EAC UTFALLSROM (UNCERTAINTY / FAN CHART)
# ------------------------------------------------------------------------------
elif selected_page == "09 Usikkerhet & EAC Vifte (Uncertainty)":
    st.title("09 Usikkerhet & EAC Utfallsrom (Visual Vocabulary: Uncertainty)")
    st.markdown("""
    I henhold til Visual Vocabulary representerer et **Fan Chart (Konfidensvifte)** den fremste måten å formidle 
    fremtidig usikkerhet til et styre. I stedet for et statisk punkt-estimat, viser viften konsekvensen av styrets valg ved Gate 3:
    * **P10 (Beste utfall - 30d Technical Hold):** Sluttkostnad begrenses til **89,0 MNOK**.
    * **P50 (Forventet kurs / Status Quo):** Sluttkostnad lander på **107,2 MNOK**.
    * **P90 (Ukontrollert eskalering / Forsering):** Sluttkostnad eskalerer til **132,5 MNOK**.
    """)
    
    months_all = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des', 'Jan 27', 'Feb 27']
    ac_hist = [4.65, 7.03, 10.44, 15.34, 21.46, 29.35, 35.80, 42.78, 50.43, 57.97]
    pv_hist = [1.53, 3.34, 4.79, 6.42, 8.21, 10.13, 11.78, 13.30, 15.01, 16.62]
    
    x_proj = ['Okt', 'Nov', 'Des', 'Jan 27', 'Feb 27']
    p90 = [57.97, 75.0, 94.0, 114.0, 132.5]
    p50 = [57.97, 66.0, 78.5, 93.0, 107.2]
    p10 = [57.97, 60.5, 68.0, 78.0, 89.0]
    
    fig_fan = go.Figure()
    # Shaded band
    fig_fan.add_trace(go.Scatter(x=x_proj + x_proj[::-1], y=p90 + p10[::-1], fill='toself', fillcolor='rgba(192, 0, 0, 0.18)', line=dict(color='rgba(255,255,255,0)'), name='P10 - P90 Utfallsrom'))
    # Trajectories
    fig_fan.add_trace(go.Scatter(x=x_proj, y=p90, line=dict(color='#800000', dash='dot', width=2), name='P90: Ukontrollert Eskalering (132,5M)'))
    fig_fan.add_trace(go.Scatter(x=x_proj, y=p50, line=dict(color='#C00000', dash='dash', width=2.5), name='P50: Status Quo (107,2M)'))
    fig_fan.add_trace(go.Scatter(x=x_proj, y=p10, line=dict(color='#009E73', width=3), name='P10: 30d Technical Hold (89,0M)'))
    # Actuals
    fig_fan.add_trace(go.Scatter(x=months_all[:10], y=ac_hist, mode='lines+markers', line=dict(color='#2F5496', width=3), name='Historisk Påløpt AC'))
    fig_fan.add_trace(go.Scatter(x=months_all[:10], y=pv_hist, line=dict(color='#888888', dash='dash'), name='Planlagt Baseline (PV)'))
    
    fig_fan.add_hline(y=20.0, line_dash="dash", line_color="#555555", annotation_text="BAC Budsjett: 20,0 MNOK")
    fig_fan.add_vline(x="Okt", line_color="#C00000", line_width=2, line_dash="dash")
    fig_fan.add_annotation(
        x="Okt", y=1, yref="paper",
        text="Gate 3 Cut-off (31.10)",
        showarrow=False, xanchor="left", yanchor="top",
        font=dict(color="#C00000", size=10)
    )
    fig_fan.update_layout(yaxis_title="MNOK", plot_bgcolor="white", height=440, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_fan, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 10: FORPLIKTELSESISBERG & WBS (WATERFALL)
# ------------------------------------------------------------------------------
elif selected_page == "10 Forpliktelsesisberg & WBS (Waterfall)":
    st.title("10 Forpliktelsesisberg & WBS Kostnadsbro")
    st.markdown("Fossefallsanalyse som forklarer hvordan prosjektet beveget seg fra 20,0 MNOK til 107,2 MNOK.")
    
    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "relative", "total", "relative", "total"],
        x=["Vedtatt BAC", "WBS-100 PMO", "WBS-200 Prosess", "WBS-300 Reaktor", "WBS-400 Infra", "WBS-500/600", "Bokført AC", "Uleverte PO", "Total Eksponering"],
        y=[20.0, 4.75, 6.65, 15.19, 5.70, 5.68, 57.97, 49.23, 107.20],
        connector={"line": {"color": "#888888"}},
        decreasing={"marker": {"color": "#009E73"}},
        increasing={"marker": {"color": "#C00000"}},
        totals={"marker": {"color": "#1F4E79"}},
        text=[f"{v:.1f}M" for v in [20.0, 4.75, 6.65, 15.19, 5.70, 5.68, 57.97, 49.23, 107.20]],
        textposition="outside"
    ))
    fig_wf.update_layout(yaxis_title="MNOK", plot_bgcolor="white", height=420)
    st.plotly_chart(fig_wf, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 11: LIKVIDITETSBRO & FISKÅ ENHETER
# ------------------------------------------------------------------------------
elif selected_page == "11 Likviditetsbro & Fiskå Enheter (Cash)":
    st.title("11 Likviditet, Forfallsstruktur & Fiskå Koststeder")
    st.markdown("Likviditetsprognose basert på DPO 30d utbetalinger og timefangst ved CC-4100/4200/4300 (@ 530 kr/t).")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("A: Månedlig Likviditetsutgang vs. Enova Innbetaling")
        fig_cash = go.Figure([
            go.Bar(name='Kontantutbetalinger (AP+Lønn)', x=TIMELINE_DF["period"], y=TIMELINE_DF["cash_out"]/1e6, marker_color='#C00000'),
            go.Bar(name='Enova Tilskudd Mottatt', x=TIMELINE_DF["period"], y=TIMELINE_DF["enova_in"]/1e6, marker_color='#009E73')
        ])
        fig_cash.update_layout(yaxis_title="MNOK", plot_bgcolor="white", height=340, barmode='group')
        st.plotly_chart(fig_cash, use_container_width=True)
    with col2:
        st.subheader("B: Timefangst & Kostnader ved Fiskå (@ 530 kr/t)")
        cc_df = pd.DataFrame([
            {"cc": "CC-4100 Verksted", "hours": 3379.5, "cost": 1.79, "status": "Overtid / Forsering"},
            {"cc": "CC-4200 Sentrallab", "hours": 2999.0, "cost": 1.59, "status": "Normal drift"},
            {"cc": "CC-4300 PMO & Adm", "hours": 3394.0, "cost": 1.80, "status": "Krise / Møter"}
        ])
        fig_cc = go.Figure([go.Bar(y=cc_df["cc"], x=cc_df["hours"], orientation='h', marker_color=['#E69F00', '#2F5496', '#C00000'], text=[f"{h:.0f}t ({c:.2f}M)" for h, c in zip(cc_df['hours'], cc_df['cost'])], textposition='inside')])
        fig_cc.update_layout(xaxis_title="Faktiske Timer", plot_bgcolor="white", height=340)
        st.plotly_chart(fig_cc, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 12: HVA-OM SCENARIO SIMULATOR
# ------------------------------------------------------------------------------
elif selected_page == "12 Hva-om Scenario Simulator":
    st.title("12 Hva-om Scenario Simulator (Beslutningsstøtte)")
    st.markdown("Juster styringsparametere for å simulere finansiell eksponering og IAS 36 nedskrivningsbelastning.")
    
    col1, col2 = st.columns([1, 1.4])
    with col1:
        st.subheader("Styringsparametere")
        po_cut_pct = st.slider("Kansellering av åpne PO-er (%)", min_value=0, max_value=60, value=37, step=5)
        impair_pct = st.slider("IAS 36 Nedskrivning på balanseført AuC (%)", min_value=0, max_value=100, value=25, step=5)
        
        sim_po_saved = (DATA["OPEN_PO"] * (po_cut_pct / 100)) / 1e6
        sim_new_exp = (DATA["TOTAL_EXPOSURE"] / 1e6) - sim_po_saved
        sim_impair_loss = (DATA["AUC"] / 1e6) * (impair_pct / 100)
        
        st.markdown(f"""
        * **Kansellert PO-verdi:** +{sim_po_saved:.2f} MNOK spart likviditet
        * **Ny Total Eksponering:** {sim_new_exp:.2f} MNOK
        * **IAS 36 Tapsføring (Drift):** -{sim_impair_loss:.2f} MNOK
        """)
    with col2:
        st.subheader("Simulert Utfall")
        fig_sim = go.Figure([go.Bar(
            x=["Nåværende Eksponering", "Simulert Eksponering", "Balanseført AuC", "IAS 36 Tap"],
            y=[DATA["TOTAL_EXPOSURE"]/1e6, sim_new_exp, DATA["AUC"]/1e6, sim_impair_loss],
            text=[f"{DATA['TOTAL_EXPOSURE']/1e6:.1f}M", f"{sim_new_exp:.1f}M", f"{DATA['AUC']/1e6:.1f}M", f"{sim_impair_loss:.1f}M"],
            textposition="outside",
            marker_color=["#800000", "#2F5496", "#595959", "#C00000"]
        )])
        fig_sim.update_layout(yaxis_title="MNOK", plot_bgcolor="white", height=380)
        st.plotly_chart(fig_sim, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 13: AI CONTROLLER COPILOT (RAG)
# ------------------------------------------------------------------------------
elif selected_page == "13 AI Controller Copilot (RAG)":
    st.title("13 Elkem AI Controller Copilot (Vektor-DB & RAG)")
    st.markdown("Still spørsmål direkte til prosjektets kildekorpus (IFRS IAS 38/36, ISA 805, Enova, Board Memo).")
    
    q_col1, q_col2, q_col3 = st.columns(3)
    preset_q = ""
    if q_col1.button("Hvorfor må AuC testes for verdifall?"):
        preset_q = "Hvorfor må anlegg under utførelse testes for verdifall etter IAS 36?"
    if q_col2.button("Hva kreves for å balansekapitalisere?"):
        preset_q = "Hva er kriteriene for balanseføring etter IAS 38?"
    if q_col3.button("Hvilke regler gjelder for timesats 530 kr?"):
        preset_q = "Hva er reglene for timesats og revisjon etter ISA 805 og Enova?"
        
    user_query = st.text_input("Ditt kontrollspørsmål:", value=preset_q)
    
    if user_query:
        vec, mat = get_vector_db()
        q_vec = vec.transform([user_query])
        sims = cosine_similarity(q_vec, mat).flatten()
        top_indices = sims.argsort()[::-1][:2]
        
        st.markdown(f"### Svar fra AI Copilot (Grunner i SSOT):")
        if "verdifall" in user_query or "IAS 36" in user_query:
            st.markdown("""
            **Konklusjon etter IAS 36 Impairment of Assets:**
            * En budsjettsprekk på 536 % (EAC 107,2 MNOK mot BAC 20,0 MNOK) representerer en **obligatorisk ekstern/intern indikator på verdifall** (IAS 36.12f).
            * Prosjektet har aktivert **43,38 MNOK i Anlegg under Utførelse (AuC)**. Hvis prosjektet stanses ved Gate 3, må hele beløpet tapsføres umiddelbart over driftsresultatet.
            """)
        elif "IAS 38" in user_query or "balanseføring" in user_query:
            st.markdown("""
            **Balanseføringsvurdering etter IAS 38 Immaterielle Eiendeler:**
            * Kun utviklingsutgifter i WBS-200, 300, 400 og 500 er balanseført.
            * PMO (WBS-100) og Testkjøring (WBS-600) er korrekt driftsført (P&L) da de regnes som administrative kostnader og forskningsfase.
            """)
        elif "timesats" in user_query or "Enova" in user_query:
            st.markdown("""
            **Revisjon & Tilskuddsregler (Enova / RF-1053B / ISA 805):**
            * Timesats for internt personell er lovregulert og **oppad begrenset til 530 kr per time** (maks 1 850 timer/år).
            * Overtidstillegg kan ikke veltes over på tilskuddet. Revisor skal etter ISA 805 attestere prosjektregnskapet.
            """)
        else:
            st.markdown(f"""
            *Basert på de reviderte kildedataene per 31.10.2026:*
            Prosjektet har påløpt **57,97 MNOK** mot en ramme på **20,00 MNOK**, med ytterligere **49,23 MNOK** bundet i uleverte PO-er.
            Samlet finansiell eksponering utgjør **107,20 MNOK** (536 % av BAC).
            """)
            
        with st.expander("🔍 Dokumenterte kildeutdrag fra Vektor-DB", expanded=True):
            for idx in top_indices:
                chunk = KNOWLEDGE_CHUNKS[idx]
                st.markdown(f"**[{chunk['category']}] {chunk['title']}** *(Match: {sims[idx]*100:.1f}%)*")
                st.caption(f"Kilde: {chunk['source']}")
                st.write(chunk["text"])
                st.markdown("---")

st.markdown("---")
st.caption("Elkem ASA — GreenPilot 2026 Controller Portal | FAST Standard & IFRS Compliant | Single Source of Truth")
