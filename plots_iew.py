import pandas as pd
import os


def load_simulation_results(base_dir):
    """
    Reads specific Excel files from the result directory structure.
    Returns a dictionary of DataFrames organized by scenario and sensitivity.
    """

    # Structure to hold our loaded data
    # Format: data[scenario_name][sensitivity] = DataFrame
    data = {}

    # --- CONFIGURATION ---
    # 1. Define the folders we want to access
    scenarios = {
        'Base_case': ['high'],  # Only 'high' for Base_case
        'LR4_nziastrict': ['low', 'medium', 'high'],
        'LR4_nziaflex': ['low', 'medium', 'high']
    }

    # 2. Define the common file prefix (based on your description)
    # Assumes files are named like: "scenario_solar_recycling_high.xlsx"
    file_prefix = "scenario_solar_recycling_"

    print(f"📂 Starting data load from: {base_dir}\n")

    for folder, sensitivities in scenarios.items():
        data[folder] = {}

        for sens in sensitivities:
            # Construct the full file path
            filename = f"{file_prefix}{sens}.xlsx"
            file_path = os.path.join(base_dir, folder, filename)

            # Check if file exists before trying to read
            if os.path.exists(file_path):
                print(f"   Reading: {folder} / {filename} ...", end="")
                try:
                    # Read the Excel file
                    # NOTE: If your Excel has multiple sheets, you might want to specify sheet_name=None
                    # to read all of them, or a specific sheet name like sheet_name='Report'
                    df = pd.read_excel(file_path)

                    data[folder][sens] = df
                    print(" ✅ Done.")
                except Exception as e:
                    print(f" ❌ Error reading file: {e}")
            else:
                print(f" ⚠️ File not found: {file_path}")

    return data


# --- EXECUTION ---

# Replace this with the actual path to your 'result' directory
# Example: "C:/Users/Name/Project/result" or just "result" if relative
RESULT_DIRECTORY = "result"

# Load the data
all_results = load_simulation_results(RESULT_DIRECTORY)

# --- INSPECTION (Optional) ---
print("\n📊 Data Load Summary:")
for scenario, cases in all_results.items():
    print(f"  • {scenario}: {list(cases.keys())} loaded")


import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.ticker import StrMethodFormatter
from pathlib import Path
import os

# ================= FORMATTING =================
plt.rcParams["font.family"] = "Arial"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# Colors
SOLAR_COLOR = "#E69F00"  # Your Model
BENCHMARK_COLOR = "#333333"  # TYNDP Reference (Dark Grey)


# ================= DATA LOADING =================
def get_total_capacity_ext(base_dir, file_name="scenario_solar_recycling_high.xlsx"):
    """
    Loads Total Active Capacity from 'extension_only_totalcapacity' sheet.
    """
    file_path = os.path.join(base_dir, "Base_case", file_name)

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    try:
        df = pd.read_excel(file_path, sheet_name="extension_only_totalcapacity")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

    # Forward Fill & Filter
    cols_to_fix = ['stf', 'location', 'tech']
    existing_cols = [c for c in cols_to_fix if c in df.columns]
    df[existing_cols] = df[existing_cols].ffill()

    mask = df['tech'].astype(str).str.contains("solarPV", case=False, na=False)
    # Group by Year ('stf') -> Sum Capacity -> Convert to GW immediately here for safety
    capacity_series = df[mask].groupby('stf')['capacity_ext'].sum()

    return capacity_series


# ================= PLOTTING FUNCTION =================
def plot_cumulative_capacity_with_benchmarks(data_series, output_dir="plots"):
    """
    Vertical bar plot with TYNDP Benchmarks overlaid.
    """

    # 1. Prepare Model Data (MW -> GW)
    data_gw = data_series / 1000
    years = list(range(2024, 2041))
    plot_data = data_gw.reindex(years).fillna(0)

    # 2. Setup Figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # 3. Plotting Bars (Your Model)
    # Z-ORDER 2: Bars sit below the grid
    ax.bar(
        plot_data.index,
        plot_data.values,
        color=SOLAR_COLOR,
        label="Simulated Capacity",  # Updated label
        edgecolor="white",
        width=0.7,
        zorder=2
    )

    # ================= BENCHMARKING =================
    # Define Values (GW)
    tyndp_2030_val = 660
    tyndp_2040_low = 781.124
    tyndp_2040_high = 1448.395

    # A. Plot 2030: Single Point (Diamond)
    # zorder=10 ensures it sits ON TOP of the grid
    ax.scatter(
        2030, tyndp_2030_val,
        color=BENCHMARK_COLOR,
        s=150,  # Size
        marker='D',  # Diamond shape
        edgecolor='white',
        linewidth=1.5,
        zorder=10,
        label="TYNDP 2030 (National Trends)"
    )

    # B. Plot 2040: Range (Vertical Interval)
    # We plot a line from Low to High, and markers at the ends
    ax.plot(
        [2040, 2040], [tyndp_2040_low, tyndp_2040_high],
        color=BENCHMARK_COLOR,
        linewidth=2,
        zorder=10,
        linestyle='-'
    )

    # Add caps (markers) to the range
    ax.scatter(
        [2040, 2040], [tyndp_2040_low, tyndp_2040_high],
        color=BENCHMARK_COLOR,
        s=100,
        marker='_',  # Horizontal line marker for clear limits
        linewidth=3,
        zorder=10
    )

    # Annotate the 2040 Range
    mid_point_2040 = (tyndp_2040_low + tyndp_2040_high) / 2
    # Optional: You can text label it if you want, but Legend is usually cleaner

    # ================================================

    # 4. Axis Formatting
    ax.set_xticks([2024, 2030, 2035, 2040])
    ax.set_xticklabels([str(y) for y in [2024, 2030, 2035, 2040]], fontsize=25)

    ax.set_ylabel("Installed Capacity (GW)", fontsize=22)
    ax.tick_params(axis="x", labelsize=22, rotation=0, pad=6)
    ax.tick_params(axis="y", labelsize=22)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    # 5. Visual Styling
    ax.set_facecolor("#F3F3F3")
    ax.grid(axis="y", color="white", linewidth=2, zorder=7)

    # 6. Custom Legend
    # Create manual handles to ensure the style is exactly what we want

    # Handle 1: The Model Bar
    h_bar = mpatches.Patch(
        facecolor=SOLAR_COLOR, edgecolor="#666666", linewidth=0.6, label="Solar PV"
    )

    # Handle 2: The 2030 Point
    h_2030 = mlines.Line2D(
        [], [], color=BENCHMARK_COLOR, marker='D', linestyle='None',
        markersize=10, markeredgecolor='white', label="TYNDP (NT+)"
    )

    # Handle 3: The 2040 Range
    h_2040 = mlines.Line2D(
        [], [], color=BENCHMARK_COLOR, marker='_', linestyle='-', linewidth=2,
        markersize=10, markeredgewidth=3, label="TYNDP (Low-High)"
    )

    legend = ax.legend(
        handles=[h_bar, h_2030, h_2040],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=3,
        frameon=False,
        fontsize=18,  # Slightly smaller to fit 3 items
        handlelength=1.5,
        columnspacing=1.5,
    )

    # 7. Layout & Save
    plt.tight_layout(rect=[0.02, 0.06, 0.98, 0.94])
    plt.subplots_adjust(bottom=0.25)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "Fig_Cumulative_Solar_Capacity_Benchmarked.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()
    print(f"✔ Benchmarked Chart saved → {output_path}")


# ================= MAIN EXECUTION =================
RESULT_DIRECTORY = "result"

# Load Data
data_capacity = get_total_capacity_ext(RESULT_DIRECTORY)

if data_capacity is not None:
    plot_cumulative_capacity_with_benchmarks(data_capacity)
else:
    print("⚠️ Skipping plot due to missing data.")


import numpy as np


# ================= CONFIGURATION =================
RESULT_DIRECTORY = "result"
YEARS_TO_PLOT = [2030, 2035, 2040]
BASELINE_YEAR = 2024
STAGES = ['Polysilicon', 'Wafer', 'Cell', 'Module']

# FIXED DISPLAY ORDER
SCENARIO_ORDER = ['Base_case', 'high', 'medium', 'low']

SCENARIO_COLORS = {
    'Base_case': '#F4E100',  # Dark Grey
    'low': '#3A737D',  # Blue
    'medium': '#05A5D2',  # Orange
    'high': '#D79327'  # Red
}

SCENARIO_LABELS = {
    'Base_case': 'Base Case',
    'low': 'Low Scrap Price',
    'medium': 'Medium Scrap Price',
    'high': 'High Scrap Price'
}


# ================= DATA LOADING =================
def load_clean_data(base_dir, folder, filename):
    path = os.path.join(base_dir, folder, filename)
    if not os.path.exists(path):
        print(f"⚠️ Missing: {path}")
        return None

    try:
        df = pd.read_excel(path, sheet_name="processing_capacities")
        cols = ['stf', 'location', 'tech']
        df[[c for c in cols if c in df.columns]] = df[[c for c in cols if c in df.columns]].ffill()

        df = df[df['stages'].isin(STAGES)].copy()
        df = df[df['stf'].isin(set(YEARS_TO_PLOT) | {BASELINE_YEAR})].copy()

        # Group and sum -> Convert to GW
        agg = df.groupby(['stf', 'stages'])['capacity_processing_total'].sum().unstack()
        agg = agg.reindex(columns=STAGES).fillna(0) / 1000
        return agg
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ================= PLOTTING ENGINE =================
def create_vertical_marginal_plot(group_name, scenario_data, output_name):
    """
    3x1 Grid (Vertical Stack).
    X-Axis: Fixed (Base -> High -> Med -> Low).
    Y-Values: Marginal Delta (Sorted).
    """
    # 3 Rows, 1 Column, Taller Figure
    fig, axs = plt.subplots(3, 1, figsize=(10, 18))
    axs = axs.flatten()

    # 1. CALCULATE GLOBAL MAX Y
    global_max = 0
    for df in scenario_data.values():
        if df is not None:
            relevant_data = df[df.index.isin(YEARS_TO_PLOT)]
            if not relevant_data.empty:
                current_max = relevant_data.max().max()
                if current_max > global_max:
                    global_max = current_max

    y_limit = global_max * 1.35

    # --- LOOP YEARS ---
    for i, year in enumerate(YEARS_TO_PLOT):
        ax = axs[i]

        # Grid settings
        ax.grid(axis='y', color='white', linestyle='-', linewidth=1.5, alpha=0.5, zorder=0)
        ax.set_axisbelow(True)
        ax.set_facecolor('#F0F0F0')

        n_stages = len(STAGES)
        n_scens = len(SCENARIO_ORDER)

        bar_width = 0.18
        gap = 0.03
        indices = np.arange(n_stages)

        # --- LOOP STAGES ---
        for j, stage in enumerate(STAGES):
            center_x = indices[j]

            # 1. GATHER & SORT VALUES
            val_map = {}
            for key in SCENARIO_ORDER:
                df = scenario_data[key]
                val = df.loc[year, stage] if (df is not None and year in df.index) else 0
                val_map[key] = val

            # Sort: List of (Key, Value) based on magnitude
            sorted_items = sorted(val_map.items(), key=lambda x: x[1])

            # 2. CALCULATE START & HEIGHT (Marginal Logic)
            plot_params = {}  # Key -> (bottom, height)

            prev_val = 0
            step_levels = []

            for rank, (key, val) in enumerate(sorted_items):
                delta = val - prev_val

                # Store parameters
                plot_params[key] = (prev_val, delta)

                if rank > 0:
                    step_levels.append(prev_val)

                prev_val = val

            # 3. DRAW HELPER LINES
            group_left = center_x - (n_scens * (bar_width + gap)) / 2
            group_right = center_x + (n_scens * (bar_width + gap)) / 2

            for level in step_levels:
                ax.plot([group_left, group_right], [level, level],
                        color='gray', linestyle=':', linewidth=0.8, alpha=0.6, zorder=1)

            # 4. PLOT BARS (In Fixed X-Order)
            for k, scen_key in enumerate(SCENARIO_ORDER):
                x_pos = center_x + (k - (n_scens - 1) / 2) * (bar_width + gap)
                color = SCENARIO_COLORS[scen_key]

                bottom, height = plot_params[scen_key]

                if scen_key == 'Base_case':
                    # Base (Solid)
                    ax.bar(x_pos, height, bottom=bottom, width=bar_width,
                           color=color, edgecolor='black', linewidth=0.5, zorder=3)
                else:
                    # Scenario Delta (Hatched)
                    if height > 0.05:
                        ax.bar(x_pos, height, bottom=bottom, width=bar_width,
                               facecolor='white', edgecolor=color, hatch='////', linewidth=0.8, zorder=3)

                        ax.text(x_pos, bottom + height + (y_limit * 0.01), f"+{height:.1f}",
                                ha='center', va='bottom', fontsize=16, color=color, fontweight='bold')
                    else:
                        # Zero Delta
                        ax.plot([x_pos - bar_width / 2, x_pos + bar_width / 2],
                                [bottom, bottom],
                                color=color, linewidth=2, zorder=4)

        # Formatting
        ax.set_title(f"{year}", fontweight='bold', fontsize=16)
        ax.set_xticks(indices)

        # Only show X-axis labels on the BOTTOM plot (index 2)
        if i == 2:
            ax.set_xticklabels(STAGES, fontweight='bold', fontsize=16)
        else:
            ax.set_xticklabels([])  # Hide labels for top and middle plots

        ax.set_ylim(0, y_limit)
        ax.tick_params(axis='y', labelsize=16)  # Adjust 14 to your desired size

        ax.set_ylabel("Processing Capacity (GW/yr)",fontweight='bold', fontsize=16)

    # --- LEGEND ---
    handles = []
    handles.append(mpatches.Patch(facecolor=SCENARIO_COLORS['Base_case'], edgecolor='black', label='Base Case'))
    for key in ['high', 'medium', 'low']:
        c = SCENARIO_COLORS[key]
        l = SCENARIO_LABELS[key]
        handles.append(mpatches.Patch(facecolor='white', hatch='////', edgecolor=c, label=f"{l}"))

    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, 0.02),
               ncol=2, frameon=True, fontsize=16)

    #plt.suptitle(f"Marginal Capacity Additions: {group_name}",
     #            fontsize=18, weight='bold', y=0.99)

    plt.tight_layout()
    # Adjust layout to fit legend at bottom and title at top
    plt.subplots_adjust(bottom=0.10, top=0.95, hspace=0.15)

    out_file = f"{output_name}.pdf"
    plt.savefig(out_file, bbox_inches='tight')
    print(f"✅ Saved: {out_file}")
    plt.show()


# ================= MAIN EXECUTION =================

print("📂 Loading Data...")
df_base = load_clean_data(RESULT_DIRECTORY, "Base_case", "scenario_solar_recycling_high.xlsx")

if df_base is not None:
    data_strict = {
        'Base_case': df_base,
        'low': load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_low.xlsx"),
        'medium': load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_medium.xlsx"),
        'high': load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_high.xlsx")
    }

    data_flex = {
        'Base_case': df_base,
        'low': load_clean_data(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_low.xlsx"),
        'medium': load_clean_data(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_medium.xlsx"),
        'high': load_clean_data(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_high.xlsx")
    }

    print("📊 Generating Strict PDF...")
    create_vertical_marginal_plot("NZIA Strict", data_strict, "Plot_Vertical_Strict")

    print("📊 Generating Flex PDF...")
    create_vertical_marginal_plot("NZIA Flex", data_flex, "Plot_Vertical_Flex")
else:
    print("❌ Base Case data missing.")

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# ================= FORMATTING =================
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 10
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3
plt.rcParams["axes.axisbelow"] = True

# ================= CONFIGURATION =================
RESULT_DIRECTORY = "result"
MATERIALS = ['Ag', 'Al', 'Cu', 'Glass', 'Polymers', 'Si']

# ORIGINAL KEYS (Used for loading data)
SCENARIOS_KEYS = ['low', 'medium', 'high']

PLOT_RANGE = range(2024, 2041)

# Mapping: Abbreviation -> (Full Name, Unit, Divisor)
UNIT_MAP = {
    'Ag': ('Silver', 't', 1),
    'Al': ('Aluminum', 'kt', 1000),
    'Cu': ('Copper', 'kt', 1000),
    'Glass': ('Glass', 'kt', 1000),
    'Polymers': ('Polymers', 'kt', 1000),
    'Si': ('Silicon', 'kt', 1000)
}

STRICT_COLOR = '#EB5B44'  # Red
FLEX_COLOR = '#1f77b4'  # Blue
DEMAND_LINE_COLOR = '#EB5B44'

# ================= DATA LOADING =================
def load_mineral_data_pair(base_dir, folder, filename):
    path = os.path.join(base_dir, folder, filename)
    if not os.path.exists(path):
        return None

    try:
        df = pd.read_excel(path, sheet_name="minerals")

        # Forward Fill
        cols_to_fill = ['stf', 'materials', 'tech', 'location']
        existing_cols = [c for c in cols_to_fill if c in df.columns]
        df[existing_cols] = df[existing_cols].ffill()

        # Filter SolarPV
        if 'tech' in df.columns:
            df = df[df['tech'].astype(str).str.contains("solar", case=False, na=False)]

        # Filter Materials
        mat_col = 'materials' if 'materials' in df.columns else 'material'
        df = df[df[mat_col].isin(MATERIALS)].copy()

        # Extract Total & Imports
        results = {}
        for metric, col_name in [('total', 'demand_material_total'), ('imports', 'material_imported')]:
            if col_name in df.columns:
                agg = df.groupby(['stf', mat_col])[col_name].sum().unstack()
                agg = agg.reindex(columns=MATERIALS).fillna(0)
                agg = agg.loc[agg.index.isin(PLOT_RANGE)]
                results[metric] = agg
            else:
                return None

        # --- NEW CALCULATION ---
        # Calculate Domestic Supply = Total - Imports
        if 'total' in results and 'imports' in results:
            # We clip at 0 to ensure no negative supply due to data noise
            results['domestic'] = (results['total'] - results['imports']).clip(lower=0)

        return results

    except Exception as e:
        print(f"❌ Error loading {folder}/{filename}: {e}")
        return None


# ================= PLOTTING ENGINE =================
def create_big_grid_plot(group_name, data_dict, output_name, main_color):
    """
    Creates a 6x3 Grid.
    - Stack Order:
      1. Bottom: Imports (Grey)
      2. Top: Domestic Supply (Gold) -> This 'pushes' down on imports visually.
      3. Line: Total Demand
    """
    fig, axs = plt.subplots(6, 3, figsize=(12, 18))

    # --- COLORS ---
    DOMESTIC_COLOR = '#70C4C0'  # Gold RGB(112,196,192
    IMPORT_COLOR = '#EF85B0'  # Light Grey RGB(239,133,176

    # --- UPDATED COLUMN ORDER (High to Low) ---
    plot_order = ['high', 'medium', 'low']
    col_titles = ["High Scrap Prices", "Medium Scrap Prices", "Low Scrap Prices"]

    # Set Column Titles
    for ax, title in zip(axs[0], col_titles):
        ax.set_title(title, fontsize=14, weight='bold', pad=15)

    # LOOP ROWS (Materials)
    for i, mat in enumerate(MATERIALS):
        # Unpack info
        full_name, unit_label, divisor = UNIT_MAP[mat]

        # 1. FIND MAX Y-VALUE FOR THIS ROW
        row_max_y = 0
        for sens in SCENARIOS_KEYS:
            if sens in data_dict and data_dict[sens] is not None:
                vals = data_dict[sens]['total'][mat] / divisor
                current_max = vals.max()
                if current_max > row_max_y:
                    row_max_y = current_max

        y_limit = row_max_y * 1.1 if row_max_y > 0 else 1

        # 2. PLOT EACH COLUMN (In reversed order)
        for j, sens in enumerate(plot_order):
            ax = axs[i, j]

            if sens in data_dict and data_dict[sens] is not None:
                df_total = data_dict[sens]['total']
                df_imports = data_dict[sens]['imports']

                y_total = df_total[mat] / divisor
                y_imports = df_imports[mat] / divisor

                # --- PLOTTING LOGIC ---

                # 1. Imports (Bottom Layer) - From 0 to y_imports
                ax.fill_between(y_imports.index, 0, y_imports,
                                color=IMPORT_COLOR, alpha=0.6, linewidth=0)

                # 2. Domestic Supply (Top Layer) - From y_imports to y_total
                # This fills the gap between imports and the total line
                ax.fill_between(y_total.index, y_imports, y_total,
                                color=DOMESTIC_COLOR, alpha=0.8, linewidth=0)

                # 3. Total Demand Line (Boundary)
                ax.plot(y_total.index, y_total, color=main_color, lw=2.5)

                # Setup Axes
                ax.set_ylim(0, y_limit)
                ax.set_xlim(2024, 2040)
                ax.set_xticks([2025, 2030, 2035, 2040])

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                # Row Label (FULL NAME) - Left column only
                if j == 0:
                    ax.set_ylabel(f"{full_name}\n({unit_label})", fontsize=12, weight='bold')

                # X Labels - Bottom row only
                if i == 5:
                    ax.tick_params(axis='x', rotation=0)
                else:
                    ax.set_xticklabels([])

    # --- LEGEND ---
    handles = [
        plt.Line2D([], [], color=main_color, lw=2.5, label='Annual Demand'),
        mpatches.Patch(facecolor=DOMESTIC_COLOR, alpha=0.8, label='Domestic Supply'),
        mpatches.Patch(facecolor=IMPORT_COLOR, alpha=0.6, label='Material Imports')
    ]

    fig.legend(handles=handles, loc='lower center', ncol=3, frameon=False, fontsize=14, bbox_to_anchor=(0.5, 0.02))

    plt.tight_layout()
    plt.subplots_adjust(top=0.94, bottom=0.06)

    out_file = f"{output_name}.pdf"
    plt.savefig(out_file, bbox_inches='tight')
    print(f"✅ Saved: {out_file}")
    plt.close()


# ================= MAIN EXECUTION =================

print("📂 Loading Data...")
strict_data = {
    'low': load_mineral_data_pair(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_low.xlsx"),
    'medium': load_mineral_data_pair(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_medium.xlsx"),
    'high': load_mineral_data_pair(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_high.xlsx")
}

flex_data = {
    'low': load_mineral_data_pair(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_low.xlsx"),
    'medium': load_mineral_data_pair(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_medium.xlsx"),
    'high': load_mineral_data_pair(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_high.xlsx")
}

if any(v is not None for v in strict_data.values()):
    print("📊 Generating Grid for Strict...")
    create_big_grid_plot("NZIA Strict", strict_data, "Grid_18_Strict_FullNames", STRICT_COLOR)

if any(v is not None for v in flex_data.values()):
    print("📊 Generating Grid for Flex...")
    create_big_grid_plot("NZIA Flex", flex_data, "Grid_18_Flex_FullNames", FLEX_COLOR)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ================= FORMATTING =================
plt.rcParams["font.family"] = "Arial"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# ================= CONFIGURATION =================
RESULT_DIRECTORY = "result"
YEARS_TO_PLOT = [2030, 2035, 2040]
BASELINE_YEAR = 2024
STAGES = ['Polysilicon', 'Wafer', 'Cell', 'Module']

# FIXED DISPLAY ORDER
SCENARIO_ORDER = ['Base_case', 'high', 'medium', 'low']

SCENARIO_COLORS = {
    'Base_case': '#F4E100',  # Yellow/Gold
    'low': '#3A737D',  # Teal Blue
    'medium': '#05A5D2',  # Bright Blue
    'high': '#D79327'  # Orange/Bronze
}

SCENARIO_LABELS = {
    'Base_case': 'Base Case',
    'low': 'Low Scrap Price',
    'medium': 'Medium Scrap Price',
    'high': 'High Scrap Price'
}


# ================= DATA LOADING =================
def load_clean_data(base_dir, folder, filename):
    path = os.path.join(base_dir, folder, filename)
    if not os.path.exists(path):
        print(f"⚠️ Missing: {path}")
        return None

    try:
        df = pd.read_excel(path, sheet_name="processing_capacities")
        cols = ['stf', 'location', 'tech']
        # Fix missing values
        df[[c for c in cols if c in df.columns]] = df[[c for c in cols if c in df.columns]].ffill()

        # Filter
        df = df[df['stages'].isin(STAGES)].copy()
        df = df[df['stf'].isin(set(YEARS_TO_PLOT) | {BASELINE_YEAR})].copy()

        # Group and sum -> Convert to GW
        agg = df.groupby(['stf', 'stages'])['capacity_processing_total'].sum().unstack()
        agg = agg.reindex(columns=STAGES).fillna(0) / 1000  # Convert MW to GW
        return agg
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ================= NEW PLOTTING ENGINE (TOTALS) =================
def create_vertical_total_plot(group_name, scenario_data, output_name):
    """
    3x1 Grid (Vertical Stack).
    X-Axis: Stages.
    Y-Values: Total Capacity (Side-by-side bars, Solid colors).
    """

    # Setup Figure: 3 Rows (Years), 1 Column
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

        n_stages = len(STAGES)
        n_scens = len(SCENARIO_ORDER)

        bar_width = 0.18
        gap = 0.04
        indices = np.arange(n_stages)

        # --- LOOP STAGES ---
        for j, stage in enumerate(STAGES):
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

                # Optional: Add text label on top of very small bars or specific highlights
                # Here we just rely on the Y-axis for cleanliness, as requested.

        # Formatting
        ax.set_title(f"{year}", fontweight='bold', fontsize=16)
        ax.set_xticks(indices)

        # Only show X-axis labels on the BOTTOM plot (index 2)
        if i == 2:
            ax.set_xticklabels(STAGES, fontweight='bold', fontsize=16)
        else:
            ax.set_xticklabels([])  # Hide labels for top and middle plots

        ax.set_ylim(0, y_limit)
        ax.tick_params(axis='y', labelsize=14)
        ax.set_ylabel("Processing Capacity (GW/yr)", fontweight='bold', fontsize=14)

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

    # Title
    # plt.suptitle(f"Total Processing Capacity: {group_name}", fontsize=18, weight='bold', y=0.98)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.08, top=0.95, hspace=0.15)

    out_file = f"{output_name}.pdf"
    plt.savefig(out_file, bbox_inches='tight')
    print(f"✅ Saved: {out_file}")
    plt.show()


# ================= MAIN EXECUTION =================

print("📂 Loading Data...")
df_base = load_clean_data(RESULT_DIRECTORY, "Base_case", "scenario_solar_recycling_high.xlsx")

if df_base is not None:
    # Strict Scenarios
    data_strict = {
        'Base_case': df_base,
        'low': load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_low.xlsx"),
        'medium': load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_medium.xlsx"),
        'high': load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_high.xlsx")
    }

    # Flex Scenarios
    data_flex = {
        'Base_case': df_base,
        'low': load_clean_data(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_low.xlsx"),
        'medium': load_clean_data(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_medium.xlsx"),
        'high': load_clean_data(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_high.xlsx")
    }

    print("📊 Generating Total Capacity Plot (Strict)...")
    create_vertical_total_plot("NZIA Strict", data_strict, "Plot_Vertical_Total_Strict")

    print("📊 Generating Total Capacity Plot (Flex)...")
    create_vertical_total_plot("NZIA Flex", data_flex, "Plot_Vertical_Total_Flex")

else:
    print("❌ Base Case data missing.")