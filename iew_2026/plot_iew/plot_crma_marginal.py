import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path

# ================= FORMATTING =================
plt.rcParams["font.family"] = "Arial"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

BASE_DIR = r"../../result/urbs-LR4-20260531T0833"
OUTPUT_DIR = os.path.join("", "processing_capacities")

YEARS_TO_PLOT = [2030, 2035, 2040]
BASELINE_YEAR = 2024

TECH_STAGE_MAP = {
    "solarPV": ["Polysilicon", "Wafer", "Cell", "Module"],
    "windon": ["BladeOn", "NacelleOn", "TowerOn"],
    "windoff": ["BladeOff", "NacelleOff", "TowerOff"],
}

QUOTAS = [35, 30, 25, 20, 15, 10, 5]
STEP_ORDER = ["Base_case"] + QUOTAS

# Colors
cmap = plt.cm.get_cmap('viridis', len(QUOTAS))
COLORS = {"Base_case": "#333333"}  # Dark grey for the anchor
for i, q in enumerate(QUOTAS):
    COLORS[q] = cmap(i)

def load_clean_data(file_path, tech_filter=None, stages=None):
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path, sheet_name="processing_capacities")
        cols = ["stf", "location", "tech"]
        df[[c for c in cols if c in df.columns]] = df[[c for c in cols if c in df.columns]].ffill()
        
        if tech_filter:
            df = df[df["tech"] == tech_filter].copy()
        if stages:
            df = df[df["stages"].isin(stages)].copy()
            
        df = df[df["stf"].isin(set(YEARS_TO_PLOT) | {BASELINE_YEAR})].copy()
        
        agg = df.groupby(["stf", "stages"])["capacity_processing_total"].sum().unstack()
        agg = agg.reindex(columns=stages).fillna(0)
        return agg
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def create_vertical_marginal_plot(tech, scenario_data, stages, output_dir=OUTPUT_DIR):
    fig, axs = plt.subplots(3, 1, figsize=(10, 18))
    axs = axs.flatten()

    global_max = 0
    for df in scenario_data.values():
        if df is not None:
            relevant_data = df[df.index.isin(YEARS_TO_PLOT)]
            if not relevant_data.empty:
                current_max = relevant_data.max().max()
                if current_max > global_max:
                    global_max = current_max

    y_limit = global_max * 1.35 if global_max > 0 else 1

    for i, year in enumerate(YEARS_TO_PLOT):
        ax = axs[i]
        ax.grid(axis="y", color="white", linestyle="-", linewidth=1.5, alpha=0.5, zorder=0)
        ax.set_axisbelow(True)
        ax.set_facecolor("#F0F0F0")

        n_stages = len(stages)
        n_scens = len(STEP_ORDER)
        
        total_width = 0.8
        gap = 0.015
        bar_width = (total_width - (n_scens - 1) * gap) / n_scens
        indices = np.arange(n_stages)

        for j, stage in enumerate(stages):
            center_x = indices[j]
            running_bottom = 0

            for k, scen_key in enumerate(STEP_ORDER):
                x_pos = center_x + (k - (n_scens - 1) / 2) * (bar_width + gap)
                color = COLORS[scen_key]

                df_scen = scenario_data.get(scen_key)
                current_val = df_scen.loc[year, stage] if (df_scen is not None and stage in df_scen.columns and year in df_scen.index) else 0

                if scen_key == "Base_case":
                    # Der Anker: Solider Balken von 0 bis Base_case
                    ax.bar(x_pos, current_val, width=bar_width,
                           color=color, edgecolor="black", linewidth=0.5, zorder=3)
                    
                    # Mark initial capacity (2024) with a yellow line
                    init_val = df_scen.loc[BASELINE_YEAR, stage] if (df_scen is not None and stage in df_scen.columns and BASELINE_YEAR in df_scen.index) else 0
                    if init_val > 0:
                        ax.plot([x_pos - bar_width / 2, x_pos + bar_width / 2], [init_val, init_val],
                                color="yellow", linewidth=2.5, zorder=4)
                        
                    running_bottom = current_val
                else:
                    # Delta zum Vorgänger in der STEP_ORDER
                    prev_scen_key = STEP_ORDER[k - 1]
                    df_prev = scenario_data.get(prev_scen_key)
                    prev_val = df_prev.loc[year, stage] if (df_prev is not None and stage in df_prev.columns and year in df_prev.index) else 0

                    delta = current_val - prev_val

                    if abs(delta) > 0.05:
                        hatch_bottom = prev_val
                        ax.bar(x_pos, delta, bottom=hatch_bottom, width=bar_width,
                               facecolor="white", edgecolor=color, hatch="////", linewidth=0.8, zorder=3)

                        prefix = "+" if delta > 0 else ""
                        ax.text(x_pos, current_val + (y_limit * 0.01) if delta > 0 else current_val - (y_limit * 0.03),
                                f"{prefix}{delta:.1f}", ha="center", va="bottom" if delta > 0 else "top",
                                fontsize=9, color=color, fontweight="bold", rotation=90)

                        # Hilfslinie vom Vorgänger zum aktuellen Delta
                        ax.plot([x_pos - (bar_width + gap), x_pos], [prev_val, prev_val],
                                color="gray", linestyle=":", linewidth=0.8, alpha=0.5, zorder=2)
                    else:
                        # Wenn kein Unterschied: flache Linie
                        ax.plot([x_pos - bar_width / 2, x_pos + bar_width / 2], [prev_val, prev_val],
                                color=color, linewidth=2, zorder=4)

        ax.set_title(f"{year}", fontweight="bold", fontsize=16)
        ax.set_xticks(indices)

        if i == 2:
            display_stages = [s.replace("On", "").replace("Off", "") for s in stages]
            ax.set_xticklabels(display_stages, fontweight="bold", fontsize=16)
        else:
            ax.set_xticklabels([])

        ax.set_ylim(0, y_limit)
        ax.tick_params(axis="y", labelsize=16)
        ax.set_ylabel("Processing Capacity (GW/yr)", fontweight="bold", fontsize=16)

    handles = []
    handles.append(mpatches.Patch(facecolor=COLORS["Base_case"], edgecolor="black", label="Base Case"))
    handles.append(Line2D([0], [0], color="yellow", linewidth=2.5, label="Initial Cap. (2024)"))
    for q in QUOTAS:
        c = COLORS[q]
        handles.append(mpatches.Patch(facecolor="white", hatch="////", edgecolor=c, label=f"CRMA {q}%"))

    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.02),
               ncol=4, frameon=True, fontsize=14)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.10, top=0.95, hspace=0.15)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_file = Path(output_dir) / f"Marginal_{tech}.pdf"
    plt.savefig(out_file, bbox_inches="tight")
    print(f"✅ Saved: {out_file}")
    plt.close()

def create_horizontal_absolute_plot(tech, scenario_data, stages, output_dir=OUTPUT_DIR):
    # Group by Stage, then Year
    # e.g. Polysilicon 2030, Polysilicon 2035, Polysilicon 2040, Wafer 2030...
    
    categories = []
    for stage in stages:
        for year in YEARS_TO_PLOT:
            categories.append((stage, year))
            
    n_groups = len(categories)
    n_scens = len(STEP_ORDER)
    
    fig, ax = plt.subplots(figsize=(12, max(8, n_groups * 0.8)))
    
    # White grid lines on light gray background
    ax.set_facecolor("#F0F0F0")
    ax.grid(axis="x", color="white", linestyle="-", linewidth=1.5, alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    
    bar_height = 0.8 / n_scens
    y_base = np.arange(n_groups)
    
    # Track max value for xlim
    max_val = 0
    
    for k, scen_key in enumerate(STEP_ORDER):
        color = COLORS[scen_key]
        df_scen = scenario_data.get(scen_key)
        
        # Calculate y positions for this scenario's bars
        # Scenarios are plotted from top to bottom within the group
        y_pos = y_base + (n_scens / 2 - k - 0.5) * bar_height
        
        vals = []
        for stage, year in categories:
            if df_scen is not None and stage in df_scen.columns and year in df_scen.index:
                val = df_scen.loc[year, stage]
            else:
                val = 0
            vals.append(val)
            
        max_val = max(max_val, max(vals))
        
        ax.barh(y_pos, vals, height=bar_height, color=color, edgecolor="black", linewidth=0.5, zorder=3)
        
    ax.set_yticks(y_base)
    yticklabels = [f"{stage.replace('On', '').replace('Off', '')} {year}" for stage, year in categories]
    ax.set_yticklabels(yticklabels, fontsize=12)
    
    # Add separating lines between stages
    for i in range(1, len(stages)):
        y_line = i * len(YEARS_TO_PLOT) - 0.5
        ax.axhline(y_line, color="black", linewidth=1.5, zorder=4)
        
    ax.set_xlabel("Processing Capacity (GW/yr)", fontweight="bold", fontsize=14)

    
    ax.set_xlim(0, max_val * 1.1 if max_val > 0 else 1)
    
    handles = []
    handles.append(mpatches.Patch(facecolor=COLORS["Base_case"], edgecolor="black", label="Base Case"))
    for q in QUOTAS:
        handles.append(mpatches.Patch(facecolor=COLORS[q], edgecolor="black", label=f"CRMA {q}%"))
        
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, 0.5), title="Scenarios", fontsize=12)
    
    plt.tight_layout()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_file = Path(output_dir) / f"Absolute_Horizontal_{tech}.pdf"
    plt.savefig(out_file, bbox_inches="tight")
    print(f"✅ Saved: {out_file}")
    plt.close()

def create_diverging_delta_plot(tech, scenario_data, stages, output_dir=OUTPUT_DIR):
    n_rows = len(stages)
    n_cols = len(YEARS_TO_PLOT)
    
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(3 * n_cols, 2.5 * n_rows), sharex='row', sharey=True)
    
    # Ensure axs is always 2D
    if n_rows == 1:
        axs = np.array([axs])
    if n_cols == 1:
        axs = np.array([[ax] for ax in axs])
        if n_rows == 1:
            axs = np.array([[axs[0]]])
            
    y_pos = np.arange(len(QUOTAS))
    df_base = scenario_data.get("Base_case")
    
    max_abs_deltas = [0] * n_rows
    
    for i, stage in enumerate(stages):
        for j, year in enumerate(YEARS_TO_PLOT):
            ax = axs[i, j]
            
            # Center line for divergence
            ax.axvline(0, color='black', linewidth=1.5, zorder=1)
            
            if df_base is not None and stage in df_base.columns and year in df_base.index:
                base_val = df_base.loc[year, stage]
                if abs(base_val) < 1e-6:
                    base_val = 0
            else:
                base_val = 0
                
            deltas = []
            colors_list = []
            
            for k, q in enumerate(QUOTAS):
                df_scen = scenario_data.get(q)
                if df_scen is not None and stage in df_scen.columns and year in df_scen.index:
                    scen_val = df_scen.loc[year, stage]
                    if abs(scen_val) < 1e-6:
                        scen_val = 0
                else:
                    scen_val = 0
                    
                delta = scen_val - base_val
                deltas.append(delta)
                colors_list.append(COLORS[q])
                
                if abs(delta) > max_abs_deltas[i]:
                    max_abs_deltas[i] = abs(delta)
                
            # Plot horizontal bars
            ax.barh(y_pos, deltas, color=colors_list, edgecolor='black', linewidth=0.5, zorder=2)
            
            if i == 0:
                ax.set_title(f"{year}", fontweight="bold", fontsize=18)
            if j == 0:
                display_stage = stage.replace("On", "").replace("Off", "")
                ax.set_ylabel(f"{display_stage}", fontweight="bold", fontsize=18)
                ax.set_yticks(y_pos)
                ax.set_yticklabels([f"S{q}" for q in QUOTAS], fontsize=14, weight="bold")
            
            ax.tick_params(axis='x', labelsize=14)
            ax.grid(axis='x', color='gray', linestyle='--', alpha=0.3, zorder=0)
            ax.set_axisbelow(True)
            
    # Invert Y axis so 35% is at the top
    axs[0, 0].invert_yaxis()
    
    # Enforce symmetric X-axis for each row so the Base Case (x=0) is exactly in the middle
    for i in range(n_rows):
        limit = max_abs_deltas[i] * 1.1 if max_abs_deltas[i] > 1e-6 else 1
        axs[i, 0].set_xlim(-limit, limit)
    
    fig.text(0.5, 0.02, "Δ Capacity vs. Base Case (GW/yr)", ha='center', fontweight="bold", fontsize=18)

    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_file = Path(output_dir) / f"Diverging_Delta_{tech}.pdf"
    plt.savefig(out_file, bbox_inches="tight")
    print(f"✅ Saved: {out_file}")
    plt.close()

def main():
    print("Loading data for all scenarios...")
    scenario_data = {}
    
    # 1. Load Base Case
    base_case_dir = os.path.join(BASE_DIR, "Base_Case")
    # Finding the xlsx file inside Base_Case (ignoring standard dumps)
    base_file = None
    if os.path.exists(base_case_dir):
        for f in os.listdir(base_case_dir):
            if f.endswith(".xlsx") and "pyomo" not in f and "dump" not in f:
                base_file = os.path.join(base_case_dir, f)
                break
                
    if base_file:
        print(f"Found Base_Case file: {base_file}")
    else:
        print("⚠️ Warning: Could not find valid Excel file in Base_Case folder.")

    # 2. Iterate per Tech
    for tech, stages in TECH_STAGE_MAP.items():
        print(f"\nProcessing {tech}...")
        tech_data = {}
        
        # Load Base_case for this tech
        if base_file:
            tech_data["Base_case"] = load_clean_data(base_file, tech_filter=tech, stages=stages)
            
        # Load CRMA quotas
        for q in QUOTAS:
            folder_name = f"scenario_solar_recycling_low_crma_{q}"
            file_name = f"{folder_name}.xlsx"
            file_path = os.path.join(BASE_DIR, folder_name, file_name)
            
            res = load_clean_data(file_path, tech_filter=tech, stages=stages)
            if res is not None:
                tech_data[q] = res
            else:
                print(f"   Missing data for CRMA {q}%")
                
        if "Base_case" in tech_data and any(q in tech_data for q in QUOTAS):
            create_vertical_marginal_plot(tech, tech_data, stages)
            create_horizontal_absolute_plot(tech, tech_data, stages)
            create_diverging_delta_plot(tech, tech_data, stages)
        else:
            print(f"   ❌ Skipping {tech} due to missing data.")

if __name__ == "__main__":
    main()
