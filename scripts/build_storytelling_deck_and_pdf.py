import os
import sys
import pandas as pd
import numpy as np

# Matplotlib headless
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# PPTX
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ReportLab PDF
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ==============================================================================
# ROBUST STISØKING FOR KILDEDATA OG UT-MAPPER
# ==============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..")) if os.path.basename(SCRIPT_DIR).lower() == "scripts" else SCRIPT_DIR

def resolve_source_path(fname: str) -> str:
    possible_dirs = [
        os.path.join(PROJECT_ROOT, "data", "raw"),
        os.path.join(PROJECT_ROOT, "data", "cleaned"),
        os.path.join(PROJECT_ROOT, "data", "staging"),
        os.path.join(PROJECT_ROOT, "data"),
        os.path.join(PROJECT_ROOT, "raw"),
        r"C:\Users\frank\OneDrive\Elkem\data\raw",
        r"C:\Users\frank\OneDrive\Elkem\data",
        "/workspace/knowledge",
    ]
    for d in possible_dirs:
        p = os.path.join(d, fname)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"Fant ikke kildedata for {fname}. Søkte i: {possible_dirs}")

# Sett opp ut-mapper
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "processed", "reports")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

print("=" * 80)
print("=== GENERERER STORYTELLING VISUALS, POWERPOINT OG PDF FOR STYRET ===")
print("=" * 80)
print(f"Prosjekt-rot: {PROJECT_ROOT}")
print(f"Utdata-mappe: {OUTPUT_DIR}")

# ==============================================================================
# 1. GENERER DE 5 STORYTELLING VISUALS (MATPLOTLIB)
# ==============================================================================
print("\n--- [1/3] Genererer 5 Storytelling with Data visualiseringer ---")

C_NAVY = "#1F4E79"
C_BLUE = "#2F5496"
C_ALERT = "#C00000"
C_AMBER = "#D56B00"
C_GREEN = "#2E75B6"
C_MUTE = "#7F7F7F"

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12.5
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#EFEFEF'
plt.rcParams['grid.linestyle'] = '--'

# Chart 1: EVM S-Curve
m_labels = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt"]
pv_cum = [1.0, 2.5, 4.2, 6.0, 8.5, 11.0, 13.0, 14.5, 15.8, 16.62]
ac_cum = [1.51, 3.43, 6.85, 11.05, 20.49, 28.15, 36.41, 44.77, 52.11, 57.97]
ev_cum = [0.32, 1.24, 3.35, 4.46, 9.05, 13.45, 16.93, 18.66, 18.80, 19.22]

fig1, ax1 = plt.subplots(figsize=(10, 5.2), dpi=200)
ax1.plot(m_labels, pv_cum, label="Planlagt Verdi (PV) - Baseline", color=C_MUTE, linestyle="--", linewidth=2.0)
ax1.plot(m_labels, ev_cum, label="Opptjent Verdi (EV) - Fysisk fremdrift", color="#2E75B6", linewidth=2.5, marker="o", markersize=5)
ax1.plot(m_labels, ac_cum, label="Faktisk Påløpt Kostnad (AC)", color=C_ALERT, linewidth=3.0, marker="s", markersize=6)
ax1.fill_between(m_labels, ev_cum, ac_cum, color=C_ALERT, alpha=0.12, label="Kostnadsavvik (CV: -38,75 MNOK)")
ax1.annotate("Mars: PO passerer 149% av BAC\n(Punktet der kontrollen glapp)",
            xy=("Mar", 6.85), xytext=("Jan", 16.0),
            arrowprops=dict(facecolor=C_ALERT, edgecolor=C_ALERT, arrowstyle="->", lw=1.2),
            fontsize=9, fontweight='bold', color=C_ALERT,
            bbox=dict(boxstyle="round,pad=0.3", fc="#FFF0F0", ec=C_ALERT, lw=0.8))
ax1.annotate("Okt: AC 58,0M vs. EV 19,2M\nCPI = 0,33 (Kritisk krise)",
            xy=("Okt", 57.97), xytext=("Jun", 50.0),
            arrowprops=dict(facecolor=C_ALERT, edgecolor=C_ALERT, arrowstyle="->", lw=1.2),
            fontsize=9.5, fontweight='bold', color=C_ALERT,
            bbox=dict(boxstyle="round,pad=0.4", fc="#FFF0F0", ec=C_ALERT, lw=1.0))
ax1.axhline(20.0, color="#1F4E79", linestyle=":", linewidth=1.5)
ax1.text(0.1, 20.6, "Vedtatt Totalbudsjett (BAC: 20,0 MNOK)", color="#1F4E79", fontsize=9, fontweight='bold')
ax1.set_title("Kostnadskontrollen kollapset i Q1: AC eksploderte til 58,0M mot 19,2M i EV", pad=15)
ax1.set_ylabel("MNOK (Akkumulert)")
ax1.set_ylim(0, 65)
ax1.grid(True, axis='y')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#DDD", fontsize=9)
plt.tight_layout()
p_chart1 = os.path.join(FIG_DIR, "chart1_evm_scurve.png")
fig1.savefig(p_chart1)
plt.close(fig1)

# Chart 2: Waterfall Iceberg
categories = ["Totalbudsjett\n(BAC)", "WBS-100\nPMO", "WBS-200\nDesign", "WBS-300\nReaktor", "WBS-400\nMekanisk", "WBS-500/600\nTest/Slutt", "Bokført AC\n(Faktisk)", "Åpne PO\nForpliktelser", "Total Finansiell\nEksponering"]
bar_colors = [C_NAVY, C_ALERT, C_ALERT, C_ALERT, C_ALERT, C_ALERT, "#800000", C_AMBER, "#4A0000"]
x_pos = np.arange(len(categories))
bottoms = [0, 20.0, 24.75, 31.40, 46.59, 52.29, 0, 57.97, 0]
heights = [20.0, 4.75, 6.65, 15.19, 5.70, 5.68, 57.97, 49.23, 107.20]

fig2, ax2 = plt.subplots(figsize=(11, 5.2), dpi=200)
bars2 = ax2.bar(x_pos, heights, bottom=bottoms, color=bar_colors, width=0.62)
for i, (b, h, c) in enumerate(zip(bottoms, heights, bar_colors)):
    val = h if b == 0 else h
    y_p = b + h + 1.2
    lbl = f"{val:.1f}M" if i in [0, 6, 8] else (f"+{val:.1f}M\n(PO)" if i == 7 else f"+{val:.1f}M")
    fontw = 'bold' if i in [0, 6, 7, 8] else 'normal'
    ax2.text(x_pos[i], y_p, lbl, ha='center', va='bottom', fontsize=8.5, fontweight=fontw, color=c)
ax2.axhline(20.0, color=C_MUTE, linestyle="--", linewidth=1.0)
ax2.text(7.5, 21.5, "Opprinnelig budsjettak (20,0M)", color=C_MUTE, fontsize=8.5, fontstyle='italic')
ax2.set_title("Forpliktelsesisberget: 49,2M i åpne PO-er løfter samlet finansiell eksponering til 107,2M (536% av BAC)", pad=15)
ax2.set_ylabel("MNOK")
ax2.set_ylim(0, 125)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(categories, fontsize=8.5)
ax2.grid(True, axis='y')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
plt.tight_layout()
p_chart2 = os.path.join(FIG_DIR, "chart2_exposure_iceberg.png")
fig2.savefig(p_chart2)
plt.close(fig2)

# Chart 3: Likviditetsbro
cash_out = [1.2, 2.5, 4.8, 6.2, 9.5, 10.8, 12.1, 13.9, 14.5, 14.1]
enova_in = [0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0]
fig3, ax3 = plt.subplots(figsize=(10, 5.2), dpi=200)
w = 0.38
x3 = np.arange(len(m_labels))
ax3.bar(x3 - w/2, cash_out, w, label="Kontantutbetalinger (Leverandør DPO 30d + Lønn)", color="#C00000", alpha=0.85)
ax3.bar(x3 + w/2, enova_in, w, label="Enova Tilskudd Innbetalt (Juni: 3,0 MNOK)", color="#2E75B6")
ax3.set_ylabel("Månedlig Beløp (MNOK)", color="#333333", fontweight='bold')
ax3.set_xticks(x3)
ax3.set_xticklabels(m_labels)
ax3.set_ylim(0, 18)
ax3.grid(True, axis='y')
ax3.spines['top'].set_visible(False)
ax3.annotate("Enova Milepæl 1: 3,0 MNOK\n(Eneste kontantinnbetaling)",
            xy=(5 + w/2, 3.0), xytext=(3, 14),
            arrowprops=dict(facecolor="#2E75B6", edgecolor="#2E75B6", arrowstyle="->", lw=1.2),
            fontsize=9, fontweight='bold', color="#2E75B6",
            bbox=dict(boxstyle="round,pad=0.3", fc="#F0F8FF", ec="#2E75B6", lw=0.8))
ax3.set_title("Likviditetsgapet: Utbetalingene nådde 14,5M/mnd mens tilskuddet var låst til 3,0M", pad=15)
ax3.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#DDD", fontsize=9)
plt.tight_layout()
p_chart3 = os.path.join(FIG_DIR, "chart3_liquidity_gap.png")
fig3.savefig(p_chart3)
plt.close(fig3)

# Chart 4: Koststeder Fiskå
cc_names = ["CC-4300 Prosjektledelse/Adm\n(Overforbruk møter/feilsøking)", 
            "CC-4100 Pilot Drift & Verksted\n(Forsert montasje & overtid)", 
            "CC-4200 FoU Sentrallab\n(Kjemisk analyse / prøver)"]
cc_hours = [4320.0, 4200.0, 3800.0]
cc_cost = [2.29, 2.23, 2.01]
fig4, ax4 = plt.subplots(figsize=(10, 4.8), dpi=200)
y_pos = np.arange(len(cc_names))
bars4 = ax4.barh(y_pos, cc_hours, color=[C_ALERT, C_AMBER, C_GREEN], height=0.55)
for i, (b, h, c) in enumerate(zip(bars4, cc_hours, cc_cost)):
    ax4.text(b.get_width() + 60, b.get_y() + b.get_height()/2, 
            f"{h:,.0f} timer  |  NOK {c:.2f}M (@ 530 kr/t)", 
            va='center', fontsize=9.5, fontweight='bold', color="#222222")
ax4.set_yticks(y_pos)
ax4.set_yticklabels(cc_names, fontsize=9.5)
ax4.invert_yaxis()
ax4.set_xlabel("Registrerte Prosjekttimer (Jan-Okt 2026)")
ax4.set_xlim(0, 5600)
ax4.grid(True, axis='x')
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.set_title("Ressurslekkasje på Fiskå: 12 320 timer registrert — CC-4300 og CC-4100 bar tyngden", pad=15)
plt.tight_layout()
p_chart4 = os.path.join(FIG_DIR, "chart4_fiskaa_costcenters.png")
fig4.savefig(p_chart4)
plt.close(fig4)

# Chart 5: IFRS IAS 36 Impairment
scenarios = ["Balanseført Verdi (AuC)\nPer 31.10.2026", 
             "Scenario 1:\nFullføring (+45M lån)", 
             "Scenario 2:\nTechnical Hold / Redusert", 
             "Scenario 3:\nOff-Ramp (Stans / Skraping)"]
recoverable = [43.38, 30.0, 15.0, 0.0]
impairment = [0.0, 13.38, 28.38, 43.38]
x5 = np.arange(len(scenarios))
w5 = 0.55
fig5, ax5 = plt.subplots(figsize=(10, 5.2), dpi=200)
ax5.bar(x5, recoverable, w5, label="Gjenvinnbart Beløp (Value in Use)", color="#2F5496", alpha=0.9)
ax5.bar(x5, impairment, w5, bottom=recoverable, label="Krevd IAS 36 Nedskrivningstap (P&L Belastning)", color="#C00000", alpha=0.9)
for i in range(len(scenarios)):
    if impairment[i] > 0:
        ax5.text(x5[i], recoverable[i] + impairment[i]/2, f"Tap: {impairment[i]:.1f}M", 
                ha='center', va='center', color='white', fontweight='bold', fontsize=9.5)
    if recoverable[i] > 0:
        ax5.text(x5[i], recoverable[i]/2, f"Verdi: {recoverable[i]:.1f}M", 
                ha='center', va='center', color='white', fontweight='bold', fontsize=9.5)
    ax5.text(x5[i], 43.38 + 1.2, f"Bokført:\n43.4M", ha='center', va='bottom', fontsize=8.5, color="#7F7F7F")
ax5.set_ylabel("MNOK")
ax5.set_ylim(0, 58)
ax5.set_xticks(x5)
ax5.set_xticklabels(scenarios, fontsize=9)
ax5.grid(True, axis='y')
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#DDD", fontsize=9.0)
ax5.set_title("IFRS IAS 36 Nedskrivningsrisiko: 43,4M i AuC står i fare for 100% tap ved Off-Ramp", pad=15)
plt.tight_layout()
p_chart5 = os.path.join(FIG_DIR, "chart5_ias36_impairment.png")
fig5.savefig(p_chart5)
plt.close(fig5)
print(" [OK] 5 figurer generert og lagret til disk.")

# ==============================================================================
# 2. GENERER POWERPOINT BESLUTNINGSDEKK (.PPTX)
# ==============================================================================
print("\n--- [2/3] Bygger PowerPoint-presentasjon (16:9 Widescreen) ---")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

COLOR_DARK_BG = RGBColor(0x1F, 0x2A, 0x38) # Dark Navy
COLOR_NAVY = RGBColor(0x1F, 0x4E, 0x79)
COLOR_ALERT = RGBColor(0xC0, 0x00, 0x00)
COLOR_AMBER = RGBColor(0xD5, 0x6B, 0x00)
COLOR_TEXT_MAIN = RGBColor(0x22, 0x22, 0x22)
COLOR_TEXT_MUTED = RGBColor(0x66, 0x66, 0x66)
COLOR_CARD_BG = RGBColor(0xF4, 0xF7, 0xFA)

def add_header(slide, action_title, category="STAGE-GATE 3 REVIEW — ELKEM FISKÅ"):
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p0 = tf.paragraphs[0]
    p0.text = category.upper()
    p0.font.name = "Calibri"
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_NAVY
    
    p1 = tf.add_paragraph()
    p1.text = action_title
    p1.font.name = "Calibri"
    p1.font.size = Pt(20)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_before = Pt(3)

# ------------------------------------------------------------------------------
# SLIDE 1: TITTELSLIDE (DARK NAVY)
# ------------------------------------------------------------------------------
s1 = prs.slides.add_slide(prs.slide_layouts[6])
bg1 = s1.background
bg1.fill.solid()
bg1.fill.fore_color.rgb = COLOR_DARK_BG

tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(3.2))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "ELKEM TECHNOLOGY — GREENPILOT 2026"
p.font.name = "Calibri"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = RGBColor(0x5B, 0x9B, 0xD5)

p = tf1.add_paragraph()
p.text = "Finansiell Krisevurdering og Beslutningsgrunnlag"
p.font.name = "Calibri"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
p.space_before = Pt(8)

p = tf1.add_paragraph()
p.text = "Ekstraordinært Møte i Prosjektstyret | Stage-Gate 3 Review (Data Date: 31.10.2026)\nAnbefaling om 30 dagers Technical Hold vs. Formell Off-Ramp"
p.font.name = "Calibri"
p.font.size = Pt(14)
p.font.color.rgb = RGBColor(0xDD, 0xDD, 0xDD)
p.space_before = Pt(16)

# ------------------------------------------------------------------------------
# SLIDE 2: EXECUTIVE SUMMARY & NARRATIV
# ------------------------------------------------------------------------------
s2 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s2, "Påløpte kostnader har nådd NOK 58,0M — total finansiell eksponering utgjør 536% av budsjett")

# Left Column: KPI Cards
kpis_s2 = [
    ("Budsjett (BAC)", "20,0 MNOK", "Styrets vedtatte ramme", COLOR_NAVY),
    ("Faktisk Kost (AC)", "57,97 MNOK", "+189,8% overskridelse", COLOR_ALERT),
    ("Opptjent Verdi (EV)", "19,22 MNOK", "CPI: 0,33 | SPI: 1,16", COLOR_ALERT),
    ("Åpne Forpliktelser", "49,23 MNOK", "Ufakturerte leverandør-PO", COLOR_AMBER),
    ("Samlet Eksponering", "107,20 MNOK", "536% av totalbudsjett", COLOR_ALERT),
    ("Balanseført AuC", "43,38 MNOK", "Akutt IAS 36 nedskrivningsrisiko", COLOR_NAVY),
]

for idx, (title, val, sub, col) in enumerate(kpis_s2):
    r = idx // 2
    c = idx % 2
    x = Inches(0.8) + c * Inches(2.9)
    y = Inches(1.7) + r * Inches(1.6)
    
    card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(2.75), Inches(1.4))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD_BG
    card.line.color.rgb = RGBColor(0xDC, 0xE6, 0xF1)
    
    ctf = card.text_frame
    ctf.word_wrap = True
    ctf.margin_top = ctf.margin_left = Inches(0.12)
    
    cp0 = ctf.paragraphs[0]
    cp0.text = title.upper()
    cp0.font.size = Pt(9.5)
    cp0.font.bold = True
    cp0.font.color.rgb = COLOR_TEXT_MUTED
    
    cp1 = ctf.add_paragraph()
    cp1.text = val
    cp1.font.size = Pt(17)
    cp1.font.bold = True
    cp1.font.color.rgb = col
    cp1.space_before = Pt(3)
    
    cp2 = ctf.add_paragraph()
    cp2.text = sub
    cp2.font.size = Pt(8.5)
    cp2.font.color.rgb = COLOR_TEXT_MUTED

# Right Column: Executive Narrative Box
callout = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.0))
callout.fill.solid()
callout.fill.fore_color.rgb = RGBColor(0xFD, 0xED, 0xEC)
callout.line.color.rgb = COLOR_ALERT

ctf2 = callout.text_frame
ctf2.word_wrap = True
ctf2.margin_left = ctf2.margin_right = ctf2.margin_top = Inches(0.25)

p = ctf2.paragraphs[0]
p.text = "RØD ALARM: KRITISK KONTROLLER-SYNTESE (Per 31.10.2026)"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_ALERT

narrative_points = [
    ("1. DIAGNOSE (EVM):", "Prosjektet opererer med en kostnadseffektivitet på CPI 0,33 og et akkumulert kostnadsavvik på NOK -38,8M. Fysisk fremdrift meldes til SPI 1,16 som følge av forsert reaktormontasje."),
    ("2. DRIVER & LIKVIDITET:", "Bokførte kostnader (NOK 58,0M) pluss åpne innkjøpsordrer (NOK 49,2M) gir en samlet finansiell forpliktelse på NOK 107,2M (536% av budsjett)."),
    ("3. IFRS REGNSKAPSRISIKO:", "Av bokførte kostnader er NOK 43,4M balanseført som AuC under IAS 38. Eksploderende sluttkostnad (EAC 60,3M-107M) utløser akutt krav om nedskrivningstest etter IAS 36 før årsoppgjøret."),
    ("4. PÅBUD TIL STYRET:", "1) Umiddelbar innkjøpsfrys på alle nye rekvisisjoner. 2) Kanselleringsaudit av uleverte PO-er (49,2M). 3) 30 dagers Technical Hold for fullstendig levedyktighetsanalyse.")
]

for title, desc in narrative_points:
    p = ctf2.add_paragraph()
    p.text = title
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_NAVY
    p.space_before = Pt(8)
    
    p_body = ctf2.add_paragraph()
    p_body.text = desc
    p_body.font.size = Pt(9.5)
    p_body.font.color.rgb = COLOR_TEXT_MAIN

# ------------------------------------------------------------------------------
# SLIDE 3: EVM S-CURVE & POINT OF DIVERGENCE
# ------------------------------------------------------------------------------
s3 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s3, "Kostnadskontrollen kollapset i Q1: AC eksploderte til 58,0M mot 19,2M i EV")

s3.shapes.add_picture(p_chart1, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))

# Sidepanel tekst
tb3 = s3.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf3 = tb3.text_frame
tf3.word_wrap = True

p = tf3.paragraphs[0]
p.text = "Funn fra S-Kurven"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY

bullets3 = [
    "Klassisk forseringsmønster: Prosjektet holdt tidsplanen (SPI 1,16) utelukkende ved massiv innleie, overtid og parallelle innkjøp.",
    "Mars 2026 vendepunktet: Akkumulerte forpliktelser (PO) nådde 29,8M (149% av BAC). Her burde en automatisk innkjøpsfrys ha slått inn.",
    "Sviktende kostnadseffektivitet: For hver 1,00 krone Elkem brukte, ble det kun skapt 33 øre i fysisk anleggsverdi (CPI: 0,33).",
    "Kostnadsavviket: CV har nådd NOK -38,75M, og gapet fortsetter å vide seg ut mot ferdigstillelse."
]
for b in bullets3:
    p = tf3.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE 4: THE EXPOSURE ICEBERG (WATERFALL)
# ------------------------------------------------------------------------------
s4 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s4, "Forpliktelsesisberget: 49,2M i åpne PO-er løfter samlet finansiell eksponering til 107,2M")

s4.shapes.add_picture(p_chart2, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))

tb4 = s4.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf4 = tb4.text_frame
tf4.word_wrap = True

p = tf4.paragraphs[0]
p.text = "Dekomponering av Forpliktelser"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY

bullets4 = [
    "WBS-300 Reaktor er hovedsynderen: Alene ansvarlig for NOK 15,2M i budsjettoverskridelse, drevet av uregulerte endringsordrer.",
    "Åpne PO-forpliktelser (49,23M): Kontraktsfestede bestillinger som er sendt til leverandører, men ennå ikke fakturert i regnskapet.",
    "Tradisjonell regnskapsfelle: Fordi hovedboken bare viste 58M i AC, trodde ledelsen at prosjektet nærmet seg slutten. Reell forpliktelse er 107,2M.",
    "EAC Fremskriving: Hvis uleverte PO-er fullføres, ender piloten på over 107M — 5,3 ganger godkjent ramme."
]
for b in bullets4:
    p = tf4.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE 5: LIKVIDITETSGAP & WORKING CAPITAL
# ------------------------------------------------------------------------------
s5 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s5, "Likviditetsgapet: Kontantutbetalingene nådde 14,5M/mnd mens Enova-tilskudd var begrenset til 3,0M")

s5.shapes.add_picture(p_chart3, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))

tb5 = s5.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf5 = tb5.text_frame
tf5.word_wrap = True

p = tf5.paragraphs[0]
p.text = "Likviditets- og Tilskuddsrisiko"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY

bullets5 = [
    "DPO Forskyvning: 30 dagers leverandørkreditt skapte en illusjon av god likviditet i Q1, før betalingsbølgen traff med full tyngde i august-oktober.",
    "Enova Transje 1: Kun 3,0 MNOK ble utbetalt i juni. Resterende 7,0 MNOK krever oppnådde milepæler og revisorattesterte sluttrapporter.",
    "Arbeidskapitaldrenering: Elkem har måttet forskuttere over NOK 54M i ren kontantstrøm for å dekke løpende leverandørkrav.",
    "Refusjonsfare: Ved manglende idriftsettelse eller brudd på tilskuddsvilkår kan Enova stanse fremtidige utbetalinger eller kreve tilbakebetaling."
]
for b in bullets5:
    p = tf5.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE 6: FISKÅ ENHETER & REVISJONSSPOR (ISA 805)
# ------------------------------------------------------------------------------
s6 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s6, "CC-4300 Prosjektledelse og CC-4100 Drift bar tyngden av forseringen — 12 320 timer totalt")

s6.shapes.add_picture(p_chart4, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))

tb6 = s6.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf6 = tb6.text_frame
tf6.word_wrap = True

p = tf6.paragraphs[0]
p.text = "Enhetskontroll & Revisjonskrav"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY

bullets6 = [
    "1 537 timelister avstemt: Samtlige timer er kontrollert mot SkatteFUNN- og Forskningsrådets tak på 530 kr/t (totalt NOK 6,53M).",
    "Uforholdsmessig møtetid: CC-4300 (PMO/Adm) brukte 4 320 timer — en unormalt høy andel forårsaket av krisehåndtering og leverandørkonflikter.",
    "Overtid på piloten: CC-4100 loggførte 4 200 timer under forsering av mekanisk montering i Bygg 12.",
    "Revisorkrav (ISA 805): Ekstern revisor krever dokumentert timeliste-til-hovedbok sporbarhet for at timene skal godkjennes av tilskuddsgiver."
]
for b in bullets6:
    p = tf6.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE 7: IFRS IAS 38 vs IAS 36 IMPAIRMENT
# ------------------------------------------------------------------------------
s7 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s7, "Balanseført AuC på 43,4M trues av 100% nedskrivningstap ved prosjektterminering")

s7.shapes.add_picture(p_chart5, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))

tb7 = s7.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf7 = tb7.text_frame
tf7.word_wrap = True

p = tf7.paragraphs[0]
p.text = "IFRS Regnskapskonsekvenser"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY

bullets7 = [
    "IAS 38 Allokering: Av 58,0M i faktiske kostnader er 43,38M balanseført som AuC, mens 14,59M er kostnadsført over P&L som forskning.",
    "Eksploderende sluttkostnad (EAC): Med forventet totalkostnad på over 107M vil anlegget aldri oppnå tilstrekkelig avkastning til å forsvare balanseverdien.",
    "Obligatorisk IAS 36 test: Revisor vil kreve formell verdifallstest før årsoppgjøret 2026.",
    "Resultatsmell: Hvis prosjektet stanses (Off-Ramp), må samtlige NOK 43,4M i AuC tapsføres umiddelbart som en engangsnedskrivning i Q4."
]
for b in bullets7:
    p = tf7.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE 8: STYRETS BESLUTNINGSMATRISE (ACTION / GOVERNANCE)
# ------------------------------------------------------------------------------
s8 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s8, "Styrets to handlingsvalg: 30 dagers Technical Hold vs. Formell Off-Ramp", "STRATEGISK BESLUTNING — VEDTAKSSAK")

# Alternativ A Card
cardA = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2))
cardA.fill.solid()
cardA.fill.fore_color.rgb = RGBColor(0xF0, 0xF4, 0xF8)
cardA.line.color.rgb = COLOR_NAVY
cardA.line.width = Pt(1.5)

tfA = cardA.text_frame
tfA.word_wrap = True
tfA.margin_left = tfA.margin_right = tfA.margin_top = Inches(0.25)

p = tfA.paragraphs[0]
p.text = "ALTERNATIV A: 30 DAGERS TECHNICAL HOLD"
p.font.bold = True
p.font.size = Pt(13)
p.font.color.rgb = COLOR_NAVY

p_sub = tfA.add_paragraph()
p_sub.text = "ANBEFALT AV PROSJEKTCONTROLLER"
p_sub.font.bold = True
p_sub.font.size = Pt(9.5)
p_sub.font.color.rgb = COLOR_AMBER

pointsA = [
    ("1. Umiddelbar innkjøpsfrys:", "Stans all fullmakt til nye innkjøpsordrer (PO) med umiddelbar virkning."),
    ("2. Kanselleringsaudit av PO:", "Gjennomgå samtlige åpne forpliktelser (49,2M). Kanseller uleverte ordrer for å begrense kontanttapet."),
    ("3. Teknisk Scope-Reduction:", "Nedskaler anlegget til minimum levedyktig pilot (MVP) for å redusere gjenstående montasje."),
    ("4. Enova Forhandling:", "Be om omforhandling av prosjektplan og milepæler for å redde resterende 7,0M i tilskudd.")
]
for t, d in pointsA:
    p = tfA.add_paragraph()
    p.text = t
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)
    p2 = tfA.add_paragraph()
    p2.text = d
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = COLOR_TEXT_MUTED

# Alternativ B Card
cardB = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.2))
cardB.fill.solid()
cardB.fill.fore_color.rgb = RGBColor(0xFD, 0xED, 0xEC)
cardB.line.color.rgb = COLOR_ALERT
cardB.line.width = Pt(1.5)

tfB = cardB.text_frame
tfB.word_wrap = True
tfB.margin_left = tfB.margin_right = tfB.margin_top = Inches(0.25)

p = tfB.paragraphs[0]
p.text = "ALTERNATIV B: FORMELL OFF-RAMP (PROSJEKTSTANS)"
p.font.bold = True
p.font.size = Pt(13)
p.font.color.rgb = COLOR_ALERT

p_sub = tfB.add_paragraph()
p_sub.text = "KONSEKVENS: FULL NEDSKRIVNING"
p_sub.font.bold = True
p_sub.font.size = Pt(9.5)
p_sub.font.color.rgb = COLOR_ALERT

pointsB = [
    ("1. Umiddelbar prosjektstans:", "Avbryt alt arbeid på Bygg 12 og permitter innleide konsulenter og entreprenører."),
    ("2. Kontraktsforhandlinger:", "Maksimal juridisk begrensning av kanselleringsgebyrer på åpne PO-er (forventet tap 10-15M)."),
    ("3. IFRS IAS 36 Nedskrivning:", "Umiddelbar tapsføring av samtlige NOK 43,4M i balanseført AuC i Q4 2026 regnskapet."),
    ("4. Tilskuddsavregning:", "Risiko for at Enova krever tilbakebetalt de 3,0 MNOK som ble utbetalt i juni.")
]
for t, d in pointsB:
    p = tfB.add_paragraph()
    p.text = t
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)
    p2 = tfB.add_paragraph()
    p2.text = d
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = COLOR_TEXT_MUTED

output_pptx_path = os.path.join(OUTPUT_DIR, "GreenPilot_2026_Board_Deck.pptx")
prs.save(output_pptx_path)
print(f" [OK] PowerPoint generert: {output_pptx_path}")

# ==============================================================================
# 3. GENERER FORMELT PDF-STYRENOTAT (REPORTLAB)
# ==============================================================================
print("\n--- [3/3] Bygger Formelt Styrenotat i PDF (ReportLab) ---")

output_pdf_path = os.path.join(OUTPUT_DIR, "GreenPilot_2026_Board_Memo.pdf")
doc = SimpleDocTemplate(
    output_pdf_path,
    pagesize=A4,
    leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40
)

styles = getSampleStyleSheet()

# Egendefinerte stiler
style_title = ParagraphStyle(
    "DocTitle",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=24,
    textColor=colors.HexColor("#1F4E79")
)

style_subtitle = ParagraphStyle(
    "DocSub",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=10,
    leading=14,
    textColor=colors.HexColor("#555555")
)

style_h2 = ParagraphStyle(
    "SectionH2",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=16,
    textColor=colors.HexColor("#1F4E79"),
    spaceBefore=14,
    spaceAfter=6
)

style_body = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=13,
    textColor=colors.HexColor("#222222")
)

style_alert_box = ParagraphStyle(
    "AlertBox",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=12,
    textColor=colors.HexColor("#C00000")
)

story = []

# Header
story.append(Paragraph("ELKEM TECHNOLOGY — SAK FOR PROSJEKTSTYRET", style_title))
story.append(Paragraph("Dato: 12. november 2026 | Cut-off regnskap: 31.10.2026 | Saksansvarlig: Prosjektcontroller", style_subtitle))
story.append(Spacer(1, 10))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1F4E79"), spaceAfter=12))

# Executive Box
exec_text = """<b>VEDTAKSSAK: KRITISK STATUSVURDERING & STAGE-GATE 3 BESLUTNING</b><br/>
GreenPilot 2026 har overskredet sitt styrevedtatte baseline-budsjett (BAC 20,0 MNOK) med +189,8% i bokførte kostnader (AC: 57,97 MNOK). 
Samtidig utgjør uleverte leverandørforpliktelser (PO) hele 49,23 MNOK, noe som gir en samlet finansiell eksponering på <b>107,20 MNOK (536% av budsjett)</b>. 
Prosjektcontroller anbefaler at styret fatter vedtak om <b>30 dagers Technical Hold</b> og umiddelbar innkjøpsfrys fremfor ukontrollert videreføring.
"""
t_exec = Table([[Paragraph(exec_text, style_alert_box)]], colWidths=[515])
t_exec.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FDEDEC")),
    ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor("#C00000")),
    ('PADDING', (0,0), (-1,-1), 8),
]))
story.append(t_exec)
story.append(Spacer(1, 12))

# 1. Hovedtall
story.append(Paragraph("1. Finansiell og Operasjonell Hovedstatus (EVM Status per 31.10.2026)", style_h2))

table_data = [
    [Paragraph("<b>Metrikk</b>", style_body), Paragraph("<b>Verdi</b>", style_body), Paragraph("<b>Status</b>", style_body), Paragraph("<b>Vurdering / Avvik</b>", style_body)],
    ["Totalbudsjett (BAC)", "NOK 20,00M", "Baseline", "Vedtatt ramme for pilotprosjektet ved Elkem Fiskå"],
    ["Faktisk Påløpt Kostnad (AC)", "NOK 57,97M", "RØD", "Kostnadsoverskridelse på +37,97 MNOK (+189,8%)"],
    ["Opptjent Verdi (EV)", "NOK 19,22M", "RØD", "96,1% fysisk ferdigstillelse; alvorlig kostnadsineffektivitet"],
    ["Cost Performance Index (CPI)", "0,331", "RØD", "For hver krone brukt skapes kun 33 øre i fysisk anleggsverdi"],
    ["Schedule Performance Index (SPI)", "1,156", "GRØNN", "Raskere fremdrift pga. forsert mekanisk montasje"],
    ["Åpne Innkjøpsforpliktelser (PO)", "NOK 49,23M", "RØD", "Uavstemte forpliktelser som aldri ble fanget opp av fakturakontroll"],
    ["Samlet Finansiell Eksponering", "NOK 107,20M", "RØD", "Reell kontant- og forpliktelsesbelastning (536% av budsjett)"],
    ["Balanseført AuC (IAS 38)", "NOK 43,38M", "VARSEL", "Anlegg under utførelse; akutt IAS 36 nedskrivningsrisiko"],
    ["Offentlig Tilskudd (Enova)", "NOK 3,00M", "Utbetalt", "Transje 1 mottatt; resterende 7,0M i fare ved terminering"],
]

t_metrics = Table(table_data, colWidths=[140, 75, 55, 245])
t_metrics.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2F5496")),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D9D9D9")),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9FAFB")]),
    ('PADDING', (0,0), (-1,-1), 4),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t_metrics)
story.append(Spacer(1, 14))

# Visuals Section: S-Curve
story.append(Paragraph("2. Analyse av Kostnadsutvikling og Divergens (EVM S-Kurve)", style_h2))
story.append(Paragraph("Grafen nedenfor illustrerer hvordan kostnadskontrollen glapp i Q1 2026. Fra mars 2026 skilte faktisk kostnad (AC) lag med opptjent verdi (EV).", style_body))
story.append(Spacer(1, 6))
story.append(RLImage(p_chart1, width=500, height=240))
story.append(Spacer(1, 14))

# Page Break til side 2
story.append(PageBreak())

# Visual 2: Waterfall
story.append(Paragraph("3. Forpliktelsesisberget: Påløpte Kostnader vs. Åpne Ordrer", style_h2))
story.append(Paragraph("Årsaken til at prosjektledelsen ikke slo alarm tidligere, var at rapporteringen utelukkende fokuserte på bokførte fakturaer (58M), mens 49,2M lå skjult i åpne innkjøpsordrer.", style_body))
story.append(Spacer(1, 6))
story.append(RLImage(p_chart2, width=500, height=230))
story.append(Spacer(1, 14))

# Visual 3: Likviditetsbro
story.append(Paragraph("4. Likviditetsgap og Arbeidskapitalbinding (Cash Flow Bridge)", style_h2))
story.append(Paragraph("Med 30 dagers leverandørkreditt (DPO) ble kontantbelastningen skjøvet ut i tid, før den kulminerte med opptil 14,5 MNOK/mnd i september og oktober 2026.", style_body))
story.append(Spacer(1, 6))
story.append(RLImage(p_chart3, width=500, height=230))
story.append(Spacer(1, 14))

# Page Break til side 3
story.append(PageBreak())

# Visual 4 & 5: Fiskå og IFRS
story.append(Paragraph("5. Enhetsbelastning på Elkem Fiskå og IFRS IAS 36 Nedskrivningsrisiko", style_h2))
story.append(RLImage(p_chart4, width=500, height=210))
story.append(Spacer(1, 10))
story.append(RLImage(p_chart5, width=500, height=220))
story.append(Spacer(1, 14))

# Beslutningsanbefaling
story.append(Paragraph("6. Controllerens Anbefaling og Vedtaksforslag", style_h2))
decision_text = """<b>Styret inviteres til å fatte følgende vedtak:</b><br/>
1. <b>Innkjøpsfrys:</b> Det innføres øyeblikkelig frys for alle nye innkjøpsrekvisisjoner og bestillinger knyttet til prosjekt GreenPilot 2026.<br/>
2. <b>Technical Hold:</b> Prosjektet settes i 30 dagers teknisk og finansiell pause for å gjennomføre en fullstendig kanselleringsaudit av åpne forpliktelser (49,2M).<br/>
3. <b>Enova-dialog:</b> Ledelsen gis fullmakt til å innlede samtaler med Enova for å avklare mulighetsrommet for revidert prosjektplan uten tap av tilskudd.<br/>
4. <b>Nedskrivningsvurdering:</b> Finansavdelingen utarbeider en formell IAS 36 verdifallstest for balanseført AuC (43,4M) i samråd med ekstern revisor (PwC).
"""
story.append(Paragraph(decision_text, style_body))

doc.build(story)
print(f" [OK] PDF Styrenotat generert: {output_pdf_path}")

print("=" * 80)
print("=== ALLE LEVERANSER VELLYKKET FULLFØRT ===")
print("=" * 80)
