from matplotlib import ticker as mticker
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------
# Paths
# -------------------------------
BASE_PATH = Path("result/base")
NZIA_PATH = Path("result/NZIA")

# Learning rate folders
LR_FOLDERS = ["LR1", "LR3_5", "LR4", "LR5", "LR6", "LR7", "LR8", "LR9", "LR10"]

# Scenario names
SCENARIO_NAMES = [
    "scenario_min_min_min",
    "scenario_min_min_avg",
    "scenario_min_min_high",
    "scenario_min_avg_min",
    "scenario_min_avg_avg",
    "scenario_min_avg_high",
    "scenario_min_high_min",
    "scenario_min_high_avg",
    "scenario_min_high_high",
    "scenario_avg_min_min",
    "scenario_avg_min_avg",
    "scenario_avg_min_high",
    "scenario_avg_avg_min",
    "scenario_avg_avg_avg",
    "scenario_avg_avg_high",
    "scenario_avg_high_min",
    "scenario_avg_high_avg",
    "scenario_avg_high_high",
    "scenario_high_min_min",
    "scenario_high_min_avg",
    "scenario_high_min_high",
    "scenario_high_avg_min",
    "scenario_high_avg_avg",
    "scenario_high_avg_high",
    "scenario_high_high_min",
    "scenario_high_high_avg",
    "scenario_high_high_high",
]

# -------------------------------
# Map LR folder + scenario → Excel path
# -------------------------------
NZIA_SCENARIOS = {}
for lr in LR_FOLDERS:
    lr_path = NZIA_PATH / lr
    for scenario in SCENARIO_NAMES:
        scenario_file = lr_path / f"{scenario}.xlsx"
        NZIA_SCENARIOS[(lr, scenario)] = scenario_file

# Base scenario
BASE_SCENARIO = BASE_PATH / "LR1" / "scenario_high_high_high.xlsx"

GROUPS = {
    "Fossil fuels generation": [
        "Coal Plant", "Coal Plant CCUS", "Gas Plant (CCGT)", "Gas Plant (CCGT) CCUS",
        "Lignite Plant", "Lignite Plant CCUS", "Oil Plant", "Other non-res"
    ],
    "Renewable generation": [
        "Hydro (reservoir)", "Hydro (run-of-river)", "solarPV", "windoff", "windon"
    ],
    "Thermal nuclear generation": ["Nuclear Plant"]
}

GROUP_COLORS = {
    "Fossil fuels generation": "#F4C20D",
    "Renewable generation": "#009688",
    "Thermal nuclear generation": "#F57C00"
}

def mwh_to_bcm(mwh):
    """
    Convert MWh to BCM (billion cubic meters of natural gas equivalent).
    """
    mmbtu = mwh * 3.412         # 1 MWh = 3.412 MMBtu
    bcm = mmbtu / 35_315_000    # 1 BCM = 35,315,000 MMBtu
    return bcm

def load_lng(file_path, years):
    df = pd.read_excel(file_path, sheet_name="gas demand per block")
    df["blocks"] = df["blocks"].astype(str).str.strip()
    df["stf"] = df["stf"].ffill()
    lng_df = df[~df["blocks"].str.lower().str.contains("pipegas")]
    lng_df = lng_df[lng_df["stf"].between(min(years), max(years))]

    yearly = lng_df.groupby("stf")["gas_usage_block"].sum().reset_index()
    yearly["lng_bcm"] = yearly["gas_usage_block"].apply(mwh_to_bcm)

    series = pd.Series(0, index=years, dtype=float)
    for _, row in yearly.iterrows():
        series[int(row["stf"])] = row["lng_bcm"]
    return series

def plot_base_scenario(
        base_file: Path,
        sheet_name: str = "extension_balance",
        years: list = list(range(2025, 2041)),
        output_dir: str = "plots",
        convert_to_twh: bool = True
):
    """
    Plot the base scenario generation mix:
      1) 4x4 donut charts per year
      2) 100% stacked horizontal bar chart

    Args:
        base_file (Path): Path to the base scenario Excel file
        sheet_name (str): Sheet name in Excel
        years (list): List of years to plot
        output_dir (str): Directory to save the plots
        convert_to_twh (bool): Convert MWh → TWh if True
    """
    df = pd.read_excel(base_file, sheet_name=sheet_name)


    # -------------------------------
    # Prepare yearly aggregated data
    # -------------------------------
    yearly_data = {}
    for year in years:
        year_df = df[df["Stf"] == year]
        summary = {}
        for group, processes in GROUPS.items():
            value = year_df[year_df["Process"].isin(processes)]["Value"].sum()
            if convert_to_twh:
                value /= 1_000_000
            summary[group] = value
        yearly_data[year] = summary

    # -------------------------------
    # Donut Chart (4x4)
    # -------------------------------
    fig, axes = plt.subplots(4, 4, figsize=(16, 16))
    axes = axes.flatten()

    for i, year in enumerate(years):
        data = yearly_data[year]
        total = sum(data.values())
        sizes = [v / total for v in data.values()]

        axes[i].pie(
            sizes,
            labels=list(data.keys()),
            colors=[GROUP_COLORS[k] for k in data.keys()],
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor="w")
        )
        axes[i].set_title(f"{year} (TWh)" if convert_to_twh else str(year), fontsize=12)

    # Remove empty subplots
    for j in range(i + 1, 16):
        fig.delaxes(axes[j])

    plt.suptitle(
        "Base Scenario Generation Mix (TWh)" if convert_to_twh else "Base Scenario Generation Mix",
        fontsize=16
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    output_path = Path(output_dir) / "base_generation_mix_donut.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.show()
    print(f"✔ Base scenario donut chart saved → {output_path}")

    # -------------------------------
    # 100% Stacked Horizontal Bar Chart
    # -------------------------------
    # Prepare DataFrame
    records = []
    group_order = list(GROUPS.keys())
    for year in years:
        year_df = df[df["Stf"] == year]
        totals = {g: year_df[year_df["Process"].isin(GROUPS[g])]["Value"].sum() for g in group_order}
        total_all = sum(totals.values())
        if total_all <= 0:
            shares = {g: 0 for g in group_order}
        else:
            shares = {g: totals[g] / total_all for g in group_order}
        records.append({"year": year, **shares})

    data = pd.DataFrame(records)

    # Plot
    n = len(years)
    fig_h = max(10, 0.52 * n + 3.5)
    fig, ax = plt.subplots(figsize=(10, fig_h))

    y_pos = np.arange(n)
    left = np.zeros(n)
    bar_height = 0.6

    for g in group_order:
        width = data[g].values * 100
        ax.barh(
            y_pos,
            width,
            left=left,
            height=bar_height,
            color=GROUP_COLORS[g],
            edgecolor="white",
            linewidth=1.2,
            zorder=5
        )
        left += width

    ax.set_yticks(y_pos, [str(y) for y in years])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
    ax.xaxis.set_ticks_position("top")
    ax.tick_params(axis="x", labelsize=11, colors="#3C3C3C")
    ax.tick_params(axis="y", labelsize=11, colors="#3C3C3C")

    # Vertical separators every 10%
    ax.vlines(np.arange(0, 101, 10), -0.5, n - 0.5, colors="white", linewidth=1.5, zorder=7)

    ax.set_facecolor("#E6E6E6")
    for spine in ax.spines.values():
        spine.set_color("#9E9E9E")
        spine.set_linewidth(1)

    ax.set_title("Base Scenario Generation Share by Year (%)", loc="left", fontsize=18, fontweight="bold",
                 color="#1F4E79")

    handles = [plt.Rectangle((0, 0), 1, 1, color=GROUP_COLORS[g]) for g in group_order]
    ax.legend(handles, group_order, loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=len(group_order),
              frameon=False, fontsize=11)

    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.94])
    output_path = Path(output_dir) / "base_generation_share_100pct.png"
    plt.savefig(output_path, dpi=300)
    plt.show()
    print(f"✔ Base scenario 100% stacked bar chart saved → {output_path}")

def plot_scrap_with_nzia_range_from_dict(
    base_file: Path,
    nzia_scenarios_dict: dict,
    sheet_name: str = "Total_Scrap",
    years: list = list(range(2024, 2041)),
    output_dir: str = "plots/scrap_range",
    convert_to_mt: bool = True,
    include_mean: bool = True,
    lr_filter: str = None,
    scenario_filter: str = None,
):
    """
    For each technology:
      - plot base scenario line (base_file)
      - plot NZIA min-max shaded band across provided NZIA files (from nzia_scenarios_dict)
      - optionally plot NZIA mean dashed line

    nzia_scenarios_dict: dict with keys (lr, scenario) and values Path objects pointing to .xlsx files
    """

    years = list(years)
    min_year, max_year = min(years), max(years)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # helper: find which column names exist in a dataframe
    def _find_col(df, candidates):
        for c in candidates:
            if c in df.columns:
                return c
        return None

    # helper: load a file and return a pivot DataFrame (index=years, columns=techs) aggregated by year,tech
    def _load_and_pivot(file_path):
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            print(f"⚠ could not read {file_path}: {e}")
            return pd.DataFrame(index=years)  # empty

        # guess column names
        year_col = _find_col(df, ["stf", "Stf", "year", "Year"])
        tech_col = _find_col(df, ["tech", "Tech", "key_1", "key1", "technology", "Process"])
        value_col = _find_col(df, ["capacity_scrap_total", "value", "capacity_scrap", "capacity_scrap_tonnes"])

        if year_col is None or tech_col is None or value_col is None:
            print(f"⚠ Missing expected columns in {file_path}. Found: {df.columns.tolist()}")
            return pd.DataFrame(index=years)

        # forward-fill years because your sheet shows a single year cell then blank rows
        df[year_col] = df[year_col].ffill()

        # convert year to numeric (coerce bad values -> NaN) and drop non-numeric
        df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
        df = df.dropna(subset=[year_col])
        df[year_col] = df[year_col].astype(int)

        # filter by year range
        df = df[(df[year_col] >= min_year) & (df[year_col] <= max_year)]

        # convert values to numeric and aggregate duplicates by summing
        df[value_col] = pd.to_numeric(df[value_col], errors="coerce").fillna(0)

        grouped = df.groupby([year_col, tech_col], as_index=True)[value_col].sum().reset_index()

        # pivot so index = year, columns = tech, values = aggregated scrap
        pivot = grouped.pivot(index=year_col, columns=tech_col, values=value_col).fillna(0)

        # reindex to ensure all years are present and sorted
        pivot = pivot.reindex(years, fill_value=0)

        # optionally convert to Mt (from tonnes)
        if convert_to_mt:
            pivot = pivot / 1e6

        return pivot

    # --- load base pivot ---
    base_pivot = _load_and_pivot(base_file)
    if base_pivot.empty:
        print(f"⚠ Base file produced no data: {base_file}")

    # --- collect NZIA files (respect optional filters) ---
    nzia_files = []
    for (lr, scenario), path in nzia_scenarios_dict.items():
        if lr_filter is not None and lr != lr_filter:
            continue
        if scenario_filter is not None and scenario != scenario_filter:
            continue
        if not Path(path).exists():
            # warn but keep going
            print(f"⚠ NZIA file not found, skipping: {path}")
            continue
        nzia_files.append(Path(path))

    if not nzia_files:
        print("⚠ No NZIA files found after applying filters — aborting.")
        return

    # --- load all NZIA pivots and build per-tech series lists ---
    # We'll make a union of techs across base and all nzia files
    tech_set = set(base_pivot.columns.tolist())
    nzia_pivots = []
    for f in nzia_files:
        p = _load_and_pivot(f)
        nzia_pivots.append(p)
        tech_set.update(p.columns.tolist())

    techs = sorted(list(tech_set))

    # For each tech, collect a DataFrame where columns are scenarios and index=years
    for tech in techs:
        # base series (if missing -> zeros)
        if tech in base_pivot.columns:
            base_series = base_pivot[tech].reindex(years).fillna(0)
        else:
            base_series = pd.Series(0.0, index=years)

        # collect NZIA series for this tech
        nzia_series_list = []
        for p in nzia_pivots:
            if tech in p.columns:
                s = p[tech].reindex(years).fillna(0)
            else:
                s = pd.Series(0.0, index=years)
            nzia_series_list.append(s)

        if len(nzia_series_list) == 0:
            print(f"⚠ No NZIA data for tech '{tech}', skipping.")
            continue

        nzia_df = pd.DataFrame(nzia_series_list).T  # index=years, columns=scenarios

        # compute min, max, mean across NZIA scenarios
        nz_min = nzia_df.min(axis=1)
        nz_max = nzia_df.max(axis=1)
        nz_mean = nzia_df.mean(axis=1)

        # skip if everything zero
        if (base_series.sum() == 0) and (nz_max.max() == 0):
            print(f"⚠ All-zero for tech '{tech}', skipping.")
            continue

        # --- Plot ---
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(years, base_series.values, color="darkred", linewidth=2.2, label="Base scenario")
        ax.fill_between(years, nz_min.values, nz_max.values, color="seagreen", alpha=0.25, label="NZIA min–max range")
        if include_mean:
            ax.plot(years, nz_mean.values, color="seagreen", linestyle="--", linewidth=1.5, label="NZIA mean")

        ax.set_title(f"Scrap volume — {tech}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Scrap [Mt]" if convert_to_mt else "Scrap [tonnes]")
        ax.set_xlim(min_year - 1, max_year + 1)
        ax.set_xticks([2025, 2030, 2035, 2040])
        # safe y-limit
        ymax = max(base_series.max(), nz_max.max())
        ax.set_ylim(0, ymax * 1.1 if ymax > 0 else 1)
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.legend()

        plt.tight_layout()
        safe_tech = str(tech).replace("/", "_").replace(" ", "_")
        fname = out_path / f"scrap_range_{safe_tech}.png"
        fig.savefig(fname, dpi=300)
        plt.close(fig)

        print(f"✔ Saved: {fname}")

def plot_lng_spaghetti(base_file, nzia_files, years=range(2024, 2041), output_file="lng_spaghetti.png"):
    """
    Plot LNG demand across all NZIA scenarios as thin lines,
    highlighting the base scenario.

    Args:
        base_file (Path): Path to the base scenario Excel file.
        nzia_files (list[Path]): List of NZIA scenario Excel files.
        years (range): Year range to plot.
        output_file (str): Where to save the figure.
    """

    # Helper to load LNG demand from a file
    def load_lng(file_path):
        df = pd.read_excel(file_path, sheet_name="gas demand per block")
        df["blocks"] = df["blocks"].astype(str).str.strip()
        df["stf"] = df["stf"].ffill()
        lng_df = df[~df["blocks"].str.lower().str.contains("pipegas")]
        lng_df = lng_df[lng_df["stf"].between(min(years), max(years))]

        yearly = lng_df.groupby("stf")["gas_usage_block"].sum().reset_index()
        yearly["lng_bcm"] = yearly["gas_usage_block"].apply(mwh_to_bcm)

        series = pd.Series(0, index=years, dtype=float)
        for _, row in yearly.iterrows():
            series[int(row["stf"])] = row["lng_bcm"]
        return series

    plt.figure(figsize=(8, 5))

    # Plot NZIA scenarios as thin grey lines
    for f in nzia_files:
        series = load_lng(f)
        plt.plot(series.index, series.values, color="grey", alpha=0.3, linewidth=1)

    # Plot base scenario bold
    base_series = load_lng(base_file)
    plt.plot(
        base_series.index,
        base_series.values,
        color="seagreen",
        linewidth=2.5,
        label="Base scenario"
    )

    # Labels & style
    plt.xlabel("Year")
    plt.ylabel("LNG Demand [BCM]")
    plt.title("LNG Demand – NZIA scenarios vs. Base")
    plt.xlim(min(years) - 1, max(years) + 1)
    plt.xticks([2025, 2030, 2035, 2040])
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()

    # Save
    output_file = Path(output_file)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(output_file, dpi=300)
    plt.show()
    print(f"✔ LNG spaghetti plot saved → {output_file}")


def plot_lng_cumulative_pct_deviation_pretty(base_file, nzia_files, years=range(2024, 2041),
                                             target_years=[2025, 2030, 2035, 2040],
                                             output_file="lng_cumulative_pct_boxplot_pretty.png"):
    """
    Beautiful boxplots of cumulative LNG percentage deviations from base,
    with scatter points for individual scenarios.
    """

    # --- Load base cumulative ---
    base_series = load_lng(base_file, years).cumsum()

    # --- Load NZIA cumulative ---
    nzia_series = [load_lng(f, years).cumsum() for f in nzia_files]

    # --- Build DataFrame ---
    data = pd.DataFrame({i: s for i, s in enumerate(nzia_series)}).T

    # --- Percentage deviations ---
    pct_dev = pd.DataFrame({
        y: 100 * (data[y] - base_series[y]) / base_series[y] for y in target_years
    })

    # --- Plot ---
    plt.figure(figsize=(8, 5))

    # Boxplots with soft colors
    box_data = [pct_dev[y].dropna() for y in target_years]
    bp = plt.boxplot(
        box_data,
        positions=target_years,
        widths=1.0,
        patch_artist=True,
        boxprops=dict(facecolor="lightsteelblue", alpha=0.6, linewidth=1.2),
        medianprops=dict(color="darkblue", linewidth=2),
        whiskerprops=dict(color="grey", linestyle="--", linewidth=1.2),
        capprops=dict(color="grey", linewidth=1.2),
        flierprops=dict(marker="o", markersize=4, markerfacecolor="lightgrey", alpha=0.5)
    )

    # Scatter points for each scenario (jittered)
    for year in target_years:
        y_vals = pct_dev[year].dropna().values
        x_vals = [year + 0.08*(np.random.rand() - 0.5) for _ in y_vals]  # jitter
        plt.scatter(x_vals, y_vals, color="grey", alpha=0.6, s=30, zorder=3)

    # Base scenario reference line
    plt.axhline(0, color="seagreen", linewidth=2.5, linestyle="-", label="Base scenario")

    # --- Style ---
    plt.title("Cumulative LNG Demand – Percentage Deviation from Base", fontsize=14, weight="bold")
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Deviation from Base [%]", fontsize=12)
    plt.xticks(target_years, fontsize=11)
    plt.yticks(fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.legend(frameon=False, fontsize=11)

    plt.tight_layout()
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300)
    plt.show()
    print(f"✔ Pretty cumulative LNG % deviation boxplot saved → {output_file}")

def plot_lng_cumulative_pct_deviation_comparison(base_file, nzia_files, years=range(2024, 2041),
                                                 periods=[(2024, 2030), (2030, 2035), (2035, 2040), (2024, 2040)],
                                                 labels=["2024–2030", "2030–2035", "2035–2040", "2024–2040"],
                                                 output_file="lng_cumulative_pct_scatter_comparison.png"):
    """
    Replicates compact scatter+median style plot:
    - Groups: 2024–2030, 2030–2035, 2035–2040, 2024–2040
    - Each group has colorful scatters + median deviation line
    - X-axis labeled 'Comparison to base'
    """

    # --- Load base cumulative ---
    base_series = load_lng(base_file, years).cumsum()

    # --- Load NZIA cumulative ---
    nzia_series = [load_lng(f, years).cumsum() for f in nzia_files]
    data = pd.DataFrame({i: s for i, s in enumerate(nzia_series)}).T

    # --- Calculate deviations for periods ---
    pct_dev = {}
    for (start, end), label in zip(periods, labels):
        dev_vals = 100 * ((data[end] - data[start]) - (base_series[end] - base_series[start])) \
                   / (base_series[end] - base_series[start])
        pct_dev[label] = dev_vals.dropna()

    # --- Plot ---
    plt.figure(figsize=(6.5, 4))
    positions = np.arange(len(labels))

    # Bright colors (one per group)
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for i, (label, color) in enumerate(zip(labels, colors)):
        vals = pct_dev[label]

        # Scatter points
        x_vals = [positions[i] + 0.15*(np.random.rand() - 0.5) for _ in vals]
        plt.scatter(x_vals, vals, color=color, alpha=0.9, s=28, zorder=3, edgecolors="k", linewidth=0.3)

        # Median line
        median_val = np.median(vals)
        plt.hlines(median_val, positions[i]-0.25, positions[i]+0.25, colors="black", linewidth=2.8)

    # --- Style ---
    plt.xticks(positions, labels, fontsize=11)
    plt.xlabel("Comparison to base", fontsize=12)
    plt.ylabel("Deviation from Base [%]", fontsize=12)
    plt.title("Cumulative LNG Demand – Comparison to Base", fontsize=13, weight="bold")

    # Clean grid (only y axis)
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()

    # Save
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300)
    plt.show()
    print(f"✔ Scatter+median comparison plot saved → {output_file}")




def plot_lng_boxplot(base_file, nzia_files, target_years=[2025, 2030, 2035, 2040],
                     output_file="plot/lng_boxplot.png", deviations=False):
    """
    Create boxplots of LNG demand (or deviations from base) for selected years.

    Args:
        base_file (Path): Path to the base scenario Excel file.
        nzia_files (list[Path]): List of NZIA scenario Excel files.
        target_years (list[int]): Target years to plot.
        output_file (str): File to save the plot.
        deviations (bool): If True, plot deviations from base scenario instead of absolute values.
    """

    # --- Helper to load LNG demand series ---
    def load_lng(file_path, years):
        df = pd.read_excel(file_path, sheet_name="gas demand per block")
        df["blocks"] = df["blocks"].astype(str).str.strip()
        df["stf"] = df["stf"].ffill()
        lng_df = df[~df["blocks"].str.lower().str.contains("pipegas")]
        lng_df = lng_df[lng_df["stf"].between(min(years), max(years))]

        yearly = lng_df.groupby("stf")["gas_usage_block"].sum().reset_index()
        yearly["lng_bcm"] = yearly["gas_usage_block"].apply(mwh_to_bcm)

        series = pd.Series(0, index=years, dtype=float)
        for _, row in yearly.iterrows():
            series[int(row["stf"])] = row["lng_bcm"]
        return series

    # --- Load base series ---
    base_series = load_lng(base_file, target_years)

    # --- Load all NZIA series ---
    nzia_series = [load_lng(f, target_years) for f in nzia_files]

    # Build dataframe for easier handling
    # Build dataframe: scenarios as rows, years as columns
    data = pd.DataFrame({i: s for i, s in enumerate(nzia_series)}).T

    # Keep only target years
    data = data[target_years]

    if deviations:
        # Compute deviation from base scenario
        for y in target_years:
            data[y] = data[y] - base_series[y]
        base_vals = [0 for y in target_years]  # base is reference (zero deviation)
        ylabel = "Deviation from Base [BCM]"
    else:
        base_vals = [base_series[y] for y in target_years]
        ylabel = "LNG Demand [BCM]"

    # --- Plot ---
    plt.figure(figsize=(7, 5))
    data.boxplot(column=target_years)
    plt.plot(range(1, len(target_years)+1), base_vals, "o-", color="seagreen",
             label="Base scenario", linewidth=2, markersize=6)

    plt.title("LNG Demand Scenarios – Boxplot")
    plt.ylabel(ylabel)
    plt.xticks(range(1, len(target_years)+1), target_years)
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.legend()

    # Save
    output_file = Path(output_file)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(output_file, dpi=300)
    plt.show()
    print(f"✔ LNG boxplot saved → {output_file}")

def plot_lng_cumulative_boxplot(base_file, nzia_files, years=range(2024, 2041),
                                target_years=[2025, 2030, 2035, 2040],
                                output_file="lng_cumulative_boxplot.png"):
    """
    Plot boxplots of cumulative LNG demand deviations from the base scenario
    for selected target years.

    Args:
        base_file (Path): Path to the base scenario Excel file.
        nzia_files (list[Path]): List of NZIA scenario Excel files.
        years (range): Full year range for cumulative calculation.
        target_years (list[int]): Years for which to show cumulative demand.
        output_file (str): File path to save the plot.
    """

    # --- Helper to load LNG demand as series ---
    def load_lng(file_path, years):
        df = pd.read_excel(file_path, sheet_name="gas demand per block")
        df["blocks"] = df["blocks"].astype(str).str.strip()
        df["stf"] = df["stf"].ffill()
        lng_df = df[~df["blocks"].str.lower().str.contains("pipegas")]
        lng_df = lng_df[lng_df["stf"].between(min(years), max(years))]

        yearly = lng_df.groupby("stf")["gas_usage_block"].sum().reset_index()
        yearly["lng_bcm"] = yearly["gas_usage_block"].apply(mwh_to_bcm)

        series = pd.Series(0, index=years, dtype=float)
        for _, row in yearly.iterrows():
            series[int(row["stf"])] = row["lng_bcm"]
        return series

    # --- Load base ---
    base_series = load_lng(base_file, years).cumsum()

    # --- Load all NZIA scenarios ---
    nzia_series = [load_lng(f, years).cumsum() for f in nzia_files]

    # --- Build dataframe (scenarios as rows, target years as columns) ---
    data = pd.DataFrame(
        {i: s for i, s in enumerate(nzia_series)}
    ).T[target_years]

    # --- Convert to deviations from base ---
    deviations = pd.DataFrame({
        y: data[y] - base_series[y] for y in target_years
    })

    # --- Base values (always 0 deviation) ---
    base_vals = [0 for _ in target_years]

    # --- Plot ---
    plt.figure(figsize=(7, 5))
    deviations.boxplot(column=target_years)
    plt.plot(range(1, len(target_years)+1), base_vals, "o-", color="seagreen",
             label="Base scenario", linewidth=2, markersize=6)

    plt.title("Cumulative LNG Demand – Deviation from Base Scenario")
    plt.ylabel("Deviation from Base [BCM]")
    plt.xticks(range(1, len(target_years)+1), target_years)
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.legend()

    # Save
    output_file = Path(output_file)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(output_file, dpi=300)
    plt.show()
    print(f"✔ Cumulative LNG boxplot saved → {output_file}")


def plot_system_costs_boxplot(base_file, nzia_files, years=range(2024, 2041), output_file="system_costs_boxplot.png"):
    """
    Plot total system costs over time:
    - Boxplots for NZIA scenarios
    - Base case as a line
    """
    # Load base scenario
    base_df = pd.read_excel(base_file, sheet_name="extension_cost")
    base_total = base_df.groupby("stf")["Total_Cost"].sum().reindex(years)

    # Collect NZIA totals
    nzia_totals = []
    for file in nzia_files:
        df = pd.read_excel(file, sheet_name="extension_cost")
        yearly_total = df.groupby("stf")["Total_Cost"].sum().reindex(years)
        nzia_totals.append(yearly_total.values)

    # Convert to DataFrame for plotting
    nzia_df = pd.DataFrame(nzia_totals, columns=years)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.boxplot(nzia_df.values, positions=years, widths=0.6, patch_artist=True,
               boxprops=dict(facecolor="lightblue", color="blue"),
               medianprops=dict(color="darkblue"),
               whiskerprops=dict(color="blue"),
               capprops=dict(color="blue"),
               flierprops=dict(markerfacecolor='blue', marker='o', alpha=0.5))

    # Base case line
    ax.plot(years, base_total.values, color="red", linewidth=2.5, label="Base Scenario")

    ax.set_xlabel("Year")
    ax.set_ylabel("Total System Cost [€]")
    ax.set_title("System Cost Comparison: NZIA Scenarios vs Base Case")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()

    # Save
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.show()
    print(f"✔ System costs boxplot saved → {output_path}")

def plot_system_costs_total_boxplot(
    base_file: Path,
    nzia_files: list,
    years=[2025, 2030, 2035, 2040],
    output_file="system_costs_total_boxplot.png",
):
    """
    Plot total system costs per scenario as boxplots for select years,
    with the base scenario overlaid as a line.
    """

    # --- Load base scenario ---
    df_base = pd.read_excel(base_file, sheet_name="extension_cost")
    df_base_total = df_base.groupby("stf")["Total_Cost"].sum()
    df_base_total = df_base_total.reindex(years)

    # --- Load NZIA scenarios ---
    nzia_totals = {y: [] for y in years}
    for f in nzia_files:
        df = pd.read_excel(f, sheet_name="extension_cost")
        totals = df.groupby("stf")["Total_Cost"].sum()
        for y in years:
            nzia_totals[y].append(totals.get(y, np.nan))

    # --- Prepare data for boxplots ---
    data = [nzia_totals[y] for y in years]

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(8, 5))
    box = ax.boxplot(data, labels=years, patch_artist=True, showfliers=False)

    # Color the boxes
    for patch in box['boxes']:
        patch.set_facecolor('#ADD8E6')  # light blue

    # Overlay base scenario as red line
    ax.plot(range(1, len(years)+1), df_base_total.values, color='red', marker='o', linewidth=2, label="Base scenario")

    ax.set_xlabel("Year")
    ax.set_ylabel("Total System Costs")
    ax.set_title("Total System Costs Comparison (NZIA vs Base)")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend()

    plt.tight_layout()
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300)
    plt.show()
    print(f"✔ Boxplot saved → {output_file}")

def plot_system_costs_cumulative_boxplot(base_file, nzia_files, years, output_file):
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    from pathlib import Path

    # --- Base scenario ---
    df_base = pd.read_excel(base_file, sheet_name="extension_cost")
    base_yearly = df_base.groupby("stf")["Total_Cost"].sum()
    base_cum = base_yearly.cumsum() / 1e9  # convert to billion €

    # --- NZIA scenarios ---
    nzia_cum_list = []
    for file in nzia_files:
        df = pd.read_excel(file, sheet_name="extension_cost")
        yearly_total = df.groupby("stf")["Total_Cost"].sum()
        cum = yearly_total.cumsum() / 1e9  # cumulative in billion €
        nzia_cum_list.append(cum)

    # --- Prepare boxplot data for selected years ---
    box_data = []
    for year in years:
        year_vals = [cum.get(year, np.nan) for cum in nzia_cum_list]
        box_data.append(year_vals)

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot(box_data, positions=range(len(years)), widths=0.6, patch_artist=True,
               boxprops=dict(facecolor='lightblue', color='blue'),
               medianprops=dict(color='blue'))

    # Plot base scenario cumulative values at selected years
    base_vals = [base_cum.get(y, np.nan) for y in years]
    ax.plot(range(len(years)), base_vals, color='red', marker='o', linewidth=2, label='Base Scenario')

    ax.set_xticks(range(len(years)))
    ax.set_xticklabels([str(y) for y in years])
    ax.set_ylabel("Cumulative System Cost [Billion €]")
    ax.set_xlabel("Year")
    ax.set_title("Cumulative System Costs with NZIA Scenarios")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()

    output_file = Path(output_file)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(output_file, dpi=300)
    plt.show()
    print(f"✔ Plot saved → {output_file}")

def plot_lng_cumulative_pct_deviation_compact(base_file, nzia_files,
                                              years=range(2024, 2041),
                                              target_years=[2025, 2030, 2035, 2040],
                                              output_file="lng_cumulative_pct_boxplot_compact.png"):
    """
    Compact, beautiful boxplot of cumulative LNG percentage deviation from base,
    with scatter points and base scenario reference markers only at target years.
    """

    # Load cumulative data
    base_series = load_lng(base_file, years).cumsum()
    nzia_series = [load_lng(f, years).cumsum() for f in nzia_files]
    data = pd.DataFrame({i: s for i, s in enumerate(nzia_series)}).T

    # Percentage deviations at target years
    pct_dev = pd.DataFrame({
        y: 100 * (data[y] - base_series[y]) / base_series[y] for y in target_years
    })

    # X-axis positions for boxplots (compact spacing)
    x_pos = np.arange(len(target_years)) + 1  # 1,2,3,4

    plt.figure(figsize=(7, 5))

    # Boxplots
    box_data = [pct_dev[y].dropna() for y in target_years]
    bp = plt.boxplot(
        box_data,
        positions=x_pos,
        widths=0.6,
        patch_artist=True,
        boxprops=dict(facecolor="lightsteelblue", alpha=0.6, linewidth=1.2),
        medianprops=dict(color="darkblue", linewidth=2),
        whiskerprops=dict(color="grey", linestyle="--", linewidth=1.2),
        capprops=dict(color="grey", linewidth=1.2),
        flierprops=dict(marker="o", markersize=4, markerfacecolor="lightgrey", alpha=0.5)
    )

    # Scatter points with jitter
    for i, year in enumerate(target_years):
        y_vals = pct_dev[year].dropna().values
        x_vals = [x_pos[i] + 0.08*(np.random.rand() - 0.5) for _ in y_vals]
        plt.scatter(x_vals, y_vals, color="grey", alpha=0.6, s=30, zorder=3)

    # Base scenario markers/line at target years
    base_pct = [0]*len(target_years)  # 0% deviation
    plt.plot(x_pos, base_pct, "o-", color="seagreen", linewidth=2.5, markersize=7, label="Base scenario")

    # --- Style ---
    plt.title("Cumulative LNG – % Deviation from Base", fontsize=13, weight="bold")
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Deviation from Base [%]", fontsize=12)
    plt.xticks(x_pos, target_years, fontsize=11)
    plt.yticks(fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.xlim(x_pos[0]-0.5, x_pos[-1]+0.5)
    plt.legend(frameon=False, fontsize=11)

    plt.tight_layout()
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300)
    plt.show()
    print(f"✔ Compact cumulative LNG % deviation boxplot saved → {output_file}")


nzia_files = list(NZIA_SCENARIOS.values())
BASE_FILE = BASE_SCENARIO
#plot_base_scenario(base_file=BASE_SCENARIO)
#plot_scrap_with_nzia_range_from_dict(
#    base_file=BASE_SCENARIO,
#    nzia_scenarios_dict=NZIA_SCENARIOS,
#    sheet_name="scrap",     output_dir="plots/scrap_range",
#    convert_to_mt=True,     include_mean=True
# )

#plot_lng_spaghetti(
#    base_file=BASE_FILE,
#    nzia_files=list(NZIA_SCENARIOS.values()),
#    years=range(2024, 2041),
#    output_file="scenario_comparison/lng_spaghetti.png"
#)

#plot_system_costs_boxplot(
#    base_file=BASE_FILE,
#    nzia_files=nzia_files,
#    output_file="plots/system_costs_boxplot.png"
#)

#plot_system_costs_cumulative_boxplot(
#    base_file=BASE_FILE,
#    nzia_files=nzia_files,
#    years=[2025, 2030, 2035, 2040],  # select the years you want to visualize
#    output_file="figures/system_costs_cumulative_boxplot.png"
#)

plot_lng_cumulative_pct_deviation_comparison(
    base_file=BASE_FILE,
    nzia_files=nzia_files,
    output_file="figures/lng_boxplots_deviation.png"
)