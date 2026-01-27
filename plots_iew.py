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
from matplotlib.ticker import StrMethodFormatter
from pathlib import Path
import os

# ================= FORMATTING =================
plt.rcParams["font.family"] = "Arial"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# Define the specific color for Solar PV (Adjust if you have a specific palette)
SOLAR_COLOR = "#E69F00"

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

    # Forward Fill columns
    cols_to_fix = ['stf', 'location', 'tech']
    existing_cols = [c for c in cols_to_fix if c in df.columns]
    df[existing_cols] = df[existing_cols].ffill()

    # Filter for 'solarPV'
    mask = df['tech'].astype(str).str.contains("solarPV", case=False, na=False)
    df_filtered = df[mask].copy()

    # Group by Year ('stf')
    capacity_series = df_filtered.groupby('stf')['capacity_ext'].sum()

    return capacity_series


# ================= PLOTTING FUNCTION =================
def plot_cumulative_capacity_styled(data_series, output_dir="plots"):
    """
    Vertical bar plot of Total Solar Installed Capacity (GW) 2024-2040.
    Exact style match: Frame visible, White grid overlays bars.
    """

    # 1. Prepare Data (MW -> GW)
    data_gw = data_series / 1000
    years = list(range(2024, 2041))
    plot_data = data_gw.reindex(years).fillna(0)

    # 2. Setup Figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # 3. Plotting
    # Z-ORDER 2: Bars sit below the grid (which is 7)
    ax.bar(
        plot_data.index,
        plot_data.values,
        color=SOLAR_COLOR,
        label="Solar PV",
        edgecolor="white",  # Matches reference style for bar edges
        width=0.7,
        zorder=2
    )

    # 4. Axis Formatting
    ax.set_xticks([2024, 2030, 2035, 2040])
    ax.set_xticklabels([str(y) for y in [2024, 2030, 2035, 2040]], fontsize=25)

    ax.set_ylabel("Installed Capacity (GW)", fontsize=22)
    ax.tick_params(axis="x", labelsize=22, rotation=0, pad=6)
    ax.tick_params(axis="y", labelsize=22)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    # 5. Visual Styling (Background & Grid)
    ax.set_facecolor("#F3F3F3")

    # Z-ORDER 7: Grid sits ON TOP of bars
    ax.grid(axis="y", color="white", linewidth=2, zorder=7)

    # NOTE: We removed the lines that hid the spines (ax.spines[...].set_visible(False))
    # This restores the default black frame around the plot.

    # 6. Legend
    handles = [
        mpatches.Patch(
            facecolor=SOLAR_COLOR,
            edgecolor="#666666",
            linewidth=0.6,
            label="Solar PV"
        )
    ]

    legend = ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=1,
        frameon=False,
        fontsize=22,
        handlelength=1.5,
        handletextpad=0.6,
        columnspacing=1.2,
    )

    # Make legend boxes more visible
    for lh in legend.legendHandles:
        try:
            lh.set_linewidth(0.6)
        except Exception:
            pass

    # 7. Layout & Save
    plt.tight_layout(rect=[0.02, 0.06, 0.98, 0.94])
    plt.subplots_adjust(bottom=0.25)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "Fig_Cumulative_Solar_Capacity.png"
    plt.savefig(output_path, dpi=900, bbox_inches="tight")
    plt.show()
    print(f"✔ Styled Cumulative Capacity chart saved → {output_path}")


# ================= MAIN EXECUTION =================
RESULT_DIRECTORY = "result"

# Load Data
data_capacity = get_total_capacity_ext(RESULT_DIRECTORY)

if data_capacity is not None:
    plot_cumulative_capacity_styled(data_capacity)
else:
    print("⚠️ Skipping plot due to missing data.")
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ================= FORMATTING =================
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 16
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3
plt.rcParams["axes.axisbelow"] = True

# ================= CONFIGURATION =================
RESULT_DIRECTORY = "result"
YEARS_TO_PLOT = [2025, 2030, 2035, 2040]
BASELINE_YEAR = 2024
STAGES = ['Polysilicon', 'Wafer', 'Cell', 'Module']

STAGE_COLORS = {
    'Polysilicon': '#F4E100',
    'Wafer': '#3A737D',
    'Cell': '#05A5D2',
    'Module': '#D79327'
}


# ================= DATA LOADING =================
def load_clean_data(base_dir, folder, filename):
    path = os.path.join(base_dir, folder, filename)
    if not os.path.exists(path):
        print(f"⚠️ Missing: {path}")
        return None

    try:
        df = pd.read_excel(path, sheet_name="processing_capacities")
        # Fix merged cells
        cols = ['stf', 'location', 'tech']
        df[[c for c in cols if c in df.columns]] = df[[c for c in cols if c in df.columns]].ffill()

        # Filter
        df = df[df['stages'].isin(STAGES)].copy()
        df = df[df['stf'].isin(set(YEARS_TO_PLOT) | {BASELINE_YEAR})].copy()

        # Aggregation (GW)
        agg = df.groupby(['stf', 'stages'])['capacity_processing_total'].sum().unstack()
        agg = agg.reindex(columns=STAGES).fillna(0) / 1000
        return agg
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ================= PLOTTING ENGINE =================
def create_2x2_plot(group_name, scenario_data, output_name):
    """
    Generates a 2x2 plot (2025, 2030, 2035, 2040) with a bottom legend.
    """
    fig, axs = plt.subplots(2, 2, figsize=(16, 10))
    axs = axs.flatten()

    x_labels = ["Base Case", "Low", "Medium", "High"]

    # Get Baseline (2024)
    base_df = scenario_data['Base_case']
    baseline_vals = base_df.loc[BASELINE_YEAR] if BASELINE_YEAR in base_df.index else pd.Series(0, index=STAGES)

    # --- LOOP YEARS ---
    for i, year in enumerate(YEARS_TO_PLOT):
        ax = axs[i]

        # Collect data for [Base, Low, Med, High] for this specific year
        datasets = []
        keys = ['Base_case', 'low', 'medium', 'high']

        for k in keys:
            df = scenario_data[k] if k in scenario_data else scenario_data['Base_case']
            if df is not None and year in df.index:
                datasets.append(df.loc[year])
            else:
                datasets.append(pd.Series(0, index=STAGES))

        # --- BAR LOGIC ---
        n_groups = len(datasets)
        n_bars = len(STAGES)
        total_width = 0.85
        bar_width = total_width / n_bars
        indices = np.arange(n_groups)

        for j, stage in enumerate(STAGES):
            color = STAGE_COLORS.get(stage, 'gray')
            x_pos = indices + (j - n_bars / 2 + 0.5) * bar_width

            totals = [ds[stage] for ds in datasets]
            base_val = baseline_vals[stage]
            solids = [min(t, base_val) for t in totals]

            # Layer 1: Hatched (Total)
            ax.bar(x_pos, totals, width=bar_width,
                   facecolor='white', edgecolor=color, hatch='////',
                   linewidth=0.6, label='_nolegend_')

            # Layer 2: Solid (Baseline)
            ax.bar(x_pos, solids, width=bar_width,
                   color=color, edgecolor='black', linewidth=0.5,
                   label='_nolegend_')  # Legend is handled manually below

        # Formatting
        ax.set_title(f"{year}")
        ax.set_xticks(indices)
        ax.set_xticklabels(x_labels)
        ax.set_ylabel("Processing Capacity (GW)")

        all_max = max([d.max() for d in datasets]) if datasets else 1
        ax.set_ylim(0, all_max * 1.15)

        # --- LEGEND CONSTRUCTION ---
        handles = []

        # 1. Colors (Now with black borders)
        for s in STAGES:
            handles.append(mpatches.Patch(
                facecolor=STAGE_COLORS[s],
                edgecolor='black',  # Adds the black frame
                linewidth=0.6,  # Sets the frame thickness
                label=s
            ))

        # 2. Hatch (Already had a border, just ensuring it matches)
        handles.append(mpatches.Patch(
            facecolor='white',
            edgecolor='black',
            hatch='////',
            linewidth=0.6,
            label='New Capacity'
        ))

        # Place legend beneath the entire figure
        fig.legend(handles=handles,
                   loc='lower center',
                   bbox_to_anchor=(0.5, 0.02),
                   ncol=5,
                   frameon=True,
                   fontsize=16)  # Check your fontsize here

    # Title & Layout
    plt.suptitle(f"Processing Capacities: {group_name}", fontsize=16, weight='bold', y=0.98)

    # Adjust bottom margin to make space for the legend
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)

    # Save
    out_file = f"{output_name}.pdf"
    plt.savefig(out_file, bbox_inches='tight')
    print(f"✅ Saved: {out_file}")
    plt.show()


# ================= MAIN EXECUTION =================

print("📂 Loading Data...")
df_base = load_clean_data(RESULT_DIRECTORY, "Base_case", "scenario_solar_recycling_high.xlsx")

if df_base is not None:
    # NZIA Strict Data
    data_strict = {
        'Base_case': df_base,
        'low': load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_low.xlsx"),
        'medium': load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_medium.xlsx"),
        'high': load_clean_data(RESULT_DIRECTORY, "LR4_nziastrict", "scenario_solar_recycling_high.xlsx")
    }

    # NZIA Flex Data
    data_flex = {
        'Base_case': df_base,
        'low': load_clean_data(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_low.xlsx"),
        'medium': load_clean_data(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_medium.xlsx"),
        'high': load_clean_data(RESULT_DIRECTORY, "LR4_nziaflex", "scenario_solar_recycling_high.xlsx")
    }

    print("📊 Generating Strict PDF...")
    create_2x2_plot("NZIA Strict Scenarios", data_strict, "Plot_2x2_NZIA_Strict")

    print("📊 Generating Flex PDF...")
    create_2x2_plot("NZIA Flex Scenarios", data_flex, "Plot_2x2_NZIA_Flex")
else:
    print("❌ Base Case data missing. Cannot plot.")

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
SCENARIOS = ['low', 'medium', 'high']
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

STRICT_COLOR = '#d62728'  # Red
FLEX_COLOR = '#1f77b4'  # Blue


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
        return results

    except Exception as e:
        print(f"❌ Error loading {folder}/{filename}: {e}")
        return None


# ================= PLOTTING ENGINE =================
def create_big_grid_plot(group_name, data_dict, output_name, main_color):
    """
    Creates a 6x3 Grid.
    - Rows = Materials (Full Names)
    - Cols = Scenarios
    - Shared Y-Axis Scale per Row
    """
    fig, axs = plt.subplots(6, 3, figsize=(12, 18))

    # Column Titles
    cols = ["Low Scrap Prices", "Medium Scrap Prices", "High Scrap Prices"]
    for ax, col in zip(axs[0], cols):
        ax.set_title(col, fontsize=14, weight='bold', pad=15)

    # LOOP ROWS (Materials)
    for i, mat in enumerate(MATERIALS):
        # Unpack the new 3-element tuple
        full_name, unit_label, divisor = UNIT_MAP[mat]

        # 1. FIND MAX Y-VALUE FOR THIS ROW
        row_max_y = 0
        for sens in SCENARIOS:
            if sens in data_dict and data_dict[sens] is not None:
                vals = data_dict[sens]['total'][mat] / divisor
                current_max = vals.max()
                if current_max > row_max_y:
                    row_max_y = current_max

        y_limit = row_max_y * 1.1 if row_max_y > 0 else 1

        # 2. PLOT EACH COLUMN
        for j, sens in enumerate(SCENARIOS):
            ax = axs[i, j]

            if sens in data_dict and data_dict[sens] is not None:
                df_total = data_dict[sens]['total']
                df_imports = data_dict[sens]['imports']

                y_total = df_total[mat] / divisor
                y_imports = df_imports[mat] / divisor

                # Plot
                ax.plot(y_total.index, y_total, color=main_color, lw=2)
                ax.fill_between(y_imports.index, 0, y_imports, color=main_color, alpha=0.3, linewidth=0)

                # Setup Axes
                ax.set_ylim(0, y_limit)
                ax.set_xlim(2024, 2040)
                ax.set_xticks([2025, 2030, 2035, 2040])

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                # Row Label (FULL NAME) - Left column only
                if j == 0:
                    ax.set_ylabel(f"{full_name}\n({unit_label})", fontsize=12, weight='bold')

                # X Labels - Bottom row only, Horizontal
                if i == 5:
                    ax.tick_params(axis='x', rotation=0)
                else:
                    ax.set_xticklabels([])

                    # --- LEGEND ---
    handles = [
        plt.Line2D([], [], color=main_color, lw=2, label='Annual Demand'),
        mpatches.Patch(color=main_color, alpha=0.3, label='Material Imports'),
        mpatches.Patch(facecolor='white', edgecolor='lightgray', hatch='///', label='Domestic Supply')
    ]

    fig.legend(handles=handles, loc='lower center', ncol=3, frameon=False, fontsize=14, bbox_to_anchor=(0.5, 0.02))

    #plt.suptitle(f"Material Demand & Imports (Yearly): {group_name}", fontsize=18, weight='bold', y=0.99)
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