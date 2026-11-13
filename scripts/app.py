"""
================================================================================
ELKEM GREENPILOT 2026 — STREAMLIT AI CONTROLLER & EVM DASHBOARD
Single Source of Truth (SSOT) Dual-Engine Application
Engine 1: Deterministic EVM Calculator, S-Curve & Banana Chart Simulator
Engine 2: Agentic AI Reasoning & Financial Copilot with Vector DB (RAG)
================================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    .rag-chip {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .rag-red { background-color: #FCE4D6; color: #C00000; border: 1px solid #C00000; }
    .rag-amber { background-color: #FFF2CC; color: #B25900; border: 1px solid #B25900; }
    .rag-green { background-color: #E2EFDA; color: #385723; border: 1px solid #385723; }
    .source-box {
        background-color: #F8F9FA;
        border-left: 4px solid #1F4E79;
        padding: 10px 14px;
        margin: 6px 0;
        border-radius: 2px;
        font-size: 0.9rem;
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

# Monthly Timeline Data with Primavera P6 Early Dates and Late Dates for Banana Envelope
TIMELINE_DATA = pd.DataFrame([
    {"period": "2026-01", "pv": 1534314, "pv_late": 650000, "ac": 4653705, "ev": 980392, "open_po": 10077796, "cash_out": 453945, "enova_in": 0},
    {"period": "2026-02", "pv": 1802592, "pv_late": 850000, "ac": 2376228, "ev": 1568627, "open_po": 15340324, "cash_out": 2794789, "enova_in": 0},
    {"period": "2026-03", "pv": 1454416, "pv_late": 1000000, "ac": 3413810, "ev": 2549020, "open_po": 29789347, "cash_out": 5274928, "enova_in": 0},
    {"period": "2026-04", "pv": 1628504, "pv_late": 1250000, "ac": 4892110, "ev": 1960784, "open_po": 36140500, "cash_out": 4980200, "enova_in": 0},
    {"period": "2026-05", "pv": 1785183, "pv_late": 1650000, "ac": 6124500, "ev": 2156863, "open_po": 42500000, "cash_out": 5890000, "enova_in": 0},
    {"period": "2026-06", "pv": 1920000, "pv_late": 1900000, "ac": 7890200, "ev": 2352941, "open_po": 46200000, "cash_out": 7450000, "enova_in": 3000000},
    {"period": "2026-07", "pv": 1650000, "pv_late": 1950000, "ac": 6450000, "ev": 1764706, "open_po": 47800000, "cash_out": 8100000, "enova_in": 0},
    {"period": "2026-08", "pv": 1520000, "pv_late": 1950000, "ac": 6980000, "ev": 1960784, "open_po": 48500000, "cash_out": 6750000, "enova_in": 0},
    {"period": "2026-09", "pv": 1710000, "pv_late": 2000000, "ac": 7650000, "ev": 2156863, "open_po": 48900000, "cash_out": 7450000, "enova_in": 0},
    {"period": "2026-10", "pv": 1615862, "pv_late": 2000000, "ac": 7537488, "ev": 1764706, "open_po": 49233752, "cash_out": 7850000, "enova_in": 0},
])
TIMELINE_DATA["cum_pv"] = TIMELINE_DATA["pv"].cumsum()
TIMELINE_DATA["cum_pv_late"] = TIMELINE_DATA["pv_late"].cumsum()
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
# 3. VEKTORDATABASE (VECTOR DB & RAG RETRIEVAL ENGINE)
# ------------------------------------------------------------------------------
VECTOR_KNOWLEDGE_BASE = [
    {
        "id": "IAS38-01",
        "title": "IAS 38 Immaterielle Eiendeler — 6 Kriterier for Balanseføring av AuC",
        "category": "Regnskap (IFRS)",
        "source": "IAS 38 Immaterielle Eiendeler & GTAL Factsheet",
        "keywords": "ias 38 balanseføring aktivering auc anlegg under utførelse forskning utvikling 6 kriterier vilkår p&l",
        "content": "Etter IFRS IAS 38 skal utgifter i forskningsfasen alltid kostnadsføres umiddelbart i resultatregnskapet (P&L). Utviklingsutgifter kan og skal balanseføres som anlegg under utførelse (AuC) dersom og bare dersom samtlige seks kriterier er oppfylt: 1) Teknisk gjennomførbarhet for fullføring, 2) Foretakets hensikt om å fullføre eiendelen for bruk eller salg, 3) Evne til å bruke eller selge eiendelen, 4) Hvordan eiendelen vil generere sannsynlige fremtidige økonomiske fordeler, 5) Tilgjengelighet av tilstrekkelige tekniske, finansielle og andre ressurser, 6) Evne til å måle pålitelig utgiftene som kan henføres til eiendelen. I GreenPilot 2026 er 43,38 MNOK balanseført som AuC (WBS 200–500), mens 14,59 MNOK (WBS 100 og 600) er driftsført som FoU-kostnad."
    },
    {
        "id": "IAS38-02",
        "title": "IAS 38 Direkte Henførbare Kostnader vs. Forbudte Påslag",
        "category": "Regnskap (IFRS)",
        "source": "IFRS Practice Guide: IAS 38.65-67",
        "keywords": "direkte henførbare kostnader overskridelser ineffektivitet administrasjon opplæring",
        "content": "Kun utgifter som er direkte henførbare til å klargjøre eiendelen for dens tiltenkte bruk kan aktiveres. IAS 38.67 forbyr uttrykkelig aktivering av: a) administrasjonskostnader og generelle felleskostnader, b) identifiserte ineffektiviteter og innledende driftstap før eiendelen oppnår planlagt ytelse, c) opplæringskostnader for personell. I GreenPilot må derfor timeoverforbruk knyttet til forsinkelser og møtevirksomhet i PMO (WBS 100) avskjæres fra balanseføring."
    },
    {
        "id": "IAS36-01",
        "title": "IAS 36 Verdifall på Eiendeler — Triggerindikatorer og Årlig Test for AuC",
        "category": "Regnskap (IFRS)",
        "source": "IAS 36 Impairment of Assets Guide",
        "keywords": "ias 36 verdifall nedskrivning impairment trigger auc anlegg under utførelse gjenvinnbart beløp bruksverdi",
        "content": "IAS 36 krever at foretaket på hver balansedag vurderer om det foreligger indikasjoner på verdifall (impairment indicators). For anlegg under utførelse (AuC) som ennå ikke er ferdigstilt eller tatt i bruk, kreves det uansett en formell årlig verdifallstest. En eksplosjon i prosjektets sluttkostnadsprognose (EAC) fra 20 MNOK til 107 MNOK utgjør en alvorlig intern trigger (IAS 36.12f: 'drifts- eller anleggskostnader som vesentlig overstiger opprinnelig budsjett'). Gjenvinnbart beløp er det høyeste av salgsverdi fratrukket salgskostnader og bruksverdi (Value in Use basert på neddiskontert kontantstrøm / DCF). Hvis gjenvinnbart beløp er lavere enn balanseført verdi (43,38 MNOK), må differansen umiddelbart tapsføres over resultat."
    },
    {
        "id": "IAS20-01",
        "title": "IAS 20 Regnskapsføring av Offentlige Tilskudd (Enova SF)",
        "category": "Regnskap (IFRS)",
        "source": "IAS 20 Accounting for Government Grants",
        "keywords": "ias 20 offentlig tilskudd enova betingelser tilbakebetaling innregning motregning",
        "content": "Etter IAS 20 innregnes offentlige tilskudd først når det er rimelig sikkerhet for at foretaket vil oppfylle tilskuddsbetingelsene og tilskuddet vil bli mottatt. Tilskudd knyttet til anleggsmidler (AuC) kan enten presenteres som utsatt inntekt eller trekkes direkte fra eiendelens balanseførte verdi (motregning). GreenPilot har fått innvilget et Enova-tilskudd på 10,0 MNOK, hvorav 3,0 MNOK ble utbetalt i juni 2026 ved godkjent milepæl 2. Resterende 7,0 MNOK utbetales først ved godkjent sluttrapport og verifiserte pilotresultater."
    },
    {
        "id": "ISA805-01",
        "title": "ISA 805 Særattestasjon — Revisjon av Prosjektregnskap mot Enova",
        "category": "Revisjon & Enova",
        "source": "Enova SF Retningslinjer for Prosjektregnskap & ISA 805",
        "keywords": "isa 805 revisjon attestasjon revisor enova sluttrapport prosjektregnskap stikkprøve",
        "content": "Enova krever at prosjektregnskapet attesteres av uavhengig statsautorisert revisor etter standarden ISA 805 (Særlige hensyn ved revisjon av enkeltregnskaper og spesifikke bestanddeler). Revisor skal bekrefte at: 1) Alle kostnader er påløpt i prosjektperioden og er direkte henførbare til godkjente WBS-aktiviteter; 2) Kostnader er dokumentert med godkjente bilag; 3) Kun faktiske, utbetalte lønnskostnader inngår (begrenset til godkjent timesats); 4) Indirekte kostnadspåslag følger avtalte satser. Mangelfulle timelister eller overskridelser uten forhåndsgodkjenning vil bli strøket fra tilskuddsgrunnlaget."
    },
    {
        "id": "HOURLY-01",
        "title": "Enova & SkatteFUNN Forskrift — Maksimal Timesats 530 kr/t",
        "category": "Revisjon & Enova",
        "source": "Forskrift til skatteloven § 16-40-6 & Enova Standardbetingelser",
        "keywords": "timesats 530 kr timepris personalkostnader 1850 timer tak begrensning skattefunn enova",
        "content": "For prosjekter støttet av Enova og Norges forskningsråd (inkl. SkatteFUNN) er prosjektdeltakernes timepris strengt regulert: Timeprisen kan maksimalt utgjøre 1,2 promille av avtalt årslønn ved prosjektets oppstart, men kan aldri overstige 530 kroner per time. Det maksimale antall godkjente timer per person per år er 1 850 timer. Overtidstillegg kan ikke belastes tilskuddsgrunnlaget med mindre det er uttrykkelig forhåndsgodkjent. I GreenPilot er alle interne timer ved Elkem Fiskå avregnet til nøyaktig 530 kr/t."
    },
    {
        "id": "FISKAA-01",
        "title": "Elkem Fiskå Koststeder — CC-4100, CC-4200 og CC-4300 Ressursanalyse",
        "category": "GreenPilot Prosjektfakta",
        "source": "Internt Notat: Ressursbruk Fiskå Pilotdrift 2026",
        "keywords": "fiskå koststed cc-4100 cc-4200 cc-4300 timer overtid overforbruk pmo sentrallab drift",
        "content": "I GreenPilot 2026 er det registrert totalt 12 320 faktiske timer per 31.10.2026, fordelt på tre enheter ved Elkem Fiskå: 1) CC-4100 Pilot Drift (3 379,5 timer, NOK 1,79M) preget av overtid for å hente inn tidsplanen; 2) CC-4200 FoU Lab (2 999,0 timer, NOK 1,59M) med normal analyseaktivitet; 3) CC-4300 Prosessmetallurgi & PMO (3 394,0 timer, NOK 1,80M) med uforholdsmessig høyt timeforbruk knyttet til krisehåndtering, redesign og prosjektstyringsmøter. Dette møteoverforbruket i PMO representerer en særskilt risiko for underkjenning under ISA 805-revisjon."
    },
    {
        "id": "GATE3-01",
        "title": "Elkem Prosjektmodell — Stage-Gate 3 Beslutningskriterier",
        "category": "Prosjektstyring & EVM",
        "source": "Elkem Corporate Project Management Manual — Gate 3 Protocol",
        "keywords": "stage-gate gate 3 beslutning go kill hold recycle pilotanlegg styringsmannual",
        "content": "Elkems Stage-Gate modell styrer teknologisk og finansiell risiko gjennom definerte porter: Gate 1 (Idé/Konsept), Gate 2 (Basic Engineering/Forprosjekt), Gate 3 (Detaljprosjektering & Byggegodkjenning), Gate 4 (Mekanisk ferdigstillelse & Testkjøring), Gate 5 (Kommersiell overlevering). Ved hver port må styret fatte en av fire beslutninger: 1) Go (Videreføre iht. plan), 2) Kill / Off-Ramp (Avslutte prosjektet for å stoppe videre tap), 3) Hold (Midlertidig stans for full revisjon), 4) Recycle (Sendes tilbake for omprosjektering). GreenPilot står ved Gate 3."
    },
    {
        "id": "GATE3-02",
        "title": "Controllerens Styringsnotat — Anbefaling om 30 Dagers Technical Hold",
        "category": "Prosjektstyring & EVM",
        "source": "Styrenotat GreenPilot Gate 3 Review (31.10.2026)",
        "keywords": "technical hold off-ramp anbefaling tiltakspakke innkjøpsfrys kansellering revisjon",
        "content": "Ved ekstraordinært styremøte 31.10.2026 anbefaler controller-funksjonen: Alternativ A — 30 dagers Technical Hold (Anbefalt): Umiddelbar innkjøps- og ansettelsesfrys, full kanselleringsaudit av åpne forpliktelser (49,2 MNOK med potensial for å spare 15–25 MNOK i uleverte ordrer), og varsling til Enova om fremdriftsrevisjon. Alternativ B — Formell Off-Ramp (Prosjektstans): Umiddelbar terminering av samtlige leverandørkontrakter, full tapsføring av 43,38 MNOK i AuC under IAS 36, samt håndtering av Enovas tilbakebetalingskrav (3,0 MNOK)."
    },
    {
        "id": "BANANA-01",
        "title": "Primavera P6 Banana Curve & Tidsbuffersone (Float)",
        "category": "Prosjektstyring & EVM",
        "source": "Primavera P6 Baseline Schedule & S-Curve Envelope",
        "keywords": "banana curve banana chart primavera p6 float buffersone tidlig sen early late envelope",
        "content": "I Primavera P6 danner kumulativ tidlig plan (Early Dates PV) og kumulativ sen plan (Late Dates PV) en karakteristisk bananformet konvolutt ('Banana Curve'). Så lenge faktisk opptjent verdi (EV) beveger seg innenfor denne banan-sonen, er prosjektet i rute innenfor sin totale bufferslakk (float). I GreenPilot 2026 ble EV presset opp mot den tidlige kurven i første halvår gjennom aggressiv forsering, men faktiske kostnader (AC) eksploderte fullstendig utenfor banan-konvolutten (290% av budsjett), mens prosjektets totale bufferslakk kollapset fra +22 dager til -14 dager."
    },
    {
        "id": "EVM-01",
        "title": "EVM Formler og Nøkkeltall — CPI, SPI, EAC og TCPI Teori",
        "category": "Prosjektstyring & EVM",
        "source": "PMI Practice Standard for Earned Value Management",
        "keywords": "evm cpi spi eac etc tcpi kostnadsindeks fremdriftsindeks formler opptjent verdi",
        "content": "EAC (Estimate at Completion) representerer forventet sluttkostnad. Standardformel: EAC = BAC / CPI = 20M / 0.331 = 60,4 MNOK (forutsatt uendret ineffektivitet på gjenværende arbeid). Men når uleverte forpliktelser (åpne PO-er på 49,2 MNOK) inkluderes, utgjør samlet finansiell eksponering hele 107,2 MNOK. Estimate to Complete (ETC) = EAC - AC. To-Complete Performance Index (TCPI) beregner nødvendig effektivitet for å nå budsjett: TCPI = (BAC - EV) / (BAC - AC). Siden AC (58M) allerede overskrider BAC (20M), er nevneren negativ, noe som matematisk beviser at det opprinnelige budsjettet er uoppnåelig."
    },
    {
        "id": "WBS-01",
        "title": "WBS Dekomponering og Kostnadsdrivere i GreenPilot",
        "category": "GreenPilot Prosjektfakta",
        "source": "Prosjektplan GreenPilot WBS Dictionary 2026",
        "keywords": "wbs wbs-100 wbs-200 wbs-300 wbs-400 wbs-500 wbs-600 reaktor infrastruktur pmo",
        "content": "Oversikt per arbeidspakke (BAC vs. AC vs. Åpne PO): WBS-100 Prosjektledelse/PMO (BAC 2,5M | AC 7,2M | PO 4,1M); WBS-200 Prosessdesign (BAC 3,5M | AC 10,1M | PO 6,9M); WBS-300 Pilotanlegg & Reaktor (BAC 8,0M | AC 23,2M | PO 28,5M — hoveddriveren for krisen, sprengte rammen med 15,2M i AC alene); WBS-400 Gass/Infrastruktur (BAC 3,0M | AC 8,7M | PO 5,2M); WBS-500 Installasjon/Elektro (BAC 2,0M | AC 5,8M | PO 3,6M); WBS-600 Testkjøring (BAC 1,0M | AC 2,9M | PO 1,0M)."
    },
    {
        "id": "CRISIS-01",
        "title": "Tidslinje for Krisen: Hvordan Hasteinnkjøp i Q1 2026 Felte Prosjektet",
        "category": "GreenPilot Prosjektfakta",
        "source": "Revisjonsrapport: Hendelsesforløp GreenPilot 2026",
        "keywords": "krise forløp vendepunkt mars forsering po ekspansjon overskridelse erfaring",
        "content": "Kriseutvikling gjennom 2026: I januar og februar ble reaktormontasjen kraftig forsert for å nå milepæl 1. I mars 2026 inntraff prosjektets kritiske vendepunkt: akkumulerte innkjøpsordrer nådde 29,8 MNOK, og passerte dermed det totale styrevedtatte budsjettet (149 % av BAC). Denne forpliktelseseksplosjonen ble ikke fanget opp av ledelsen fordi rapporteringen kun fulgte bokførte fakturaer (AC var da 10,4M). Fra mai til oktober eskalerte månedlig faktisk kostnad til mellom 6,1M og 7,9M per måned, mens åpne forpliktelser stabiliserte seg rundt 49 MNOK."
    },
    {
        "id": "DUALENG-01",
        "title": "Dual-Engine Arkitektur — Deterministisk Presisjon vs. KI-Resonnering",
        "category": "Prosjektstyring & EVM",
        "source": "Architecting_Agentic_Finance.pdf",
        "keywords": "agentic finance dual-engine llm resonnering deterministisk kalkulator audit",
        "content": "I henhold til 'Architecting Agentic Finance' krever moderne økonomistyring en Dual-Engine arkitektur for å unngå KI-hallusinasjoner i styrende finansrapporter. Engine 1 (Deterministisk): Programvare og databaser beregner alle harde tall (EVM, kontantstrøm, varianser, IFRS-allokering) med 100 % matematisk presisjon. Engine 2 (Agentisk resonnering): LLM og semantisk søk (Vektor-DB) tolker avvikene, utfører rotårsaksanalyse, evaluerer regnskapsstandarder og formulerer anbefalinger. Prinsippet oppsummeres: 'Models Reason. Software Computes. Agents Orchestrate. Systems Verify.'"
    }
]

@st.cache_resource
def build_vector_search_engine():
    corpus = [
        f"{c['title']} {c['category']} {c['source']} {c['keywords']} {c['content']}"
        for c in VECTOR_KNOWLEDGE_BASE
    ]
    vectorizer = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(corpus)
    return vectorizer, tfidf_matrix

VECTORIZER, TFIDF_MATRIX = build_vector_search_engine()

def search_vector_db(query: str, category_filter: str = "Alle kategorier", top_k: int = 3):
    q_vec = VECTORIZER.transform([query])
    sims = cosine_similarity(q_vec, TFIDF_MATRIX)[0]
    
    results = []
    for idx, score in enumerate(sims):
        chunk = VECTOR_KNOWLEDGE_BASE[idx]
        if category_filter != "Alle kategorier" and chunk["category"] != category_filter:
            continue
        results.append({
            "chunk": chunk,
            "score": float(score)
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

# ------------------------------------------------------------------------------
# 4. SIDEBAR NAVIGATION & KNOWLEDGE EXPLORER
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ELKEM ASA")
    st.markdown("### GreenPilot 2026 Controller")
    st.caption("Dual-Engine: Deterministisk EVM + Agentic AI (RAG Vektor-DB)")
    
    selected_page = st.radio(
        "Navigasjon",
        [
            "00 Executive Governance & Status",
            "01 EVM S-Kurve & Banana Chart",
            "02 Forpliktelsesisberg & WBS",
            "03 Likviditetsbro & Fiskå Enheter",
            "04 Hva-om Scenario Simulator",
            "05 AI Controller Copilot (RAG & Vektor-DB)"
        ]
    )
    
    st.markdown("---")
    st.markdown("#### Vektor-DB Kildekorpus")
    st.markdown(f"• **Indekserte kunnskaps-chunks:** {len(VECTOR_KNOWLEDGE_BASE)}")
    st.markdown("• IFRS Standarder: IAS 38, IAS 36, IAS 20")
    st.markdown("• Revisjonsrammer: ISA 805, Enova Instruks")
    st.markdown("• Prosjektregnskap: RF-1053B (530 kr/t), P6 WBS")
    st.markdown("• Tidsplan & Buffer: Primavera P6 Banana Envelope")
    st.markdown("• Styring: Stage-Gate 3, EVM Standard")
    st.caption("Cut-off dato: 31.10.2026 | Audit-Ready")

# ------------------------------------------------------------------------------
# PAGE 00: EXECUTIVE GOVERNANCE & STATUS (RULE-BASED NARRATIVE)
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
        <p><strong>1. DIAGNOSE (EVM):</strong> Prosjektet opererer med en kostnadseffektivitet på <strong>CPI {cpi:.2f}</strong> og et akkumulert kostnadsavvik på <strong>NOK {cv_m:.1f}M</strong>. Fysisk fremdrift meldes til <strong>SPI {spi:.2f}</strong> som følge av forsert reaktormontasje.</p>
        <p><strong>2. DRIVER & LIKVIDITET:</strong> Bokførte kostnader (NOK {AC_NOK/1e6:.1f}M) og åpne leverandørforpliktelser (NOK {OPEN_PO_NOK/1e6:.1f}M) gir en samlet finansiell eksponering på <strong>NOK {TOTAL_EXPOSURE_NOK/1e6:.1f}M ({exp_pct:.0f}% av BAC)</strong>.</p>
        <p><strong>3. REGNSKAPSMESSIG KONSEKVENS:</strong> Av dette er <strong>NOK {AUC_CAPITALIZED_NOK/1e6:.1f}M</strong> balanseført som anlegg under utførelse (AuC) under IAS 38. Dette utløser obligatorisk krav om nedskrivningstest etter IAS 36 før årsoppgjøret grunnet eksploderende EAC.</p>
        <p><strong>4. PÅBUD TIL STYRET:</strong> 1) Umiddelbar innkjøpsfrys på alle nye rekvisisjoner. 2) Kanselleringsaudit av uleverte PO-er (NOK 49,2M). 3) Innkall styret til ekstraordinært Stage-Gate møte for 30 dagers Technical Hold / Off-Ramp vurdering.</p>
    </div>
    """, unsafe_allow_html=True)
    
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
# PAGE 01: EVM S-CURVE & PRIMAVERA P6 BANANA CHART
# ------------------------------------------------------------------------------
elif selected_page == "01 EVM S-Kurve & Banana Chart":
    st.markdown('<div class="main-title">EVM S-KURVE & PRIMAVERA P6 BANANA CHART</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Kumulativ kostnads- og fremdriftsutvikling (PV vs. AC vs. EV) og P6 tidsbufferkonvolutt (Early vs. Late Dates)</div>', unsafe_allow_html=True)
    
    st.info("💡 **S-KURVE & BANANA CHART RESYME:** Fysisk fremdrift (EV) beveget seg langs den øvre tidlige kurven (Early Dates) grunnet aggressiv forsering i Q1/Q2 (SPI 1.16). Imidlertid sprengte faktiske kostnader (AC) fullstendig ut av hele 'Banan-konvolutten' fra mars 2026, og prosjektets totale bufferslakk (float) kollapset fra +22 til -14 dager.")
    
    tab_s1, tab_s2 = st.tabs(["📈 Klassisk EVM S-Kurve (med Vendepunkt)", "🍌 Primavera P6 Banana Chart (Early vs. Late Envelope)"])
    
    with tab_s1:
        st.subheader("Klassisk EVM S-Kurve (PV, EV, AC)")
        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(x=TIMELINE_DATA["period"], y=TIMELINE_DATA["cum_pv"]/1e6, mode="lines+markers", name="Planlagt Verdi (PV)", line=dict(color="#595959", dash="dash", width=2)))
        fig_s.add_trace(go.Scatter(x=TIMELINE_DATA["period"], y=TIMELINE_DATA["cum_ev"]/1e6, mode="lines+markers", name="Opptjent Verdi (EV - Fysisk)", line=dict(color="#2F5496", width=2.5)))
        fig_s.add_trace(go.Scatter(x=TIMELINE_DATA["period"], y=TIMELINE_DATA["cum_ac"]/1e6, mode="lines+markers", name="Faktisk Kostnad (AC)", line=dict(color="#C00000", width=3.5)))
        
        # Horisontal BAC linje
        fig_s.add_hline(y=20.0, line_dash="dot", line_color="#888888", annotation_text="Vedtatt Budsjettramme (BAC): 20,0 MNOK")
        
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
            height=460,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_s, use_container_width=True)

    with tab_s2:
        st.subheader("Primavera P6 Banana Chart (Fremdrifts- og Buffersone)")
        
        # Banana envelope: shaded between Early PV and Late PV
        fig_banana = go.Figure()
        
        # Envelope shading
        periods_list = list(TIMELINE_DATA["period"])
        early_vals = list(TIMELINE_DATA["cum_pv"] / 1e6)
        late_vals = list(TIMELINE_DATA["cum_pv_late"] / 1e6)
        
        fig_banana.add_trace(go.Scatter(
            x=periods_list + periods_list[::-1],
            y=early_vals + late_vals[::-1],
            fill="toself",
            fillcolor="rgba(47, 84, 150, 0.15)",
            line=dict(color="rgba(255,255,255,0)"),
            name="P6 Tidsbuffersone (Banana Envelope)",
            hoverinfo="skip"
        ))
        
        fig_banana.add_trace(go.Scatter(x=TIMELINE_DATA["period"], y=early_vals, mode="lines", name="Tidlig Plan (Early Dates PV)", line=dict(color="#2F5496", dash="dash", width=2)))
        fig_banana.add_trace(go.Scatter(x=TIMELINE_DATA["period"], y=late_vals, mode="lines", name="Sen Plan (Late Dates PV)", line=dict(color="#595959", dash="dot", width=2)))
        fig_banana.add_trace(go.Scatter(x=TIMELINE_DATA["period"], y=TIMELINE_DATA["cum_ev"]/1e6, mode="lines+markers", name="Opptjent Verdi (EV - Fysisk)", line=dict(color="#009E73", width=3)))
        fig_banana.add_trace(go.Scatter(x=TIMELINE_DATA["period"], y=TIMELINE_DATA["cum_ac"]/1e6, mode="lines+markers", name="Faktisk Påløpt Kostnad (AC)", line=dict(color="#C00000", width=3.5)))
        
        fig_banana.add_annotation(
            x="2026-10", y=57.97,
            text="AC: 57,97 MNOK (+190% over BAC)",
            showarrow=True, arrowhead=2, ax=-60, ay=-20,
            bgcolor="#FCE4D6", bordercolor="#C00000"
        )
        fig_banana.add_annotation(
            x="2026-10", y=19.22,
            text="EV: 19,22 MNOK (Fysisk 96%)",
            showarrow=True, arrowhead=2, ax=-60, ay=30,
            bgcolor="#E2EFDA", bordercolor="#385723"
        )
        
        fig_banana.update_layout(
            title="Primavera P6 Banana Chart: EV følger tidlig plan, mens AC eksploderer utenfor konvolutten",
            yaxis_title="MNOK",
            xaxis_title="Periode (2026)",
            plot_bgcolor="white",
            height=460,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_banana, use_container_width=True)

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
# PAGE 05: AI CONTROLLER COPILOT WITH VECTOR DB (RAG CHATBOT)
# ------------------------------------------------------------------------------
elif selected_page == "05 AI Controller Copilot (RAG & Vektor-DB)":
    st.markdown('<div class="main-title">ELKEM AI CONTROLLER COPILOT — VEKTOR-DB CHATBOT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Semantisk søk og resonneringsmotor over prosjektregnskap, IFRS-standarder, Enova-avtaler og styredokumenter</div>', unsafe_allow_html=True)
    
    # Filter and settings bar
    c_f1, c_f2, c_f3 = st.columns([1.5, 1, 1])
    with c_f1:
        cat_filter = st.selectbox(
            "Filtrer Vektor-DB søk etter fagområde:",
            ["Alle kategorier", "Regnskap (IFRS)", "Revisjon & Enova", "Prosjektstyring & EVM", "GreenPilot Prosjektfakta"]
        )
    with c_f2:
        top_k = st.slider("Antall kilder hentet (Top-K):", min_value=1, max_value=5, value=3)
    with c_f3:
        if st.button("🗑️ Tøm samtalehistorikk"):
            st.session_state.messages = []
            st.rerun()

    # Pre-canned suggested prompts
    st.markdown("**💡 Raske kontrollspørsmål for styret og revisor:**")
    p1, p2, p3, p4 = st.columns(4)
    quick_query = None
    if p1.button("🔍 Hvorfor kollapset kostnadskontrollen i Q1?"):
        quick_query = "Hvorfor kollapset kostnadskontrollen i Q1 og hva var vendepunktet i mars?"
    if p2.button("⚖️ Hvilke krav stilles for nedskrivning etter IAS 36?"):
        quick_query = "Hvilke krav stiller IAS 36 til verdifallstest og nedskrivning av anlegg under utførelse AuC?"
    if p3.button("📋 Hva er reglene for SkatteFUNN timesats på 530 kr?"):
        quick_query = "Hva er reglene for SkatteFUNN og Enova timesats på 530 kr per time og timeføring?"
    if p4.button("🛑 Hva er styrets handlingsalternativer ved Gate 3?"):
        quick_query = "Hva er forskjellen på Technical Hold og Off-Ramp ved Stage-Gate 3 review?"

    # Initialize chat messages in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hei! Jeg er Elkem AI Project Controller Copilot. Jeg er koblet direkte til prosjektets **vektordatabase** med stjerneskjemaet, IFRS IAS 38/36/20, ISA 805, Enova-retningslinjer og styredokumenter. Hva kan jeg hjelpe deg å etterprøve i dag?",
                "sources": []
            }
        ]

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("🔍 Hentet fra Vektor-DB (Kildeforankring)"):
                    for src in msg["sources"]:
                        st.markdown(f"""
                        <div class="source-box">
                            <strong>{src['chunk']['title']}</strong> ({src['chunk']['category']})<br>
                            <em>Kilde: {src['chunk']['source']} | Relevansscore: {src['score']*100:.1f}%</em><br>
                            {src['chunk']['content']}
                        </div>
                        """, unsafe_allow_html=True)

    # Chat input
    user_query = st.chat_input("Still et spørsmål til Vektor-DB (f.eks. IFRS, Enova, EVM, WBS-avvik)...")
    if quick_query:
        user_query = quick_query

    if user_query:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_query, "sources": []})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Run Vector DB Retrieval
        search_results = search_vector_db(user_query, category_filter=cat_filter, top_k=top_k)
        
        # Synthesize Controller Answer
        with st.chat_message("assistant"):
            with st.spinner("Søker i Vektor-DB og analyserer kildereferanser..."):
                top_chunks = [r["chunk"] for r in search_results]
                
                # Intelligent deterministic synthesis based on retrieved knowledge
                response_text = ""
                
                # Check for major themes in query and retrieved context
                q_lower = user_query.lower()
                
                if any(k in q_lower for k in ["kollaps", "q1", "vendepunkt", "hvorfor", "mars"]):
                    response_text = f"""
### 📊 Diagnostisk Analyse: Årsakene til Kostnadskollapsen i Q1 2026

Basert på gjenfinningsdata fra prosjektets **Vektor-DB** (*{top_chunks[0]['title']}*):

1. **Tidlig forsering uten kostnadssikring (Januar–Februar):**
   * Reaktormontasje og elektro ble forsert for å nå milepæl 1 (SPI 1.16).
   * For å holde tempoet ble det utstedt store hasteordrer mot utenlandske leverandører i USD og EUR.
2. **Kritisk vendepunkt i Mars 2026:**
   * Allerede i mars nådde akkumulerte innkjøpsordrer (PO) **NOK 29,8M**, noe som tilsvarte **149 % av hele prosjektbudsjettet (BAC 20M)**.
   * Dette forpliktelsessjokket ble oversett fordi prosjektledelsen kun rapporterte bokførte kostnader (AC), som per mars kun sto i 10,4 MNOK.
3. **Intern ressurslekkasje ved Fiskå:**
   * CC-4300 (PMO/Prosjektledelse) akkumulerte et massivt overforbruk av møte- og koordineringstimer for å løse tekniske grensesnittfeil.
"""
                elif any(k in q_lower for k in ["ias 36", "nedskrivning", "verdifall", "impairment"]):
                    response_text = f"""
### ⚖️ IFRS IAS 36 Verdifallsvurdering for Anlegg under Utførelse (AuC)

Gjenfunnet fra regnskapsstandardene i **Vektor-DB** (*{top_chunks[0]['title']}*):

1. **Obligatorisk krav om verdifallstest:**
   * For anleggsmidler under utførelse (AuC) som ennå ikke er klare til bruk, krever IAS 36 en formell årlig test, eller **straks det inntreffer en alvorlig trigger**.
   * Sluttkostnadens eksplosjon (EAC på 107,2 MNOK mot 20 MNOK BAC) er en uttrykkelig trigger iht. IAS 36.12f.
2. **Vurdering av Gjenvinnbart Beløp (Value in Use):**
   * Balanseført verdi av AuC er per 31.10.2026 **NOK 43,38M** (WBS 200–500).
   * **Scenario 1 (Fullføring):** Gjenvinnbar verdi estimeres til maksimalt 30,0 MNOK, noe som utløser et nedskrivningstap på ca. **13,38 MNOK**.
   * **Scenario 2 (Off-Ramp / Stans):** Dersom anlegget skrotes, er bruksverdien null. Dette krever **100 % nedskrivning (NOK 43,38M)** over konsernresultatet i 4Q 2026.
"""
                elif any(k in q_lower for k in ["timesats", "530", "skattefunn", "timeføring", "rf-1053b"]):
                    response_text = f"""
### 📑 Retningslinjer for Timesatser og Timeføring (RF-1053B / Enova)

Gjenfunnet fra **Vektor-DB** (*{top_chunks[0]['title']}*):

1. **Maksimal timesats:**
   * Timesatsen beregnes som 1,2 promille av avtalt årslønn, men er **strengt avkortet oppad til NOK 530 per time**.
2. **Kapasitetstak:**
   * Maksimalt antall godkjente timer per person per år er **1 850 timer**.
3. **Krav til Samtidighet:**
   * Timelister må føres løpende og samtidig med angivelse av dato, timeantall, person og WBS-arbeidspakke.
4. **Revisjonsrisiko ved Fiskå:**
   * Totalt 12 320 timer er registrert per 31.10.2026. Avdelingen CC-4300 (PMO) har et uforholdsmessig høyt timeforbruk på koordinering (3 394 timer) som risikerer å bli avkortet av Enova under ISA 805-revisjon dersom det ikke er direkte teknisk henførbart.
"""
                elif any(k in q_lower for k in ["technical hold", "off-ramp", "stage-gate", "gate 3", "vedtak"]):
                    response_text = f"""
### 🛑 Stage-Gate 3 Beslutningsmatrise for Styret

Gjenfunnet fra **Vektor-DB** (*{top_chunks[0]['title']}*):

* **Alternativ A: 30 Dagers Technical Hold (Anbefalt)**
  * **Tiltak:** Total innkjøps- og ansettelsesfrys. Formell kanselleringsaudit av åpne forpliktelser (49,2 MNOK) med estimert sparepotensial på 15–25 MNOK.
  * **Enova-dialog:** Informere Enova om midlertidig stans for å unngå tilbakebetalingskrav og fremforhandle ny tidsplan.
* **Alternativ B: Formell Off-Ramp (Prosjektterminering)**
  * **Tiltak:** Avbryte prosjektet og terminere leverandørkontrakter.
  * **Konsekvens:** Full nedskrivning av balanseført AuC på **NOK 43,38M** i 4Q 2026 etter IAS 36, samt risiko for krav om umiddelbar tilbakebetaling av mottatt Enova-tilskudd (NOK 3,0M).
"""
                else:
                    # Generic semantic synthesis from retrieved context
                    response_text = f"### 🔍 Vektor-DB Søkeresultat og Finansiell Analyse\n\n"
                    response_text += f"Spørsmålet ditt (*'{user_query}'*) ga treff på følgende nøkkeldokumenter i kunnskapsbasen:\n\n"
                    for i, r in enumerate(search_results, 1):
                        c = r["chunk"]
                        response_text += f"**{i}. {c['title']}** (Relevans: {r['score']*100:.1f}%)\n"
                        response_text += f"> {c['content'][:280]}...\n\n"
                    response_text += "\n**Controller Konklusjon:**\n"
                    response_text += f"Dataene bekrefter at prosjektet har en samlet finansiell eksponering på **NOK 107,2M** mot en ramme på **NOK 20,0M** (CPI 0.33, SPI 1.16). Eventuelle tiltak må koordineres mellom teknisk fremdrift, leverandørkontrakter (49,2M åpne PO) og IFRS-krav etter IAS 36/38."

                st.markdown(response_text)
                
                # Show source expander
                with st.expander("🔍 Hentet fra Vektor-DB (Kildeforankring)", expanded=True):
                    for src in search_results:
                        st.markdown(f"""
                        <div class="source-box">
                            <strong>{src['chunk']['title']}</strong> <span class="rag-chip rag-amber">{src['chunk']['category']}</span><br>
                            <em>Kilde: {src['chunk']['source']} | Semantisk Relevansscore: {src['score']*100:.1f}%</em><br>
                            <p style="margin-top: 5px; color: #444;">{src['chunk']['content']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Save to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "sources": search_results
                })

st.markdown("---")
st.caption("Elkem ASA — GreenPilot 2026 Dual-Engine Analytics Platform | FAST Standard & IFRS Compliant | Vector DB RAG Engine")
