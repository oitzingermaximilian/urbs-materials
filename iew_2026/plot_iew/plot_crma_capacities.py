import pandas as pd
import os
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import math
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# ================= FORMATTING =================
plt.rcParams["font.family"] = "Arial"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

BASE_DIR = r"../../result/urbs-LR4-20260531T0833"
OUTPUT_DIR = os.path.join("", "final_capacities")
YEARS_TO_PLOT = list(range(2025, 2041))

TECHS = {
    "solarPV": "Solar PV",
    "windon": "Onshore Wind",
    "windoff": "Offshore Wind"
}

TECH_COLORS = {
    "solarPV": "#E69F00",  # Orange
    "windon": "#66C2A5",   # Teal
    "windoff": "#00876C",  # Dark Green
}

QUOTAS = [5, 10, 15, 20, 25, 30, 35]

cmap = plt.cm.get_cmap('plasma', len(QUOTAS))
LINE_COLORS = {q: cmap(i) for i, q in enumerate(QUOTAS)}
LINE_COLORS["Base_case"] = "#333333"

def get_total_capacity(file_path, tech_filter):
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path, sheet_name="extension_only_totalcapacity")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    cols_to_fix = ["stf", "location", "tech"]
    existing_cols = [c for c in cols_to_fix if c in df.columns]
    df[existing_cols] = df[existing_cols].ffill()

    mask = df["tech"].astype(str).str.contains(tech_filter, case=False, na=False)
    val_col = "capacity_ext" if "capacity_ext" in df.columns else "capacity"
    
    if val_col in df.columns:
        capacity_series = df[mask].groupby("stf")[val_col].sum()
    else:
        val_col = df.select_dtypes(include=['number']).columns[-1]
        capacity_series = df[mask].groupby("stf")[val_col].sum()

    return capacity_series

def create_boxplot(tech_id, tech_label, scenarios_dict, output_dir):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor('white')
    ax.grid(axis='y', color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    
    base_series = scenarios_dict.get("Base_case")
    
    scen_data_by_year = {y: [] for y in YEARS_TO_PLOT}
    for q in QUOTAS:
        series = scenarios_dict.get(q)
        if series is not None:
            for y in YEARS_TO_PLOT:
                scen_data_by_year[y].append(series.loc[y])
                
    t_color = TECH_COLORS[tech_id]
    
    if base_series is not None:
        ax.bar(
            YEARS_TO_PLOT, 
            base_series.values, 
            color="#D3D3D3", 
            edgecolor="#555555",
            linewidth=1.5,
            alpha=0.6, 
            width=0.8,
            zorder=2,
            label="Base Case"
        )
    
    box_data = [scen_data_by_year[y] for y in YEARS_TO_PLOT]
    if any(len(d) > 0 for d in box_data):
        bp = ax.boxplot(
            box_data, 
            positions=YEARS_TO_PLOT, 
            widths=0.4,
            patch_artist=True,
            zorder=3,
            manage_ticks=False,
            showfliers=False
        )
        for box in bp['boxes']:
            box.set(facecolor=t_color, alpha=0.85, linewidth=1.5, edgecolor='#333333')
        for median in bp['medians']:
            median.set(color='#111111', linewidth=2)
        for whisker in bp['whiskers']:
            whisker.set(color='#333333', linewidth=1.5)
        for cap in bp['caps']:
            cap.set(color='#333333', linewidth=1.5)
    

    ax.set_ylabel("Total Installed Capacity (GW)", fontsize=18, labelpad=15, weight="bold")
    
    ax.set_xlim(2024.2, 2040.8)
    ax.set_xticks([2025, 2030, 2035, 2040])
    ax.set_xticklabels([2025, 2030, 2035, 2040], fontsize=16, weight="bold")
    ax.tick_params(axis="y", labelsize=16, length=6)
    ax.tick_params(axis="x", length=6)
    
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#333333')
        spine.set_linewidth(1.5)
    
    legend_elements = [
        Patch(facecolor='#D3D3D3', edgecolor='#555555', linewidth=1.5, alpha=0.6, label='Base Case'),
        Patch(facecolor=t_color, edgecolor='#333333', alpha=0.85, label='CRMA Scenarios (Range)'),
        Line2D([0], [0], color='#111111', lw=2, label='Scenario Median')
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True, facecolor='white', edgecolor='black', framealpha=1.0)
    
    plt.tight_layout()
    out_file = os.path.join(output_dir, f"Capacities_Boxplot_CRMA_{tech_id}.png")
    plt.savefig(out_file, dpi=500, bbox_inches="tight")
    plt.close(fig)

def create_line_plot(tech_id, tech_label, scenarios_dict, output_dir):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor('white')
    ax.grid(axis='y', color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    
    end_labels = []
    
    for q, series in scenarios_dict.items():
        if series is None: continue
        
        if q == "Base_case":
            label = "Base Case"
            linestyle = '--'
            linewidth = 3.0
            color = LINE_COLORS["Base_case"]
            zorder = 5
        else:
            label = f"CRMA {q}%"
            linestyle = '-'
            linewidth = 2.0
            color = LINE_COLORS[q]
            zorder = 3
            
        ax.plot(series.index, series.values, color=color, linestyle=linestyle, linewidth=linewidth, zorder=zorder)
        end_labels.append((series.values[-1], label, color))
            

    ax.set_ylabel("Total Installed Capacity (GW)", fontsize=18, labelpad=15, weight="bold")
    
    ax.set_xlim(2024.2, 2040.8)
    ax.set_xticks([2025, 2030, 2035, 2040])
    ax.set_xticklabels([2025, 2030, 2035, 2040], fontsize=16, weight="bold")
    ax.tick_params(axis="y", labelsize=16, length=6)
    ax.tick_params(axis="x", length=6)
    
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#333333')
        spine.set_linewidth(1.5)
        
    end_labels.sort(key=lambda x: x[0])
    for i, (val, label, color) in enumerate(end_labels):
        y_pos = val
        if i > 0:
            y_span = ax.get_ylim()[1] - ax.get_ylim()[0]
            min_dist = y_span * 0.03
            if y_pos - end_labels[i-1][0] < min_dist:
                y_pos = end_labels[i-1][0] + min_dist
        end_labels[i] = (y_pos, label, color)
        ax.text(2040.5, y_pos, label, color=color, fontweight="bold", fontsize=11, va="center")
    
    ax.set_xlim(2024.2, 2043.5)
    plt.tight_layout()
    out_file = os.path.join(output_dir, f"Capacities_Lineplot_CRMA_{tech_id}.png")
    plt.savefig(out_file, dpi=500, bbox_inches="tight")
    plt.close(fig)

def analyze_gradients(tech_label, scenarios_dict):
    intervals = [(2030, 2032), (2032, 2034), (2034, 2036), (2036, 2038), (2038, 2040)]
    rows = []
    
    for scen_name, series in scenarios_dict.items():
        if series is None or series.empty: continue
        
        row = {"Technology": tech_label, "Scenario": scen_name}
        for start_yr, end_yr in intervals:
            if start_yr in series.index and end_yr in series.index:
                val_start = series.loc[start_yr]
                val_end = series.loc[end_yr]
                
                dy = val_end - val_start
                dx = end_yr - start_yr
                slope = dy / dx # GW/yr
                degrees = math.degrees(math.atan(slope))
                
                row[f"Slope_{start_yr}_{end_yr}"] = round(slope, 3)
                row[f"Degrees_{start_yr}_{end_yr}"] = round(degrees, 2)
        rows.append(row)
    return rows

def plot_combined_heatmap(all_gradients, output_dir):
    df = pd.DataFrame(all_gradients)
    if df.empty: return
    
    intervals = ["2030_2032", "2032_2034", "2034_2036", "2036_2038", "2038_2040"]
    deg_cols = [f"Degrees_{interval}" for interval in intervals if f"Degrees_{interval}" in df.columns]
    
    if not deg_cols: return

    # Desired ordering
    scen_order = ["Base_case"] + [q for q in reversed(QUOTAS)]
    tech_order = ["Solar PV", "Onshore Wind", "Offshore Wind"]
    
    # Create an ordered categorization to ensure correct sorting
    df['Scenario'] = pd.Categorical(df['Scenario'], categories=scen_order, ordered=True)
    df['Technology'] = pd.Categorical(df['Technology'], categories=tech_order, ordered=True)
    df = df.sort_values(['Scenario', 'Technology'])
    
    # Create unified Y-axis labels
    y_labels = []
    for _, row in df.iterrows():
        s = row['Scenario']
        t = row['Technology']
        s_str = "Base Case" if s == "Base_case" else f"CRMA {s}%"
        y_labels.append(f"{s_str} | {t}")
        
    data = df[deg_cols].values
    display_cols = [c.replace("Degrees_", "").replace("_", "-") for c in deg_cols]
    
    fig, ax = plt.subplots(figsize=(10, max(6, len(y_labels)*0.35)))
    
    im = ax.imshow(data, cmap="RdBu", aspect="auto")
    
    max_abs = np.nanmax(np.abs(data))
    if max_abs == 0 or np.isnan(max_abs): max_abs = 1
    im.set_clim(-max_abs, max_abs)
    
    ax.set_xticks(np.arange(len(display_cols)))
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_xticklabels(display_cols, fontsize=11)
    ax.set_yticklabels(y_labels, fontsize=11)
    
    # Grid lines to separate scenarios
    ax.set_xticks(np.arange(-.5, len(display_cols), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(y_labels), 1), minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=0.5, alpha=0.5)
    
    # Thicker lines between different scenarios
    for i in range(len(y_labels)):
        if i % 3 == 0 and i > 0:
            ax.axhline(i - 0.5, color='black', linewidth=1.5)

    ax.tick_params(which="minor", bottom=False, left=False)
    
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            if not np.isnan(val):
                text_color = "white" if abs(val) > (max_abs * 0.5) else "black"
                ax.text(j, i, f"{val:.1f}°", ha="center", va="center", color=text_color, fontsize=9, weight="bold")
                
    ax.set_title("Capacity Gradient by Scenario & Technology (Degrees)", fontsize=16, weight="bold", pad=15)
    
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel("Gradient Angle (Degrees)", rotation=-90, va="bottom", fontsize=12, weight="bold")
    
    plt.tight_layout()
    out_file = os.path.join(output_dir, "Gradient_Heatmap_Combined.png")
    plt.savefig(out_file, dpi=500, bbox_inches="tight")
    plt.close(fig)

def create_combined_relative_boxplot(all_tech_data, output_dir):
    print("📊 Building Combined Relative Capacities Boxplot...")
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_facecolor('white')
    ax.grid(axis='y', color='gray', linestyle='--', linewidth=0.5, alpha=0.5, zorder=0)
    
    # Draw the 100% base case line
    ax.axhline(100, color='#333333', linestyle='--', linewidth=2, zorder=1, label="Base Case (100%)")
    
    tech_keys = list(TECHS.keys())
    offsets = [-0.25, 0, 0.25]
    
    legend_elements = [Line2D([0], [0], color='#333333', linestyle='--', lw=2, label="Base Case (100%)")]
    
    for idx, tech_id in enumerate(tech_keys):
        tech_label = TECHS[tech_id]
        scenarios_dict = all_tech_data.get(tech_id, {})
        base_series = scenarios_dict.get("Base_case")
        
        if base_series is None:
            continue
            
        t_color = TECH_COLORS[tech_id]
        legend_elements.append(Patch(facecolor=t_color, edgecolor='#333333', alpha=0.85, label=tech_label))
        
        box_data = []
        positions = []
        
        for y in YEARS_TO_PLOT:
            base_val = base_series.loc[y] if y in base_series.index else 0
            
            y_vals = []
            if base_val > 1e-3:
                for q in QUOTAS:
                    s = scenarios_dict.get(q)
                    if s is not None and y in s.index:
                        rel_val = (s.loc[y] / base_val) * 100
                        y_vals.append(rel_val)
                        
            box_data.append(y_vals)
            positions.append(y + offsets[idx])
            
        valid_box_data = []
        valid_positions = []
        for d, p in zip(box_data, positions):
            if len(d) > 0:
                valid_box_data.append(d)
                valid_positions.append(p)
                
        if valid_box_data:
            bp = ax.boxplot(
                valid_box_data, 
                positions=valid_positions, 
                widths=0.2,
                patch_artist=True,
                zorder=3,
                manage_ticks=False,
                showfliers=False
            )
            for box in bp['boxes']:
                box.set(facecolor=t_color, alpha=0.85, linewidth=1.2, edgecolor='#333333')
            for median in bp['medians']:
                median.set(color='#111111', linewidth=1.5)
            for whisker in bp['whiskers']:
                whisker.set(color='#333333', linewidth=1.2)
            for cap in bp['caps']:
                cap.set(color='#333333', linewidth=1.2)

    ax.set_ylabel("Installed Capacity vs. Base Case (%)", fontsize=18, labelpad=15, weight="bold")
    ax.set_xlim(YEARS_TO_PLOT[0] - 0.6, YEARS_TO_PLOT[-1] + 0.6)
    
    # Custom x-ticks at each 5-year step
    ax.set_xticks([2025, 2030, 2035, 2040])
    ax.set_xticklabels([2025, 2030, 2035, 2040], rotation=0, ha='center', fontsize=16, weight="bold")
    ax.tick_params(axis="y", labelsize=16)
    
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#333333')
        spine.set_linewidth(1.5)
        
    ax.legend(handles=legend_elements, loc='upper left', frameon=True, facecolor='white', edgecolor='black', framealpha=1.0, fontsize=14)
    
    plt.tight_layout()
    out_file = os.path.join(output_dir, "Capacities_Combined_Relative_Boxplot.png")
    plt.savefig(out_file, dpi=500, bbox_inches="tight")
    plt.close(fig)
    print(f"   ✔ Saved Combined Relative Boxplot -> {out_file}")


def main():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    base_case_dir = os.path.join(BASE_DIR, "Base_Case")
    base_file = None
    if os.path.exists(base_case_dir):
        for f in os.listdir(base_case_dir):
            if f.endswith(".xlsx") and "pyomo" not in f and "dump" not in f:
                base_file = os.path.join(base_case_dir, f)
                break
                
    all_gradients = []
    all_tech_data = {}
    
    for tech_id, tech_label in TECHS.items():
        print(f"📊 Processing capacity data for {tech_label}...")
        scenarios_dict = {}
        
        if base_file:
            base_s = get_total_capacity(base_file, tech_id)
            if base_s is not None and not base_s.empty:
                scenarios_dict["Base_case"] = base_s.reindex(YEARS_TO_PLOT).fillna(0)
                
        for q in QUOTAS:
            folder_name = f"scenario_solar_recycling_low_crma_{q}"
            file_path = os.path.join(BASE_DIR, folder_name, f"{folder_name}.xlsx")
            if os.path.exists(file_path):
                s = get_total_capacity(file_path, tech_id)
                if s is not None and not s.empty:
                    scenarios_dict[q] = s.reindex(YEARS_TO_PLOT).fillna(0)
                    
        if scenarios_dict:
            all_tech_data[tech_id] = scenarios_dict
            create_boxplot(tech_id, tech_label, scenarios_dict, OUTPUT_DIR)
            create_line_plot(tech_id, tech_label, scenarios_dict, OUTPUT_DIR)
            
            tech_grads = analyze_gradients(tech_label, scenarios_dict)
            all_gradients.extend(tech_grads)
            print(f"   ✔ Generated Boxplot & Lineplot")
        else:
            print(f"   ❌ No data found.")
            
    if all_gradients:
        plot_combined_heatmap(all_gradients, OUTPUT_DIR)
        print(f"   ✔ Generated Combined Heatmap")
        
        grad_df = pd.DataFrame(all_gradients)
        grad_csv = os.path.join(OUTPUT_DIR, "Gradient_Analysis_2030_2040.csv")
        grad_df.to_csv(grad_csv, index=False)
        print(f"✅ Exported comprehensive gradient table -> {grad_csv}")

    if all_tech_data:
        create_combined_relative_boxplot(all_tech_data, OUTPUT_DIR)

if __name__ == "__main__":
    main()
