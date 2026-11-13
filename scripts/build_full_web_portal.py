import os
import re

print("--- Bygger komplett Elkem GreenPilot Web Portal ---")

# Les original index.html
with open("index.html", "r", encoding="utf-8") as f:
    orig_html = f.read()

# Ekstraher body-innholdet fra original index.html slik at det kan plasseres på bunnen uten duplikate <html>/<body> tags
body_match = re.search(r'<body[^>]*>(.*?)</body>', orig_html, re.DOTALL | re.IGNORECASE)
if body_match:
    orig_body_content = body_match.group(1).strip()
else:
    orig_body_content = orig_html

# Ekstraher original scriptblokk hvis den fantes
script_match = re.search(r'<script>(.*?)</script>\s*</body>', orig_html, re.DOTALL | re.IGNORECASE)
orig_script_code = script_match.group(1).strip() if script_match else ""

# Fjern den originale <script> taggen fra orig_body_content så vi ikke har doble kjøringer som overskriver
orig_body_content_clean = re.sub(r'<script>.*?</script>', '', orig_body_content, flags=re.DOTALL | re.IGNORECASE)

full_html = f"""<!DOCTYPE html>
<html lang="no" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Elkem GreenPilot 2026 — Executive EVM & Full Visual Vocabulary Portal</title>
  <!-- Tailwind CSS & Plotly JS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    .metric-card {{
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 0.75rem;
      padding: 1rem 1.25rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      transition: all 0.2s ease;
    }}
    .metric-card:hover {{
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
      border-color: #cbd5e1;
    }}
    .section-card {{
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 1rem;
      padding: 1.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      margin-bottom: 2rem;
    }}
    .alert-card-red {{
      background-color: #FEF2F2;
      border-left: 6px solid #DC2626;
      border-radius: 0.5rem;
      padding: 1.25rem;
    }}
    .nav-pill {{
      transition: all 0.15s ease-in-out;
    }}
    .nav-pill:hover {{
      background-color: #1E293B;
      color: #FFFFFF;
    }}
    .tab-btn.active {{
      border-bottom: 3px solid #1F4E79;
      color: #1F4E79;
      font-weight: 700;
    }}
  </style>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col antialiased">

  <!-- ========================================================================= -->
  <!-- TOP STICKY HEADER & QUICK KPI STRIP (SSOT PER 31.10.2026) -->
  <!-- ========================================================================= -->
  <header class="bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 text-white py-4 px-6 shadow-lg border-b border-slate-800 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
      <div>
        <div class="flex items-center gap-3">
          <span class="bg-red-600 text-white text-[11px] font-black px-2.5 py-1 rounded uppercase tracking-wider animate-pulse">Rød Alarm (Gate 3)</span>
          <h1 class="text-xl sm:text-2xl font-bold tracking-tight">ELKEM GREENPILOT 2026 — FULL VISUAL VOCABULARY PORTAL</h1>
        </div>
        <p class="text-xs text-slate-300 mt-1">Dual-Engine Styringsportal: Deterministisk EVM + Agentic RAG Copilot | FAST Standard & IFRS Compliant | Status: 31.10.2026</p>
      </div>
      <div class="flex flex-wrap items-center gap-2 sm:gap-4 text-xs bg-slate-800/90 px-3 py-2 rounded-xl border border-slate-700 shadow-inner">
        <div><span class="text-slate-400 block text-[10px]">Vedtatt Budsjett</span><span class="font-bold text-sm text-slate-100">20,0 MNOK</span></div>
        <div class="border-l border-slate-700 pl-3"><span class="text-slate-400 block text-[10px]">Påløpt AC</span><span class="font-bold text-sm text-rose-400">58,0 MNOK</span></div>
        <div class="border-l border-slate-700 pl-3"><span class="text-slate-400 block text-[10px]">Opptjent EV</span><span class="font-bold text-sm text-sky-400">19,2 MNOK</span></div>
        <div class="border-l border-slate-700 pl-3"><span class="text-slate-400 block text-[10px]">Åpen PO</span><span class="font-bold text-sm text-amber-400">49,2 MNOK</span></div>
        <div class="border-l border-slate-700 pl-3"><span class="text-slate-400 block text-[10px]">Total Eksponering</span><span class="font-bold text-sm text-purple-300">107,2 MNOK</span></div>
        <div class="border-l border-slate-700 pl-3"><span class="text-slate-400 block text-[10px]">CPI / SPI</span><span class="font-bold text-sm text-red-400">0,33 / 1,16</span></div>
      </div>
    </div>
  </header>

  <!-- ========================================================================= -->
  <!-- HORIZONTAL FAST JUMP NAVIGATION (ALL 14 MODULES + ORIGINAL ARCHIVE) -->
  <!-- ========================================================================= -->
  <nav class="bg-white border-b border-slate-200 sticky top-[73px] z-40 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-2 overflow-x-auto py-2.5 text-xs font-semibold scrollbar-thin">
      <a href="#mod-00" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">00 Styringsnotat</a>
      <a href="#mod-01" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">01 Avvik (Bars)</a>
      <a href="#mod-02" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">02 Jerntriangel</a>
      <a href="#mod-03" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">03 Tidsplan (Gantt)</a>
      <a href="#mod-04" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">04 Korrelasjon</a>
      <a href="#mod-05" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">05 Rangering</a>
      <a href="#mod-06" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">06 Fordeling</a>
      <a href="#mod-07" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">07 Del til Helhet</a>
      <a href="#mod-08" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">08 Sankey Flyt</a>
      <a href="#mod-09" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">09 Usikkerhet (Vifte)</a>
      <a href="#mod-10" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">10 Isberg Fossefall</a>
      <a href="#mod-11" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">11 Likviditet & Fiskå</a>
      <a href="#mod-12" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">12 Simulator</a>
      <a href="#mod-13" class="nav-pill px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 whitespace-nowrap">13 AI Copilot</a>
      <a href="#original-archive-section" class="nav-pill px-3 py-1.5 rounded-lg bg-blue-100 text-blue-900 font-bold whitespace-nowrap border border-blue-200">📁 Opprinnelig Arkiv (Bunn)</a>
    </div>
  </nav>

  <!-- ========================================================================= -->
  <!-- MAIN FULL-VIEW STREAMLIT-STYLE DASHBOARD CONTAINER (ALL VISUALS SHOW) -->
  <!-- ========================================================================= -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-grow space-y-8">

    <!-- INTRO BANNER -->
    <div class="bg-gradient-to-r from-blue-900 to-slate-900 text-white rounded-2xl p-6 shadow-md border border-slate-700">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <span class="text-xs uppercase tracking-wider text-blue-300 font-bold">Financial Times Visual Vocabulary Suite</span>
          <h2 class="text-2xl font-bold mt-1">Komplett Styrings- og Avviksportal (Viser Samtlige 14 Seksjoner)</h2>
          <p class="text-xs text-slate-300 mt-2 max-w-3xl leading-relaxed">
            Denne rapporten gjengir samtlige moduler, analyser og interaktive verktøy fra prosjektets Streamlit-applikasjon 
            (<code>scripts/app.py</code>) samlet på én rullende flate. Det opprinnelige fanebaserte dashboardet er bevart i sin helhet 
            i et dedikert referansearkiv nederst på siden.
          </p>
        </div>
        <div class="flex gap-2">
          <a href="#original-archive-section" class="bg-white/10 hover:bg-white/20 text-white border border-white/20 text-xs px-3.5 py-2 rounded-lg font-medium transition">
            Gå til Opprinnelig Arkiv ↓
          </a>
        </div>
      </div>
    </div>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 00: EXECUTIVE GOVERNANCE & STATUS -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-00" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">00</span>
          Styrets Beslutningsnotat & Overordnet Prosjektstatus
        </h3>
        <span class="text-xs font-semibold text-rose-600 bg-rose-50 px-2 py-1 rounded border border-rose-200">Stage-Gate 3 Gjennomgang</span>
      </div>

      <!-- Red Alert Card -->
      <div class="alert-card-red mb-6 space-y-2 text-xs text-rose-950 leading-relaxed shadow-sm">
        <div class="font-bold text-sm text-rose-900 flex items-center gap-2">
          <span>🔴 KRITISK STYRINGSSVIKT & LIKVIDITETSEKSPONERING (Per 31.10.2026)</span>
        </div>
        <p><strong>1. DIAGNOSE (EVM):</strong> Prosjektet opererer med kostnadseffektivitet <strong>CPI 0,33</strong> og et akkumulert kostnadsavvik på <strong>NOK -38,8M</strong>. Fremdriften meldes likevel til <strong>SPI 1,16</strong> (+5 uker foran plan) grunnet aggressiv forsering.</p>
        <p><strong>2. FORPLIKTELSER & EKSPONERING:</strong> Bokførte kostnader (NOK 58,0M) og uleverte innkjøpsordrer (NOK 49,2M) gir en samlet eksponering på <strong>NOK 107,2M (536% av BAC)</strong>.</p>
        <p><strong>3. IFRS BALANSERISIKO:</strong> Av dette er <strong>NOK 43,4M</strong> balanseført som anlegg under utførelse (AuC) etter IAS 38. Dette utløser obligatorisk krav om nedskrivningstest etter IAS 36 før årsoppgjøret.</p>
        <p><strong>4. ANBEFALT STYREVEDTAK:</strong> Vedta umiddelbar <strong>30 dagers Technical Hold & Innkjøpsfrys</strong> for å kansellere uleverte PO-er (sparer 18,2 MNOK) og forskyve ferdigstillelse til januar 2027.</p>
      </div>

      <!-- KPI Grid -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        <div class="metric-card"><span class="text-xs text-slate-500 block">Budsjett (BAC)</span><span class="text-xl font-bold text-slate-800">20,0 MNOK</span><span class="text-[10px] text-slate-400 block mt-0.5">Vedtatt ramme</span></div>
        <div class="metric-card"><span class="text-xs text-slate-500 block">Påløpt Kostnad (AC)</span><span class="text-xl font-bold text-rose-600">58,0 MNOK</span><span class="text-[10px] text-rose-500 font-semibold block mt-0.5">+190% over BAC</span></div>
        <div class="metric-card"><span class="text-xs text-slate-500 block">Opptjent Verdi (EV)</span><span class="text-xl font-bold text-blue-600">19,2 MNOK</span><span class="text-[10px] text-blue-500 font-semibold block mt-0.5">SPI 1,16 (Forsert)</span></div>
        <div class="metric-card"><span class="text-xs text-slate-500 block">Åpne PO-er</span><span class="text-xl font-bold text-amber-600">49,2 MNOK</span><span class="text-[10px] text-amber-500 block mt-0.5">Ufakturert binding</span></div>
        <div class="metric-card"><span class="text-xs text-slate-500 block">Total Eksponering</span><span class="text-xl font-bold text-purple-700">107,2 MNOK</span><span class="text-[10px] text-purple-600 font-semibold block mt-0.5">536% av budsjett</span></div>
      </div>

      <!-- Charts & Decision Cards -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="font-bold text-slate-800 text-xs mb-2">Styringsgap: Eksponering vs. Budsjett</h4>
          <div id="full-chart-exec-bar" style="height: 300px;"></div>
        </div>
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50 flex flex-col justify-between">
          <div>
            <h4 class="font-bold text-slate-800 text-xs mb-3">Styrets Beslutningsalternativer ved Gate 3</h4>
            <div class="space-y-3 text-xs">
              <div class="p-3.5 bg-blue-50/80 border border-blue-200 rounded-xl">
                <span class="font-bold text-blue-900 block text-xs mb-1">Alternativ A: 30 Dagers Technical Hold (Anbefalt)</span>
                <p class="text-slate-600">Full innkjøps- og ansettelsesfrys. Kanselleringsaudit av 49,2 MNOK uleverte PO-er (sparer ca. <strong>18,2 MNOK</strong>). Capper samlet eksponering på <strong>89,0 MNOK</strong> mot 4–6 ukers utsettelse til januar 2027.</p>
              </div>
              <div class="p-3.5 bg-rose-50/80 border border-rose-200 rounded-xl">
                <span class="font-bold text-rose-900 block text-xs mb-1">Alternativ B: Formell Prosjektstans (Off-Ramp)</span>
                <p class="text-slate-600">Terminere prosjektet ved Stage-Gate 3. Umiddelbar tapsføring av <strong>43,4 MNOK</strong> i balanseført AuC rett over konsernresultatet etter IAS 36, samt tilbakebetalingsrisiko for 3,0 MNOK i utbetalt Enova-tilskudd.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- WBS Detailed Table -->
      <div class="overflow-x-auto border border-slate-200 rounded-xl shadow-sm">
        <table class="w-full text-xs text-left">
          <thead class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
            <tr>
              <th class="py-2.5 px-3">WBS ID</th>
              <th class="py-2.5 px-3">Beskrivelse</th>
              <th class="py-2.5 px-3">IFRS Behandling</th>
              <th class="py-2.5 px-3 text-right">BAC NOK</th>
              <th class="py-2.5 px-3 text-right">Påløpt AC NOK</th>
              <th class="py-2.5 px-3 text-right">Opptjent EV NOK</th>
              <th class="py-2.5 px-3 text-right">Åpen PO NOK</th>
              <th class="py-2.5 px-3 text-right">Eksponering NOK</th>
              <th class="py-2.5 px-3 text-center">CPI</th>
              <th class="py-2.5 px-3 text-center">SPI</th>
              <th class="py-2.5 px-3 text-center">RAG</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr class="hover:bg-slate-50"><td class="py-2 px-3 font-mono font-bold">WBS-100</td><td class="py-2 px-3">PMO & Prosjektledelse</td><td class="py-2 px-3 text-slate-500">Driftsført FoU (P&L)</td><td class="py-2 px-3 text-right">2 500 000</td><td class="py-2 px-3 text-right text-rose-600 font-semibold">7 248 011</td><td class="py-2 px-3 text-right">2 401 961</td><td class="py-2 px-3 text-right">4 120 000</td><td class="py-2 px-3 text-right font-bold">11 368 011</td><td class="py-2 px-3 text-center font-bold text-rose-600">0,33</td><td class="py-2 px-3 text-center text-emerald-600">1,12</td><td class="py-2 px-3 text-center"><span class="px-2 py-0.5 rounded bg-rose-100 text-rose-700 font-bold text-[10px]">RØD</span></td></tr>
            <tr class="hover:bg-slate-50"><td class="py-2 px-3 font-mono font-bold">WBS-200</td><td class="py-2 px-3">Prosessdesign & Basic Eng.</td><td class="py-2 px-3 text-blue-600 font-medium">Balanseført AuC</td><td class="py-2 px-3 text-right">3 500 000</td><td class="py-2 px-3 text-right text-rose-600 font-semibold">10 147 215</td><td class="py-2 px-3 text-right">3 362 745</td><td class="py-2 px-3 text-right">6 850 000</td><td class="py-2 px-3 text-right font-bold">16 997 215</td><td class="py-2 px-3 text-center font-bold text-rose-600">0,33</td><td class="py-2 px-3 text-center text-emerald-600">1,14</td><td class="py-2 px-3 text-center"><span class="px-2 py-0.5 rounded bg-rose-100 text-rose-700 font-bold text-[10px]">RØD</span></td></tr>
            <tr class="hover:bg-slate-50"><td class="py-2 px-3 font-mono font-bold">WBS-300</td><td class="py-2 px-3">Pilotanlegg & Reaktor</td><td class="py-2 px-3 text-blue-600 font-medium">Balanseført AuC</td><td class="py-2 px-3 text-right">8 000 000</td><td class="py-2 px-3 text-right text-rose-600 font-semibold">23 193 616</td><td class="py-2 px-3 text-right">7 686 275</td><td class="py-2 px-3 text-right font-semibold text-amber-600">28 450 000</td><td class="py-2 px-3 text-right font-bold text-purple-900">51 643 616</td><td class="py-2 px-3 text-center font-bold text-rose-600">0,33</td><td class="py-2 px-3 text-center text-emerald-600">1,17</td><td class="py-2 px-3 text-center"><span class="px-2 py-0.5 rounded bg-rose-100 text-rose-700 font-bold text-[10px]">RØD</span></td></tr>
            <tr class="hover:bg-slate-50"><td class="py-2 px-3 font-mono font-bold">WBS-400</td><td class="py-2 px-3">Infrastruktur & Gass</td><td class="py-2 px-3 text-blue-600 font-medium">Balanseført AuC</td><td class="py-2 px-3 text-right">3 000 000</td><td class="py-2 px-3 text-right text-rose-600 font-semibold">8 697 606</td><td class="py-2 px-3 text-right">2 882 353</td><td class="py-2 px-3 text-right">5 213 751</td><td class="py-2 px-3 text-right font-bold">13 911 357</td><td class="py-2 px-3 text-center font-bold text-rose-600">0,33</td><td class="py-2 px-3 text-center text-emerald-600">1,10</td><td class="py-2 px-3 text-center"><span class="px-2 py-0.5 rounded bg-rose-100 text-rose-700 font-bold text-[10px]">RØD</span></td></tr>
            <tr class="hover:bg-slate-50"><td class="py-2 px-3 font-mono font-bold">WBS-500</td><td class="py-2 px-3">Installasjon & Elektro</td><td class="py-2 px-3 text-blue-600 font-medium">Balanseført AuC</td><td class="py-2 px-3 text-right">2 000 000</td><td class="py-2 px-3 text-right text-rose-600 font-semibold">5 796 804</td><td class="py-2 px-3 text-right">1 921 569</td><td class="py-2 px-3 text-right">3 600 000</td><td class="py-2 px-3 text-right font-bold">9 396 804</td><td class="py-2 px-3 text-center font-bold text-rose-600">0,33</td><td class="py-2 px-3 text-center text-emerald-600">1,24</td><td class="py-2 px-3 text-center"><span class="px-2 py-0.5 rounded bg-rose-100 text-rose-700 font-bold text-[10px]">RØD</span></td></tr>
            <tr class="hover:bg-slate-50"><td class="py-2 px-3 font-mono font-bold">WBS-600</td><td class="py-2 px-3">Testkjøring & Overlevering</td><td class="py-2 px-3 text-slate-500">Driftsført FoU (P&L)</td><td class="py-2 px-3 text-right">1 000 000</td><td class="py-2 px-3 text-right text-rose-600 font-semibold">2 884 789</td><td class="py-2 px-3 text-right">960 784</td><td class="py-2 px-3 text-right">1 000 000</td><td class="py-2 px-3 text-right font-bold">3 884 789</td><td class="py-2 px-3 text-center font-bold text-rose-600">0,33</td><td class="py-2 px-3 text-center text-emerald-600">1,20</td><td class="py-2 px-3 text-center"><span class="px-2 py-0.5 rounded bg-rose-100 text-rose-700 font-bold text-[10px]">RØD</span></td></tr>
          </tbody>
          <tfoot class="bg-slate-200/80 font-bold text-slate-900 border-t-2 border-slate-300">
            <tr>
              <td class="py-2.5 px-3" colspan="3">TOTAL GREENPILOT PORTEFØLJE</td>
              <td class="py-2.5 px-3 text-right">20 000 000</td>
              <td class="py-2.5 px-3 text-right text-rose-700">57 968 041</td>
              <td class="py-2.5 px-3 text-right text-blue-700">19 215 686</td>
              <td class="py-2.5 px-3 text-right text-amber-700">49 233 752</td>
              <td class="py-2.5 px-3 text-right text-purple-900 font-black">107 201 793</td>
              <td class="py-2.5 px-3 text-center font-black text-rose-700">0,33</td>
              <td class="py-2.5 px-3 text-center font-black text-emerald-700">1,16</td>
              <td class="py-2.5 px-3 text-center"><span class="px-2 py-0.5 rounded bg-rose-600 text-white font-bold text-[10px]">KRITISK</span></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 01: AVVIK & DIVERGING BARS (DEVIATION) -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-01" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">01</span>
          Avviksanalyse: Diverging Bars (FT Visual Vocabulary: Deviation)
        </h3>
        <span class="text-xs text-slate-500 font-medium">CV (EV - AC) mot SV (EV - PV)</span>
      </div>
      <p class="text-xs text-slate-600 mb-4 leading-relaxed">
        Visual Vocabulary definerer <strong>Diverging Bar Charts</strong> som den overlegne metoden for å vise variasjoner (+/-) 
        rundt et fast referansepunkt (0-linjen). Her ser vi GreenPilot-paradokset:
        <strong>Kostnadsavviket (CV)</strong> kollapser mot venstre i dyp rød sone pga. ekstreme overskridelser, 
        mens <strong>Tidsplanavviket (SV)</strong> peker mot høyre i grønt pga. aggressiv forsering og for tidlig innkjøp.
      </p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">A: Kostnadsavvik per WBS (CV = EV - AC)</h4>
          <div id="full-chart-cv-bars" style="height: 300px;"></div>
        </div>
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">B: Tidsplanavvik per WBS (SV = EV - PV)</h4>
          <div id="full-chart-sv-bars" style="height: 300px;"></div>
        </div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 02: DYNAMISK JERNTRIANGEL (CONSTRAINTS / SPATIAL) -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-02" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">02</span>
          Dynamisk Jerntriangel: Avveininger & Beslutningsfront
        </h3>
        <span class="text-xs text-slate-500 font-medium">Omfang, Tid & Kostnad</span>
      </div>
      <p class="text-xs text-slate-600 mb-4 leading-relaxed">
        Jerntriangelet visualiserer spenningen mellom leveranseomfang, tidsbruk og totalkostnad. 
        Mens fremdrift og omfang er nær baseline, er kostnadsvektoren sprengt til <strong>290 %</strong> av opprinnelig plan.
      </p>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">A: Sanntids Operasjonspunkt (Polar Radar)</h4>
          <div id="full-chart-triangle-polar" style="height: 320px;"></div>
        </div>
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">B: Beslutningsfront ved Oppbremsing (Slow Down)</h4>
          <div id="full-chart-triangle-frontier" style="height: 320px;"></div>
        </div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 03: TIDSPLAN & GOVERNANCE GANTT (SCHEDULE) -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-03" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">03</span>
          Tidsplan & Governance Gantt (Stage-Gates & 30d Hold)
        </h3>
        <span class="text-xs text-slate-500 font-medium">102 Primavera Aktiviteter</span>
      </div>
      <p class="text-xs text-slate-600 mb-4 leading-relaxed">
        Gantt-diagrammet over de 6 WBS-pakkene synliggjør hvordan en kontrollert oppbremsing i november (30 dagers Technical Hold) 
        fryser innkjøp og forskyver Gate 4 til januar 2027 uten å true kjerneprosessene. Den stiplede røde linjen markerer status per cut-off 31.10.2026.
      </p>
      <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
        <div id="full-chart-gantt" style="height: 350px;"></div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 04: KORRELASJON: FAST-TRACK FELLEN & DØDSSPIRALEN -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-04" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">04</span>
          Korrelasjon: Fast-Track Fellen & Dødsspiralen (Correlation)
        </h3>
        <span class="text-xs text-slate-500 font-medium">Forsering (SPI) mot Kostnadskollaps (CPI)</span>
      </div>
      <p class="text-xs text-slate-600 mb-4 leading-relaxed">
        Viser samspillet mellom forsering og kostnadseskalering. Boblediagrammet illustrerer at de største arbeidspakkene 
        (spesielt WBS-300 Reaktor) har høyest forsering og størst finansiell binding. Trajektorien til høyre viser hvordan CPI kollapset i mars 2026.
      </p>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">A: WBS Boblediagram (Størrelse = Eksponering)</h4>
          <div id="full-chart-bubble" style="height: 320px;"></div>
        </div>
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">B: Månedlig Connected Trajectory (Jan-Okt 2026)</h4>
          <div id="full-chart-connected" style="height: 320px;"></div>
        </div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 05: RANGERING & FORHANDLINGSLISTE (RANKING) -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-05" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">05</span>
          Rangering & Forhandlingsliste (Ranking / Lollipop)
        </h3>
        <span class="text-xs text-slate-500 font-medium">Topp 8 Leverandører</span>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">A: Topp 8 Leverandører etter Åpen PO (Kanselleringsmål)</h4>
          <div id="full-chart-vendor-rank" style="height: 330px;"></div>
        </div>
        <div class="border border-slate-200 rounded-xl p-5 bg-slate-50/50 flex flex-col justify-between text-xs space-y-3">
          <div>
            <h4 class="font-bold text-slate-800 text-xs mb-2">Forhandlingsmandat for 30d Technical Hold</h4>
            <div class="space-y-2.5">
              <div class="p-2.5 bg-white border border-slate-200 rounded-lg">
                <strong class="text-rose-700 block">Mål 1 (V006 - Tyskland): 4,36 MNOK åpen PO</strong>
                Reaktorkomponenter og spesialstål. Krever umiddelbar produksjonsstans for ustartede delleveranser.
              </div>
              <div class="p-2.5 bg-white border border-slate-200 rounded-lg">
                <strong class="text-rose-700 block">Mål 2 (V020 - Norge): 4,16 MNOK åpen PO</strong>
                Elektro- og automasjonsmontasje. Forhandle forskyvning av installasjonsstart til januar 2027.
              </div>
              <div class="p-2.5 bg-white border border-slate-200 rounded-lg">
                <strong class="text-rose-700 block">Mål 3 (V007 - USA): 3,78 MNOK i USD</strong>
                Spesialpumper. Valutasikring mot ytterligere svekkelse av NOK og terminering av opsjoner.
              </div>
            </div>
          </div>
          <div class="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-900 font-bold text-center">
            Spart likviditet ved topp 3 leverandører: 12,30 MNOK (25% av hele forpliktelsesisberget).
          </div>
        </div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 06: FORDELING & REVISJONSRISIKO (DISTRIBUTION) -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-06" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">06</span>
          Fordeling & Revisjonsrisiko (Distribution / Boxplot & Histogram)
        </h3>
        <span class="text-xs text-slate-500 font-medium">ISA 805 & 530 kr/t Tak</span>
      </div>
      <p class="text-xs text-slate-600 mb-4 leading-relaxed">
        Statistisk spredning i timeregistreringer (ISA 805 tak på 530 kr/t) og bimodal fordeling i PO-størrelser. 
        Boksplottet synliggjør overforbruk av timer ved CC-4300 PMO, mens histogrammet viser en lang hale av store utstyrsordrer.
      </p>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">A: Ukentlig Timefordeling per Koststed (1 537 Linjer)</h4>
          <div id="full-chart-dist-box" style="height: 310px;"></div>
        </div>
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">B: Bimodal Innkjøpsstørrelse (150 PO-er)</h4>
          <div id="full-chart-dist-hist" style="height: 310px;"></div>
        </div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 07: DEL TIL HELHET & IFRS BALANSE (PART-TO-WHOLE) -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-07" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">07</span>
          Del til Helhet & IFRS Balanse (Part-to-Whole / Treemap & Stacked)
        </h3>
        <span class="text-xs text-slate-500 font-medium">IAS 38 Kapitalisering</span>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">A: Treemap over Total Eksponering (107,2 MNOK)</h4>
          <div id="full-chart-ptw-tree" style="height: 320px;"></div>
        </div>
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">B: 100% Stacked Bar (AuC vs. P&L Forskyvning)</h4>
          <div id="full-chart-ptw-stacked" style="height: 320px;"></div>
        </div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 08: KAPITAL- & FORPLIKTELSESFLYT (FLOW / SANKEY) -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-08" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">08</span>
          Kapital- & Forpliktelsesflyt (Flow / Sankey Diagram)
        </h3>
        <span class="text-xs text-slate-500 font-medium">Full Forpliktelsessporing</span>
      </div>
      <p class="text-xs text-slate-600 mb-4 leading-relaxed">
        Sankey-diagrammet sporer kapitalen fra arbeidspakker gjennom ERP-systemet til balanseført AuC (43,4M), 
        resultatført FoU (14,6M) og uleverte PO-er fordelt på kansellerbare ordrer (18,2M) og låste forpliktelser (31,0M).
      </p>
      <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
        <div id="full-chart-sankey" style="height: 420px;"></div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 09: USIKKERHET & EAC UTFALLSROM (UNCERTAINTY / FAN CHART) -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-09" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">09</span>
          Usikkerhet & EAC Utfallsrom (Uncertainty / Fan Chart)
        </h3>
        <span class="text-xs text-slate-500 font-medium">P10, P50 & P90 Fremtidsscenarier</span>
      </div>
      <p class="text-xs text-slate-600 mb-4 leading-relaxed">
        I stedet for et statisk punkt-estimat, viser viftediagrammet konsekvensen av styrets valg ved Gate 3:
        <strong>P10 (Beste utfall - 30d Technical Hold):</strong> Sluttkostnad begrenses til <strong>89,0 MNOK</strong>.
        <strong>P50 (Forventet kurs / Status Quo):</strong> Sluttkostnad lander på <strong>107,2 MNOK</strong>.
        <strong>P90 (Ukontrollert eskalering / Forsering):</strong> Sluttkostnad eskalerer til <strong>132,5 MNOK</strong>.
      </p>
      <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
        <div id="full-chart-fan" style="height: 380px;"></div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 10: FORPLIKTELSESISBERG & WBS KOSTNADSBRO (WATERFALL) -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-10" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">10</span>
          Forpliktelsesisberg & WBS Kostnadsbro (Waterfall)
        </h3>
        <span class="text-xs text-slate-500 font-medium">Fra 20,0M BAC til 107,2M Total Eksponering</span>
      </div>
      <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
        <div id="full-chart-waterfall" style="height: 360px;"></div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 11: LIKVIDITETSBRO & FISKÅ ENHETER (CASH) -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-11" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">11</span>
          Likviditet, Forfallsstruktur & Fiskå Koststeder (Cash & Timesheets)
        </h3>
        <span class="text-xs text-slate-500 font-medium">DPO 30d Utbetalinger & 530 kr/t Sats</span>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">A: Månedlig Likviditetsutgang vs. Enova Innbetaling</h4>
          <div id="full-chart-cashflow" style="height: 310px;"></div>
        </div>
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <h4 class="text-xs font-bold text-slate-700 mb-2">B: Faktiske Timer per Koststed ved Fiskå (@ 530 kr/t)</h4>
          <div id="full-chart-costcenters" style="height: 310px;"></div>
        </div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 12: HVA-OM SCENARIO SIMULATOR -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-12" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">12</span>
          Hva-om Scenario Simulator (Interaktiv Beslutningsstøtte)
        </h3>
        <span class="text-xs text-slate-500 font-medium">PO-Kansellering & IAS 36 Nedskrivning</span>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-center">
        <div class="space-y-4">
          <div>
            <div class="flex justify-between text-xs font-bold text-slate-700 mb-1">
              <span>Kansellering av åpne PO-er:</span>
              <span id="full-val-pocut" class="text-blue-700">37%</span>
            </div>
            <input type="range" id="full-slider-pocut" min="0" max="60" value="37" step="5" class="w-full accent-blue-900" oninput="updateFullSim()">
          </div>
          <div>
            <div class="flex justify-between text-xs font-bold text-slate-700 mb-1">
              <span>IAS 36 Nedskrivning på balanseført AuC:</span>
              <span id="full-val-impair" class="text-rose-700">25%</span>
            </div>
            <input type="range" id="full-slider-impair" min="0" max="100" value="25" step="5" class="w-full accent-rose-700" oninput="updateFullSim()">
          </div>
          <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-2">
            <div class="flex justify-between"><span class="text-slate-500">Spart Likviditet:</span><strong id="full-sim-saved" class="text-emerald-700 text-sm">+18.22 MNOK</strong></div>
            <div class="flex justify-between"><span class="text-slate-500">Ny Total Eksponering:</span><strong id="full-sim-newexp" class="text-slate-900 text-sm">88.98 MNOK</strong></div>
            <div class="flex justify-between"><span class="text-slate-500">IAS 36 Tapsføring (Drift):</span><strong id="full-sim-loss" class="text-rose-700 text-sm">-10.84 MNOK</strong></div>
          </div>
        </div>
        <div class="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
          <div id="full-chart-sim" style="height: 290px;"></div>
        </div>
      </div>
    </section>

    <!-- ----------------------------------------------------------------------- -->
    <!-- MODUL 13: ELKEM AI CONTROLLER COPILOT (RAG & VEKTOR-DB) -->
    <!-- ----------------------------------------------------------------------- -->
    <section id="mod-13" class="section-card scroll-mt-28">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="bg-blue-900 text-white text-xs px-2 py-0.5 rounded font-mono">13</span>
          Elkem AI Controller Copilot (Vektor-DB & Semantisk Søk)
        </h3>
        <span class="text-xs text-slate-500 font-medium">IFRS, ISA 805, Enova & Styrenotat</span>
      </div>
      <p class="text-xs text-slate-600 mb-3 leading-relaxed">
        Still kontrollspørsmål direkte til prosjektets kildekorpus for umiddelbar faglig begrunnelse forankret i regnskapsstandarder.
      </p>
      <div class="flex gap-2 mb-2">
        <input type="text" id="full-ai-query" placeholder="Still et spørsmål (f.eks. Hvorfor må AuC testes etter IAS 36?)" class="flex-grow p-2.5 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-900 outline-none">
        <button onclick="runFullQuery()" class="bg-blue-900 text-white px-5 py-2.5 rounded-xl text-xs font-bold hover:bg-blue-800 transition">Søk i Korpus</button>
      </div>
      <div class="flex flex-wrap gap-2 mb-4">
        <button onclick="setFullQuery('Hvorfor må AuC testes for verdifall etter IAS 36?')" class="text-[11px] bg-slate-100 hover:bg-slate-200 border border-slate-300 px-2.5 py-1 rounded-lg">IAS 36 Verdifall</button>
        <button onclick="setFullQuery('Hva er kriteriene for balanseføring etter IAS 38?')" class="text-[11px] bg-slate-100 hover:bg-slate-200 border border-slate-300 px-2.5 py-1 rounded-lg">IAS 38 Balanseføring</button>
        <button onclick="setFullQuery('Hva er reglene for timesats 530 kr og revisjon etter ISA 805?')" class="text-[11px] bg-slate-100 hover:bg-slate-200 border border-slate-300 px-2.5 py-1 rounded-lg">Timesats 530 kr / ISA 805</button>
        <button onclick="setFullQuery('Hva er formålet med 30 dagers Technical Hold?')" class="text-[11px] bg-slate-100 hover:bg-slate-200 border border-slate-300 px-2.5 py-1 rounded-lg">30d Technical Hold</button>
      </div>
      <div id="full-ai-response" class="p-4 bg-blue-50/70 rounded-xl border border-blue-200 text-xs hidden leading-relaxed space-y-3">
        <!-- Result filled by JS -->
      </div>
    </section>

    <!-- ======================================================================= -->
    <!-- DEDIKERT AVSNITT: OPPRINNELIG PROSJEKTUNDERLAG & REFERANSEARKIV -->
    <!-- (Retained at bottom of index.html per user request) -->
    <!-- ======================================================================= -->
    <div id="original-archive-section" class="mt-16 border-t-8 border-slate-300 pt-8 bg-slate-100/70 p-6 sm:p-8 rounded-3xl shadow-inner scroll-mt-28">
      <div class="bg-slate-900 text-white p-5 rounded-2xl mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
        <div>
          <span class="bg-blue-600 text-white text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">Referansearkiv</span>
          <h3 class="text-xl font-bold mt-1">Opprinnelig Prosjektunderlag & Fanebasert Visning</h3>
          <p class="text-xs text-slate-300 mt-1">Dette avsnittet bevarer det opprinnelige innholdet i <code>index.html</code> i sin helhet i henhold til instruks.</p>
        </div>
        <a href="#mod-00" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition">
          Tilbake til toppen ↑
        </a>
      </div>

      <!-- INNHOLD FRA OPPRINNELIG INDEX.HTML -->
      <div class="border border-slate-200 rounded-2xl bg-white p-4 sm:p-6 shadow-sm">
        {orig_body_content_clean}
      </div>
    </div>

  </main>

  <footer class="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500 mt-12">
    Elkem ASA — GreenPilot 2026 Controller Portal | Single Source of Truth Datapipeline | FAST Standard & IFRS Compliant
  </footer>

  <!-- ========================================================================= -->
  <!-- JAVASCRIPT: PLOTLY CHARTS & INTERACTIVE LOGIC (BOTH FULL-VIEW & ARCHIVE) -->
  <!-- ========================================================================= -->
  <script>
    // -------------------------------------------------------------------------
    // ORIGINAL ARCHIVE TAB SWITCHER
    // -------------------------------------------------------------------------
    function switchTab(tabId) {{
      document.querySelectorAll('#original-archive-section .tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('#original-archive-section .tab-btn').forEach(el => el.classList.remove('active'));
      const target = document.getElementById(tabId);
      if (target) target.classList.remove('hidden');
      const btn = document.getElementById('btn-' + tabId);
      if (btn) btn.classList.add('active');
      window.dispatchEvent(new Event('resize'));
    }}

    // -------------------------------------------------------------------------
    // RENDER FULL-VIEW STREAMLIT DASHBOARD PLOTS ON LOAD
    // -------------------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function () {{
      const wbsNames = ['WBS-100 PMO', 'WBS-200 Prosess', 'WBS-300 Reaktor', 'WBS-400 Infra', 'WBS-500 Elektro', 'WBS-600 Test'];

      // 00 Exec Bar
      Plotly.newPlot('full-chart-exec-bar', [{{
        x: ["Budsjett (BAC)", "Opptjent (EV)", "Påløpt (AC)", "Total Eksponering"],
        y: [20.0, 19.2, 58.0, 107.2],
        type: 'bar',
        marker: {{ color: ["#595959", "#2F5496", "#C00000", "#800000"] }},
        text: ["20.0M", "19.2M", "58.0M", "107.2M"],
        textposition: 'outside'
      }}], {{ yaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 30 }} }}, {{ responsive: true }});

      // 01 CV & SV Bars
      Plotly.newPlot('full-chart-cv-bars', [{{
        y: wbsNames, x: [-4.85, -6.78, -15.51, -5.82, -3.88, -1.92], type: 'bar', orientation: 'h',
        marker: {{ color: '#C00000' }}, text: ['-4.85M', '-6.78M', '-15.51M', '-5.82M', '-3.88M', '-1.92M'], textposition: 'inside'
      }}], {{ xaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 90, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});

      Plotly.newPlot('full-chart-sv-bars', [{{
        y: wbsNames, x: [0.25, 0.41, 1.14, 0.26, 0.37, 0.16], type: 'bar', orientation: 'h',
        marker: {{ color: '#009E73' }}, text: ['+0.25M', '+0.41M', '+1.14M', '+0.26M', '+0.37M', '+0.16M'], textposition: 'inside'
      }}], {{ xaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 90, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});

      // 02 Triangle Polar & Frontier
      const triCats = ['KOST (107.2M Exp)', 'TID (SPI 1.16 / +5u)', 'OMFANG (96% EV / 43.4M AuC)'];
      Plotly.newPlot('full-chart-triangle-polar', [
        {{ type: 'scatterpolar', r: [100, 100, 100, 100], theta: [...triCats, triCats[0]], fill: 'toself', fillcolor: 'rgba(180, 180, 180, 0.15)', line: {{ color: '#888888', dash: 'dash', width: 2 }}, name: 'Baseline Plan' }},
        {{ type: 'scatterpolar', r: [289.8, 115.6, 96.1, 289.8], theta: [...triCats, triCats[0]], fill: 'toself', fillcolor: 'rgba(192, 0, 0, 0.25)', line: {{ color: '#C00000', width: 3 }}, name: 'Faktisk Tilstand' }}
      ], {{ polar: {{ radialaxis: {{ visible: true, range: [0, 320], ticksuffix: '%' }} }}, legend: {{ orientation: 'h', y: -0.15 }}, margin: {{ l: 20, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});

      Plotly.newPlot('full-chart-triangle-frontier', [
        {{ y: ['1. Status Quo', '2. Lavrisiko PO-kutt (+15d)', '3. Technical Hold (+30d)', '4. Omfangsreduksjon (+60d)'], x: [107.2, 98.7, 89.0, 79.7], type: 'bar', orientation: 'h', name: 'Gjenværende Eksponering', marker: {{ color: '#2F5496' }} }},
        {{ y: ['1. Status Quo', '2. Lavrisiko PO-kutt (+15d)', '3. Technical Hold (+30d)', '4. Omfangsreduksjon (+60d)'], x: [0.0, 8.5, 18.2, 27.5], type: 'bar', orientation: 'h', name: 'Spart Likviditet', marker: {{ color: '#009E73' }} }}
      ], {{ barmode: 'stack', plot_bgcolor: 'white', legend: {{ orientation: 'h', y: -0.15 }}, margin: {{ l: 140, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});

      // 03 Gantt
      Plotly.newPlot('full-chart-gantt', [
        {{ x: ['2026-11-03', '2026-11-14', '2026-11-17', '2026-11-06', '2026-11-23', '2026-11-11', '2026-11-30'], 
          base: ['2026-01-05', '2026-01-08', '2026-01-11', '2026-01-14', '2026-01-17', '2026-01-20', '2026-11-01'], 
          y: [...wbsNames, 'ANBEFALT: 30d Technical Hold'], type: 'bar', orientation: 'h', 
          marker: {{ color: ['#2F5496', '#2F5496', '#C00000', '#2F5496', '#E69F00', '#E69F00', '#009E73'] }}, name: 'WBS Fremdrift' }}
      ], {{ 
        shapes: [{{ type: 'line', x0: '2026-10-31', x1: '2026-10-31', y0: 0, y1: 1, yref: 'paper', line: {{ color: '#C00000', width: 2, dash: 'dash' }} }}],
        annotations: [{{ x: '2026-10-31', y: 1, yref: 'paper', text: 'Status per 31.10.2026', showarrow: false, font: {{ color: '#C00000', size: 10 }}, xanchor: 'left' }}],
        plot_bgcolor: 'white', margin: {{ l: 140, r: 20, t: 10, b: 30 }} 
      }}, {{ responsive: true }});

      // 04 Bubble & Connected
      Plotly.newPlot('full-chart-bubble', [{{
        x: [1.12, 1.14, 1.17, 1.10, 1.24, 1.20], y: [0.33, 0.33, 0.33, 0.33, 0.33, 0.33],
        mode: 'markers+text',
        marker: {{ size: [25, 35, 60, 30, 26, 18], color: ['#2F5496', '#C00000', '#C00000', '#C00000', '#C00000', '#2F5496'] }},
        text: wbsNames, textposition: 'top center'
      }}], {{ xaxis: {{ title: 'SPI' }}, yaxis: {{ title: 'CPI' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 40 }} }}, {{ responsive: true }});

      Plotly.newPlot('full-chart-connected', [{{
        x: [0.64, 0.76, 1.06, 1.08, 1.12, 1.14, 1.13, 1.14, 1.15, 1.16],
        y: [0.21, 0.36, 0.49, 0.45, 0.43, 0.40, 0.37, 0.35, 0.34, 0.33],
        mode: 'lines+markers+text', line: {{ color: '#C00000', width: 2.5 }},
        text: ['Jan', 'Feb', 'Mar (Knekkpunkt)', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt'],
        textposition: 'top right'
      }}], {{ xaxis: {{ title: 'Akkumulert SPI' }}, yaxis: {{ title: 'Akkumulert CPI' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 40 }} }}, {{ responsive: true }});

      // 05 Vendor Rank
      Plotly.newPlot('full-chart-vendor-rank', [{{
        y: ['V010 (DE)', 'V003 (US)', 'V017 (SE)', 'V002 (DE)', 'V016 (NO)', 'V007 (US)', 'V020 (NO)', 'V006 (DE)'],
        x: [2.14, 2.88, 2.96, 3.28, 3.48, 3.78, 4.16, 4.36],
        type: 'bar', orientation: 'h', marker: {{ color: '#C00000' }},
        text: ['2.14M', '2.88M', '2.96M', '3.28M', '3.48M', '3.78M', '4.16M', '4.36M'], textposition: 'inside'
      }}], {{ xaxis: {{ title: 'Åpen Ulevert PO (MNOK)' }}, plot_bgcolor: 'white', margin: {{ l: 90, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});

      // 06 Dist Box & Hist
      Plotly.newPlot('full-chart-dist-box', [
        {{ y: [8, 8, 8, 7.5, 8, 12, 14, 16], type: 'box', name: 'CC-4100 Verksted', marker: {{ color: '#E69F00' }} }},
        {{ y: [7.5, 7.5, 8, 8, 7.5, 7.5, 10, 11], type: 'box', name: 'CC-4200 Lab', marker: {{ color: '#2F5496' }} }},
        {{ y: [8, 8, 8.5, 8, 12, 14, 15, 16], type: 'box', name: 'CC-4300 PMO', marker: {{ color: '#C00000' }} }}
      ], {{ yaxis: {{ title: 'Timer/uke' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 30 }} }}, {{ responsive: true }});

      Plotly.newPlot('full-chart-dist-hist', [{{
        x: [0.1, 0.1, 0.1, 0.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.9, 2.0],
        type: 'histogram', marker: {{ color: '#2F5496' }}
      }}], {{ xaxis: {{ title: 'PO Beløp (MNOK)' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 30 }} }}, {{ responsive: true }});

      // 07 Part to Whole Tree & Stacked
      Plotly.newPlot('full-chart-ptw-tree', [{{
        type: 'treemap',
        labels: ['GreenPilot', 'WBS-100 PMO', 'WBS-200 Prosess', 'WBS-300 Reaktor', 'WBS-400 Infra', 'WBS-500 Elektro', 'WBS-600 Test'],
        parents: ['', 'GreenPilot', 'GreenPilot', 'GreenPilot', 'GreenPilot', 'GreenPilot', 'GreenPilot'],
        values: [107.2, 11.37, 17.00, 51.64, 13.91, 9.40, 3.88],
        marker: {{ colors: ['#595959', '#2F5496', '#C00000', '#C00000', '#C00000', '#C00000', '#2F5496'] }}
      }}], {{ margin: {{ l: 10, r: 10, t: 10, b: 10 }} }}, {{ responsive: true }});

      Plotly.newPlot('full-chart-ptw-stacked', [
        {{ x: ['BAC (20M)', 'AC (58M)', 'EXP (107M)'], y: [70, 74.8, 85.8], type: 'bar', name: 'Balanseført AuC', marker: {{ color: '#2F5496' }} }},
        {{ x: ['BAC (20M)', 'AC (58M)', 'EXP (107M)'], y: [30, 25.2, 14.2], type: 'bar', name: 'Driftsført FoU', marker: {{ color: '#595959' }} }}
      ], {{ barmode: 'stack', yaxis: {{ ticksuffix: '%' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});

      // 08 Sankey
      Plotly.newPlot('full-chart-sankey', [{{
        type: 'sankey',
        node: {{
          pad: 15, thickness: 20, line: {{ color: 'black', width: 0.5 }},
          label: ["WBS-100 PMO", "WBS-200 Prosess", "WBS-300 Reaktor", "WBS-400 Infra", "WBS-500 Elektro", "WBS-600 Test", "Bokført AC (58.0M)", "Åpne PO-er (49.2M)", "Balanseført AuC (43.4M)", "Resultatført FoU (14.6M)", "Kansellerbar PO (18.2M)", "Låst PO (31.0M)"],
          color: ["#2F5496", "#2F5496", "#C00000", "#2F5496", "#2F5496", "#2F5496", "#C00000", "#E69F00", "#C00000", "#595959", "#009E73", "#800000"]
        }},
        link: {{
          source: [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5, 6, 6, 7, 7],
          target: [6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 8, 9, 10, 11],
          value: [7.25, 10.15, 23.19, 8.70, 5.80, 2.88, 4.12, 6.85, 28.45, 5.21, 3.60, 1.00, 43.38, 14.59, 18.20, 31.03]
        }}
      }}], {{ margin: {{ l: 20, r: 20, t: 10, b: 20 }} }}, {{ responsive: true }});

      // 09 Fan Chart
      Plotly.newPlot('full-chart-fan', [
        {{ x: ['Okt', 'Nov', 'Des', 'Jan 27', 'Feb 27', 'Feb 27', 'Jan 27', 'Des', 'Nov', 'Okt'], y: [57.97, 75.0, 94.0, 114.0, 132.5, 89.0, 78.0, 68.0, 60.5, 57.97], fill: 'toself', fillcolor: 'rgba(192,0,0,0.18)', line: {{ color: 'transparent' }}, name: 'P10-P90 Utfallsrom' }},
        {{ x: ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt'], y: [4.65, 7.03, 10.44, 15.34, 21.46, 29.35, 35.80, 42.78, 50.43, 57.97], mode: 'lines+markers', line: {{ color: '#2F5496', width: 3 }}, name: 'Historisk AC' }},
        {{ x: ['Okt', 'Nov', 'Des', 'Jan 27', 'Feb 27'], y: [57.97, 60.5, 68.0, 78.0, 89.0], line: {{ color: '#009E73', width: 3 }}, name: 'P10: 30d Hold (89M)' }},
        {{ x: ['Okt', 'Nov', 'Des', 'Jan 27', 'Feb 27'], y: [57.97, 66.0, 78.5, 93.0, 107.2], line: {{ color: '#C00000', dash: 'dash', width: 2.5 }}, name: 'P50: Status Quo (107,2M)' }},
        {{ x: ['Okt', 'Nov', 'Des', 'Jan 27', 'Feb 27'], y: [57.97, 75.0, 94.0, 114.0, 132.5], line: {{ color: '#800000', dash: 'dot', width: 2 }}, name: 'P90: Eskalering (132,5M)' }}
      ], {{ 
        yaxis: {{ title: 'MNOK' }}, 
        shapes: [{{ type: 'line', x0: 'Jan', x1: 'Feb 27', y0: 20.0, y1: 20.0, line: {{ color: '#555555', dash: 'dash' }} }}],
        annotations: [{{ x: 'Okt', y: 20.0, text: 'BAC Budsjett: 20,0 MNOK', showarrow: false, yanchor: 'bottom', font: {{ size: 10, color: '#555' }} }}],
        plot_bgcolor: 'white', legend: {{ orientation: 'h', y: -0.2 }}, margin: {{ l: 40, r: 20, t: 20, b: 40 }} 
      }}, {{ responsive: true }});

      // 10 Waterfall
      Plotly.newPlot('full-chart-waterfall', [{{
        type: 'waterfall', orientation: 'v',
        x: ["BAC", "WBS-100", "WBS-200", "WBS-300", "WBS-400", "WBS-500/600", "Bokført AC", "Uleverte PO", "Total Eksponering"],
        y: [20.0, 4.75, 6.65, 15.19, 5.70, 5.68, 57.97, 49.23, 107.20],
        measure: ["relative", "relative", "relative", "relative", "relative", "relative", "total", "relative", "total"],
        increasing: {{ marker: {{ color: "#C00000" }} }},
        totals: {{ marker: {{ color: "#1F4E79" }} }}
      }}], {{ yaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 30 }} }}, {{ responsive: true }});

      // 11 Cash & Cost Centers
      Plotly.newPlot('full-chart-cashflow', [
        {{ x: ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt'], y: [0.45, 2.79, 5.27, 4.98, 5.89, 7.45, 8.10, 6.75, 7.45, 7.85], type: 'bar', name: 'Utbetalt (MNOK)', marker: {{ color: '#C00000' }} }},
        {{ x: ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt'], y: [0, 0, 0, 0, 0, 3.0, 0, 0, 0, 0], type: 'bar', name: 'Enova Tilskudd', marker: {{ color: '#009E73' }} }}
      ], {{ yaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});

      Plotly.newPlot('full-chart-costcenters', [{{
        y: ['CC-4100 Verksted', 'CC-4200 Lab', 'CC-4300 PMO'], x: [3379.5, 2999.0, 3394.0], type: 'bar', orientation: 'h',
        marker: {{ color: ['#E69F00', '#2F5496', '#C00000'] }},
        text: ['3 380t (1,79M)', '2 999t (1,59M)', '3 394t (1,80M)'], textposition: 'inside'
      }}], {{ xaxis: {{ title: 'Faktiske Timer' }}, plot_bgcolor: 'white', margin: {{ l: 110, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});

      // 12 Simulator Initial
      updateFullSim();

      // =======================================================================
      // ALSO INITIALIZE ORIGINAL ARCHIVE CHARTS IF PRESENT
      // =======================================================================
      try {{
        // Exec Bar
        if (document.getElementById('chart-exec-bar')) {{
          Plotly.newPlot('chart-exec-bar', [{{
            x: ["Budsjett (BAC)", "Opptjent (EV)", "Påløpt (AC)", "Total Eksponering"],
            y: [20.0, 19.2, 58.0, 107.2],
            type: 'bar',
            marker: {{ color: ["#595959", "#2F5496", "#C00000", "#800000"] }},
            text: ["20.0M", "19.2M", "58.0M", "107.2M"],
            textposition: 'outside'
          }}], {{ yaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 30 }} }}, {{ responsive: true }});
        }}
        // CV / SV
        if (document.getElementById('chart-cv-bars')) {{
          Plotly.newPlot('chart-cv-bars', [{{
            y: wbsNames, x: [-4.85, -6.78, -15.51, -5.82, -3.88, -1.92], type: 'bar', orientation: 'h',
            marker: {{ color: '#C00000' }}, text: ['-4.85M', '-6.78M', '-15.51M', '-5.82M', '-3.88M', '-1.92M'], textposition: 'inside'
          }}], {{ xaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 90, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});
        }}
        if (document.getElementById('chart-sv-bars')) {{
          Plotly.newPlot('chart-sv-bars', [{{
            y: wbsNames, x: [0.25, 0.41, 1.14, 0.26, 0.37, 0.16], type: 'bar', orientation: 'h',
            marker: {{ color: '#009E73' }}, text: ['+0.25M', '+0.41M', '+1.14M', '+0.26M', '+0.37M', '+0.16M'], textposition: 'inside'
          }}], {{ xaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 90, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});
        }}
        // Polar
        if (document.getElementById('chart-triangle-polar')) {{
          Plotly.newPlot('chart-triangle-polar', [
            {{ type: 'scatterpolar', r: [100, 100, 100, 100], theta: [...triCats, triCats[0]], fill: 'toself', fillcolor: 'rgba(180, 180, 180, 0.15)', line: {{ color: '#888888', dash: 'dash', width: 2 }}, name: 'Baseline Plan' }},
            {{ type: 'scatterpolar', r: [289.8, 115.6, 96.1, 289.8], theta: [...triCats, triCats[0]], fill: 'toself', fillcolor: 'rgba(192, 0, 0, 0.25)', line: {{ color: '#C00000', width: 3 }}, name: 'Faktisk Tilstand' }}
          ], {{ polar: {{ radialaxis: {{ visible: true, range: [0, 320], ticksuffix: '%' }} }}, legend: {{ orientation: 'h', y: -0.15 }}, margin: {{ l: 20, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});
        }}
        if (document.getElementById('chart-triangle-frontier')) {{
          Plotly.newPlot('chart-triangle-frontier', [
            {{ y: ['1. Status Quo', '2. Lavrisiko PO-kutt (+15d)', '3. Technical Hold (+30d)', '4. Omfangsreduksjon (+60d)'], x: [107.2, 98.7, 89.0, 79.7], type: 'bar', orientation: 'h', name: 'Gjenværende Eksponering', marker: {{ color: '#2F5496' }} }},
            {{ y: ['1. Status Quo', '2. Lavrisiko PO-kutt (+15d)', '3. Technical Hold (+30d)', '4. Omfangsreduksjon (+60d)'], x: [0.0, 8.5, 18.2, 27.5], type: 'bar', orientation: 'h', name: 'Spart Likviditet', marker: {{ color: '#009E73' }} }}
          ], {{ barmode: 'stack', plot_bgcolor: 'white', legend: {{ orientation: 'h', y: -0.15 }}, margin: {{ l: 140, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});
        }}
        // Gantt
        if (document.getElementById('chart-gantt')) {{
          Plotly.newPlot('chart-gantt', [
            {{ x: ['2026-11-03', '2026-11-14', '2026-11-17', '2026-11-06', '2026-11-23', '2026-11-11'], base: ['2026-01-05', '2026-01-08', '2026-01-11', '2026-01-14', '2026-01-17', '2026-01-20'], y: wbsNames, type: 'bar', orientation: 'h', marker: {{ color: ['#2F5496', '#2F5496', '#C00000', '#2F5496', '#E69F00', '#E69F00'] }}, name: 'WBS Fremdrift' }}
          ], {{ plot_bgcolor: 'white', margin: {{ l: 120, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});
        }}
        // Bubble / Connected
        if (document.getElementById('chart-bubble')) {{
          Plotly.newPlot('chart-bubble', [{{
            x: [1.12, 1.14, 1.17, 1.10, 1.24, 1.20], y: [0.33, 0.33, 0.33, 0.33, 0.33, 0.33],
            mode: 'markers+text',
            marker: {{ size: [25, 35, 60, 30, 26, 18], color: ['#2F5496', '#C00000', '#C00000', '#C00000', '#C00000', '#2F5496'] }},
            text: wbsNames, textposition: 'top center'
          }}], {{ xaxis: {{ title: 'SPI' }}, yaxis: {{ title: 'CPI' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 40 }} }}, {{ responsive: true }});
        }}
        if (document.getElementById('chart-connected')) {{
          Plotly.newPlot('chart-connected', [{{
            x: [0.64, 0.76, 1.06, 1.08, 1.12, 1.14, 1.13, 1.14, 1.15, 1.16],
            y: [0.21, 0.36, 0.49, 0.45, 0.43, 0.40, 0.37, 0.35, 0.34, 0.33],
            mode: 'lines+markers+text', line: {{ color: '#C00000', width: 2.5 }},
            text: ['Jan', 'Feb', 'Mar (Knekkpunkt)', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt'],
            textposition: 'top right'
          }}], {{ xaxis: {{ title: 'Akkumulert SPI' }}, yaxis: {{ title: 'Akkumulert CPI' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 40 }} }}, {{ responsive: true }});
        }}
        // Vendor Rank
        if (document.getElementById('chart-vendor-rank')) {{
          Plotly.newPlot('chart-vendor-rank', [{{
            y: ['V010 (DE)', 'V003 (US)', 'V017 (SE)', 'V002 (DE)', 'V016 (NO)', 'V007 (US)', 'V020 (NO)', 'V006 (DE)'],
            x: [2.14, 2.88, 2.96, 3.28, 3.48, 3.78, 4.16, 4.36],
            type: 'bar', orientation: 'h', marker: {{ color: '#C00000' }}
          }}], {{ xaxis: {{ title: 'Åpen PO (MNOK)' }}, plot_bgcolor: 'white', margin: {{ l: 90, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});
        }}
        // Dist
        if (document.getElementById('chart-dist-box')) {{
          Plotly.newPlot('chart-dist-box', [
            {{ y: [8, 8, 8, 7.5, 8, 12, 14, 16], type: 'box', name: 'CC-4100 Verksted', marker: {{ color: '#E69F00' }} }},
            {{ y: [7.5, 7.5, 8, 8, 7.5, 7.5, 10, 11], type: 'box', name: 'CC-4200 Lab', marker: {{ color: '#2F5496' }} }},
            {{ y: [8, 8, 8.5, 8, 12, 14, 15, 16], type: 'box', name: 'CC-4300 PMO', marker: {{ color: '#C00000' }} }}
          ], {{ yaxis: {{ title: 'Timer/uke' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 30 }} }}, {{ responsive: true }});
        }}
        if (document.getElementById('chart-dist-hist')) {{
          Plotly.newPlot('chart-dist-hist', [{{
            x: [0.1, 0.1, 0.1, 0.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.9, 2.0],
            type: 'histogram', marker: {{ color: '#2F5496' }}
          }}], {{ xaxis: {{ title: 'PO Beløp (MNOK)' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 30 }} }}, {{ responsive: true }});
        }}
        // PTW
        if (document.getElementById('chart-ptw-tree')) {{
          Plotly.newPlot('chart-ptw-tree', [{{
            type: 'treemap',
            labels: ['GreenPilot', 'WBS-100 PMO', 'WBS-200 Prosess', 'WBS-300 Reaktor', 'WBS-400 Infra', 'WBS-500 Elektro', 'WBS-600 Test'],
            parents: ['', 'GreenPilot', 'GreenPilot', 'GreenPilot', 'GreenPilot', 'GreenPilot', 'GreenPilot'],
            values: [107.2, 11.37, 17.00, 51.64, 13.91, 9.40, 3.88],
            marker: {{ colors: ['#595959', '#2F5496', '#C00000', '#C00000', '#C00000', '#C00000', '#2F5496'] }}
          }}], {{ margin: {{ l: 10, r: 10, t: 10, b: 10 }} }}, {{ responsive: true }});
        }}
        if (document.getElementById('chart-ptw-stacked')) {{
          Plotly.newPlot('chart-ptw-stacked', [
            {{ x: ['BAC (20M)', 'AC (58M)', 'EXP (107M)'], y: [70, 74.8, 85.8], type: 'bar', name: 'Balanseført AuC', marker: {{ color: '#2F5496' }} }},
            {{ x: ['BAC (20M)', 'AC (58M)', 'EXP (107M)'], y: [30, 25.2, 14.2], type: 'bar', name: 'Driftsført FoU', marker: {{ color: '#595959' }} }}
          ], {{ barmode: 'stack', yaxis: {{ ticksuffix: '%' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});
        }}
        // Sankey
        if (document.getElementById('chart-sankey')) {{
          Plotly.newPlot('chart-sankey', [{{
            type: 'sankey',
            node: {{
              pad: 15, thickness: 20, line: {{ color: 'black', width: 0.5 }},
              label: ["WBS-100 PMO", "WBS-200 Prosess", "WBS-300 Reaktor", "WBS-400 Infra", "WBS-500 Elektro", "WBS-600 Test", "Bokført AC (58.0M)", "Åpne PO-er (49.2M)", "Balanseført AuC (43.4M)", "Resultatført FoU (14.6M)", "Kansellerbar PO (18.2M)", "Låst PO (31.0M)"],
              color: ["#2F5496", "#2F5496", "#C00000", "#2F5496", "#2F5496", "#2F5496", "#C00000", "#E69F00", "#C00000", "#595959", "#009E73", "#800000"]
            }},
            link: {{
              source: [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5, 6, 6, 7, 7],
              target: [6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 8, 9, 10, 11],
              value: [7.25, 10.15, 23.19, 8.70, 5.80, 2.88, 4.12, 6.85, 28.45, 5.21, 3.60, 1.00, 43.38, 14.59, 18.20, 31.03]
            }}
          }}], {{ margin: {{ l: 20, r: 20, t: 10, b: 20 }} }}, {{ responsive: true }});
        }}
        // Fan
        if (document.getElementById('chart-fan')) {{
          Plotly.newPlot('chart-fan', [
            {{ x: ['Okt', 'Nov', 'Des', 'Jan 27', 'Feb 27', 'Feb 27', 'Jan 27', 'Des', 'Nov', 'Okt'], y: [57.97, 75.0, 94.0, 114.0, 132.5, 89.0, 78.0, 68.0, 60.5, 57.97], fill: 'toself', fillcolor: 'rgba(192,0,0,0.18)', line: {{ color: 'transparent' }}, name: 'P10-P90 Utfallsrom' }},
            {{ x: ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt'], y: [4.65, 7.03, 10.44, 15.34, 21.46, 29.35, 35.80, 42.78, 50.43, 57.97], mode: 'lines+markers', line: {{ color: '#2F5496', width: 3 }}, name: 'Historisk AC' }},
            {{ x: ['Okt', 'Nov', 'Des', 'Jan 27', 'Feb 27'], y: [57.97, 60.5, 68.0, 78.0, 89.0], line: {{ color: '#009E73', width: 3 }}, name: 'P10: 30d Hold (89M)' }},
            {{ x: ['Okt', 'Nov', 'Des', 'Jan 27', 'Feb 27'], y: [57.97, 66.0, 78.5, 93.0, 107.2], line: {{ color: '#C00000', dash: 'dash', width: 2.5 }}, name: 'P50: Status Quo (107,2M)' }},
            {{ x: ['Okt', 'Nov', 'Des', 'Jan 27', 'Feb 27'], y: [57.97, 75.0, 94.0, 114.0, 132.5], line: {{ color: '#800000', dash: 'dot', width: 2 }}, name: 'P90: Eskalering (132,5M)' }}
          ], {{ yaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', legend: {{ orientation: 'h', y: -0.2 }}, margin: {{ l: 40, r: 20, t: 20, b: 40 }} }}, {{ responsive: true }});
        }}
        // Waterfall
        if (document.getElementById('chart-waterfall')) {{
          Plotly.newPlot('chart-waterfall', [{{
            type: 'waterfall', orientation: 'v',
            x: ["BAC", "WBS-100", "WBS-200", "WBS-300", "WBS-400", "WBS-500/600", "Bokført AC", "Uleverte PO", "Total Eksponering"],
            y: [20.0, 4.75, 6.65, 15.19, 5.70, 5.68, 57.97, 49.23, 107.20],
            measure: ["relative", "relative", "relative", "relative", "relative", "relative", "total", "relative", "total"],
            increasing: {{ marker: {{ color: "#C00000" }} }},
            totals: {{ marker: {{ color: "#1F4E79" }} }}
          }}], {{ yaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 30 }} }}, {{ responsive: true }});
        }}
        // Cashflow
        if (document.getElementById('chart-cashflow')) {{
          Plotly.newPlot('chart-cashflow', [
            {{ x: ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt'], y: [0.45, 2.79, 5.27, 4.98, 5.89, 7.45, 8.10, 6.75, 7.45, 7.85], type: 'bar', name: 'Utbetalt (MNOK)', marker: {{ color: '#C00000' }} }},
            {{ x: ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt'], y: [0, 0, 0, 0, 0, 3.0, 0, 0, 0, 0], type: 'bar', name: 'Enova Tilskudd', marker: {{ color: '#009E73' }} }}
          ], {{ yaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});
        }}
        if (document.getElementById('chart-costcenters')) {{
          Plotly.newPlot('chart-costcenters', [{{
            y: ['CC-4100 Verksted', 'CC-4200 Lab', 'CC-4300 PMO'], x: [3379.5, 2999.0, 3394.0], type: 'bar', orientation: 'h',
            marker: {{ color: ['#E69F00', '#2F5496', '#C00000'] }}
          }}], {{ xaxis: {{ title: 'Faktiske Timer' }}, plot_bgcolor: 'white', margin: {{ l: 110, r: 20, t: 10, b: 30 }} }}, {{ responsive: true }});
        }}
        // Sim archive
        if (typeof updateSim === 'function') {{
          updateSim();
        }}
      }} catch (e) {{
        console.warn("Archive plot init note:", e);
      }}
    }});

    // -------------------------------------------------------------------------
    // FULL-VIEW SIMULATOR LOGIC
    // -------------------------------------------------------------------------
    function updateFullSim() {{
      const poCut = parseFloat(document.getElementById('full-slider-pocut').value);
      const impairPct = parseFloat(document.getElementById('full-slider-impair').value);
      document.getElementById('full-val-pocut').innerText = poCut + '%';
      document.getElementById('full-val-impair').innerText = impairPct + '%';

      const baseExp = 107.20;
      const openPo = 49.23;
      const baseAuc = 43.38;

      const saved = openPo * (poCut / 100);
      const newExp = baseExp - saved;
      const impairLoss = baseAuc * (impairPct / 100);

      document.getElementById('full-sim-saved').innerText = '+' + saved.toFixed(2) + ' MNOK';
      document.getElementById('full-sim-newexp').innerText = newExp.toFixed(2) + ' MNOK';
      document.getElementById('full-sim-loss').innerText = '-' + impairLoss.toFixed(2) + ' MNOK';

      Plotly.newPlot('full-chart-sim', [{{
        x: ['Nåværende Eksponering', 'Simulert Eksponering', 'Balanseført AuC', 'IAS 36 Tap'],
        y: [baseExp, newExp, baseAuc, impairLoss],
        type: 'bar',
        marker: {{ color: ['#800000', '#2F5496', '#595959', '#C00000'] }},
        text: [baseExp.toFixed(1) + 'M', newExp.toFixed(1) + 'M', baseAuc.toFixed(1) + 'M', impairLoss.toFixed(1) + 'M'],
        textposition: 'outside'
      }}], {{ yaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 30 }} }}, {{ responsive: true }});
    }}

    // -------------------------------------------------------------------------
    // FULL-VIEW AI COPILOT LOGIC
    // -------------------------------------------------------------------------
    const KB = [
      {{
        title: "IAS 36 Impairment of Assets (SSOT)",
        cat: "Regnskap (IFRS)",
        match: ["ias 36", "verdifall", "tap", "nedskrivning", "off-ramp"],
        ans: "En budsjettsprekk på 536 % (EAC 107,2M mot BAC 20,0M) utløser en lovpålagt nedskrivningstest (IAS 36.12f). Prosjektet har balanseført <strong>43,38 MNOK i AuC</strong>. Hvis prosjektet termineres ved Gate 3, må hele dette beløpet tapsføres umiddelbart i Elkems konsernregnskap."
      }},
      {{
        title: "IAS 38 Immaterielle Eiendeler (SSOT)",
        cat: "Regnskap (IFRS)",
        match: ["ias 38", "balanseføring", "aktivering", "utvikling", "forskning"],
        ans: "Utviklingsutgifter i WBS-200, 300, 400 og 500 oppfyller de 6 kapitaliseringskriteriene under IAS 38.57 og er aktivert. WBS-100 PMO og WBS-600 Testkjøring er korrekt resultatført (P&L) som administrasjon og forskning."
      }},
      {{
        title: "ISA 805 & Enova Retningslinjer (SSOT)",
        cat: "Revisjon & Tilskudd",
        match: ["530", "enova", "isa 805", "timesats", "skattefunn", "timer"],
        ans: "Intern personalkostnad er oppad begrenset til en fast timesats på <strong>530 kr per time</strong> og maks 1 850 timer per år per person. Revisor skal attestere timelistene etter ISA 805. Overtid utover 530 kr/t dekkes 100 % av Elkem."
      }},
      {{
        title: "30 Dagers Technical Hold Løsningen (SSOT)",
        cat: "Styringstiltak",
        match: ["hold", "technical hold", "fryse", "pause", "tiltak", "vedtak", "gate 3"],
        ans: "Ved å innføre et 30 dagers Technical Hold ved Gate 3 pauses montasjen. Kontrollteamet gjennomfører kanselleringsaudit på de 49,2 MNOK i åpne innkjøpsordrer (forventet besparelse: <strong>18,2 MNOK</strong>) og capper samlet eksponering på 89,0 MNOK."
      }}
    ];

    function setFullQuery(q) {{
      document.getElementById('full-ai-query').value = q;
      runFullQuery();
    }}

    function runFullQuery() {{
      const q = document.getElementById('full-ai-query').value.toLowerCase().trim();
      const resBox = document.getElementById('full-ai-response');
      resBox.classList.remove('hidden');

      let bestMatch = null;
      let maxScore = 0;

      for (const item of KB) {{
        let score = 0;
        for (const kw of item.match) {{
          if (q.includes(kw)) score += 1;
        }}
        if (score > maxScore) {{
          maxScore = score;
          bestMatch = item;
        }}
      }}

      if (!bestMatch) {{
        bestMatch = {{
          title: "Generell Prosjektstatus & Styringsindikatorer (SSOT)",
          cat: "EVM Status",
          ans: "Prosjektet har påløpt <strong>57,97 MNOK</strong> mot en ramme på <strong>20,00 MNOK</strong>, med <strong>49,23 MNOK</strong> i åpne forpliktelser (total eksponering <strong>107,2 MNOK / 536 % av BAC</strong>). Styret anbefales å vedta 30 dagers Technical Hold for å redusere forpliktelsene med 18,2 MNOK."
        }};
      }}

      resBox.innerHTML = `
        <div class="flex items-center justify-between border-b border-blue-200 pb-2">
          <span class="font-bold text-blue-950 text-xs">${{bestMatch.title}}</span>
          <span class="bg-blue-200 text-blue-900 text-[10px] font-bold px-2 py-0.5 rounded">${{bestMatch.cat}}</span>
        </div>
        <p class="text-slate-800 text-xs mt-2">${{bestMatch.ans}}</p>
        <div class="mt-3 pt-2 border-t border-blue-100 text-[11px] text-slate-500">
          Grunner i: <code>05_erp_budget_baseline.csv</code>, <code>10_erp_gl_actuals.csv</code>, <code>06_erp_purchase_orders.csv</code> &amp; styrenotat.
        </div>
      `;
    }}

    // Archive simulation and query fallback
    function updateSim() {{
      const poCut = parseFloat(document.getElementById('slider-pocut')?.value || 37);
      const impairPct = parseFloat(document.getElementById('slider-impair')?.value || 25);
      if (document.getElementById('val-pocut')) document.getElementById('val-pocut').innerText = poCut;
      if (document.getElementById('val-impair')) document.getElementById('val-impair').innerText = impairPct;

      const baseExp = 107.20;
      const openPo = 49.23;
      const baseAuc = 43.38;

      const saved = openPo * (poCut / 100);
      const newExp = baseExp - saved;
      const impairLoss = baseAuc * (impairPct / 100);

      if (document.getElementById('sim-saved')) document.getElementById('sim-saved').innerText = '+' + saved.toFixed(2) + ' MNOK';
      if (document.getElementById('sim-newexp')) document.getElementById('sim-newexp').innerText = newExp.toFixed(2) + ' MNOK';
      if (document.getElementById('sim-loss')) document.getElementById('sim-loss').innerText = '-' + impairLoss.toFixed(2) + ' MNOK';

      if (document.getElementById('chart-sim')) {{
        Plotly.newPlot('chart-sim', [{{
          x: ['Nåværende Eksponering', 'Simulert Eksponering', 'Balanseført AuC', 'IAS 36 Tap'],
          y: [baseExp, newExp, baseAuc, impairLoss],
          type: 'bar',
          marker: {{ color: ['#800000', '#2F5496', '#595959', '#C00000'] }},
          text: [baseExp.toFixed(1) + 'M', newExp.toFixed(1) + 'M', baseAuc.toFixed(1) + 'M', impairLoss.toFixed(1) + 'M'],
          textposition: 'outside'
        }}], {{ yaxis: {{ title: 'MNOK' }}, plot_bgcolor: 'white', margin: {{ l: 40, r: 20, t: 20, b: 30 }} }}, {{ responsive: true }});
      }}
    }}

    function setQuery(q) {{
      if (document.getElementById('ai-query')) {{
        document.getElementById('ai-query').value = q;
        runQuery();
      }}
    }}

    function runQuery() {{
      const q = document.getElementById('ai-query')?.value?.toLowerCase() || '';
      const res = document.getElementById('ai-response');
      if (!res) return;
      res.classList.remove('hidden');

      if (q.includes('ias 36') || q.includes('verdifall') || q.includes('tap')) {{
        res.innerHTML = `<strong>IAS 36 Impairment of Assets (SSOT):</strong><br>
        En budsjettsprekk på 536 % (EAC 107,2M mot BAC 20,0M) utløser en lovpålagt nedskrivningstest (IAS 36.12f).
        Prosjektet har balanseført <strong>43,38 MNOK i AuC</strong>. Hvis prosjektet termineres ved Gate 3, må hele dette beløpet tapsføres umiddelbart i Elkems konsernregnskap.`;
      }} else if (q.includes('ias 38') || q.includes('balanseføring')) {{
        res.innerHTML = `<strong>IAS 38 Immaterielle Eiendeler (SSOT):</strong><br>
        Utviklingsutgifter i WBS-200, 300, 400 og 500 oppfyller de 6 kapitaliseringskriteriene under IAS 38.57 og er aktivert. WBS-100 PMO og WBS-600 Testkjøring er korrekt resultatført (P&L) som administrasjon og forskning.`;
      }} else if (q.includes('530') || q.includes('enova') || q.includes('isa 805') || q.includes('timesats')) {{
        res.innerHTML = `<strong>ISA 805 & Enova Retningslinjer (SSOT):</strong><br>
        Intern personalkostnad er oppad begrenset til en fast timesats på <strong>530 kr per time</strong> og maks 1 850 timer per år per person. Revisor skal attestere timelistene etter ISA 805. Overtid utover 530 kr/t dekkes 100 % av Elkem.`;
      }} else {{
        res.innerHTML = `<strong>Prosjektstatus (SSOT per 31.10.2026):</strong><br>
        Prosjektet har påløpt 57,97 MNOK mot en ramme på 20,00 MNOK, med 49,23 MNOK i åpne forpliktelser (total eksponering 107,2 MNOK / 536 % av BAC). Styret anbefales å vedta 30 dagers Technical Hold for å redusere forpliktelsene med 18,2 MNOK.`;
      }}
    }}
  </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print(" [OK] index.html vellykket regenerert med full visning av alle 14 moduler + opprinnelig arkiv i bunnen!")
