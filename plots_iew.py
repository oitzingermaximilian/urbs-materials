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
        "LR4_seperate_CRMA_1905": ["low", "medium", "high"],
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

        STEP_ORDER = ["Base_case", "high", "medium", "low"]

        for j, stage in enumerate(stages):
            center_x = indices[j]

            # Wir halten fest, wo der letzte Balken geendet hat (Startwert = 0)
            # Aber für die marginale Anzeige: Der erste Vergleichspunkt ist der Base_case Wert
            running_bottom = 0

            for k, scen_key in enumerate(STEP_ORDER):
                x_pos = center_x + (k - (len(STEP_ORDER) - 1) / 2) * (bar_width + gap)
                color = SCENARIO_COLORS[scen_key]

                df_scen = scenario_data[scen_key]
                current_val = df_scen.loc[year, stage] if (df_scen is not None and stage in df_scen.columns) else 0

                if scen_key == "Base_case":
                    # Der Anker: Solider Balken von 0 bis Base_case
                    ax.bar(x_pos, current_val, width=bar_width,
                           color=color, edgecolor="black", linewidth=0.5, zorder=3)
                    running_bottom = current_val  # Ab hier messen wir die Deltas
                else:
                    # Berechne das Delta zum VORGÄNGER in der STEP_ORDER
                    # Wir brauchen den Wert des Szenarios, das in der Liste davor steht
                    prev_scen_key = STEP_ORDER[k - 1]
                    df_prev = scenario_data[prev_scen_key]
                    prev_val = df_prev.loc[year, stage] if (df_prev is not None and stage in df_prev.columns) else 0

                    delta = current_val - prev_val

                    if abs(delta) > 0.05:
                        # Zeichne das schraffierte Delta
                        # Wir setzen es auf die Höhe des vorherigen Szenarios (prev_val)
                        hatch_bottom = prev_val
                        ax.bar(x_pos, delta, bottom=hatch_bottom, width=bar_width,
                               facecolor="white", edgecolor=color, hatch="////", linewidth=0.8, zorder=3)

                        # Label: Zeigt die Differenz zum Vorgänger
                        prefix = "+" if delta > 0 else ""
                        ax.text(x_pos, current_val + (y_limit * 0.01) if delta > 0 else current_val - (y_limit * 0.03),
                                f"{prefix}{delta:.1f}", ha="center", va="bottom" if delta > 0 else "top",
                                fontsize=11, color=color, fontweight="bold")

                        # Hilfslinie vom Vorgänger zum aktuellen Delta
                        ax.plot([x_pos - (bar_width + gap), x_pos], [prev_val, prev_val],
                                color="gray", linestyle=":", linewidth=0.8, alpha=0.5, zorder=2)
                    else:
                        # Wenn kein Unterschied zum Vorgänger: Nur eine flache Linie auf dessen Höhe
                        ax.plot([x_pos - bar_width / 2, x_pos + bar_width / 2], [prev_val, prev_val],
                                color=color, linewidth=2, zorder=4)

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
        # Added mined and recycled to the extraction list
        metrics_to_extract = [
            ("total", "demand_material_total"),
            ("imports", "material_imported"),
            ("mined", "material_mined"),
            ("recycled", "material_recycled")
        ]

        for metric, col_name in metrics_to_extract:
            # We use a default of 0 if the column is missing to prevent breaking
            if col_name in df.columns:
                agg = df.groupby(["stf", mat_col])[col_name].sum().unstack()
                agg = agg.reindex(columns=CRMA_TARGET_MATERIALS).fillna(0)
                agg = agg.loc[agg.index.isin(range(2024, 2041))]
                results[metric] = agg
            else:
                # If your model drops zero-value variables entirely, we create an empty frame
                print(f"⚠️ Warning: Column '{col_name}' missing in {filename}. Defaulting to 0.")
                empty_df = pd.DataFrame(0, index=range(2024, 2041), columns=CRMA_TARGET_MATERIALS)
                empty_df.index.name = 'stf'
                results[metric] = empty_df

        # Removed the old "domestic" calculation since we now have mined and recycled explicitly.

        return results

    except Exception as e:
        print(f"❌ Error loading {folder}/{filename}: {e}")
        return None


# Define units and conversion factors (Assuming input is in kt)
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
    unit_order = {"kt": 0, "tons": 1, "kg": 2}
    sorted_materials = sorted(
        CRMA_TARGET_MATERIALS,
        key=lambda m: (unit_order.get(UNIT_CONFIG[m]["unit"], 3), m)
    )

    n_rows = len(sorted_materials)
    n_cols = 3
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(14, 3.5 * n_rows))

    # Updated Color Palette
    DOMESTIC_MINED_COLOR = "#70C4C0"  # Teal for primary mining
    DOMESTIC_RECYCLED_COLOR = "#F4A261"  # Orange/Sand for recycled
    IMPORT_COLOR = "#EF85B0"  # Pink for imports

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
                y_total = data_dict[sens]["total"][mat] * factor
                y_imports = data_dict[sens]["imports"][mat] * factor
                y_mined = data_dict[sens]["mined"][mat] * factor
                y_recycled = data_dict[sens]["recycled"][mat] * factor

                # Calculate stacking boundaries
                bottom_mined = y_imports
                top_mined = y_imports + y_mined
                top_recycled = top_mined + y_recycled

                # Layer 1: Imports (0 to Imports)
                ax.fill_between(y_imports.index, 0, y_imports, color=IMPORT_COLOR, alpha=0.6, linewidth=0)
                # Layer 2: Mined (Imports to Mined)
                ax.fill_between(y_imports.index, bottom_mined, top_mined, color=DOMESTIC_MINED_COLOR, alpha=0.8,
                                linewidth=0)
                # Layer 3: Recycled (Mined to Recycled)
                ax.fill_between(y_imports.index, top_mined, top_recycled, color=DOMESTIC_RECYCLED_COLOR, alpha=0.8,
                                linewidth=0)

                # Top Line: Total Demand
                ax.plot(y_total.index, y_total, color=main_color, lw=2.5)

                # Formatting
                ax.set_xlim(2024, 2040)
                ax.set_xticks([2025, 2030, 2035, 2040])
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.grid(axis='y', linestyle='--', alpha=0.3)

                if j == 0:
                    ax.set_ylabel(f"{mat.capitalize()}\n[{unit_label}]", fontsize=11, weight="bold")

                if i != n_rows - 1:
                    ax.set_xticklabels([])

    # Updated Legend
    handles = [
        plt.Line2D([], [], color=main_color, lw=2.5, label="Total Demand"),
        mpatches.Patch(facecolor=DOMESTIC_RECYCLED_COLOR, alpha=0.8, label="Domestic Recycled"),
        mpatches.Patch(facecolor=DOMESTIC_MINED_COLOR, alpha=0.8, label="Domestic Mined"),
        mpatches.Patch(facecolor=IMPORT_COLOR, alpha=0.6, label="Material Imports"),
    ]

    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
               fontsize=13, bbox_to_anchor=(0.5, 0.005))

    plt.tight_layout()
    plt.subplots_adjust(top=0.96, bottom=0.04, hspace=0.3)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{output_name}.pdf"
    plt.savefig(out_file, bbox_inches="tight")
    print(f"✅ Saved unit-sorted grid: {out_file}")
    plt.close()


# ==============================================================================
# 4. NEW PLOTTING: SCRAP LINE PLOTS (kt)
# ==============================================================================
def create_scrap_line_plots(base_dir, output_dir=PLOT_OUTPUT_DIR):
    """
    Loads data from the 'scrap' sheet and creates a separate line plot
    for each technology showing scrap generation over time across scenarios.
    """
    print("\n📊 Generating Scrap Line Plots...")

    scenarios = {
        "Base_case": ("Base_case", "scenario_solar_recycling_high.xlsx"),
        "high": ("LR4_seperate_CRMA_1905", "scenario_solar_recycling_high.xlsx"),
        "medium": ("LR4_seperate_CRMA_1905", "scenario_solar_recycling_medium.xlsx"),
        "low": ("LR4_seperate_CRMA_1905", "scenario_solar_recycling_low.xlsx")
    }

    # Structure to hold scrap data: {tech: {scenario: series_of_scrap}}
    scrap_master_data = {tech: {} for tech in TECH_STAGE_MAP.keys()}

    # --- 1. DATA LOADING & EXTRACTION ---
    for scen_name, (folder, filename) in scenarios.items():
        path = os.path.join(base_dir, folder, filename)
        if not os.path.exists(path):
            print(f"   ⚠️ Skipping scrap data for {scen_name}: {path} missing.")
            continue

        try:
            df = pd.read_excel(path, sheet_name="scrap")

            # Close formatting gaps via ffill
            cols_to_fill = ["stf", "tech"]
            existing_cols = [c for c in cols_to_fill if c in df.columns]
            df[existing_cols] = df[existing_cols].ffill()

            # Look for common mass/quantity columns
            qty_col = "scrap_quantity" if "scrap_quantity" in df.columns else df.columns[-1]

            for tech in TECH_STAGE_MAP.keys():
                # Filter by explicit tech key
                df_tech = df[df["tech"].astype(str).str.contains(tech, case=False, na=False)]

                if not df_tech.empty:
                    # Aggregate duplicates if your model tracks sub-nodes
                    series = df_tech.groupby("stf")[qty_col].sum()
                    # Keep timeframe locked between baseline and targets
                    series = series.reindex(range(2024, 2041)).fillna(0)
                    scrap_master_data[tech][scen_name] = series

        except Exception as e:
            print(f"   ❌ Error processing scrap for {scen_name}: {e}")

    # --- 2. RENDERING CHARTS ---
    for tech, scen_dict in scrap_master_data.items():
        if not scen_dict:
            continue

        fig, ax = plt.subplots(figsize=(11, 6))
        ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
        ax.set_facecolor('#F8F9FA')

        for scen_key in SCENARIO_ORDER:
            if scen_key in scen_dict:
                data_series = scen_dict[scen_key]
                ax.plot(
                    data_series.index,
                    data_series.values,
                    label=SCENARIO_LABELS[scen_key],
                    color=SCENARIO_COLORS[scen_key],
                    linewidth=3,
                    marker='o',
                    markersize=5,
                    zorder=3
                )

        ax.set_title(f"Scrap Generation Profile: {TECH_LABELS[tech]}", fontsize=15, weight='bold', pad=12)
        ax.set_xlabel("Year", fontsize=12, weight='bold')
        ax.set_ylabel("Scrap Generated (kt)", fontsize=12, weight='bold')
        ax.set_xlim(2024, 2040)
        ax.set_xticks([2024, 2026, 2028, 2030, 2032, 2034, 2035, 2036, 2038, 2040])

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(frameon=True, facecolor='white', edgecolor='none', fontsize=11)

        plt.tight_layout()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        out_file = output_dir / f"Scrap_Lineplot_{tech}.pdf"
        plt.savefig(out_file, bbox_inches="tight")
        plt.close()
        print(f"   ✔ Scrap plot successfully saved → {out_file}")


# ==============================================================================
# 5. NEW PLOTTING: STACKED STOCK LEVEL CHARTS (GW) - CORRECTED SHEET NAME
# ==============================================================================
def create_stock_level_stacked_bars(base_dir, output_dir=PLOT_OUTPUT_DIR):
    """
    Loads data from the 'stock_levels' sheet.
    Generates a 4-chart layout for each technology (one grid plot per tech).
    Each subplot tracks stacked capacity over every individual model year (2024-2040).
    """
    print("\n📊 Generating Stacked Stock Level Profiles...")

    scenarios = {
        "Base_case": ("Base_case", "scenario_solar_recycling_high.xlsx"),
        "high": ("LR4_seperate_CRMA_1905", "scenario_solar_recycling_high.xlsx"),
        "medium": ("LR4_seperate_CRMA_1905", "scenario_solar_recycling_medium.xlsx"),
        "low": ("LR4_seperate_CRMA_1905", "scenario_solar_recycling_low.xlsx")
    }

    # Configuration for targeting structural tracking limits
    STOCK_CONFIG = {
        "solarPV": ["Polysilicon", "Wafer", "Cell", "Module"],
        "windon": ["AssemblyOn", "BladeOn", "NacelleOn", "TowerOn"],
        "windoff": ["AssemblyOff", "BladeOff", "NacelleOff", "TowerOff"]
    }

    # Clean visual palette for stages stacking
    STAGE_PALETTE = ["#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"]

    for tech, target_stages in STOCK_CONFIG.items():
        # Setup matrix: 2x2 grid for our 4 execution states
        fig, axs = plt.subplots(2, 2, figsize=(16, 12), sharex=True, sharey=True)
        axs = axs.flatten()

        has_plotted_data = False

        for idx, scen_key in enumerate(SCENARIO_ORDER):
            ax = axs[idx]
            folder, filename = scenarios[scen_key]
            path = os.path.join(base_dir, folder, filename)

            # Setup layout grid system backgrounds
            ax.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)
            ax.set_facecolor('#FDFDFD')

            if not os.path.exists(path):
                ax.text(0.5, 0.5, "Data File Missing", ha='center', va='center', color='red')
                ax.set_title(f"{SCENARIO_LABELS[scen_key]} (N/A)", fontsize=12, weight='bold')
                continue

            try:
                # FIXED: Targeted the explicit user provided worksheet name
                sheet_name = "stock_levels"
                df = pd.read_excel(path, sheet_name=sheet_name)

                # Clear formatting gaps
                cols_to_fill = ["stf", "tech", "stages"]
                existing_cols = [c for c in cols_to_fill if c in df.columns]
                df[existing_cols] = df[existing_cols].ffill()

                # Isolate target variables
                df_filtered = df[
                    df["tech"].astype(str).str.contains(tech, case=False, na=False) &
                    df["stages"].isin(target_stages)
                    ].copy()

                if df_filtered.empty:
                    ax.text(0.5, 0.5, "No Matching Tech/Stage Entries", ha='center', va='center')
                    ax.set_title(f"{SCENARIO_LABELS[scen_key]}", fontsize=12, weight='bold')
                    continue

                # FIXED: Target the explicit column name for values
                val_col = "components_stockpile"

                if val_col not in df_filtered.columns:
                    # Fallback to last column if column name has a stray space in Excel
                    val_col = [c for c in df_filtered.columns if "stockpile" in str(c).lower()][0]

                # Transform data mapping into year-by-stage dimensions
                pivot_df = df_filtered.groupby(["stf", "stages"])[val_col].sum().unstack()
                # Enforce continuous time tracking
                pivot_df = pivot_df.reindex(index=range(2024, 2041), columns=target_stages).fillna(0)

                # Render Stacked Bars
                bottoms = np.zeros(len(pivot_df.index))
                for s_idx, stage in enumerate(target_stages):
                    ax.bar(
                        pivot_df.index,
                        pivot_df[stage],
                        bottom=bottoms,
                        label=stage if idx == 0 else "",
                        color=STAGE_PALETTE[s_idx],
                        edgecolor='black',
                        linewidth=0.4,
                        width=0.75,
                        zorder=3
                    )
                    bottoms += pivot_df[stage].values

                ax.set_title(SCENARIO_LABELS[scen_key], fontsize=13, weight='bold')
                ax.set_xlim(2023, 2041)
                ax.set_xticks(range(2024, 2041, 2))
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                has_plotted_data = True

            except Exception as e:
                ax.text(0.5, 0.5, f"Execution Error", ha='center', va='center', fontsize=9)
                ax.set_title(SCENARIO_LABELS[scen_key], fontsize=12, weight='bold')
                print(f"   ❌ Error on stock stacked chart parsing [{scen_key}]: {e}")

        if has_plotted_data:
            fig.suptitle(f"Stock Deployment Capacity Profile: {TECH_LABELS[tech]}", fontsize=18, weight='bold', y=0.98)

            fig.text(0.5, 0.04, 'Model Evaluation Year', ha='center', fontsize=14, weight='bold')
            fig.text(0.02, 0.5, 'Cumulative Stock Volume (GW)', va='center', rotation='vertical', fontsize=14,
                     weight='bold')

            handles = [mpatches.Patch(facecolor=STAGE_PALETTE[i], edgecolor='black', label=stage) for i, stage in
                       enumerate(target_stages)]
            fig.legend(handles=handles, loc='lower center', ncol=4, frameon=True, facecolor='white', edgecolor='none',
                       fontsize=12, bbox_to_anchor=(0.5, -0.02))

            plt.tight_layout()
            plt.subplots_adjust(left=0.07, bottom=0.08, right=0.96, top=0.92, hspace=0.22, wspace=0.15)

            output_path = Path(output_dir) / f"Stock_StackedBars_{tech}.pdf"
            plt.savefig(output_path, bbox_inches="tight")
            plt.close()
            print(f"   ✔ Stock level grid saved successfully → {output_path}")
        else:
            plt.close()


# ================= MAIN EXECUTION =================
def run_old_plots():
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
            "low": load_clean_data(RESULT_DIRECTORY, "LR4_seperate_CRMA_1905", "scenario_solar_recycling_low.xlsx",
                                   tech_filter=[tech], stages=stages),
            "medium": load_clean_data(RESULT_DIRECTORY, "LR4_seperate_CRMA_1905", "scenario_solar_recycling_medium.xlsx",
                                      tech_filter=[tech], stages=stages),
            "high": load_clean_data(RESULT_DIRECTORY, "LR4_seperate_CRMA_1905", "scenario_solar_recycling_high.xlsx",
                                    tech_filter=[tech], stages=stages),
        }

        # --- Data Preparation for Combined Nacelle Plot ---
        nacelle_stages = ["Nacelle Onshore", "Nacelle Offshore"]
        combined_nacelle_data = {scen: pd.DataFrame() for scen in SCENARIO_ORDER}

        for scen in SCENARIO_ORDER:
            # Load Onshore
            df_on = load_clean_data(RESULT_DIRECTORY, "LR4_seperate_CRMA_1905" if scen != "Base_case" else "Base_case",
                                    f"scenario_solar_recycling_{scen.lower() if scen != 'Base_case' else 'high'}.xlsx",
                                    tech_filter=["windon"], stages=["NacelleOn"])

            # Load Offshore
            df_off = load_clean_data(RESULT_DIRECTORY, "LR4_seperate_CRMA_1905" if scen != "Base_case" else "Base_case",
                                     f"scenario_solar_recycling_{scen.lower() if scen != 'Base_case' else 'high'}.xlsx",
                                     tech_filter=["windoff"], stages=["NacelleOff"])

            if df_on is not None and df_off is not None:
                # Rename columns to distinguish them on the X-axis
                df_on = df_on.rename(columns={"NacelleOn": "Nacelle Onshore"})
                df_off = df_off.rename(columns={"NacelleOff": "Nacelle Offshore"})
                # Combine
                combined_nacelle_data[scen] = pd.concat([df_on, df_off], axis=1)

        # Now call the plot function with this combined data
        create_vertical_marginal_plot("Wind Nacelle Combined", combined_nacelle_data,
                                      "Plot_Vertical_Nacelle_Combined", nacelle_stages)

        print(f"📊 Generating Marginal Plot (Strict) for {tech}...")
        create_vertical_marginal_plot(f"{TECH_LABELS[tech]} NZIA Strict", data_strict,
                                      f"Plot_Vertical_Strict_{tech}", stages)

    # 3) Materials grids (CRMA)
    strict_data = {
        "low": load_mineral_data_pair(RESULT_DIRECTORY, "LR4_seperate_CRMA_1905", "scenario_solar_recycling_low.xlsx"),
        "medium": load_mineral_data_pair(RESULT_DIRECTORY, "LR4_seperate_CRMA_1905", "scenario_solar_recycling_medium.xlsx"),
        "high": load_mineral_data_pair(RESULT_DIRECTORY, "LR4_seperate_CRMA_1905", "scenario_solar_recycling_high.xlsx"),
    }

    if any(v is not None for v in strict_data.values()):
        print("📊 Generating Grid for Strict...")
        create_big_grid_plot("NZIA Strict", strict_data, "Grid_CRMA_Strict", "#EB5B44")

    # ==================== RUN NEW COOPERATIVE PLOTS ====================
    # 4) Process and generate tech scrap metrics lineplots (kt)
    create_scrap_line_plots(RESULT_DIRECTORY)

    # 5) Process and generate annual stacked inventory/stock layers (GW)
    create_stock_level_stacked_bars(RESULT_DIRECTORY)

# ==============================================================================
# 6. CRMA COMPARISON PLOTS (ALL SENSITIVITY SCENARIOS)
# ==============================================================================
POLICY_COLORS = {
    5: "#1A9850",   # Green
    10: "#66BD63",  # Light Green
    15: "#A6D96A",  # Yellow-Green
    20: "#FDAE61",  # Orange
    25: "#F46D43",  # Dark Orange
    30: "#D73027",  # Light Red
    35: "#A50026",  # Deep Red
}

SCENARIO_CACHE = {}

def get_scenario_sheet(base_dir, folder, filename, sheet_name):
    file_path = os.path.join(base_dir, folder, filename)
    if not os.path.exists(file_path):
        return None
        
    cache_key = (file_path, sheet_name)
    if cache_key in SCENARIO_CACHE:
        return SCENARIO_CACHE[cache_key].copy()
        
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        SCENARIO_CACHE[cache_key] = df
        return df.copy()
    except Exception as e:
        print(f"⚠️ Error reading {sheet_name} from {file_path}: {e}")
        return None

def get_total_capacity_for_scenario(base_dir, folder, filename, tech_filter="solarPV"):
    df = get_scenario_sheet(base_dir, folder, filename, "extension_only_totalcapacity")
    if df is None:
        return None
    cols_to_fix = ["stf", "location", "tech"]
    existing_cols = [c for c in cols_to_fix if c in df.columns]
    df[existing_cols] = df[existing_cols].ffill()
    mask = df["tech"].astype(str).str.contains(tech_filter, case=False, na=False)
    capacity_series = df[mask].groupby("stf")["capacity_ext"].sum()
    return capacity_series.reindex(range(2024, 2041)).fillna(0)

def get_scrap_for_scenario(base_dir, folder, filename, tech):
    df = get_scenario_sheet(base_dir, folder, filename, "scrap")
    if df is None:
        return None
    cols_to_fill = ["stf", "tech"]
    existing_cols = [c for c in cols_to_fill if c in df.columns]
    df[existing_cols] = df[existing_cols].ffill()
    qty_col = "scrap_quantity" if "scrap_quantity" in df.columns else df.columns[-1]
    df_tech = df[df["tech"].astype(str).str.contains(tech, case=False, na=False)]
    if df_tech.empty:
        return pd.Series(0.0, index=range(2024, 2041))
    series = df_tech.groupby("stf")[qty_col].sum()
    return series.reindex(range(2024, 2041)).fillna(0)

def get_recycled_share_for_scenario(base_dir, folder, filename, material):
    df = get_scenario_sheet(base_dir, folder, filename, "minerals")
    if df is None:
        return None
    cols_to_fill = ["stf", "materials"]
    existing_cols = [c for c in cols_to_fill if c in df.columns]
    df[existing_cols] = df[existing_cols].ffill()
    
    mat_col = "materials" if "materials" in df.columns else "material"
    df_mat = df[df[mat_col] == material]
    if df_mat.empty:
        return pd.Series(0.0, index=range(2024, 2041))
        
    recycled_col = "material_recycled"
    total_col = "demand_material_total"
    
    recycled_series = df_mat.groupby("stf")[recycled_col].sum().reindex(range(2024, 2041)).fillna(0)
    total_series = df_mat.groupby("stf")[total_col].sum().reindex(range(2024, 2041)).fillna(0)
    
    share = (recycled_series / total_series * 100).fillna(0)
    share[total_series == 0] = 0.0
    return share

def compare_installed_capacities_crma(base_dir=RESULT_DIRECTORY, output_dir=PLOT_OUTPUT_DIR):
    print("\n📊 Generating CRMA Installed Capacity Comparison plots...")
    technologies = ["solarPV", "windon", "windoff"]
    prices = ["low", "medium", "high"]
    targets = [5, 10, 15, 20, 25, 30, 35]
    
    for tech in technologies:
        fig, axs = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
        tech_label = TECH_LABELS.get(tech, tech)
        
        for idx, price in enumerate(prices):
            ax = axs[idx]
            ax.set_facecolor('#F8F9FA')
            ax.grid(axis='both', linestyle='--', alpha=0.5, zorder=0)
            
            for target in targets:
                folder = f"scenario_solar_recycling_{price}_crma_{target}"
                filename = f"scenario_solar_recycling_{price}_crma_{target}.xlsx"
                series = get_total_capacity_for_scenario(base_dir, folder, filename, tech)
                
                if series is not None:
                    ax.plot(
                        series.index,
                        series.values,
                        label=f"{target}%",
                        color=POLICY_COLORS[target],
                        linewidth=2.5,
                        zorder=3
                    )
            
            ax.set_title(f"{price.capitalize()} Scrap Price", fontsize=14, weight='bold')
            ax.set_xlabel("Year", fontsize=12)
            if idx == 0:
                ax.set_ylabel("Installed Capacity (GW)", fontsize=12, weight='bold')
            ax.set_xlim(2024, 2040)
            ax.set_xticks([2024, 2028, 2032, 2036, 2040])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
        fig.suptitle(f"Installed Capacity Comparison: {tech_label} (5% - 35% Policy Targets)", fontsize=16, weight='bold', y=0.98)
        
        # Legend
        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='lower center', ncol=7, frameon=True, facecolor='white', edgecolor='none',
                   title="CRMA Recycling Policy Target", title_fontsize=12, fontsize=11, bbox_to_anchor=(0.5, -0.06))
        
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.18, top=0.88, wspace=0.15)
        
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        out_file = output_dir_path / f"Compare_Capacity_{tech}.pdf"
        plt.savefig(out_file, bbox_inches="tight")
        plt.close()
        print(f"   ✔ Installed capacity comparison saved for {tech} → {out_file}")

def compare_scrap_generation_crma(base_dir=RESULT_DIRECTORY, output_dir=PLOT_OUTPUT_DIR):
    print("\n📊 Generating CRMA Scrap Generation Comparison plots...")
    technologies = ["solarPV", "windon", "windoff"]
    prices = ["low", "medium", "high"]
    targets = [5, 10, 15, 20, 25, 30, 35]
    
    for tech in technologies:
        fig, axs = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
        tech_label = TECH_LABELS.get(tech, tech)
        
        for idx, price in enumerate(prices):
            ax = axs[idx]
            ax.set_facecolor('#F8F9FA')
            ax.grid(axis='both', linestyle='--', alpha=0.5, zorder=0)
            
            for target in targets:
                folder = f"scenario_solar_recycling_{price}_crma_{target}"
                filename = f"scenario_solar_recycling_{price}_crma_{target}.xlsx"
                series = get_scrap_for_scenario(base_dir, folder, filename, tech)
                
                if series is not None:
                    ax.plot(
                        series.index,
                        series.values,
                        label=f"{target}%",
                        color=POLICY_COLORS[target],
                        linewidth=2.5,
                        zorder=3
                    )
            
            ax.set_title(f"{price.capitalize()} Scrap Price", fontsize=14, weight='bold')
            ax.set_xlabel("Year", fontsize=12)
            if idx == 0:
                ax.set_ylabel("Scrap Generated (kt)", fontsize=12, weight='bold')
            ax.set_xlim(2024, 2040)
            ax.set_xticks([2024, 2028, 2032, 2036, 2040])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
        fig.suptitle(f"Scrap Generation Comparison: {tech_label} (5% - 35% Policy Targets)", fontsize=16, weight='bold', y=0.98)
        
        # Legend
        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='lower center', ncol=7, frameon=True, facecolor='white', edgecolor='none',
                   title="CRMA Recycling Policy Target", title_fontsize=12, fontsize=11, bbox_to_anchor=(0.5, -0.06))
        
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.18, top=0.88, wspace=0.15)
        
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        out_file = output_dir_path / f"Compare_Scrap_{tech}.pdf"
        plt.savefig(out_file, bbox_inches="tight")
        plt.close()
        print(f"   ✔ Scrap generation comparison saved for {tech} → {out_file}")

def compare_crma_grid_crma(base_dir=RESULT_DIRECTORY, output_dir=PLOT_OUTPUT_DIR):
    print("\n📊 Generating CRMA Grid Recycling Share Comparison...")
    unit_order = {"kt": 0, "tons": 1, "kg": 2}
    sorted_materials = sorted(
        CRMA_TARGET_MATERIALS,
        key=lambda m: (unit_order.get(UNIT_CONFIG[m]["unit"], 3), m)
    )
    
    n_rows = len(sorted_materials)
    n_cols = 3
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(15, 3.5 * n_rows))
    
    prices = ["low", "medium", "high"]
    targets = [5, 10, 15, 20, 25, 30, 35]
    col_titles = ["Low Scrap Prices", "Medium Scrap Prices", "High Scrap Prices"]
    
    for ax, title in zip(axs[0], col_titles):
        ax.set_title(title, fontsize=14, weight="bold", pad=15)
        
    for i, mat in enumerate(sorted_materials):
        for j, price in enumerate(prices):
            ax = axs[i, j]
            ax.set_facecolor('#F8F9FA')
            ax.grid(axis='both', linestyle='--', alpha=0.3)
            
            for target in targets:
                folder = f"scenario_solar_recycling_{price}_crma_{target}"
                filename = f"scenario_solar_recycling_{price}_crma_{target}.xlsx"
                share = get_recycled_share_for_scenario(base_dir, folder, filename, mat)
                
                if share is not None:
                    ax.plot(
                        share.index,
                        share.values,
                        label=f"{target}%",
                        color=POLICY_COLORS[target],
                        linewidth=2.0,
                        zorder=3
                    )
            
            ax.set_xlim(2024, 2040)
            ax.set_ylim(-5, 105)
            ax.set_xticks([2025, 2030, 2035, 2040])
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            
            if j == 0:
                ax.set_ylabel(f"{mat.capitalize()}\nRecycled Share [%]", fontsize=11, weight="bold")
                
            if i != n_rows - 1:
                ax.set_xticklabels([])
                
    # Legend
    handles = [plt.Line2D([], [], color=POLICY_COLORS[t], lw=2.5, label=f"{t}% Policy Target") for t in targets]
    fig.legend(handles=handles, loc="lower center", ncol=7, frameon=True, facecolor='white', edgecolor='none',
               fontsize=13, bbox_to_anchor=(0.5, 0.005))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.97, bottom=0.03, hspace=0.3, wspace=0.18)
    
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    out_file = output_dir_path / "Compare_CRMA_Recycling_Share.pdf"
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"   ✔ CRMA grid comparison saved → {out_file}")

def run_all_crma_comparisons():
    print("\n🚀 Starting CRMA Comparison Plots Generation...")
    compare_installed_capacities_crma(RESULT_DIRECTORY, PLOT_OUTPUT_DIR)
    compare_scrap_generation_crma(RESULT_DIRECTORY, PLOT_OUTPUT_DIR)
    compare_crma_grid_crma(RESULT_DIRECTORY, PLOT_OUTPUT_DIR)
    print("\n🚀 All comparison plots generated successfully!")

# Run all sensitivity comparisons
run_all_crma_comparisons()

print("\n🚀 All structural chart extensions and CRMA comparisons evaluated successfully.")


