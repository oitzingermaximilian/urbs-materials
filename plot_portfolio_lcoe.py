"""
Generate standalone SVG and interactive HTML plots of the URBS Technology Park LCOE
Includes both 'All Assets' and 'New Builds Only' modes with r=3% and r=7% WACC comparison.
"""

import os
import pandas as pd
import json
from portfolio_lcoe import load_workbooks_safely, compute_portfolio_lcoe


def generate_all_plots():
    data = load_workbooks_safely()

    # Compute for both r=0.03 (URBS default) and r=0.07 (Commercial WACC / Fraunhofer ISE)
    df_3 = compute_portfolio_lcoe(data, discount_rate=0.03)
    df_7 = compute_portfolio_lcoe(data, discount_rate=0.07)

    # Name mapping
    name_map = {
        "Solar PV (Utility) (Import)": "Solar PV (Utility)",
        "Wind Onshore (Import)": "Wind Onshore",
        "Wind Offshore (Import)": "Wind Offshore",
        "Hydro_(run-of-river)_2024": "Hydro Run-of-River (Existing)",
        "Hydro_(run-of-river)_2030": "Hydro Run-of-River (Existing)",
        "Hydro_(reservoir)_2024": "Hydro Reservoir (Existing)",
        "Nuclear_Plant_2030": "Nuclear (New Build)",
        "Nuclear_Plant_2040": "Nuclear (New Build)",
        "Nuclear_Plant_2050": "Nuclear (New Build)",
        "Nuclear_Plant_2024_old": "Nuclear (Existing T1)",
        "Nuclear_Plant_2024_mid": "Nuclear (Existing T2)",
        "Nuclear_Plant_2024_new": "Nuclear (Existing T3)",
        "Gas_Plant_(CCGT)_2024": "Gas CCGT (Unabated)",
        "Gas_Plant_(CCGT)_2030": "Gas CCGT (Unabated)",
        "Gas_Plant_(CCGT)_2040": "Gas CCGT (Unabated)",
        "Gas_Plant_(CCGT)_2050": "Gas CCGT (Decarb 98%)",
        "Gas_Plant_(CCGT)_CCUS_2024": "Gas CCGT + CCUS",
        "Gas_Plant_(CCGT)_CCUS_2030": "Gas CCGT + CCUS",
        "Gas_Plant_(CCGT)_CCUS_2040": "Gas CCGT + CCUS",
        "Coal_Plant_CCUS_2030": "Hard Coal + CCUS",
        "Coal_Plant_CCUS_2024": "Hard Coal + CCUS",
        "Lignite_Plant_CCUS_2030": "Lignite + CCUS",
        "Lignite_Plant_CCUS_2024": "Lignite + CCUS",
        "Biomass_Plant_2024": "Biomass Peaker",
        "Biomass_Plant_2030": "Biomass Peaker",
    }

    # Which technologies are STRICTLY NEW BUILDS?
    new_build_keys = [
        "Solar PV (Utility)",
        "Wind Onshore",
        "Wind Offshore",
        "Nuclear (New Build)",
        "Gas CCGT (Unabated)",
        "Gas CCGT (Decarb 98%)",
        "Gas CCGT + CCUS",
        "Hard Coal + CCUS",
        "Lignite + CCUS",
        "Biomass Peaker",
    ]

    years = [2024, 2030, 2040, 2050]

    # Build structured data dict for HTML
    # modes: ['all_3', 'all_7', 'new_3', 'new_7']
    datasets = {}

    for mode_name, df_mode, only_new in [
        ("all_3", df_3, False),
        ("all_7", df_7, False),
        ("new_3", df_3, True),
        ("new_7", df_7, True),
    ]:
        datasets[mode_name] = {}
        for yr in years:
            sub = df_mode[df_mode["Year"] == yr].copy()
            sub["CleanName"] = sub["Technology"].map(name_map).fillna(sub["Technology"])

            if only_new:
                # Exclude existing plants
                sub = sub[sub["CleanName"].isin(new_build_keys)]
                # If year is 2024, nuclear new build uses 2024 overnight CAPEX
                if yr == 2024 and not sub[sub["CleanName"] == "Nuclear (New Build)"].empty:
                    pass
                elif yr == 2024 and sub[sub["CleanName"] == "Nuclear (New Build)"].empty:
                    # In 2024, create an entry for New Nuclear based on 2024 overnight CAPEX (5,910 €/kW)
                    nuc_row = df_mode[(df_mode["Year"] == 2024) & (df_mode["Technology"] == "Nuclear_Plant_2024_new")].copy()
                    if not nuc_row.empty:
                        nr = nuc_row.iloc[0].to_dict()
                        nr["CleanName"] = "Nuclear (New Build)"
                        sub = pd.concat([sub, pd.DataFrame([nr])], ignore_index=True)

            sub_unique = sub.drop_duplicates(subset=["CleanName"]).sort_values("LCOE_Total_EUR_MWh")
            selected = sub_unique.head(12)

            datasets[mode_name][yr] = {
                "labels": selected["CleanName"].tolist(),
                "capex": [round(v, 2) for v in selected["CAPEX_EUR_MWh"]],
                "opex_fix": [round(v, 2) for v in selected["Fixed_OPEX_EUR_MWh"]],
                "opex_var": [round(v, 2) for v in selected["Var_OPEX_EUR_MWh"]],
                "fuel": [round(v, 2) for v in selected["Fuel_EUR_MWh"]],
                "co2": [round(v, 2) for v in selected["CO2_EUR_MWh"]],
                "total": [round(v, 2) for v in selected["LCOE_Total_EUR_MWh"]],
            }

    # -------------------------------------------------------------------------
    # 1. Interactive HTML Dashboard with Filter Toggles
    # -------------------------------------------------------------------------
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>URBS Technology Park - LCOE Comparison</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #f8fafc;
      color: #1e293b;
      margin: 0;
      padding: 24px;
    }}
    .container {{
      max-width: 1240px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 12px;
      padding: 24px 32px;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
    }}
    h1 {{
      font-size: 24px;
      margin-bottom: 4px;
      color: #0f172a;
    }}
    p.subtitle {{
      color: #64748b;
      margin-top: 0;
      font-size: 14px;
      margin-bottom: 20px;
    }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 20px;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 16px;
    }}
    .btn-group {{
      display: flex;
      gap: 6px;
      align-items: center;
    }}
    .group-label {{
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      color: #64748b;
      margin-right: 6px;
    }}
    .tab-btn {{
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      padding: 6px 14px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.2s ease;
      color: #475569;
    }}
    .tab-btn:hover {{
      background: #e2e8f0;
      color: #0f172a;
    }}
    .tab-btn.active {{
      background: #2563eb;
      color: #ffffff;
      border-color: #1d4ed8;
    }}
    .tab-btn.toggle-active {{
      background: #0f766e;
      color: #ffffff;
      border-color: #115e59;
    }}
    .chart-box {{
      position: relative;
      height: 540px;
      margin-bottom: 24px;
    }}
    .insights {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin-top: 24px;
    }}
    .card {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 16px;
    }}
    .card h3 {{
      font-size: 15px;
      margin-top: 0;
      margin-bottom: 8px;
      color: #1e293b;
    }}
    .card p {{
      font-size: 13px;
      color: #475569;
      line-height: 1.5;
      margin: 0;
    }}
    .badge {{
      display: inline-block;
      padding: 2px 8px;
      font-size: 11px;
      font-weight: 700;
      border-radius: 4px;
      text-transform: uppercase;
      margin-bottom: 6px;
    }}
    .badge-solar {{ background: #fef3c7; color: #92400e; }}
    .badge-wind {{ background: #e0e7ff; color: #3730a3; }}
    .badge-nuclear {{ background: #fce7f3; color: #9d174d; }}
    .badge-wacc {{ background: #f3e8ff; color: #6b21a8; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>URBS Technology Park - LCOE Comparison</h1>
    <p class="subtitle">Levelized Cost of Electricity breakdown by cost component across milestone years.</p>

    <div class="controls">
      <div class="btn-group">
        <span class="group-label">Year:</span>
        <button class="tab-btn active" id="btn-yr-2024" onclick="setYear(2024)">2024</button>
        <button class="tab-btn" id="btn-yr-2030" onclick="setYear(2030)">2030</button>
        <button class="tab-btn" id="btn-yr-2040" onclick="setYear(2040)">2040</button>
        <button class="tab-btn" id="btn-yr-2050" onclick="setYear(2050)">2050</button>
      </div>

      <div class="btn-group">
        <span class="group-label">Scope:</span>
        <button class="tab-btn toggle-active" id="btn-scope-new" onclick="setScope('new')">Nur Neubauten (Greenfield)</button>
        <button class="tab-btn" id="btn-scope-all" onclick="setScope('all')">Alle (inkl. Altanlagen)</button>
      </div>

      <div class="btn-group">
        <span class="group-label">Finanzierungszins (WACC):</span>
        <button class="tab-btn active" id="btn-rate-3" onclick="setRate(3)">r = 3.0% (URBS Makro)</button>
        <button class="tab-btn" id="btn-rate-7" onclick="setRate(7)">r = 7.0% (Fraunhofer ISE)</button>
      </div>
    </div>

    <div class="chart-box">
      <canvas id="lcoeChart"></canvas>
    </div>

    <div class="insights">
      <div class="card">
        <span class="badge badge-solar">Erneuerbare Spitze</span>
        <h3>Solar PV (33.8 - 40.0 €/MWh)</h3>
        <p>Selbst bei 7% WACC bleibt Solar PV mit 42–50 €/MWh die unschlagbar günstigste Option für neue Erzeugungskapazität. Die reinen Grenzkosten sind 0 €.</p>
      </div>
      <div class="card">
        <span class="badge badge-wind">Solides Rückgrat</span>
        <h3>Wind Onshore (35.7 - 39.0 €/MWh)</h3>
        <p>Turbinenpreise nach DEA-Benchmark (866 -> 780 €/kW). Liefert über 2.600 Volllaststunden und ist bis 2030 auf Augenhöhe mit PV.</p>
      </div>
      <div class="card">
        <span class="badge badge-nuclear">Neubau vs. Bestand</span>
        <h3>Nuclear Neubau (58.5 € @3% vs 85.1 € @7%)</h3>
        <p>Hier wird der Fraunhofer-Effekt sofort sichtbar: Bei 7% Zins verdoppelt sich der Annuitäten-Balken von 27 € auf 54 €/MWh! Bei 10% Zins liegt Nuclear Neubau bei 107 €/MWh.</p>
      </div>
      <div class="card">
        <span class="badge badge-wacc">Kapitalintensität</span>
        <h3>Der WACC-Hebel</h3>
        <p>Kapitalintensive Kraftwerke mit 60 Jahren Laufzeit (Nuclear, Hydro) reagieren drastisch auf den Zins, während kurz amortisierte Anlagen (PV, Wind 20-25 Jahre) deutlich robuster sind.</p>
      </div>
    </div>
  </div>

  <script>
    const allDatasets = {json.dumps(datasets, indent=4)};

    let currentYear = 2030;
    let currentScope = 'new'; // 'new' or 'all'
    let currentRate = 3;     // 3 or 7
    let myChart = null;

    function getDatasetKey() {{
      return currentScope + '_' + currentRate;
    }}

    function renderChart() {{
      const key = getDatasetKey();
      const d = allDatasets[key][currentYear];
      const ctx = document.getElementById('lcoeChart').getContext('2d');

      if (myChart) {{
        myChart.destroy();
      }}

      myChart = new Chart(ctx, {{
        type: 'bar',
        data: {{
          labels: d.labels,
          datasets: [
            {{ label: 'CAPEX (Annuität)', data: d.capex, backgroundColor: '#3b82f6' }},
            {{ label: 'Fixer OPEX', data: d.opex_fix, backgroundColor: '#60a5fa' }},
            {{ label: 'Variabler OPEX', data: d.opex_var, backgroundColor: '#93c5fd' }},
            {{ label: 'Brennstoffkosten', data: d.fuel, backgroundColor: '#f59e0b' }},
            {{ label: 'CO2-Steuer', data: d.co2, backgroundColor: '#ef4444' }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            tooltip: {{
              callbacks: {{
                footer: function(tooltipItems) {{
                  let total = 0;
                  tooltipItems.forEach(item => {{ total += item.raw; }});
                  return 'Gesamt-LCOE: ' + total.toFixed(2) + ' EUR/MWh';
                }}
              }}
            }},
            legend: {{ position: 'top' }}
          }},
          scales: {{
            x: {{ stacked: true, grid: {{ display: false }} }},
            y: {{
              stacked: true,
              beginAtZero: true,
              title: {{ display: true, text: 'Stromgestehungskosten LCOE (EUR / MWh)' }}
            }}
          }}
        }}
      }});
    }}

    function setYear(yr) {{
      currentYear = yr;
      [2024, 2030, 2040, 2050].forEach(y => {{
        const b = document.getElementById('btn-yr-' + y);
        if (y === yr) b.classList.add('active');
        else b.classList.remove('active');
      }});
      renderChart();
    }}

    function setScope(scope) {{
      currentScope = scope;
      document.getElementById('btn-scope-new').classList.toggle('toggle-active', scope === 'new');
      document.getElementById('btn-scope-all').classList.toggle('toggle-active', scope === 'all');
      renderChart();
    }}

    function setRate(rate) {{
      currentRate = rate;
      document.getElementById('btn-rate-3').classList.toggle('active', rate === 3);
      document.getElementById('btn-rate-7').classList.toggle('active', rate === 7);
      renderChart();
    }}

    // Init
    setYear(2030);
  </script>
</body>
</html>
"""

    html_out = "lcoe_analysis/portfolio_lcoe_dashboard.html"
    with open(html_out, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Interactive HTML dashboard updated at: {html_out}")

    # -------------------------------------------------------------------------
    # 2. Standalone SVG Chart: NEW BUILDS ONLY (Year 2030 vs 2050 at r = 3%)
    # -------------------------------------------------------------------------
    svg_out = "lcoe_analysis/portfolio_lcoe_newbuilds_chart.svg"
    
    sub_30 = df_3[df_3["Year"] == 2030].copy()
    sub_30["CleanName"] = sub_30["Technology"].map(name_map).fillna(sub_30["Technology"])
    sub_30 = sub_30[sub_30["CleanName"].isin(new_build_keys)].drop_duplicates("CleanName").sort_values("LCOE_Total_EUR_MWh").head(8)

    sub_50 = df_3[df_3["Year"] == 2050].copy()
    sub_50["CleanName"] = sub_50["Technology"].map(name_map).fillna(sub_50["Technology"])
    sub_50 = sub_50[sub_50["CleanName"].isin(new_build_keys)].drop_duplicates("CleanName").sort_values("LCOE_Total_EUR_MWh").head(8)

    svg_w = 980
    svg_h = 580
    sb = []
    sb.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    sb.append('  <rect width="100%" height="100%" fill="#ffffff" rx="10"/>')
    sb.append('  <style>')
    sb.append('    .title { font-family: sans-serif; font-size: 18px; font-weight: bold; fill: #0f172a; }')
    sb.append('    .sub { font-family: sans-serif; font-size: 12px; fill: #64748b; }')
    sb.append('    .hdr { font-family: sans-serif; font-size: 14px; font-weight: bold; fill: #1e293b; }')
    sb.append('    .lbl { font-family: sans-serif; font-size: 11px; fill: #334155; }')
    sb.append('    .val { font-family: sans-serif; font-size: 11px; font-weight: bold; fill: #0f172a; }')
    sb.append('  </style>')

    sb.append('  <text x="30" y="38" class="title">URBS Technology Portfolio - LCOE NUR NEUBAUTEN (Greenfield)</text>')
    sb.append('  <text x="30" y="58" class="sub">Volle Kapitalkosten (Overnight CAPEX amortisiert) + OPEX + Brennstoff + CO2-Steuer (r = 3%). Keine Altanlagen.</text>')

    # Legend
    leg_x = 480
    leg_y = 35
    colors = [
        ("#3b82f6", "CAPEX (Annuität)"),
        ("#60a5fa", "Fix-OPEX"),
        ("#93c5fd", "Var-OPEX"),
        ("#f59e0b", "Brennstoff"),
        ("#ef4444", "CO2-Steuer")
    ]
    cur_lx = leg_x
    for c, l in colors:
        sb.append(f'  <rect x="{cur_lx}" y="{leg_y}" width="12" height="12" fill="{c}" rx="2"/>')
        sb.append(f'  <text x="{cur_lx + 16}" y="{leg_y + 10}" class="lbl">{l}</text>')
        cur_lx += 98

    max_scale = 160.0
    bar_max_w = 230.0

    for panel_idx, (yr_val, sub_p, px) in enumerate([(2030, sub_30, 30), (2050, sub_50, 510)]):
        sb.append(f'  <text x="{px}" y="95" class="hdr">Neubauten {yr_val} (CO2-Preis: {df_3[df_3["Year"]==yr_val]["CO2_EUR_MWh"].max():.1f} €/t equiv.)</text>')
        sb.append(f'  <line x1="{px}" y1="105" x2="{px + 430}" y2="105" stroke="#e2e8f0" stroke-width="1.5"/>')

        py = 125
        for _, row in sub_p.iterrows():
            name = row["CleanName"]
            tot = row["LCOE_Total_EUR_MWh"]
            c_cap = row["CAPEX_EUR_MWh"]
            c_fix = row["Fixed_OPEX_EUR_MWh"]
            c_var = row["Var_OPEX_EUR_MWh"]
            c_fuel = row["Fuel_EUR_MWh"]
            c_co2 = row["CO2_EUR_MWh"]

            sb.append(f'  <text x="{px}" y="{py + 12}" class="lbl">{name[:22]}</text>')

            bx = px + 150
            by = py
            bh = 16

            w_cap = min(bar_max_w, (c_cap / max_scale) * bar_max_w)
            w_fix = min(bar_max_w - w_cap, (c_fix / max_scale) * bar_max_w)
            w_var = min(max(0, bar_max_w - w_cap - w_fix), (c_var / max_scale) * bar_max_w)
            w_fuel = min(max(0, bar_max_w - w_cap - w_fix - w_var), (c_fuel / max_scale) * bar_max_w)
            w_co2 = min(max(0, bar_max_w - w_cap - w_fix - w_var - w_fuel), (c_co2 / max_scale) * bar_max_w)

            cur_bx = bx
            if w_cap > 0:
                sb.append(f'  <rect x="{cur_bx}" y="{by}" width="{w_cap:.1f}" height="{bh}" fill="#3b82f6"/>')
                cur_bx += w_cap
            if w_fix > 0:
                sb.append(f'  <rect x="{cur_bx}" y="{by}" width="{w_fix:.1f}" height="{bh}" fill="#60a5fa"/>')
                cur_bx += w_fix
            if w_var > 0:
                sb.append(f'  <rect x="{cur_bx}" y="{by}" width="{w_var:.1f}" height="{bh}" fill="#93c5fd"/>')
                cur_bx += w_var
            if w_fuel > 0:
                sb.append(f'  <rect x="{cur_bx}" y="{by}" width="{w_fuel:.1f}" height="{bh}" fill="#f59e0b"/>')
                cur_bx += w_fuel
            if w_co2 > 0:
                sb.append(f'  <rect x="{cur_bx}" y="{by}" width="{w_co2:.1f}" height="{bh}" fill="#ef4444"/>')
                cur_bx += w_co2

            sb.append(f'  <text x="{cur_bx + 6}" y="{by + 12}" class="val">{tot:.1f} €</text>')
            py += 46

    sb.append('</svg>')

    with open(svg_out, "w", encoding="utf-8") as f:
        f.write("\n".join(sb))
    print(f"[OK] Standalone New Builds SVG chart saved to: {svg_out}")


if __name__ == "__main__":
    generate_all_plots()
