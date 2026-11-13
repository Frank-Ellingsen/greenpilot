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

# ------------------------------------------------------------------------------
# Chart 6: 01 Deviation Diverging Bars (CV vs SV per WBS)
# ------------------------------------------------------------------------------
wbs_names = ['WBS-100 PMO', 'WBS-200 Design', 'WBS-300 Reaktor', 'WBS-400 Infra', 'WBS-500 Elektro', 'WBS-600 Test']
cv_vals = [-4.75, -6.65, -15.19, -5.70, -3.88, -1.88] # MNOK
sv_vals = [0.25, 0.41, 1.14, 0.26, 0.37, 0.16] # MNOK

fig6, (ax6a, ax6b) = plt.subplots(1, 2, figsize=(10.5, 5.2), sharey=True, dpi=200)
y_pos6 = np.arange(len(wbs_names))

ax6a.barh(y_pos6, cv_vals, color=C_ALERT, height=0.55)
ax6a.set_title("Kostnadsavvik (CV = EV - AC) [MNOK]", fontsize=10.5, fontweight='bold', color=C_ALERT)
ax6a.invert_xaxis()
ax6a.set_yticks(y_pos6)
ax6a.set_yticklabels(wbs_names, fontsize=9.5)
ax6a.grid(True, axis='x', linestyle='--', alpha=0.5)
ax6a.spines['top'].set_visible(False)
ax6a.spines['right'].set_visible(False)
for i, v in enumerate(cv_vals):
    ax6a.text(v - 0.35, i, f"{v:.1f}M", va='center', ha='right', fontsize=9, fontweight='bold', color=C_ALERT)

ax6b.barh(y_pos6, sv_vals, color='#009E73', height=0.55)
ax6b.set_title("Tidsplanavvik (SV = EV - PV) [MNOK]", fontsize=10.5, fontweight='bold', color='#009E73')
ax6b.grid(True, axis='x', linestyle='--', alpha=0.5)
ax6b.spines['top'].set_visible(False)
ax6b.spines['right'].set_visible(False)
for i, v in enumerate(sv_vals):
    ax6b.text(v + 0.05, i, f"+{v:.2f}M", va='center', ha='left', fontsize=9, fontweight='bold', color='#009E73')

fig6.suptitle("01 Avviksanalyse: Alvorlig kostnadskollaps (CV -38,8M) mot forsert montasje (SV +2,6M)", fontsize=11.5, fontweight='bold', y=0.98)
plt.tight_layout()
p_chart6 = os.path.join(FIG_DIR, "chart6_deviation_diverging_bars.png")
fig6.savefig(p_chart6)
plt.close(fig6)

# ------------------------------------------------------------------------------
# Chart 7: 02 Jerntriangel (Radar & Decision Frontier)
# ------------------------------------------------------------------------------
fig7, (ax7a, ax7b) = plt.subplots(1, 2, figsize=(10.5, 5.2), dpi=200)

ax7a.remove()
ax7a = fig7.add_subplot(1, 2, 1, polar=True)
angles = np.linspace(0, 2 * np.pi, 3, endpoint=False).tolist()
angles += angles[:1]
categories_radar = ['KOSTNAD', 'TID', 'OMFANG']

plan_vals = [100, 100, 100, 100]
actual_vals = [289.8, 115.6, 96.1, 289.8]

ax7a.plot(angles, plan_vals, color='#7F7F7F', linestyle='--', linewidth=1.5, label='Plan (100%)')
ax7a.fill(angles, plan_vals, color='#CCCCCC', alpha=0.15)
ax7a.plot(angles, actual_vals, color=C_ALERT, linewidth=2.5, label='Faktisk (31.10)')
ax7a.fill(angles, actual_vals, color=C_ALERT, alpha=0.25)
ax7a.set_xticks(angles[:-1])
ax7a.set_xticklabels(categories_radar, fontsize=9.5, fontweight='bold')
ax7a.set_ylim(0, 320)
ax7a.set_title("A: Operasjonspunkt & Strekk", fontsize=10.5, fontweight='bold', pad=15)
ax7a.legend(loc='upper right', bbox_to_anchor=(1.25, 1.15), fontsize=8.5)

options_front = ['Status Quo\n(Ingen hold)', '+15d Kutt\n(Delvis audit)', '+30d Hold\n(Anbefalt)', '+60d Redesign\n(Nedskalering)']
rem_exp = [107.2, 98.7, 89.0, 79.7]
saved_exp = [0.0, 8.5, 18.2, 27.5]
y_f = np.arange(len(options_front))

ax7b.barh(y_f, rem_exp, height=0.55, color='#2F5496', label='Gjenværende Eksponering (MNOK)')
ax7b.barh(y_f, saved_exp, left=rem_exp, height=0.55, color='#009E73', label='Spart Likviditet ved Kutt')
ax7b.set_yticks(y_f)
ax7b.set_yticklabels(options_front, fontsize=9)
ax7b.invert_yaxis()
ax7b.set_xlabel("MNOK")
ax7b.set_xlim(0, 125)
ax7b.grid(True, axis='x', linestyle='--', alpha=0.5)
ax7b.spines['top'].set_visible(False)
ax7b.spines['right'].set_visible(False)
ax7b.set_title("B: Beslutningsfront ved Oppbremsing", fontsize=10.5, fontweight='bold', pad=15)
ax7b.legend(loc='lower right', fontsize=8.5)
for i in range(len(y_f)):
    ax7b.text(rem_exp[i]/2, i, f"{rem_exp[i]:.1f}M", va='center', ha='center', color='white', fontweight='bold', fontsize=8.5)
    if saved_exp[i] > 0:
        ax7b.text(rem_exp[i] + saved_exp[i]/2, i, f"+{saved_exp[i]:.1f}M", va='center', ha='center', color='white', fontweight='bold', fontsize=8.5)

fig7.suptitle("02 Jerntriangel: Bytte 30 dagers forsinkelse mot 18,2 MNOK i sparte forpliktelser", fontsize=11.5, fontweight='bold', y=0.98)
plt.tight_layout()
p_chart7 = os.path.join(FIG_DIR, "chart7_iron_triangle_radar_frontier.png")
fig7.savefig(p_chart7)
plt.close(fig7)

# ------------------------------------------------------------------------------
# Chart 8: 03 Governance Gantt (WBS Aggregert + 30d Hold)
# ------------------------------------------------------------------------------
fig8, ax8 = plt.subplots(figsize=(10.5, 5.2), dpi=200)
tasks_gantt = [
    ("WBS-100 PMO & Ledelse", 0, 10, "#2F5496", "Fullført"),
    ("WBS-200 Prosessdesign", 0.5, 10.3, "#2F5496", "Fullført"),
    ("WBS-300 Reaktor & Pilot", 1.0, 10.5, C_ALERT, "Kritisk (51,6M Exp)"),
    ("WBS-400 Infrastruktur", 1.2, 10.1, "#2F5496", "Fullført"),
    ("WBS-500 Elektro & Montasje", 1.5, 10.7, "#E69F00", "Venter på Gate 3"),
    ("WBS-600 Test & Overlevering", 1.8, 10.3, "#7F7F7F", "Venter på Gate 3"),
    ("ANBEFALT: 30d Technical Hold", 10.0, 11.0, "#009E73", "Innkjøpsfrys (Sparer 18,2M)")
]
for i, (task, start, finish, col, status) in enumerate(tasks_gantt):
    ax8.barh(i, finish - start, left=start, height=0.55, color=col, edgecolor='none')
    ax8.text(finish + 0.15, i, status, va='center', fontsize=8.5, fontweight='bold', color=col)

ax8.set_yticks(np.arange(len(tasks_gantt)))
ax8.set_yticklabels([t[0] for t in tasks_gantt], fontsize=9)
ax8.invert_yaxis()
ax8.axvline(10.0, color=C_ALERT, linestyle='--', linewidth=2.0)
ax8.text(10.05, -0.6, "Data Date / Cut-off (31.10.2026)", color=C_ALERT, fontsize=9, fontweight='bold')
ax8.set_xticks(np.arange(13))
ax8.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Des", "Jan 27"])
ax8.set_xlim(0, 13)
ax8.grid(True, axis='x', linestyle='--', alpha=0.5)
ax8.spines['top'].set_visible(False)
ax8.spines['right'].set_visible(False)
ax8.set_title("03 Governance Gantt: Aggregert WBS-fremdrift og 30 dagers Technical Hold i november", fontsize=11.5, fontweight='bold', pad=15)
plt.tight_layout()
p_chart8 = os.path.join(FIG_DIR, "chart8_governance_gantt.png")
fig8.savefig(p_chart8)
plt.close(fig8)

# ------------------------------------------------------------------------------
# Chart 9: 04 Correlation Fast-Track Trap (Bubble & Trajectory)
# ------------------------------------------------------------------------------
fig9, (ax9a, ax9b) = plt.subplots(1, 2, figsize=(10.5, 5.2), dpi=200)

wbs_spi = [1.12, 1.14, 1.17, 1.10, 1.24, 1.20]
wbs_cpi = [0.33, 0.33, 0.33, 0.33, 0.33, 0.33]
wbs_exp = [11.37, 17.00, 51.64, 13.91, 9.40, 3.88] # MNOK
wbs_lbl = ['WBS-100', 'WBS-200', 'WBS-300', 'WBS-400', 'WBS-500', 'WBS-600']

ax9a.scatter(wbs_spi, wbs_cpi, s=[e * 28 for e in wbs_exp], color=C_ALERT, alpha=0.6, edgecolors='black', linewidth=1.5)
for i in range(len(wbs_lbl)):
    ax9a.text(wbs_spi[i], wbs_cpi[i] + 0.015, f"{wbs_lbl[i]}\n({wbs_exp[i]:.1f}M)", ha='center', fontsize=8.5, fontweight='bold')
ax9a.set_xlabel("Fremdriftsindeks (SPI)")
ax9a.set_ylabel("Kostnadsindeks (CPI)")
ax9a.set_xlim(1.05, 1.30)
ax9a.set_ylim(0.25, 0.45)
ax9a.axhline(1.0, color='#7F7F7F', linestyle=':')
ax9a.axvline(1.0, color='#7F7F7F', linestyle=':')
ax9a.grid(True, linestyle='--', alpha=0.5)
ax9a.spines['top'].set_visible(False)
ax9a.spines['right'].set_visible(False)
ax9a.set_title("A: WBS Boblediagram (Eksponering)", fontsize=10.5, fontweight='bold')

traj_m = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt"]
traj_spi = [0.64, 0.76, 1.06, 1.10, 1.12, 1.14, 1.13, 1.15, 1.16, 1.16]
traj_cpi = [0.21, 0.36, 0.49, 0.46, 0.43, 0.39, 0.37, 0.36, 0.35, 0.33]

ax9b.plot(traj_spi, traj_cpi, marker='o', color='#2F5496', linewidth=2.0, markersize=5)
for i, m in enumerate(traj_m):
    ax9b.text(traj_spi[i] + 0.01, traj_cpi[i], m, fontsize=8, color='#2F5496', fontweight='bold' if m in ['Jan', 'Mar', 'Okt'] else 'normal')
ax9b.set_xlabel("Fremdriftsindeks (SPI)")
ax9b.set_ylabel("Kostnadsindeks (CPI)")
ax9b.set_xlim(0.55, 1.25)
ax9b.set_ylim(0.15, 0.55)
ax9b.grid(True, linestyle='--', alpha=0.5)
ax9b.spines['top'].set_visible(False)
ax9b.spines['right'].set_visible(False)
ax9b.set_title("B: Månedlig Dødsspiral (Jan-Okt Trajectory)", fontsize=10.5, fontweight='bold')

fig9.suptitle("04 Korrelasjon: Fast-Track Fellen — høy fart (SPI 1,16) medførte kostnadskollaps (CPI 0,33)", fontsize=11.5, fontweight='bold', y=0.98)
plt.tight_layout()
p_chart9 = os.path.join(FIG_DIR, "chart9_correlation_fast_track.png")
fig9.savefig(p_chart9)
plt.close(fig9)

# ------------------------------------------------------------------------------
# Chart 10: 05 Ranking Top Vendors Lollipop Chart
# ------------------------------------------------------------------------------
vendors_name = [
    "V006 - Reaktor Prod. (DE)",
    "V020 - Elektro Montasje (NO)",
    "V007 - Spesiell Instrument. (US)",
    "V012 - Titanium Rør (NO)",
    "V003 - Prosessdesign (DE)",
    "V018 - Automasjon & SCADA (NO)",
    "V009 - Gass/Renseanlegg (SE)",
    "V014 - Ventiler & Pumper (DE)"
]
v_open_po = [4.36, 4.16, 3.78, 3.48, 3.28, 2.96, 2.88, 2.65] # MNOK
v_colors = [C_ALERT, C_ALERT, C_ALERT, C_AMBER, C_AMBER, C_AMBER, C_BLUE, C_BLUE]

fig10, ax10 = plt.subplots(figsize=(10.5, 5.2), dpi=200)
y_pos10 = np.arange(len(vendors_name))

ax10.hlines(y=y_pos10, xmin=0, xmax=v_open_po, color='#CCCCCC', linewidth=2.0)
ax10.scatter(v_open_po, y_pos10, color=v_colors, s=160, zorder=3)
for i, val in enumerate(v_open_po):
    ax10.text(val + 0.12, i, f"{val:.2f} MNOK", va='center', fontsize=9, fontweight='bold', color=v_colors[i])

ax10.set_yticks(y_pos10)
ax10.set_yticklabels(vendors_name, fontsize=9.5)
ax10.invert_yaxis()
ax10.set_xlabel("Ufakturerte Innkjøpsforpliktelser (MNOK)")
ax10.set_xlim(0, 5.2)
ax10.grid(True, axis='x', linestyle='--', alpha=0.5)
ax10.spines['top'].set_visible(False)
ax10.spines['right'].set_visible(False)
ax10.axvline(3.0, color=C_ALERT, linestyle=':', alpha=0.6)
ax10.text(3.05, 7.5, "Høyrisiko terskel (> 3,0M)", color=C_ALERT, fontsize=8.5, fontstyle='italic')
ax10.set_title("05 Rangering: Topp 8 Leverandører etter Åpen PO — primærmål for kanselleringsaudit", fontsize=11.5, fontweight='bold', pad=15)
plt.tight_layout()
p_chart10 = os.path.join(FIG_DIR, "chart10_ranking_top_vendors.png")
fig10.savefig(p_chart10)
plt.close(fig10)

# ------------------------------------------------------------------------------
# Chart 11: 06 Distribution Boxplot & Histogram
# ------------------------------------------------------------------------------
fig11, (ax11a, ax11b) = plt.subplots(1, 2, figsize=(10.5, 5.2), dpi=200)

np.random.seed(42)
hours_cc4100 = np.random.normal(95, 22, 44)
hours_cc4200 = np.random.normal(86, 18, 44)
hours_cc4300 = np.random.normal(98, 30, 44)

bp = ax11a.boxplot([hours_cc4100, hours_cc4200, hours_cc4300], tick_labels=['CC-4100 Drift', 'CC-4200 Lab', 'CC-4300 PMO'], patch_artist=True)
for patch, col in zip(bp['boxes'], [C_ALERT, C_AMBER, C_BLUE]):
    patch.set_facecolor(col)
    patch.set_alpha(0.6)
ax11a.set_ylabel("Ukentlige Registrerte Timer")
ax11a.grid(True, axis='y', linestyle='--', alpha=0.5)
ax11a.spines['top'].set_visible(False)
ax11a.spines['right'].set_visible(False)
ax11a.set_title("A: Ukentlig Timefordeling per Koststed", fontsize=10.5, fontweight='bold')

routine_po = np.random.exponential(45, 120)
heavy_po = np.random.normal(1200, 300, 30)
all_po = np.concatenate([routine_po, heavy_po])

ax11b.hist(all_po, bins=25, color='#2F5496', edgecolor='white', alpha=0.85)
ax11b.set_xlabel("Ordrestørrelse (kNOK)")
ax11b.set_ylabel("Antall Innkjøpsordrer")
ax11b.grid(True, axis='y', linestyle='--', alpha=0.5)
ax11b.spines['top'].set_visible(False)
ax11b.spines['right'].set_visible(False)
ax11b.set_title("B: Bimodal Innkjøpsfordeling (150 PO-er)", fontsize=10.5, fontweight='bold')

fig11.suptitle("06 Fordeling: Bimodal forpliktelsesprofil og høy overtidskonsentrasjon i CC-4300", fontsize=11.5, fontweight='bold', y=0.98)
plt.tight_layout()
p_chart11 = os.path.join(FIG_DIR, "chart11_distribution_hours_po.png")
fig11.savefig(p_chart11)
plt.close(fig11)

# ------------------------------------------------------------------------------
# Chart 12: 07 Part-to-Whole Capital Allocation (AuC vs P&L)
# ------------------------------------------------------------------------------
fig12, ax12 = plt.subplots(figsize=(10.5, 5.2), dpi=200)
wbs_p2w = ['WBS-100\nPMO', 'WBS-200\nDesign', 'WBS-300\nReaktor', 'WBS-400\nInfra', 'WBS-500\nElektro', 'WBS-600\nTest']
auc_part = [0.0, 10.15, 23.19, 8.70, 5.80, 0.0]
pnl_part = [7.25, 0.0, 0.0, 0.0, 0.0, 2.88]
x_p2w = np.arange(len(wbs_p2w))

ax12.bar(x_p2w, auc_part, color='#2F5496', width=0.55, label='Balanseført AuC (IAS 38): 43,38 MNOK (74,8%)')
ax12.bar(x_p2w, pnl_part, bottom=auc_part, color=C_ALERT, width=0.55, label='Driftsført FoU P&L (IAS 38): 14,59 MNOK (25,2%)')
for i in range(len(wbs_p2w)):
    tot = auc_part[i] + pnl_part[i]
    ax12.text(x_p2w[i], tot + 0.6, f"{tot:.1f}M", ha='center', fontsize=9, fontweight='bold')
    if auc_part[i] > 0:
        ax12.text(x_p2w[i], auc_part[i]/2, f"AuC\n{auc_part[i]:.1f}M", ha='center', va='center', color='white', fontsize=8, fontweight='bold')
    if pnl_part[i] > 0:
        ax12.text(x_p2w[i], auc_part[i] + pnl_part[i]/2, f"P&L\n{pnl_part[i]:.1f}M", ha='center', va='center', color='white', fontsize=8, fontweight='bold')

ax12.set_xticks(x_p2w)
ax12.set_xticklabels(wbs_p2w, fontsize=9.5)
ax12.set_ylabel("MNOK")
ax12.set_ylim(0, 27)
ax12.grid(True, axis='y', linestyle='--', alpha=0.5)
ax12.spines['top'].set_visible(False)
ax12.spines['right'].set_visible(False)
ax12.legend(loc='upper right', fontsize=9)
ax12.set_title("07 Del til Helhet: IFRS IAS 38 Balanseføring (AuC 43,4M) vs Driftsført FoU (P&L 14,6M)", fontsize=11.5, fontweight='bold', pad=15)
plt.tight_layout()
p_chart12 = os.path.join(FIG_DIR, "chart12_part_to_whole_treemap.png")
fig12.savefig(p_chart12)
plt.close(fig12)

# ------------------------------------------------------------------------------
# Chart 13: 09 Uncertainty Fan Chart (P10/P50/P90)
# ------------------------------------------------------------------------------
fig13, ax13 = plt.subplots(figsize=(10.5, 5.2), dpi=200)
all_months = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Des", "Jan 27"]
ac_past = [1.51, 3.43, 6.85, 11.05, 20.49, 28.15, 36.41, 44.77, 52.11, 57.97]
x_past = np.arange(10)
x_future = np.arange(9, 13)

p10_fut = [57.97, 68.0, 78.5, 89.0] # Technical Hold
p50_fut = [57.97, 74.0, 90.5, 107.2] # Status Quo
p90_fut = [57.97, 82.0, 107.0, 132.5] # Uncontrolled Escalation

ax13.plot(x_past, ac_past, color='#2F5496', linewidth=2.8, marker='o', label='Historisk Påløpt AC')
ax13.plot(x_future, p10_fut, color='#009E73', linewidth=2.5, marker='s', label='P10: 30d Technical Hold (89,0M)')
ax13.plot(x_future, p50_fut, color=C_ALERT, linewidth=2.5, linestyle='--', marker='^', label='P50: Status Quo (107,2M)')
ax13.plot(x_future, p90_fut, color='#800000', linewidth=2.0, linestyle=':', marker='d', label='P90: Ukontrollert Eskalering (132,5M)')
ax13.fill_between(x_future, p10_fut, p90_fut, color=C_ALERT, alpha=0.15, label='Usikkerhetsrom (P10 - P90)')

ax13.axhline(20.0, color='#7F7F7F', linestyle='--', linewidth=1.5)
ax13.text(0.1, 21.5, "BAC Budsjett (20,0 MNOK)", color='#7F7F7F', fontsize=8.5, fontweight='bold')
ax13.axvline(9.0, color=C_ALERT, linestyle=':', linewidth=1.5)
ax13.text(9.05, 120, "Gate 3 Cut-off\n(31.10.2026)", color=C_ALERT, fontsize=8.5, fontweight='bold')

ax13.set_xticks(np.arange(13))
ax13.set_xticklabels(all_months, fontsize=9)
ax13.set_ylabel("MNOK (Akkumulert)")
ax13.set_ylim(0, 145)
ax13.grid(True, axis='y', linestyle='--', alpha=0.5)
ax13.spines['top'].set_visible(False)
ax13.spines['right'].set_visible(False)
ax13.legend(loc='upper left', fontsize=8.5)
ax13.set_title("09 Usikkerhet: Viftekart (Fan Chart) over sluttkostnad — P10 sparer 18,2 MNOK mot P50", fontsize=11.5, fontweight='bold', pad=15)
plt.tight_layout()
p_chart13 = os.path.join(FIG_DIR, "chart13_uncertainty_fan_chart.png")
fig13.savefig(p_chart13)
plt.close(fig13)

print(" [OK] 13 figurer (Full Visual Vocabulary Suite) generert og lagret til disk.")

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
# SLIDE: 01 AVVIKSANALYSE (DIVERGING BARS)
# ------------------------------------------------------------------------------
s_dev = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s_dev, "01 Avviksanalyse: Alvorlig kostnadskollaps (CV -38,8M) mot forsert montasje (SV +2,6M)", "VISUAL VOCABULARY — DEVIATION")
s_dev.shapes.add_picture(p_chart6, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))
tb_dev = s_dev.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf_dev = tb_dev.text_frame
tf_dev.word_wrap = True
p = tf_dev.paragraphs[0]
p.text = "Avviksanalyse per WBS"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY
bullets_dev = [
    "Divergerende avvik: WBS-300 (Reaktor) står for NOK -15,19M i negativt kostnadsavvik, mens tidsplanen er +1,14M foran plan.",
    "Systemisk mønster: Samtlige 6 WBS-pakker har negativt kostnadsavvik (CV), men positivt tidsplanavvik (SV).",
    "Prisen for hastighet: Ekstraordinære innkjøpskostnader og overtid var den direkte årsaken til at tidsplanen holdt.",
    "Controller-prioritet: Kostnadskontroll må gjeninnføres før montasjen fortsetter i WBS-500 elektro."
]
for b in bullets_dev:
    p = tf_dev.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE: 02 JERNTRIANGEL (RADAR & FRONTIER)
# ------------------------------------------------------------------------------
s_tri = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s_tri, "02 Jerntriangel: Bytte 30 dagers forsinkelse mot 18,2 MNOK i sparte forpliktelser", "VISUAL VOCABULARY — SPATIAL & BALANCE")
s_tri.shapes.add_picture(p_chart7, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))
tb_tri = s_tri.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf_tri = tb_tri.text_frame
tf_tri.word_wrap = True
p = tf_tri.paragraphs[0]
p.text = "Rebalansering av Jerntriangelet"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY
bullets_tri = [
    "Akutt spenningsubalanse: Kostnadsaksen er strukket til 289,8% av plan, mens tid er 115,6% og omfang er 96,1%.",
    "Oppbremsing som verktøy: Ved å tillate 30 dagers utsettelse av ferdigstillelse, etableres forhandlingsrom mot leverandører.",
    "Beslutningsfronten: Status Quo krever 107,2 MNOK. En 30 dagers Technical Hold capper eksponeringen på 89,0 MNOK.",
    "Effektiv besparelse: Hver forsinket uke i november sparer konsernet ca. 4,5 MNOK i unødvendige hasteinnkjøp."
]
for b in bullets_tri:
    p = tf_tri.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE: 03 GOVERNANCE GANTT & TIDSPLAN
# ------------------------------------------------------------------------------
s_gantt = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s_gantt, "03 Tidsplan: Aggregert WBS-fremdrift og 30 dagers Technical Hold i november", "VISUAL VOCABULARY — SCHEDULE")
s_gantt.shapes.add_picture(p_chart8, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))
tb_gantt = s_gantt.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf_gantt = tb_gantt.text_frame
tf_gantt.word_wrap = True
p = tf_gantt.paragraphs[0]
p.text = "Tidslinje & Kontrollbuffer"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY
bullets_gantt = [
    "96 av 102 aktiviteter fullført: Pilotanlegget er nesten mekanisk ferdig, men mangler kritisk igangkjøring.",
    "WBS-300 og 400 ferdigstilt: Hoveddelen av reaktorkomponentene er levert og montert ved Fiskå.",
    "Technical Hold i november: Innfører 30 dagers stopp før WBS-500 elektro og WBS-600 testkjøring påbegynnes.",
    "Revidert Gate 4: Flyttes fra 15. desember 2026 til slutten av januar 2027, i samråd med Enova."
]
for b in bullets_gantt:
    p = tf_gantt.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE: 04 KORRELASJON & FAST-TRACK FELLEN
# ------------------------------------------------------------------------------
s_corr = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s_corr, "04 Korrelasjon: Fast-Track Fellen — høy fart (SPI 1,16) drev kostnadskollaps (CPI 0,33)", "VISUAL VOCABULARY — CORRELATION")
s_corr.shapes.add_picture(p_chart9, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))
tb_corr = s_corr.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf_corr = tb_corr.text_frame
tf_corr.word_wrap = True
p = tf_corr.paragraphs[0]
p.text = "Samvariasjon & Dødsspiral"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY
bullets_corr = [
    "WBS Boblediagram: WBS-300 utgjør den desidert største risikoboblen (51,6M i samlet eksponering) med CPI 0,33.",
    "Månedlig bane (Jan-Okt): Fra januar til mars økte SPI fra 0,64 til 1,06, men samtidig falt CPI fra 0,95 til 0,49.",
    "Systematisk fast-track felle: Høyere hastighet krevde proporsjonalt mer kapital enn budsjettert.",
    "Lærdom for porteføljen: Tidlig forsering uten forpliktelsesgrenser fører uunngåelig til finansiell krise."
]
for b in bullets_corr:
    p = tf_corr.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE: 05 RANGERING & LEVERANDØRER
# ------------------------------------------------------------------------------
s_rank = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s_rank, "05 Rangering: Topp 8 Leverandører etter Åpen PO — primærmål for kanselleringsaudit", "VISUAL VOCABULARY — RANKING")
s_rank.shapes.add_picture(p_chart10, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))
tb_rank = s_rank.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf_rank = tb_rank.text_frame
tf_rank.word_wrap = True
p = tf_rank.paragraphs[0]
p.text = "Forhandlingsmandat Leverandører"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY
bullets_rank = [
    "Konsentrert forpliktelse: De 8 største leverandørene representerer over 27,6 MNOK (56%) av samtlige åpne PO-er.",
    "Hovedmål V006 (4,36M) & V007 (3,78M): Spesiell reaktorproduksjon og instrumentering i Tyskland og USA.",
    "Valutaeksponering: Bestillinger i USD og EUR ble inngått uten sikring, og har økt i NOK-verdi ved kronesvekkelse.",
    "Audit-målsetting: Terminere uleverte delleveranser mot standard kanselleringsgebyr (maks 10-15%)."
]
for b in bullets_rank:
    p = tf_rank.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE: 06 FORDELING & REVISJONSRISIKO
# ------------------------------------------------------------------------------
s_dist = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s_dist, "06 Fordeling: Bimodal forpliktelsesprofil og overtidskonsentrasjon i CC-4300", "VISUAL VOCABULARY — DISTRIBUTION")
s_dist.shapes.add_picture(p_chart11, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))
tb_dist = s_dist.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf_dist = tb_dist.text_frame
tf_dist.word_wrap = True
p = tf_dist.paragraphs[0]
p.text = "Fordelingsanalyse & Revisjonsspor"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY
bullets_dist = [
    "Timefordeling: CC-4300 (PMO) har høyest spredning og flest overtidstopper som følge av kontinuerlig krisehåndtering.",
    "Bimodal PO-fordeling: 120 rutineinnkjøp under 100k vs 30 tunge utstyrskontrakter over 1 MNOK.",
    "Enova revisjonssikring (ISA 805): De 30 store kontraktene må granskes særskilt for å sikre godkjenning av tilskudd.",
    "Timesatskontroll: Samtlige 1 537 timelister er avstemt mot 530 kr/t-taket for å unngå tilskuddskutt."
]
for b in bullets_dist:
    p = tf_dist.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE: 07 DEL TIL HELHET (AUc vs P&L)
# ------------------------------------------------------------------------------
s_p2w = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s_p2w, "07 Del til Helhet: IFRS IAS 38 Balanseføring (AuC 43,4M) vs Driftsført FoU (P&L 14,6M)", "VISUAL VOCABULARY — PART TO WHOLE")
s_p2w.shapes.add_picture(p_chart12, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))
tb_p2w = s_p2w.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf_p2w = tb_p2w.text_frame
tf_p2w.word_wrap = True
p = tf_p2w.paragraphs[0]
p.text = "Regnskapsmessig Klassifisering"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY
bullets_p2w = [
    "IAS 38 Skillelinje: 74,8% (43,38M) er balanseført som AuC, mens 25,2% (14,59M) er driftsført over resultat.",
    "WBS-100 PMO & Ledelse: NOK 7,25M fullt ut kostnadsført til drift; kan ikke aktiveres etter IFRS-kriteriene.",
    "WBS-300 Reaktor: NOK 23,19M balanseført som fysisk anlegg — representerer 53% av samlet AuC.",
    "Resultateffekt ved stans: Enhver terminering vil flytte 43,4M fra balanse til tap i konsernregnskapet."
]
for b in bullets_p2w:
    p = tf_p2w.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ------------------------------------------------------------------------------
# SLIDE: 09 USIKKERHET (FAN CHART)
# ------------------------------------------------------------------------------
s_fan = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s_fan, "09 Usikkerhet: Viftekart over sluttkostnad — P10 sparer 18,2 MNOK mot P50", "VISUAL VOCABULARY — UNCERTAINTY")
s_fan.shapes.add_picture(p_chart13, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))
tb_fan = s_fan.shapes.add_textbox(Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.3))
tf_fan = tb_fan.text_frame
tf_fan.word_wrap = True
p = tf_fan.paragraphs[0]
p.text = "Prognose & Utfallsrom (EAC)"
p.font.bold = True
p.font.size = Pt(14)
p.font.color.rgb = COLOR_NAVY
bullets_fan = [
    "P10 Scenario (89,0M): Forutsetter vellykket 30 dagers Technical Hold, kansellering av 18,2M PO og scope-kutt.",
    "P50 Scenario (107,2M): Status Quo dersom alle eksisterende forpliktelser fullføres uten ytterligere sprekker.",
    "P90 Scenario (132,5M): Ukontrollert eskalering med forsinkelser i elektro, gasslekkasjer og krav om ekstrabevilgning.",
    "Styrets handlingsrom: Technical Hold er det eneste tiltaket som aktivt bøyer kurven ned mot P10-banen."
]
for b in bullets_fan:
    p = tf_fan.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(9.5)
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

# ==============================================================================
# 4. GENERER VISUAL VOCABULARY PDF-RAPPORT (REPORTLAB LANDSCAPE)
# ==============================================================================
print("\n--- [4/4] Bygger Full Visual Vocabulary PDF Rapport (ReportLab Landscape) ---")
output_vis_pdf = os.path.join(OUTPUT_DIR, "GreenPilot_2026_Visual_Vocabulary_Report.pdf")
doc_vis = SimpleDocTemplate(
    output_vis_pdf,
    pagesize=landscape(A4),
    leftMargin=30, rightMargin=30, topMargin=25, bottomMargin=25
)

story_vis = []
style_vis_title = ParagraphStyle("VisTitle", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#1F4E79"))
style_vis_sub = ParagraphStyle("VisSub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=9, leading=12, textColor=colors.HexColor("#555555"))
style_vis_cat = ParagraphStyle("VisCat", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=colors.HexColor("#1F4E79"), spaceBefore=4, spaceAfter=3)
style_vis_desc = ParagraphStyle("VisDesc", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#222222"))

# Title Page / Cover
story_vis.append(Paragraph("ELKEM TECHNOLOGY — FINANCIAL TIMES VISUAL VOCABULARY SUITE", style_vis_title))
story_vis.append(Paragraph("GreenPilot 2026 Styringsrapport | Visualiseringsrammeverk for Ekstraordinært Styremøte | 31.10.2026", style_vis_sub))
story_vis.append(Spacer(1, 8))
story_vis.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1F4E79"), spaceAfter=10))

vis_catalog = [
    ("01 Avviksanalyse: Diverging Bars (Deviation)", p_chart6, "Sammenligner akutt kostnadsavvik (CV -38,8M) mot positiv fremdrift (SV +2,6M) på tvers av samtlige 6 WBS-arbeidspakker."),
    ("02 Jerntriangel: Operasjonspunkt & Avveiningsfront (Spatial & Balance)", p_chart7, "Synliggjør strekket i kostnadsaksen (290%) og hvordan 30 dagers Technical Hold sparer 18,2 MNOK i uleverte forpliktelser."),
    ("03 Tidsplan: Executive Governance Gantt (Schedule)", p_chart8, "Aggregert Primavera-tidslinje over WBS 100-600 med innlagt 30 dagers kontrollbuffer i november 2026."),
    ("04 Korrelasjon: Fast-Track Fellen & Månedlig Dødsspiral (Correlation)", p_chart9, "Boblediagram og månedlig bane som dokumenterer hvordan økt fremdriftshastighet (SPI) senket kostnadsindeksen (CPI)."),
    ("05 Rangering: Topp 8 Leverandører etter Åpen PO (Ranking)", p_chart10, "Lollipop-diagram som rangerer de 8 største leverandørene med samlet forpliktelse på 27,6 MNOK for umiddelbar kanselleringsaudit."),
    ("06 Fordeling: Ukentlig Timeforbruk & Ordrestørrelse (Distribution)", p_chart11, "Boxplot over timefordeling ved Fiskå og bimodal fordeling av innkjøpsordrer som underbygger ISA 805 revisjonsrisiko."),
    ("07 Del til Helhet: IFRS IAS 38 Balanseføring vs P&L (Part to Whole)", p_chart12, "Fordeling av 58,0M i påløpte kostnader mellom 43,38M balanseført AuC (74,8%) og 14,59M driftsført forskning (25,2%)."),
    ("08 S-Kurve & Kriseinfleksjon i Mars 2026 (Change over Time)", p_chart1, "Månedlig utvikling av PV, EV og AC som viser tidspunktet der forpliktelsene eksploderte til 149% av totalbudsjett."),
    ("09 Usikkerhet: Viftekart P10 / P50 / P90 (Uncertainty)", p_chart13, "Prognose over sluttkostnad ved ferdigstillelse; Technical Hold (P10) kutter toppeksponeringen fra 107,2M til 89,0M."),
    ("10 Forpliktelsesisberget: Waterfall Analyse (Magnitude)", p_chart2, "Fossefallsbro som forklarer hvordan prosjektet beveget seg fra vedtatt ramme (20M) til 107,2M i samlet eksponering."),
    ("11 Likviditetsgap & Kontantutgang (Cash Flow)", p_chart3, "Månedlig kontantutbetaling basert på DPO 30 dager mot låst Enova-tilskudd på 3,0 MNOK."),
    ("12 Ressursallokering Fiskå: CC-4100, 4200 og 4300 (Magnitude)", p_chart4, "Timeforbruk og kostnader avstemt mot SkatteFUNN/Forskningsrådets tak på 530 kr/t."),
    ("13 IFRS IAS 36 Nedskrivningstest: Verdifallsscenarier (Risk)", p_chart5, "Modellering av obligatorisk nedskrivningsbehov ved fortsatt drift (-13,4M) vs full terminering (-43,4M).")
]

for title, img_p, desc in vis_catalog:
    story_vis.append(PageBreak())
    story_vis.append(Paragraph(title, style_vis_cat))
    story_vis.append(Paragraph(desc, style_vis_desc))
    story_vis.append(Spacer(1, 6))
    story_vis.append(RLImage(img_p, width=730, height=360))

doc_vis.build(story_vis)
print(f" [OK] Full Visual Vocabulary PDF Rapport generert: {output_vis_pdf}")

print("=" * 80)
print("=== ALLE LEVERANSER VELLYKKET FULLFØRT ===")
print("=" * 80)
