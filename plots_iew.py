import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.ticker import StrMethodFormatter
from pathlib import Path

# ================= FORMATTING =================
plt.rcParams["font.family"] = "Arial"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# ================= CONFIGURATION =================
RESULT_DIRECTORY = r"result\plottable_results"
PLOT_OUTPUT_DIR = "plot_iew"

# Tech -> Stage mapping
TECH_STAGE_MAP = {
    "solarPV": ["Polysilicon", "Wafer", "Cell", "Module"],
    "windon": ["BladeOn", "TowerOn", "NacelleOn"],
    "windoff": ["BladeOff", "TowerOff", "NacelleOff"],
}

TECH_LABELS = {
    "solarPV": "Solar PV",
    "windon": "Wind Onshore",
    "windoff": "Wind Offshore",
}

# Scenarios
SCENARIO_ORDER = ["Base_case", "high", "medium", "low"]
SCENARIO_COLORS = {
    "Base_case": "#F4E100",
    "low": "#3A737D",
    "medium": "#05A5D2",
    "high": "#D79327",
}
SCENARIO_LABELS = {
    "Base_case": "Base Case",
    "low": "Low Scrap Price",
    "medium": "Medium Scrap Price",
    "high": "High Scrap Price",
}

YEARS_TO_PLOT = [2030, 2035, 2040]
BASELINE_YEAR = 2024

# CRMA list
CRMA_TARGET_MATERIALS = [
    "aluminum", "copper", "silicon", "cobalt", "dysprosium", "gallium",
    "graphite", "lithium", "manganese", "neodymium", "nickel", "niobium",
    "praseodymium", "terbium", "titanium", "vanadium", "boron",
]

# ================= DATA LOADING =================
def load_simulation_results(base_dir):
    data = {}
    scenarios = {
        "Base_case": ["high"],
        "LR4_nziastrict_test": ["low", "medium", "high"],
    }
    file_prefix = "scenario_solar_recycling_"

    print(f"📂 Starting data load from: {base_dir}\n")

    for folder, sensitivities in scenarios.items():
        data[folder] = {}
        for sens in sensitivities:
            filename = f"{file_prefix}{sens}.xlsx"
            file_path = os.path.join(base_dir, folder, filename)
            if os.path.exists(file_path):
                print(f"   Reading: {folder} / {filename} ...", end="")
                try:
                    df = pd.read_excel(file_path)
                    data[folder][sens] = df
                    print(" ✅ Done.")
                except Exception as e:
                    print(f" ❌ Error reading file: {e}")
            else:
                print(f" ⚠️ File not found: {file_path}")

    return data


def get_total_capacity_ext(base_dir, file_name="scenario_solar_recycling_high.xlsx", tech_filter="solarPV"):
    file_path = os.path.join(base_dir, "Base_case", file_name)

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    try:
        df = pd.read_excel(file_path, sheet_name="extension_only_totalcapacity")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

    cols_to_fix = ["stf", "location", "tech"]
    existing_cols = [c for c in cols_to_fix if c in df.columns]
    df[existing_cols] = df[existing_cols].ffill()

    mask = df["tech"].astype(str).str.contains(tech_filter, case=False, na=False)
    capacity_series = df[mask].groupby("stf")["capacity_ext"].sum()

    return capacity_series


def load_clean_data(base_dir, folder, filename, tech_filter=None, stages=None):
    path = os.path.join(base_dir, folder, filename)
    if not os.path.exists(path):
        print(f"⚠️ Missing: {path}")
        return None

    try:
        df = pd.read_excel(path, sheet_name="processing_capacities")
        cols = ["stf", "location", "tech"]
        df[[c for c in cols if c in df.columns]] = df[[c for c in cols if c in df.columns]].ffill()

        if tech_filter:
            df = df[df["tech"].isin(tech_filter)].copy()
        if stages:
            df = df[df["stages"].isin(stages)].copy()

        df = df[df["stf"].isin(set(YEARS_TO_PLOT) | {BASELINE_YEAR})].copy()

        agg = df.groupby(["stf", "stages"])["capacity_processing_total"].sum().unstack()
        agg = agg.reindex(columns=stages).fillna(0)   # Convert MW to GW
        return agg
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ================= PLOTTING: CUMULATIVE CAPACITY =================
def plot_cumulative_capacity_with_benchmarks(data_series, output_dir=PLOT_OUTPUT_DIR, tech_label="Solar PV"):
    data_gw = data_series
    years = list(range(2024, 2041))
    plot_data = data_gw.reindex(years).fillna(0)

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.bar(
        plot_data.index,
        plot_data.values,
        color="#E69F00",
        label="Simulated Capacity",
        edgecolor="white",
        width=0.7,
        zorder=2
    )

    # Benchmark markers (kept for solar)
    if tech_label.lower().startswith("solar"):
        tyndp_2030_val = 660
        tyndp_2040_low = 781.124
        tyndp_2040_high = 1448.395

        ax.scatter(2030, tyndp_2030_val, color="#333333", s=150, marker="D",
                   edgecolor="white", linewidth=1.5, zorder=10, label="TYNDP 2030 (National Trends)")
        ax.plot([2040, 2040], [tyndp_2040_low, tyndp_2040_high],
                color="#333333", linewidth=2, zorder=10, linestyle="-")
        ax.scatter([2040, 2040], [tyndp_2040_low, tyndp_2040_high],
                   color="#333333", s=100, marker="_", linewidth=3, zorder=10)

    ax.set_xticks([2024, 2030, 2035, 2040])
    ax.set_xticklabels([str(y) for y in [2024, 2030, 2035, 2040]], fontsize=25)

    ax.set_ylabel("Installed Capacity (GW)", fontsize=22)
    ax.tick_params(axis="x", labelsize=22, rotation=0, pad=6)
    ax.tick_params(axis="y", labelsize=22)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    ax.set_facecolor("#F3F3F3")
    ax.grid(axis="y", color="white", linewidth=2, zorder=7)

    h_bar = mpatches.Patch(facecolor="#E69F00", edgecolor="#666666", linewidth=0.6, label=tech_label)
    ax.legend(handles=[h_bar], loc="upper center", bbox_to_anchor=(0.5, -0.16),
              ncol=1, frameon=False, fontsize=18)

    plt.tight_layout(rect=[0.02, 0.06, 0.98, 0.94])
    plt.subplots_adjust(bottom=0.25)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"Fig_Cumulative_{tech_label.replace(' ', '_')}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()
    print(f"✔ Benchmarked Chart saved → {output_path}")


# ================= PLOTTING: VERTICAL TOTAL =================
def create_vertical_total_plot(group_name, scenario_data, output_name, stages, output_dir=PLOT_OUTPUT_DIR):
    """
    3x1 Grid (Vertical Stack).
    X-Axis: Stages.
    Y-Values: Total Capacity (Side-by-side bars, Solid colors).
    """

    fig, axs = plt.subplots(3, 1, figsize=(10, 16))
    axs = axs.flatten()

    # 1. CALCULATE GLOBAL MAX Y for consistent scaling
    global_max = 0
    for df in scenario_data.values():
        if df is not None:
            relevant_data = df[df.index.isin(YEARS_TO_PLOT)]
            if not relevant_data.empty:
                current_max = relevant_data.max().max()
                if current_max > global_max:
                    global_max = current_max

    y_limit = global_max * 1.25  # Add headroom for labels

    # --- LOOP YEARS ---
    for i, year in enumerate(YEARS_TO_PLOT):
        ax = axs[i]

        # Grid settings
        ax.grid(axis='y', color='white', linestyle='-', linewidth=1.5, alpha=0.5, zorder=0)
        ax.set_axisbelow(True)
        ax.set_facecolor('#F0F0F0')

        n_stages = len(stages)
        n_scens = len(SCENARIO_ORDER)

        bar_width = 0.18
        gap = 0.04
        indices = np.arange(n_stages)

        # --- LOOP STAGES ---
        for j, stage in enumerate(stages):
            center_x = indices[j]

            # Plot Bars for each Scenario Side-by-Side
            for k, scen_key in enumerate(SCENARIO_ORDER):
                # Calculate X Position to center the group
                x_pos = center_x + (k - (n_scens - 1) / 2) * (bar_width + gap)

                # Get Data
                df = scenario_data[scen_key]
                val = df.loc[year, stage] if (df is not None and year in df.index) else 0
                color = SCENARIO_COLORS[scen_key]

                # Draw Bar (Solid, No Hatching)
                ax.bar(x_pos, val, width=bar_width,
                       color=color, edgecolor='black', linewidth=0.5, zorder=3)

        # Formatting
        ax.set_title(f"{year}", fontweight='bold', fontsize=16)
        ax.set_xticks(indices)

        # Only show X-axis labels on the BOTTOM plot (index 2)
        if i == 2:
            ax.set_xticklabels(stages, fontweight='bold', fontsize=16)
        else:
            ax.set_xticklabels([])  # Hide labels for top and middle plots

        ax.set_ylim(0, y_limit)
        ax.tick_params(axis='y', labelsize=14)
        ax.set_ylabel("Processing Capacity (GW/yr)", fontweight='bold', fontsize=16)

    # --- LEGEND ---
    # Create simple solid patches
    handles = []
    for key in SCENARIO_ORDER:
        c = SCENARIO_COLORS[key]
        l = SCENARIO_LABELS[key]
        # Solid patch
        handles.append(mpatches.Patch(facecolor=c, edgecolor='black', label=l))

    # Place Legend at bottom
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, 0.02),
               ncol=4, frameon=True, fontsize=14)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.08, top=0.95, hspace=0.15)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{output_name}.pdf"
    plt.savefig(out_file, bbox_inches="tight")
    print(f"✅ Saved: {out_file}")
    plt.show()


# ================= PLOTTING: VERTICAL MARGINAL =================
def create_vertical_marginal_plot(group_name, scenario_data, output_name, stages, output_dir=PLOT_OUTPUT_DIR):
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
        n_scens = len(SCENARIO_ORDER)
        bar_width = 0.18
        gap = 0.03
        indices = np.arange(n_stages)

        for j, stage in enumerate(stages):
            center_x = indices[j]
            val_map = {}
            for key in SCENARIO_ORDER:
                df = scenario_data[key]
                val = df.loc[year, stage] if (df is not None and year in df.index) else 0
                val_map[key] = val

            sorted_items = sorted(val_map.items(), key=lambda x: x[1])
            plot_params = {}
            prev_val = 0
            step_levels = []

            for rank, (key, val) in enumerate(sorted_items):
                delta = val - prev_val
                plot_params[key] = (prev_val, delta)
                if rank > 0:
                    step_levels.append(prev_val)
                prev_val = val

            group_left = center_x - (n_scens * (bar_width + gap)) / 2
            group_right = center_x + (n_scens * (bar_width + gap)) / 2

            for level in step_levels:
                ax.plot([group_left, group_right], [level, level],
                        color="gray", linestyle=":", linewidth=0.8, alpha=0.6, zorder=1)

            for k, scen_key in enumerate(SCENARIO_ORDER):
                x_pos = center_x + (k - (n_scens - 1) / 2) * (bar_width + gap)
                color = SCENARIO_COLORS[scen_key]
                bottom, height = plot_params[scen_key]

                if scen_key == "Base_case":
                    ax.bar(x_pos, height, bottom=bottom, width=bar_width,
                           color=color, edgecolor="black", linewidth=0.5, zorder=3)
                else:
                    if height > 0.05:
                        ax.bar(x_pos, height, bottom=bottom, width=bar_width,
                               facecolor="white", edgecolor=color, hatch="////", linewidth=0.8, zorder=3)
                        ax.text(x_pos, bottom + height + (y_limit * 0.01), f"+{height:.1f}",
                                ha="center", va="bottom", fontsize=16, color=color, fontweight="bold")
                    else:
                        ax.plot([x_pos - bar_width / 2, x_pos + bar_width / 2],
                                [bottom, bottom], color=color, linewidth=2, zorder=4)

        ax.set_title(f"{year}", fontweight="bold", fontsize=16)
        ax.set_xticks(indices)

        if i == 2:
            ax.set_xticklabels(stages, fontweight="bold", fontsize=16)
        else:
            ax.set_xticklabels([])

        ax.set_ylim(0, y_limit)
        ax.tick_params(axis="y", labelsize=16)
        ax.set_ylabel("Processing Capacity (GW/yr)", fontweight="bold", fontsize=16)

    handles = []
    handles.append(mpatches.Patch(facecolor=SCENARIO_COLORS["Base_case"], edgecolor="black", label="Base Case"))
    for key in ["high", "medium", "low"]:
        c = SCENARIO_COLORS[key]
        l = SCENARIO_LABELS[key]
        handles.append(mpatches.Patch(facecolor="white", hatch="////", edgecolor=c, label=f"{l}"))

    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.02),
               ncol=2, frameon=True, fontsize=16)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.10, top=0.95, hspace=0.15)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{output_name}.pdf"
    plt.savefig(out_file, bbox_inches="tight")
    print(f"✅ Saved: {out_file}")
    plt.show()


# ================= MATERIAL GRID =================
def load_mineral_data_pair(base_dir, folder, filename):
    path = os.path.join(base_dir, folder, filename)
    if not os.path.exists(path):
        return None

    try:
        df = pd.read_excel(path, sheet_name="minerals")

        cols_to_fill = ["stf", "materials", "tech", "location"]
        existing_cols = [c for c in cols_to_fill if c in df.columns]
        df[existing_cols] = df[existing_cols].ffill()

        if "tech" in df.columns:
            df = df[df["tech"].astype(str).str.contains("solar|wind", case=False, na=False)]

        mat_col = "materials" if "materials" in df.columns else "material"
        df = df[df[mat_col].isin(CRMA_TARGET_MATERIALS)].copy()

        results = {}
        for metric, col_name in [("total", "demand_material_total"), ("imports", "material_imported")]:
            if col_name in df.columns:
                agg = df.groupby(["stf", mat_col])[col_name].sum().unstack()
                agg = agg.reindex(columns=CRMA_TARGET_MATERIALS).fillna(0)
                agg = agg.loc[agg.index.isin(range(2024, 2041))]
                results[metric] = agg
            else:
                return None

        if "total" in results and "imports" in results:
            results["domestic"] = (results["total"] - results["imports"]).clip(lower=0)

        return results

    except Exception as e:
        print(f"❌ Error loading {folder}/{filename}: {e}")
        return None


# Define units and conversion factors (Assuming input is in kt)
# kt -> kt: 1.0 | kt -> tons: 1000.0 | kt -> kg: 1000000.0
UNIT_CONFIG = {
    "aluminum": {"unit": "kt", "factor": 1.0},
    "copper": {"unit": "kt", "factor": 1.0},
    "silicon": {"unit": "kt", "factor": 1.0},
    "nickel": {"unit": "kt", "factor": 1.0},
    "manganese": {"unit": "kt", "factor": 1},
    "cobalt": {"unit": "tons", "factor": 1000.0},
    "titanium": {"unit": "tons", "factor": 1000.0},
    "boron": {"unit": "tons", "factor": 1000.0},
    "dysprosium": {"unit": "tons", "factor": 1000.0},
    "graphite": {"unit": "tons", "factor": 1000.0},
    "lithium": {"unit": "tons", "factor": 1000.0},
    "praseodymium": {"unit": "tons", "factor": 1000.0},
    "neodymium": {"unit": "tons", "factor": 1000.0},
    "gallium": {"unit": "kg", "factor": 1000000.0},
    "niobium": {"unit": "kg", "factor": 1000000.0},
    "terbium": {"unit": "kg", "factor": 1000000.0},
    "vanadium": {"unit": "kg", "factor": 1000000.0},
}


def create_big_grid_plot(group_name, data_dict, output_name, main_color, output_dir=PLOT_OUTPUT_DIR):
    # 1. Sort materials by unit (kt, then tons, then kg)
    # We create a sorting key based on unit order
    unit_order = {"kt": 0, "tons": 1, "kg": 2}
    sorted_materials = sorted(
        CRMA_TARGET_MATERIALS,
        key=lambda m: (unit_order.get(UNIT_CONFIG[m]["unit"], 3), m)
    )

    n_rows = len(sorted_materials)
    n_cols = 3
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(14, 3.5 * n_rows))

    DOMESTIC_COLOR = "#70C4C0"
    IMPORT_COLOR = "#EF85B0"
    plot_order = ["high", "medium", "low"]
    col_titles = ["High Scrap Prices", "Medium Scrap Prices", "Low Scrap Prices"]

    for ax, title in zip(axs[0], col_titles):
        ax.set_title(title, fontsize=14, weight="bold", pad=15)

    for i, mat in enumerate(sorted_materials):
        config = UNIT_CONFIG.get(mat, {"unit": "kt", "factor": 1.0})
        unit_label = config["unit"]
        factor = config["factor"]

        for j, sens in enumerate(plot_order):
            ax = axs[i, j]
            if sens in data_dict and data_dict[sens] is not None:
                # Apply unit conversion
                df_total = data_dict[sens]["total"] * factor
                df_imports = data_dict[sens]["imports"] * factor

                y_total = df_total[mat]
                y_imports = df_imports[mat]

                ax.fill_between(y_imports.index, 0, y_imports, color=IMPORT_COLOR, alpha=0.6, linewidth=0)
                ax.fill_between(y_total.index, y_imports, y_total, color=DOMESTIC_COLOR, alpha=0.8, linewidth=0)
                ax.plot(y_total.index, y_total, color=main_color, lw=2.5)

                # Formatting
                ax.set_xlim(2024, 2040)
                ax.set_xticks([2025, 2030, 2035, 2040])
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.grid(axis='y', linestyle='--', alpha=0.3)

                # Add the Material name and Unit to the Y-axis of the first column
                if j == 0:
                    ax.set_ylabel(f"{mat.capitalize()}\n[{unit_label}]", fontsize=11, weight="bold")

                if i != n_rows - 1:
                    ax.set_xticklabels([])

    handles = [
        plt.Line2D([], [], color=main_color, lw=2.5, label="Total Demand"),
        mpatches.Patch(facecolor=DOMESTIC_COLOR, alpha=0.8, label="Domestic Supply (Production + Recycling)"),
        mpatches.Patch(facecolor=IMPORT_COLOR, alpha=0.6, label="Material Imports"),
    ]

    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               fontsize=13, bbox_to_anchor=(0.5, 0.005))

    plt.tight_layout()
    plt.subplots_adjust(top=0.96, bottom=0.04, hspace=0.3)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{output_name}.pdf"
    plt.savefig(out_file, bbox_inches="tight")
    print(f"✅ Saved unit-sorted grid: {out_file}")
    plt.close()


# ================= MAIN EXECUTION =================
# Quick check for loading
_ = load_simulation_results(RESULT_DIRECTORY)

# 1) Solar cumulative plot
solar_series = get_total_capacity_ext(RESULT_DIRECTORY, "scenario_solar_recycling_high.xlsx", "solarPV")
if solar_series is not None:
    plot_cumulative_capacity_with_benchmarks(solar_series, tech_label="Solar PV")

# 2) Capacity plots per tech
for tech, stages in TECH_STAGE_MAP.items():
    df_base = load_clean_data(RESULT_DIRECTORY, "Base_case", "scenario_solar_recycling_high.xlsx",
                              tech_filter=[tech], stages=stages)
    if df_base is None:
        print(f"❌ Base Case data missing for {tech}")
        continue

    data_strict = {
        "Base_case": df_base,
        "low": load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict_test", "scenario_solar_recycling_low.xlsx",
                               tech_filter=[tech], stages=stages),
        "medium": load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict_test", "scenario_solar_recycling_medium.xlsx",
                                  tech_filter=[tech], stages=stages),
        "high": load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict_test", "scenario_solar_recycling_high.xlsx",
                                tech_filter=[tech], stages=stages),
    }

    print(f"📊 Generating Marginal Plot (Strict) for {tech}...")
    create_vertical_marginal_plot(f"{TECH_LABELS[tech]} NZIA Strict", data_strict,
                                  f"Plot_Vertical_Strict_{tech}", stages)

# 3) Materials grids (CRMA)
strict_data = {
    "low": load_mineral_data_pair(RESULT_DIRECTORY, "LR4_nziastrict_test", "scenario_solar_recycling_low.xlsx"),
    "medium": load_mineral_data_pair(RESULT_DIRECTORY, "LR4_nziastrict_test", "scenario_solar_recycling_medium.xlsx"),
    "high": load_mineral_data_pair(RESULT_DIRECTORY, "LR4_nziastrict_test", "scenario_solar_recycling_high.xlsx"),
}

if any(v is not None for v in strict_data.values()):
    print("📊 Generating Grid for Strict...")
    create_big_grid_plot("NZIA Strict", strict_data, "Grid_CRMA_Strict", "#EB5B44")
