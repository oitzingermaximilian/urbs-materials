from matplotlib import ticker as mticker
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import plotly.graph_objects as go
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from plotly.subplots import make_subplots
import math
import matplotlib.patheffects as pe
from matplotlib.patches import Patch
from matplotlib.ticker import StrMethodFormatter
from adjustText import adjust_text
import matplotlib.transforms as mtransforms
# -------------------------------
# Configuration
# -------------------------------

plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 8  # around 6–8 pt target at print size
plt.rcParams["pdf.fonttype"] = (
    42  # ensures fonts are embedded properly in vector outputs
)
plt.rcParams["ps.fonttype"] = 42
print(plt.rcParams["font.family"])

BASE_PATH = Path("C:/Users/maxoi/OneDrive/Desktop/results_crm_paper/base")
NZIA_PATH = Path("C:/Users/maxoi/OneDrive/Desktop/results_crm_paper/NZIA")
LNG_LOWEST_PATH = Path("C:/Users/maxoi/OneDrive/Desktop/results_crm_paper/lng_lowest")

LR_FOLDERS = ["LR1", "LR3_5", "LR4", "LR4", "LR6", "LR7", "LR8", "LR9", "LR10"]

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

GROUPS = {
    "Fossil fuels": [
        "Coal Plant",
        "Coal Plant CCUS",
        "Gas Plant (CCGT)",
        "Gas Plant (CCGT) CCUS",
        "Lignite Plant",
        "Lignite Plant CCUS",
        "Oil Plant",
        "Other non-res",
    ],
    "Renewables": [
        "Hydro (reservoir)",
        "Hydro (run-of-river)",
        "solarPV",
        "windoff",
        "windon",
    ],
    "Thermal nuclear": ["Nuclear Plant"],
}

GROUP_COLORS = {
    "Fossil fuels": "#8C564B",  # F4C20D"
    "Renewables": "#009688",
    "Thermal nuclear": "#E6AC00",
}

IMPROVED_RENEWABLE_COLORS = {
    "Hydro (reservoir)": "#0072B2",  # strong blue
    "Hydro (run-of-river)": "#56B4E9",  # lighter blue
    "Solar PV": "#E69F00",  # bright orange/gold
    "Onshore Wind": "#66C2A5",  # light vibrant green
    "Offshore Wind": "#00876C",  # darker rich green
    "Non-renewables": "#595959",  # dark neutral grey
}


PROCESS_MAP = {
    "Hydro (reservoir)": "Hydro (reservoir)",
    "Hydro (run-of-river)": "Hydro (run-of-river)",
    "Solar PV": "solarPV",
    "Onshore Wind": "windon",
    "Offshore Wind": "windoff",
}


# -------------------------------
# Centralized Data Loading Functions
# -------------------------------
def build_scenario_dict():
    """Build dictionary of all NZIA scenarios"""
    nzia_scenarios = {}
    for lr in LR_FOLDERS:
        lr_path = NZIA_PATH / lr
        for scenario in SCENARIO_NAMES:
            scenario_file = lr_path / f"{scenario}.xlsx"
            nzia_scenarios[(lr, scenario)] = scenario_file
    return nzia_scenarios


def get_base_scenario():
    """Get base scenario path"""
    return BASE_PATH / "LR1" / "scenario_high_high_high.xlsx"


def get_lng_best_case_scenario():
    """Get LNG best-case scenario path"""
    return LNG_LOWEST_PATH / "scenario_min_min_min.xlsx"


def mwh_to_bcm(mwh):
    """Convert MWh to BCM (billion cubic meters of natural gas equivalent)"""
    mmbtu = mwh * 3.412  # 1 MWh = 3.412 MMBtu
    bcm = mmbtu / 35_315_000  # 1 BCM = 35,315,000 MMBtu
    return bcm


def load_lng(file_path, years=range(2024, 2041)):
    """Centralized LNG data loading function"""
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


def load_generation_data(
    file_path, sheet_name="extension_balance", years=range(2025, 2041)
):
    """Load generation data from Excel file"""
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df[df["Stf"].isin(years)]


def load_scrap_data(file_path, sheet_name="scrap", years=range(2024, 2041)):
    """Load scrap data from Excel file"""
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Handle column name variations
    year_col = next(
        (col for col in ["stf", "Stf", "year", "Year"] if col in df.columns), None
    )
    tech_col = next(
        (
            col
            for col in ["tech", "Tech", "key_1", "key1", "technology", "Process", "pro"]
            if col in df.columns
        ),
        None,
    )
    value_col = next(
        (
            col
            for col in [
                "capacity_scrap_total",
                "value",
                "capacity_scrap",
                "capacity_scrap_tonnes",
            ]
            if col in df.columns
        ),
        None,
    )

    if not all([year_col, tech_col, value_col]):
        raise ValueError(f"Missing required columns in {file_path}")

    df[year_col] = df[year_col].ffill()
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    df = df.dropna(subset=[year_col])
    df[year_col] = df[year_col].astype(int)
    df = df[df[year_col].between(min(years), max(years))]

    df[value_col] = pd.to_numeric(df[value_col], errors="coerce").fillna(0)
    return df, year_col, tech_col, value_col


def load_system_costs(file_path, sheet_name="extension_cost", years=range(2024, 2041)):
    """Load system costs data"""
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df[df["stf"].isin(years)]
    df_done = df.groupby("stf")["Total_Cost"].sum()
    return df_done


def load_installed_capacity(file_path):
    """Load installed capacity from 'extension_total_caps' sheet."""
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name="extension_total_caps")
    return df


def identify_capacity_clusters(df, eps=0.7, min_samples=4):
    """
    DBSCAN clustering per window (year), then re-number all clusters globally
    from 1 to n.
    """
    clustered_dfs = []
    cluster_summary = []
    next_global_id = 1  # counter for global cluster IDs

    for year, df_group in df.groupby("year"):
        df_group = df_group.copy()

        if len(df_group) < min_samples:
            df_group["cluster_id"] = -1
            cluster_summary.append(
                {
                    "year": year,
                    "num_clusters": 0,
                    "num_points": len(df_group),
                    "note": "too few points",
                }
            )
            clustered_dfs.append(df_group)
            continue

        X = df_group[["Remanufacturing", "Manufacturing"]].values
        X_scaled = StandardScaler().fit_transform(X)

        db = DBSCAN(eps=eps, min_samples=min_samples)
        labels = db.fit_predict(X_scaled)

        # Map local DBSCAN IDs to global IDs
        local_to_global = {}
        for lbl in sorted(set(labels)):
            if lbl == -1:
                continue  # noise stays -1
            local_to_global[lbl] = next_global_id
            next_global_id += 1

        df_group["cluster_id"] = [local_to_global.get(l, -1) for l in labels]

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        cluster_summary.append(
            {
                "year": year,
                "num_clusters": n_clusters,
                "num_points": len(df_group),
                "noise_points": np.sum(labels == -1),
            }
        )

        clustered_dfs.append(df_group)

    df_with_clusters = (
        pd.concat(clustered_dfs, ignore_index=True) if clustered_dfs else pd.DataFrame()
    )
    df_summary = pd.DataFrame(cluster_summary)
    return df_summary, df_with_clusters


def identify_yearly_capacity_clusters(
    df, years_of_interest=None, eps=0.7, min_samples=2
):
    """
    DBSCAN clustering per year/window. Cluster IDs are sequential globally (1,2,...).
    Noise = -1. Returns summary + df_with_clusters (same structure as original).
    """
    if years_of_interest is None:
        years_of_interest = sorted(df["year"].unique())

    clustered_dfs = []
    cluster_summary = []
    next_global_id = 1  # global counter

    for year in sorted(years_of_interest):
        df_win = df[df["year"] == year].copy()

        if len(df_win) < min_samples:
            df_win["cluster_id"] = -1
            cluster_summary.append(
                {
                    "year": year,
                    "num_clusters": 0,
                    "num_points": len(df_win),
                    "note": "too few points",
                }
            )
            clustered_dfs.append(df_win)
            continue

        X = df_win[["Manufacturing", "Remanufacturing"]].values
        X_scaled = StandardScaler().fit_transform(X)
        db = DBSCAN(eps=eps, min_samples=min_samples)
        labels = db.fit_predict(X_scaled)

        local_to_global = {
            lbl: next_global_id + i
            for i, lbl in enumerate(sorted([l for l in set(labels) if l != -1]))
        }

        df_win["cluster_id"] = [local_to_global.get(l, -1) for l in labels]
        num_clusters = len(local_to_global)
        next_global_id += num_clusters

        cluster_summary.append(
            {
                "year": year,
                "num_clusters": num_clusters,
                "num_points": len(df_win),
                "noise_points": np.sum(labels == -1),
            }
        )

        clustered_dfs.append(df_win)

    df_with_clusters = pd.concat(clustered_dfs, ignore_index=True)
    df_summary = pd.DataFrame(cluster_summary)

    return df_summary, df_with_clusters


def aggregate_and_cluster_yearly(df, windows=None, eps=0.7, min_samples=2):
    """
    Aggregate yearly data into fixed windows, then run DBSCAN.

    Args:
        df (DataFrame): Must have columns ['year', 'Manufacturing', 'Remanufacturing']
        windows (list of tuples): [(start_year, end_year), ...]
        eps (float): DBSCAN eps
        min_samples (int): DBSCAN min_samples

    Returns:
        summary_df: summary of clusters for each window
        df_with_clusters: aggregated values with cluster_id
    """
    if windows is None:
        windows = [(2024, 2025), (2026, 2030), (2031, 2035), (2036, 2040)]

    records = []
    for i, (start, end) in enumerate(windows, start=1):
        df_window = df[(df["year"] >= start) & (df["year"] <= end)]
        if df_window.empty:
            continue
        records.append(
            {
                "window_id": i,
                "start_year": start,
                "end_year": end,
                "Manufacturing": df_window["Manufacturing"].sum(),
                "Remanufacturing": df_window["Remanufacturing"].sum(),
            }
        )

    agg_df = pd.DataFrame(records)
    X = agg_df[["Manufacturing", "Remanufacturing"]].values
    X_scaled = StandardScaler().fit_transform(X)

    db = DBSCAN(eps=eps, min_samples=min_samples)
    labels = db.fit_predict(X_scaled)
    agg_df["cluster_id"] = labels

    # Summary
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = np.sum(labels == -1)
    summary_df = pd.DataFrame(
        {
            "window_id": agg_df["window_id"],
            "start_year": agg_df["start_year"],
            "end_year": agg_df["end_year"],
            "Manufacturing": agg_df["Manufacturing"],
            "Remanufacturing": agg_df["Remanufacturing"],
            "cluster_id": labels,
            "num_clusters": n_clusters,
            "noise_points": n_noise,
        }
    )

    return summary_df, agg_df


def create_cumulative_capacity_csv_with_stats(
    nzia_scenarios_dict=None,
    target_years=[2030, 2040],
    techs=["solarPV", "windon", "windoff"],
    output_csv="plots/nzia_cumulative_capacity.csv",
    stats_csv="plots/nzia_capacity_stats.csv",
):
    """
    Creates a CSV summarizing cumulative total capacity for
    selected technologies in target years, across multiple scenarios.
    Also creates a summary CSV with statistics: median, mean, min, max, delta.
    Assumes the Excel sheet already contains cumulative capacities.
    """
    results = []

    # Step 1: Extract cumulative capacity per scenario
    for (lr, scenario_name), file_path in nzia_scenarios_dict.items():
        if not file_path.exists():
            print(f"⚠ Missing file: {file_path}")
            continue

        try:
            df = pd.read_excel(file_path, sheet_name="extension_only_totalcapacity")
        except Exception as e:
            print(f"⚠ Could not read {file_path}: {e}")
            continue

        df.columns = df.columns.str.strip()
        df["tech"] = df["tech"].astype(str).str.strip()
        df["stf"] = df["stf"].ffill()

        df_scen = df[df["tech"].isin(techs)].copy()
        if df_scen.empty:
            print(f"⚠ No relevant techs in {scenario_name}")
            continue

        # Extract values for target years
        for year in target_years:
            df_year = df_scen[df_scen["stf"] == year]
            # If some techs are missing, fill with 0
            entry = {"scenario": scenario_name, "lr": lr, "year": year}
            for tech in techs:
                if tech in df_year["tech"].values:
                    entry[tech] = df_year[df_year["tech"] == tech][
                        "capacity_ext"
                    ].values[0]
                else:
                    entry[tech] = 0
            results.append(entry)

    # Output cumulative capacity CSV
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv, index=False)
    print(f"✅ Cumulative capacity CSV saved to {output_csv}")

    # Step 2: Compute statistics
    stats_list = []
    for year in target_years:
        df_year = output_df[output_df["year"] == year]
        for tech in techs:
            values = df_year[tech]
            stats_list.append(
                {
                    "year": year,
                    "tech": tech,
                    "median": values.median(),
                    "mean": values.mean(),
                    "min": values.min(),
                    "max": values.max(),
                    "delta": values.max() - values.min(),
                }
            )

    stats_df = pd.DataFrame(stats_list)
    stats_df.to_csv(stats_csv, index=False)
    print(f"✅ Statistics CSV saved to {stats_csv}")

    return output_df, stats_df


# -------------------------------
# Plotting Functions
# -------------------------------
def plot_base_generation_mix(base_file=None, output_dir="plots"):
    """Plot base scenario generation mix - donut charts and stacked bars"""
    if base_file is None:
        base_file = get_base_scenario()

    years = list(range(2025, 2041))
    df = load_generation_data(base_file, years=years)

    # Prepare yearly aggregated data
    yearly_data = {}
    for year in years:
        year_df = df[df["Stf"] == year]
        summary = {}
        for group, processes in GROUPS.items():
            value = (
                year_df[year_df["Process"].isin(processes)]["Value"].sum() / 1_000_000
            )  # Convert to TWh
            summary[group] = value
        yearly_data[year] = summary

    # 1. Donut Charts (4x4)
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
            wedgeprops=dict(width=0.4, edgecolor="w"),
        )
        axes[i].set_title(f"{year} (TWh)", fontsize=12)

    for j in range(i + 1, 16):
        fig.delaxes(axes[j])

    plt.suptitle("Base Scenario Generation Mix (TWh)", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    output_path = Path(output_dir) / "base_generation_mix_donut.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.show()
    print(f"✔ Base scenario donut chart saved → {output_path}")

    # 2. 100% Stacked Horizontal Bar Chart
    records = []
    group_order = list(GROUPS.keys())
    for year in years:
        year_df = df[df["Stf"] == year]
        totals = {
            g: year_df[year_df["Process"].isin(GROUPS[g])]["Value"].sum()
            for g in group_order
        }
        total_all = sum(totals.values())
        shares = {g: totals[g] / total_all if total_all > 0 else 0 for g in group_order}
        records.append({"year": year, **shares})

    data = pd.DataFrame(records)

    n = len(years)
    fig, ax = plt.subplots(figsize=(10, max(10, 0.52 * n + 3.5)))
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
            zorder=5,
        )
        left += width

    ax.set_yticks(y_pos, [str(y) for y in years])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
    ax.xaxis.set_ticks_position("top")

    ax.vlines(
        np.arange(0, 101, 10), -0.5, n - 0.5, colors="white", linewidth=1.5, zorder=7
    )
    ax.set_facecolor("#E6E6E6")

    # ax.set_title("Current Policies Scenario Generation Share by Year (%)", loc="left",
    # fontsize=18, fontweight="bold", color="#1F4E79")

    handles = [plt.Rectangle((0, 0), 1, 1, color=GROUP_COLORS[g]) for g in group_order]
    ax.legend(
        handles,
        group_order,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.06),
        ncol=len(group_order),
        frameon=False,
        fontsize=18,
    )

    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.94])
    ax.tick_params(axis="x", labelsize=18)  # increase x tick label size
    ax.tick_params(axis="y", labelsize=18)  # increase y tick label size
    output_path = Path(output_dir) / "Fig1.png"
    plt.savefig(output_path, dpi=300)
    plt.show()
    print(f"✔ Base scenario stacked bar chart saved → {output_path}")


def plot_renewables_breakdown_100pct(
    base_file=None, output_dir="plots", colors=IMPROVED_RENEWABLE_COLORS, years=None
):
    """100% stacked horizontal bar chart showing renewable breakdown.
    - Uses a more readable pastel palette by default.
    - Larger tick-labels and clearer legend patches.
    """
    if base_file is None:
        base_file = get_base_scenario()

    if years is None:
        years = list(range(2025, 2041))

    df = load_generation_data(base_file, years=years)

    # --- Prepare data --- #
    records = []
    group_order = [
        "Hydro (reservoir)",
        "Hydro (run-of-river)",
        "Solar PV",
        "Onshore Wind",
        "Offshore Wind",
    ]

    for year in years:
        year_df = df[df["Stf"] == year]

        totals = {}
        totals["Hydro (reservoir)"] = year_df[
            year_df["Process"] == "Hydro (reservoir)"
        ]["Value"].sum()
        totals["Hydro (run-of-river)"] = year_df[
            year_df["Process"] == "Hydro (run-of-river)"
        ]["Value"].sum()
        totals["Solar PV"] = year_df[year_df["Process"] == "solarPV"]["Value"].sum()
        totals["Onshore Wind"] = year_df[year_df["Process"] == "windon"]["Value"].sum()
        totals["Offshore Wind"] = year_df[year_df["Process"] == "windoff"][
            "Value"
        ].sum()

        # Compute NON-RENEWABLES (but do NOT include in total share calculation)
        renewable_processes = [
            "Hydro (reservoir)",
            "Hydro (run-of-river)",
            "solarPV",
            "windon",
            "windoff",
        ]
        non_renew = year_df[~year_df["Process"].isin(renewable_processes)][
            "Value"
        ].sum()
        totals["Non-renewables"] = non_renew  # keep for reporting if needed

        # ❗ total excluding non-renewables
        total_renew_only = (
            totals["Hydro (reservoir)"]
            + totals["Hydro (run-of-river)"]
            + totals["Solar PV"]
            + totals["Onshore Wind"]
            + totals["Offshore Wind"]
        )

        # Compute shares only from renewable denominator
        shares = {
            g: (totals[g] / total_renew_only if total_renew_only > 0 else 0)
            for g in group_order
            if g != "Non-renewables"  # ❗ remove non-renewables from share output
        }

        records.append({"year": year, **shares})

    data = pd.DataFrame(records)

    # --- Plot --- #
    n = len(years)
    fig, ax = plt.subplots(figsize=(10, max(10, 0.52 * n + 3.5)))
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
            color=colors[g],
            edgecolor="white",
            linewidth=1.2,
            zorder=5,
        )
        left += width

    # Formatting
    ax.set_yticks(y_pos)
    ax.set_yticklabels([str(y) for y in years])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
    ax.xaxis.set_ticks_position("top")

    # Increase tick label sizes and padding
    ax.tick_params(axis="x", labelsize=18, pad=8)
    ax.tick_params(axis="y", labelsize=18)

    for lbl in ax.get_yticklabels():
        lbl.set_fontweight("medium")

    # Vertical white grid lines and background
    ax.vlines(
        np.arange(0, 101, 10), -0.5, n - 0.5, colors="white", linewidth=1.5, zorder=7
    )
    ax.set_facecolor("#EFEFEF")

    # ax.set_title(
    #    "Renewable Generation Share Breakdown (%)",
    #    loc="left",
    #    fontsize=20,
    #    fontweight="bold",
    #    color="#1F4E79"
    # )

    # Legend: build explicit colored Patch objects so colors show reliably
    # Use a multi-column layout (ncol) to avoid one long single-line legend.
    handles = [
        mpatches.Patch(facecolor=colors[g], edgecolor="#666666", linewidth=0.6, label=g)
        for g in group_order
    ]

    # Choose ncol so legend wraps into multiple rows. With 7 items ncol=3 gives 3 rows.
    ncol = 3
    legend = ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=ncol,
        frameon=False,
        fontsize=18,
        handlelength=1.5,
        handletextpad=0.6,
        columnspacing=1.2,
    )

    # Slightly enlarge patch displayed in legend by adjusting legend handlers' sizes (if available)
    # This will affect how large the color boxes look in the legend.
    for lh in legend.legendHandles:
        # most handlers are Patch objects; set a visible edge to help contrast
        try:
            lh.set_linewidth(0.6)
        except Exception:
            pass

    # Give space for legend below the figure and ensure layout isn't clipped
    plt.tight_layout(rect=[0.02, 0.06, 0.98, 0.96])
    plt.subplots_adjust(bottom=0.24)

    output_path = Path(output_dir) / "Fig2.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.show()
    print(f"✔ Renewable 100% stacked bar chart saved → {output_path}")


def plot_renewables_installed_capacity_vertical(
    base_file, output_dir="plots", region="EU27", colors=IMPROVED_RENEWABLE_COLORS
):
    """
    Vertical stacked bar plot of renewable installed capacities (GW) 2024-2040.
    - Uses improved color palette
    - Larger tick & label sizes
    - Compact multi-column legend as colored patches (4 columns x wrap)
    """
    # Load data
    df = pd.read_excel(base_file, sheet_name="extension_total_caps")
    df["stf"] = df["stf"].ffill()
    df["sit"] = df["sit"].ffill()
    if region:
        df = df[df["sit"] == region]

    years = list(range(2024, 2041))
    group_order = list(PROCESS_MAP.keys())

    # Prepare data
    records = {g: [] for g in group_order}
    for year in years:
        year_df = df[df["stf"] == year]
        for name, pro in PROCESS_MAP.items():
            records[name].append(
                year_df[year_df["pro"] == pro]["cap_pro"].sum() / 1000
            )  # MW → GW

    # Plot
    fig, ax = plt.subplots(figsize=(14, 8))
    bottom = [0] * len(years)

    for g in group_order:
        color = colors.get(g, "#BDBDBD")
        ax.bar(
            years,
            records[g],
            bottom=bottom,
            color=color,
            label=g,
            edgecolor="white",
            width=0.7,
        )
        bottom = [b + v for b, v in zip(bottom, records[g])]

    ax.set_xticks([2024, 2030, 2035, 2040])
    ax.set_xticklabels([str(y) for y in [2024, 2030, 2035, 2040]], fontsize=25)
    # Axis labels and sizing
    # ax.set_xlabel("Year", fontsize=16)
    ax.set_ylabel("Installed Capacity (GW)", fontsize=22)
    # ax.set_title(
    #    "Renewable Installed Capacity by Technology (2024-2040)",
    #    fontsize=20, fontweight="bold", color="#1F4E79", loc="left"
    # )

    # Face and grid
    ax.set_facecolor("#F3F3F3")
    ax.grid(axis="y", color="white", linewidth=1.5, zorder=7)

    # Tick sizes
    ax.tick_params(axis="x", labelsize=22, rotation=0, pad=6)
    ax.tick_params(axis="y", labelsize=22)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    # Legend: use explicit colored Patch objects so colors show reliably
    handles = [
        mpatches.Patch(
            facecolor=colors.get(g, "#BDBDBD"),
            edgecolor="#666666",
            linewidth=0.6,
            label=g,
        )
        for g in group_order
    ]

    # Place legend below the chart; 4 columns -> will wrap to 2 rows for 7 items
    ncol = 4
    legend = ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=ncol,
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

    plt.tight_layout(rect=[0.02, 0.06, 0.98, 0.94])  # leave extra bottom space
    plt.subplots_adjust(bottom=0.25)  # increase bottom margin

    # Save plot
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "Fig3.png"
    plt.savefig(output_path, dpi=300)
    plt.show()
    print(f"✔ Vertical stacked bar chart saved → {output_path}")


def plot_capacity_violin_per_tech(
    csv_file="nzia_cumulative_totalcapacity.csv",
    year=2040,
    save_path="plots/capacity_violin_2040.png",
):
    # --- Font Settings (Clean & Professional) ---
    FS_TITLE = 25
    FS_LABEL = 25
    FS_TICK = 25

    # Load Data
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        # Dummy data for demonstration
        data = {
            "year": [year] * 100,
            "solarPV": np.random.normal(1200000, 20000, 100),
            "windon": np.random.normal(400000, 10000, 100),
            "windoff": np.random.normal(100000, 5000, 100),
        }
        df = pd.DataFrame(data)

    df_year = df[df["year"] == year].copy()

    # Convert MW → GW
    techs = ["solarPV", "windon", "windoff"]
    for tech in techs:
        df_year[tech] = df_year[tech] / 1000

    # Labels and colors
    tech_map = {
        "solarPV": "Solar PV",
        "windon": "Onshore Wind",
        "windoff": "Offshore Wind",
    }
    tech_colors = {
        "solarPV": "#E69F00",  # Orange
        "windon": "#66C2A5",  # Teal
        "windoff": "#00876C",  # Dark Green
    }

    # --- PLOT SETUP ---
    # 3 subplots side-by-side, sharing NO axes (scales differ wildly)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Adjust spacing between plots
    plt.subplots_adjust(wspace=0.4)

    for ax, tech in zip(axes, techs):
        nice_name = tech_map[tech]
        col = tech_colors[tech]

        # 1. The Violin Plot
        sns.violinplot(
            data=df_year,
            y=tech,
            ax=ax,
            inner="quartile",  # Show quartiles inside
            color=col,
            linewidth=1.2,  # Thinner, crisp lines
            width=0.6,  # Slimmer shape (less "blobby")
            alpha=0.9,
        )

        # 2. Axis Formatting
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        ax.tick_params(axis="y", labelsize=FS_TICK)

        # Remove X ticks (we will use the Label as the title/x-label)
        ax.set_xticks([])

        # 3. Labeling
        # Put the Tech Name clearly at the bottom X-axis
        ax.set_xlabel(nice_name, fontsize=FS_TITLE, fontweight="bold", labelpad=15)

        # Y-Label: Only usually needed on the far left, but since scales differ,
        # it might be good to label the top left or just assume units are known.
        if tech == "solarPV":
            ax.set_ylabel("Total Capacity (GW)", fontsize=FS_LABEL, labelpad=15)
        else:
            ax.set_ylabel("")  # Clean look

        # 4. Spines (The box around the plot)
        # Remove top and right borders for a modern look
        ax.spines["top"].set_visible(True)
        ax.spines["right"].set_visible(True)
        ax.spines["left"].set_linewidth(1.0)
        ax.spines["bottom"].set_linewidth(1.0)

        # 5. Grid
        ax.yaxis.grid(True, linestyle="--", linewidth=0.5, alpha=1)
        ax.set_axisbelow(True)

        # --- CHANGES HERE: ENSURE OFFSET ---
        # Calculate data range
        data_min = df_year[tech].min()
        data_max = df_year[tech].max()
        data_range = data_max - data_min

        # Define padding (e.g., 20% of the range)
        padding = data_range * 0.20

        # Set limits with padding so the violin doesn't touch the frame
        ax.set_ylim(data_min - padding, data_max + padding)

        # Save
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(save_path, dpi=1000, bbox_inches="tight")
    print(f"✅ Framed violin plots saved to {save_path}")
    plt.show()


def plot_scrap_comparison(
    base_file=None, nzia_scenarios_dict=None, output_dir="plots/scrap_range"
):
    """Plot scrap volume comparison between base and NZIA scenarios"""
    if base_file is None:
        base_file = get_base_scenario()
    if nzia_scenarios_dict is None:
        nzia_scenarios_dict = build_scenario_dict()

    years = list(range(2024, 2041))
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    def _load_scrap_pivot(file_path):
        """Helper to load and pivot scrap data"""
        try:
            df, year_col, tech_col, value_col = load_scrap_data(file_path, years=years)
        except Exception as e:
            print(f"⚠ Could not read {file_path}: {e}")
            return pd.DataFrame(index=years)

        grouped = (
            df.groupby([year_col, tech_col], as_index=True)[value_col]
            .sum()
            .reset_index()
        )
        pivot = grouped.pivot(
            index=year_col, columns=tech_col, values=value_col
        ).fillna(0)
        pivot = pivot.reindex(years, fill_value=0)
        return pivot / 1e6  # Convert to Mt

    # Load base data
    base_pivot = _load_scrap_pivot(base_file)

    # Load NZIA data
    nzia_files = [f for f in nzia_scenarios_dict.values() if f.exists()]
    nzia_pivots = [_load_scrap_pivot(f) for f in nzia_files]

    # Plot for each technology
    tech_set = set(base_pivot.columns.tolist())
    for p in nzia_pivots:
        tech_set.update(p.columns.tolist())

    for tech in sorted(tech_set):
        # Base series
        base_series = (
            base_pivot[tech].reindex(years).fillna(0)
            if tech in base_pivot.columns
            else pd.Series(0.0, index=years)
        )

        # NZIA series
        nzia_series_list = []
        for p in nzia_pivots:
            s = (
                p[tech].reindex(years).fillna(0)
                if tech in p.columns
                else pd.Series(0.0, index=years)
            )
            nzia_series_list.append(s)

        if not nzia_series_list:
            continue

        nzia_df = pd.DataFrame(nzia_series_list).T
        nz_min = nzia_df.min(axis=1)
        nz_max = nzia_df.max(axis=1)
        nz_mean = nzia_df.mean(axis=1)

        if (base_series.sum() == 0) and (nz_max.max() == 0):
            continue

        # Plot
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(
            years,
            base_series.values,
            color="darkred",
            linewidth=2.2,
            label="Base scenario",
        )
        ax.fill_between(
            years,
            nz_min.values,
            nz_max.values,
            color="seagreen",
            alpha=0.25,
            label="NZIA min–max range",
        )
        ax.plot(
            years,
            nz_mean.values,
            color="seagreen",
            linestyle="--",
            linewidth=1.5,
            label="NZIA mean",
        )

        ax.set_title(f"Scrap volume — {tech}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Scrap [Mt]")
        ax.set_xlim(min(years) - 1, max(years) + 1)
        ax.set_xticks([2025, 2030, 2035, 2040])
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.legend()

        plt.tight_layout()
        safe_tech = str(tech).replace("/", "_").replace(" ", "_")
        fname = out_path / f"scrap_range_{safe_tech}.png"
        fig.savefig(fname, dpi=300)
        plt.close(fig)
        print(f"✔ Saved: {fname}")


def plot_lng_analysis(
    base_file=None,
    nzia_scenarios_dict=None,
    lng_file=None,
    output_dir="plots/lng_analysis",
):
    """Comprehensive LNG analysis with NZIA scenario range, LTC overlay, and boxplot"""

    if base_file is None:
        base_file = get_base_scenario()
    if nzia_scenarios_dict is None:
        nzia_scenarios_dict = build_scenario_dict()
    if lng_file is None:
        lng_file = get_lng_best_case_scenario()

    years = range(2025, 2041)
    target_years = [2025, 2030, 2035, 2040]
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    nzia_files = [f for f in nzia_scenarios_dict.values() if f.exists()]

    # ----------------------------------------------------------------------
    # 1. RANGE PLOT — NZIA scenario range, LTC area, and main trajectories
    # ----------------------------------------------------------------------

    # Long-term contract data (BCM)
    ltc_data = {
        2025: 82,
        2026: 85,
        2027: 99,
        2028: 92,
        2029: 92,
        2030: 88,
        2031: 86,
        2032: 84,
        2035: 57,
        2040: 48,
    }
    ltc_series = pd.Series(ltc_data).sort_index()
    ltc_series = ltc_series.reindex(years).interpolate()

    plt.figure(figsize=(9, 5))
    ax = plt.gca()

    # --- Aggregate NZIA scenario data for range plot ---
    nzia_arrays = []
    for f in nzia_files:
        series = load_lng(f, years)
        nzia_arrays.append(series.values)
    if nzia_arrays:
        nzia_array = np.vstack(nzia_arrays)
        min_vals = np.nanmin(nzia_array, axis=0)
        max_vals = np.nanmax(nzia_array, axis=0)
    else:
        # fallback: empty arrays (avoid errors)
        min_vals = np.zeros(len(list(years)))
        max_vals = np.zeros(len(list(years)))

    # --- NZIA range band ---
    ax.fill_between(
        years,
        min_vals,
        max_vals,
        color="#B0C4DE",
        alpha=0.45,
        label="NZIA scenario range",
        zorder=1,
    )

    # --- Long-term contracts (grey area + dashed line) ---
    ax.fill_between(
        ltc_series.index, 0, ltc_series.values, color="#BEBEBE", alpha=0.25, zorder=2
    )
    ax.plot(
        ltc_series.index,
        ltc_series.values,
        color="#6E6E6E",
        linewidth=1.6,
        linestyle="--",
        label="long-term contracts",
        zorder=3,
    )

    # --- Base and Best-case trajectories ---
    base_series = load_lng(base_file, years)
    best_case_series = load_lng(lng_file, years)
    ax.plot(
        base_series.index,
        base_series.values,
        color="#1F3A93",
        linewidth=2.4,
        label="current policies",
        zorder=4,
    )
    ax.plot(
        best_case_series.index,
        best_case_series.values,
        color="#008080",
        linewidth=2.4,
        linestyle="--",
        label="best-case scenario",
        zorder=5,
    )

    # --- Formatting ---
    ax.set_xlim(min(years) - 1, max(years) + 1)
    ax.set_xticks([2025, 2030, 2035, 2040])
    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("LNG Demand and Supply [bcm]", fontsize=10)
    ax.set_title(
        "LNG demand trajectories vs. long-term contracts", fontsize=12, weight="bold"
    )

    ax.grid(axis="y", linestyle=":", color="0.8", linewidth=0.8)
    ax.legend(frameon=True, fontsize=9, loc="upper right")

    # increase tick label size
    ax.tick_params(axis="x", labelsize=10)
    ax.tick_params(axis="y", labelsize=10)

    plt.tight_layout()
    plt.savefig(out_path / "lng_demand_range_plot.pdf", dpi=600, bbox_inches="tight")
    plt.show()
    print("✔ LNG demand range plot saved")

    # ----------------------------------------------------------------------
    # 2. CUMULATIVE PERCENTAGE DEVIATION BOXPLOT (no outliers shown)
    # ----------------------------------------------------------------------
    base_cumulative = load_lng(base_file, years).cumsum()
    nzia_cumulative = [load_lng(f, years).cumsum() for f in nzia_files]

    # prepare DataFrame where each column is one scenario cumulative series
    # if nzia_cumulative empty, handle gracefully
    if nzia_cumulative:
        data = pd.DataFrame({i: s for i, s in enumerate(nzia_cumulative)}).T
        # pct_dev: columns for target years (we want distribution across scenarios)
        pct_dev = pd.DataFrame(
            {
                y: 100 * (data[y] - base_cumulative[y]) / base_cumulative[y]
                for y in target_years
            }
        )
    else:
        pct_dev = pd.DataFrame({y: pd.Series(dtype=float) for y in target_years})

    plt.figure(figsize=(9, 5))
    ax = plt.gca()
    positions = np.arange(len(target_years))
    box_data = [pct_dev[y].dropna() for y in target_years]

    # draw boxplot without fliers/outliers (showfliers=False)
    median_color = "#1F78B4"
    median_linewidth = 2.0
    bp = ax.boxplot(
        box_data,
        positions=positions,
        widths=0.35,
        patch_artist=True,
        showfliers=False,  # hide outliers
        boxprops=dict(facecolor="#A6CEE3", alpha=0.75, linewidth=1.2),
        medianprops=dict(color=median_color, linewidth=median_linewidth),
        whiskerprops=dict(color="#666666", linestyle="--", linewidth=1.2),
        capprops=dict(color="#666666", linewidth=1.2),
        flierprops=dict(
            marker="o", markersize=4, markeredgecolor="none"
        ),  # not shown since showfliers=False
    )

    # Formatting for readability (larger fonts etc.)
    ax.set_title(
        "Cumulative LNG demand – Compared to current policies",
        fontsize=12,
        weight="bold",
    )
    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Deviation from base [%]", fontsize=10)
    ax.set_xticks(positions)
    ax.set_xticklabels(target_years, fontsize=10)
    ax.grid(axis="y", linestyle=":", color="0.8", linewidth=0.8)

    ax.tick_params(axis="x", labelsize=10)
    ax.tick_params(axis="y", labelsize=10)

    # Draw thin dashed horizontal lines from each median to the y-axis (no numeric text)
    # Use the same color and thickness as the median, with slightly lower alpha
    # We'll draw from the left axis limit to the box x position.
    x_left = ax.get_xlim()[0]  # left axis coordinate
    for i, med_line in enumerate(bp.get("medians", [])):
        # median line y data; average the y-values to get a single median y
        ydata = med_line.get_ydata()
        if len(ydata) == 0:
            continue
        median_val = float(np.mean(ydata))

        # horizontal dashed line from left axis to the box position using median style
        ax.plot(
            [x_left, positions[i]],
            [median_val, median_val],
            color=median_color,
            linestyle="--",
            linewidth=median_linewidth,
            alpha=0.65,
            zorder=2,
        )

        # small tick at the y-axis to indicate the median point (no numeric label)
        ax.plot(
            [x_left],
            [median_val],
            marker="|",
            markersize=14,
            color=median_color,
            markeredgewidth=1.6,
            alpha=0.9,
            zorder=3,
        )

    plt.tight_layout()
    plt.savefig(
        out_path / "lng_cumulative_pct_deviation.pdf", dpi=600, bbox_inches="tight"
    )
    plt.show()
    print("✔ LNG cumulative deviation plot saved")


def export_lng_data(
    base_file=None, nzia_scenarios_dict=None, lng_file=None, output_dir="plots/lng_data"
):
    """
    Collects yearly LNG data for NZIA scenarios, base case, best-case scenario,
    and long-term contracts (LTC), and exports them to CSV files.

    CSV files format:
    - Years as rows
    - Scenarios or series as columns
    """

    if base_file is None:
        base_file = get_base_scenario()
    if nzia_scenarios_dict is None:
        nzia_scenarios_dict = build_scenario_dict()
    if lng_file is None:
        lng_file = get_lng_best_case_scenario()

    years = range(2025, 2041)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # --------------------------
    # NZIA scenarios
    # --------------------------
    nzia_arrays = []
    nzia_files = [f for f in nzia_scenarios_dict.values() if f.exists()]
    for f in nzia_files:
        series = load_lng(f, years)
        nzia_arrays.append(series.values)

    if nzia_arrays:
        nzia_array = np.vstack(nzia_arrays)
        nzia_df = pd.DataFrame(
            {name: load_lng(path, years) for name, path in nzia_scenarios_dict.items()}
        )
    else:
        nzia_df = pd.DataFrame(index=years)

    # --------------------------
    # Base case
    # --------------------------
    base_series = load_lng(base_file, years)
    base_df = pd.DataFrame({"Base": base_series.values}, index=years)

    # --------------------------
    # Best-case scenario
    # --------------------------
    best_case_series = load_lng(lng_file, years)
    best_case_df = pd.DataFrame({"Best_Case": best_case_series.values}, index=years)

    # --------------------------
    # Long-term contracts
    # --------------------------
    ltc_data = {
        2025: 82,
        2026: 85,
        2027: 99,
        2028: 92,
        2029: 92,
        2030: 88,
        2031: 86,
        2032: 84,
        2035: 57,
        2040: 48,
    }
    ltc_series = pd.Series(ltc_data).sort_index().reindex(years).interpolate()
    ltc_df = pd.DataFrame({"LTC": ltc_series.values}, index=years)

    # --------------------------
    # Export CSVs
    # --------------------------
    print("NZIA df head:\n", nzia_df.head())
    print("Base df head:\n", base_df.head())
    print("Best case df head:\n", best_case_df.head())
    print("LTC df head:\n", ltc_df.head())

    nzia_df.to_csv(out_path / "NZIA_Scenarios_Yearly.csv", index_label="Year")
    base_df.to_csv(out_path / "Base_Series_Yearly.csv", index_label="Year")
    best_case_df.to_csv(out_path / "Best_Case_Series_Yearly.csv", index_label="Year")
    ltc_df.to_csv(out_path / "LongTermContracts_Yearly.csv", index_label="Year")

    print("✔ LNG data exported to CSV files (yearly values)")
    return {"NZIA": nzia_df, "Base": base_df, "Best_Case": best_case_df, "LTC": ltc_df}


def plot_system_costs_boxplot(
    base_file=None, nzia_scenarios_dict=None, output_dir="plots/system_costs"
):
    """Boxplot of yearly system costs (in bn€) with Base scenario as a line."""
    if base_file is None:
        base_file = get_base_scenario()
    if nzia_scenarios_dict is None:
        nzia_scenarios_dict = build_scenario_dict()

    years = list(range(2024, 2041))
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Load Base costs and convert to bn€
    base_costs = load_system_costs(base_file)
    base_yearly = [base_costs.get(y, 0) / 1e9 for y in years]  # Convert to bn€

    # Load NZIA costs
    nzia_data = []
    for scenario_name, file_path in nzia_scenarios_dict.items():
        if file_path.exists():
            costs = load_system_costs(file_path)
            yearly_bn = [costs.get(y, 0) / 1e9 for y in years]  # Convert to bn€
            nzia_data.append(yearly_bn)

    # Convert to DataFrame
    df = pd.DataFrame(nzia_data, columns=years)

    # Boxplot for each year
    plt.figure(figsize=(12, 6))
    box_data = [df[y] for y in years]
    plt.boxplot(
        box_data,
        labels=years,
        patch_artist=True,
        boxprops=dict(facecolor="lightblue", color="blue"),
        medianprops=dict(color="darkblue"),
    )

    # Overlay Base scenario as a line
    plt.plot(
        range(1, len(years) + 1),
        base_yearly,
        "r-",
        linewidth=2.5,
        label="Base Scenario",
    )

    plt.xlabel("Year")
    plt.ylabel("System Costs [bn€]")
    plt.title("Yearly System Costs: NZIA Scenario Deviations vs Base")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(out_path / "system_costs_boxplot_bn.png", dpi=300)
    plt.show()
    print("✔ Boxplot of system costs (bn€) saved")


def plot_nzia_boxplots(
    tech_list,
    nzia_scenarios_dict,
    target_years=[2025, 2030, 2035, 2040],
    output_dir="plots/nzia_boxplots",
):
    """
    Plots grouped boxplots for each technology:
    - One plot for yearly capacity additions
    - One plot for cumulative capacity additions
    Each target year has 3 boxes (Manufacturing, Remanufacturing, Stockpile)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Updated components and colors
    components = [
        "Manufacturing",
        "Remanufacturing",
        "Stockpile Out",
    ]  # original column names
    components_legend = ["Manufacturing", "Remanufacturing", "Stockpile"]  # for legend
    colors = ["#FF8C42", "#4CB5AE", "#FF6B6B"]  # harmonious palette

    for tech_name in tech_list:
        all_data_yearly = []
        all_data_cumulative = []

        for (lr, scenario_name), file_path in nzia_scenarios_dict.items():
            if not file_path.exists():
                continue
            try:
                df = pd.read_excel(file_path, sheet_name="extension_only_caps")
            except Exception as e:
                print(f"⚠ Could not read {file_path}: {e}")
                continue

            df.columns = df.columns.str.strip()
            df["tech"] = df["tech"].astype(str).str.strip()
            df["stf"] = df["stf"].ffill()
            if "location" in df.columns:
                df["location"] = df["location"].ffill()

            df_tech = df[df["tech"] == tech_name].copy()
            if df_tech.empty:
                continue

            # Ensure all target years exist
            for year in target_years:
                if year not in df_tech["stf"].values:
                    df_tech = pd.concat(
                        [
                            df_tech,
                            pd.DataFrame(
                                [
                                    {
                                        "tech": tech_name,
                                        "stf": year,
                                        "location": df_tech["location"].iloc[-1]
                                        if "location" in df_tech.columns
                                        else None,
                                        "capacity_ext_eusecondary": 0,
                                        "capacity_ext_stockout": 0,
                                        "capacity_ext_euprimary": 0,
                                    }
                                ]
                            ),
                        ],
                        ignore_index=True,
                    )

            df_tech = df_tech.sort_values("stf")
            df_tech["cum_eusecondary"] = df_tech["capacity_ext_eusecondary"].cumsum()
            df_tech["cum_stockout"] = df_tech["capacity_ext_stockout"].cumsum()
            df_tech["cum_euprimary"] = df_tech["capacity_ext_euprimary"].cumsum()

            for year in target_years:
                row = df_tech[df_tech["stf"] == year]
                all_data_yearly.append(
                    {
                        "year": year,
                        "scenario": scenario_name,
                        "Manufacturing": row["capacity_ext_euprimary"].sum() / 1e3,
                        "Remanufacturing": row["capacity_ext_eusecondary"].sum() / 1e3,
                        "Stockpile Out": row["capacity_ext_stockout"].sum() / 1e3,
                    }
                )
                all_data_cumulative.append(
                    {
                        "year": year,
                        "scenario": scenario_name,
                        "Manufacturing": row["cum_euprimary"].sum() / 1e3,
                        "Remanufacturing": row["cum_eusecondary"].sum() / 1e3,
                        "Stockpile Out": row["cum_stockout"].sum() / 1e3,
                    }
                )

        if not all_data_yearly:
            print(f"No data found for {tech_name}. Skipping.")
            continue

        df_yearly = pd.DataFrame(all_data_yearly)
        df_cum = pd.DataFrame(all_data_cumulative)

        # Helper to plot grouped boxplots
        def plot_grouped_boxplot(df_plot, title, filename):
            plt.figure(figsize=(10, 6))
            box_width = 0.2
            positions = np.arange(len(target_years))

            for i, comp in enumerate(components):
                data = [
                    df_plot[df_plot["year"] == year][comp].values
                    for year in target_years
                ]
                pos = positions + (i - 1) * box_width  # shift each component
                bp = plt.boxplot(
                    data,
                    positions=pos,
                    widths=box_width,
                    patch_artist=True,
                    boxprops=dict(facecolor=colors[i], alpha=0.7, linewidth=1.2),
                    medianprops=dict(color="black", linewidth=2),
                    whiskerprops=dict(color="grey", linestyle="--", linewidth=1.2),
                    capprops=dict(color="grey", linewidth=1.2),
                )

            plt.xticks(positions, target_years)
            plt.xlabel("Year")
            plt.ylabel("Capacity Additions (GW)")
            plt.title(f"{title} for {tech_name}")
            plt.grid(axis="y", linestyle="--", alpha=0.3)

            # Legend with black outline and padding
            for i, comp_name in enumerate(components_legend):
                plt.plot(
                    [], color=colors[i], label=comp_name, linewidth=4
                )  # smaller width
            plt.legend(frameon=True, edgecolor="black", borderpad=0.5, labelspacing=0.5)

            plt.tight_layout()
            plt.savefig(output_dir / filename, dpi=300)
            plt.show()

        plot_grouped_boxplot(
            df_yearly, "Yearly Capacity Additions", f"{tech_name}_yearly_boxplot.png"
        )
        plot_grouped_boxplot(
            df_cum,
            "Cumulative Capacity Additions",
            f"{tech_name}_cumulative_boxplot.png",
        )


# Try importing sklearn for clustering
try:
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("⚠ Warning: scikit-learn not found. Clustering will be skipped.")


def identify_capacity_clusters(df_all, eps=0.5, min_samples=3):
    """
    Performs DBSCAN clustering on the 2040 data points to group similar scenarios.
    """
    if not HAS_SKLEARN:
        df_all["cluster_label"] = -1
        return pd.DataFrame(), df_all

    # Filter for the target year (2040) for clustering
    df_2040 = df_all[df_all["year"] == 2040].copy()

    if df_2040.empty:
        df_all["cluster_label"] = -1
        return pd.DataFrame(), df_all

    # Features to cluster on
    features = df_2040[["Remanufacturing", "Manufacturing"]].values

    # Standardize features (DBSCAN is sensitive to scale)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # Run DBSCAN
    # eps: The maximum distance between two samples for one to be considered as in the neighborhood of the other.
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(features_scaled)

    # Assign labels back to the 2040 slice
    df_2040["cluster_label"] = db.labels_

    # Map these labels back to the main dataframe (only for 2040 rows)
    # For other years, we can leave them as NaN or -1 since we only label 2040
    df_all["cluster_label"] = -1
    df_all.loc[df_all["year"] == 2040, "cluster_label"] = df_2040["cluster_label"]

    # Generate Summary
    summary = df_2040.groupby("cluster_label").size().reset_index(name="count")

    return summary, df_all


def plot_cumulative_capacity_scatter(
    tech_list,
    nzia_scenarios_dict,
    target_years=[2025, 2030, 2035, 2040],
    output_dir="plots/cumulative_scatter",
    save_csv=True,
    perform_clustering=True,
    eps=0.5,  # Adjusted default (sensitivity depends on data scale)
    min_samples=3,
):
    """
    Generates SEPARATE scatter plots for each technology.
    - Layout: Rectangular (Landscape)
    - Legend: Solar only
    - Clusters: Annotates 2040 clusters with scenario counts (N=...)
    """

    # ---------------------------
    # Local Settings
    # ---------------------------
    FS_TICK = 20
    FS_AXIS = 20
    FS_LEGEND = 20
    FS_ANNOTATION = 20  # Font size for the "N=..." labels

    # Color mapping
    window_colors = ["#F4E100", "#3A737D", "#05A5D2", "#D79327"]
    year_colors = dict(zip(target_years, window_colors))

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("--- Processing & Plotting Individual Figures ---")

    for tech_name in tech_list:
        all_data = []

        # -----------------------------
        # 1. Load Data
        # -----------------------------
        for (lr, scenario_name), file_path in nzia_scenarios_dict.items():
            path_obj = Path(file_path)
            if not path_obj.exists():
                continue

            try:
                df = pd.read_excel(path_obj, sheet_name="extension_only_caps")
            except Exception as e:
                print(f"⚠ Could not read {path_obj}: {e}")
                continue

            df.columns = df.columns.str.strip()
            df["tech"] = df["tech"].astype(str).str.strip()

            # Basic Filling
            if "stf" in df.columns:
                df["stf"] = df["stf"].ffill()
            if "location" in df.columns:
                df["location"] = df["location"].ffill()

            df_tech = df[df["tech"] == tech_name].copy()
            if df_tech.empty:
                continue

            df_tech = df_tech.sort_values("stf")

            # Check columns
            req_cols = [
                "capacity_ext_eusecondary",
                "capacity_ext_stockout",
                "capacity_ext_euprimary",
                "newly_added_capacity",
            ]
            if not all(c in df_tech.columns for c in req_cols):
                continue

            # Cumulative calculations
            df_tech["cum_eusecondary"] = df_tech["capacity_ext_eusecondary"].cumsum()
            df_tech["cum_stockout"] = df_tech["capacity_ext_stockout"].cumsum()
            df_tech["cum_euprimary"] = df_tech["capacity_ext_euprimary"].cumsum()
            df_tech["cum_newly_added_capacity"] = df_tech[
                "newly_added_capacity"
            ].cumsum()

            for year in target_years:
                row = df_tech[df_tech["stf"] == year]
                if not row.empty:
                    all_data.append(
                        {
                            "tech": tech_name,
                            "year": year,
                            "learning_rate": lr,
                            "scenario": scenario_name,
                            "Remanufacturing": row["cum_eusecondary"].sum() / 1e3,
                            "Manufacturing": row["cum_euprimary"].sum() / 1e3,
                            "Stockpile": row["cum_stockout"].sum() / 1e3,
                            "Totals (incl. Imports)": row[
                                "cum_newly_added_capacity"
                            ].sum()
                            / 1e3,
                        }
                    )

        if not all_data:
            print(f"No data for {tech_name}. Skipping.")
            continue

        df_all = pd.DataFrame(all_data)

        # -----------------------------
        # 2. Perform Clustering (Automatic)
        # -----------------------------
        if perform_clustering and HAS_SKLEARN:
            # We specifically cluster the 2040 endpoints
            df_summary, df_all = identify_capacity_clusters(
                df_all, eps=eps, min_samples=min_samples
            )

            # Save Clustering Results to CSV
            cluster_dir = output_dir / "clusters"
            cluster_dir.mkdir(exist_ok=True)
            df_all.to_csv(cluster_dir / f"clustered_data_{tech_name}.csv", index=False)

        # -----------------------------
        # 3. Plotting
        # -----------------------------
        plt.figure(figsize=(10, 6))  # Slightly wider for better spacing
        plt.rc("xtick", labelsize=FS_TICK)
        plt.rc("ytick", labelsize=FS_TICK)

        # Draw Arrows (Tracers)
        for (lr, scenario_name), group_df in df_all.groupby(
            ["learning_rate", "scenario"]
        ):
            group_df = group_df.sort_values("year")
            for y1, y2 in zip(target_years[:-1], target_years[1:]):
                p1 = group_df[group_df["year"] == y1]
                p2 = group_df[group_df["year"] == y2]
                if p1.empty or p2.empty:
                    continue

                x1, y1v = p1["Remanufacturing"].values[0], p1["Manufacturing"].values[0]
                x2, y2v = p2["Remanufacturing"].values[0], p2["Manufacturing"].values[0]

                plt.annotate(
                    "",
                    xy=(x2, y2v),
                    xytext=(x1, y1v),
                    arrowprops=dict(
                        arrowstyle="->",
                        color="gray",
                        lw=1.1,
                        alpha=0.3,
                        shrinkA=0,
                        shrinkB=0,
                    ),
                    zorder=1,
                )

        # Draw Scatter Points
        for year in target_years:
            point = df_all[df_all["year"] == year]
            if not point.empty:
                plt.scatter(
                    point["Remanufacturing"],
                    point["Manufacturing"],
                    color=year_colors[year],
                    s=80,
                    edgecolor="black",
                    linewidth=0.6,
                    label=str(year),
                    zorder=2,
                    alpha=0.9,
                )

        # -----------------------------
        # 4. ANNOTATE CLUSTERS (Label Positioning Logic)
        # -----------------------------
        if perform_clustering and "cluster_label" in df_all.columns:
            # Filter for 2040 data only
            df_2040 = df_all[df_all["year"] == 2040]

            # Identify valid clusters and sort them by X-position (Left -> Right)
            # This ensures "First" cluster is always the left-most one, regardless of ID
            valid_clusters = []
            unique_labels = df_2040["cluster_label"].unique()

            for label in unique_labels:
                if label == -1:
                    continue  # Skip noise

                # Get data for this cluster
                cluster_data = df_2040[df_2040["cluster_label"] == label]
                mean_x = cluster_data["Remanufacturing"].mean()

                valid_clusters.append(
                    {"id": label, "data": cluster_data, "mean_x": mean_x}
                )

            # Sort the clusters by their mean X position
            valid_clusters.sort(key=lambda x: x["mean_x"])

            # Iterate through the sorted clusters
            for i, cluster_info in enumerate(valid_clusters):
                cluster_data = cluster_info["data"]
                count = len(cluster_data)

                # Determine Label Position
                # ---------------------------------------------------------
                # Logic:
                # 1. First Cluster (index 0 in sorted list) for On/Offshore Wind -> RIGHT of Centroid
                # 2. All others -> TOP of Max Y
                # ---------------------------------------------------------

                # Check if current tech is Onshore or Offshore Wind
                is_target_wind = any(
                    x in tech_name.lower() for x in ["wind", "batteries"]
                )

                # Calculate Coordinates
                center_x = cluster_data["Remanufacturing"].mean()
                center_y = cluster_data[
                    "Manufacturing"
                ].mean()  # Needed for 'right' alignment
                top_y = cluster_data[
                    "Manufacturing"
                ].max()  # Needed for 'top' alignment

                # Since list is sorted by X, i=0 is the left-most cluster
                if is_target_wind and i == 0:
                    # ---> PLACEMENT: RIGHT
                    xy_target = (center_x, center_y)  # Anchor to the center (centroid)
                    xy_offset = (20, 0)  # Shift right (20 points)
                    ha_align = "left"  # Align text to start from x
                    va_align = "center"  # Align text vertically centered
                else:
                    # ---> PLACEMENT: TOP (Default)
                    xy_target = (
                        center_x,
                        top_y,
                    )  # Anchor to the highest point in cluster
                    xy_offset = (0, 15)  # Shift up (15 points)
                    ha_align = "center"  # Center text horizontally
                    va_align = "bottom"  # Text sits on top of anchor

                # Add Text Annotation
                plt.annotate(
                    f"n={count}",
                    xy=xy_target,
                    xytext=xy_offset,
                    textcoords="offset points",
                    fontsize=FS_ANNOTATION,
                    color="black",
                    ha=ha_align,
                    va=va_align,
                    fontweight="bold",
                    zorder=10,
                    bbox=dict(
                        boxstyle="round,pad=0.4", fc="white", ec="black", alpha=0.85
                    ),
                )

        # Styling
        plt.xlabel("Remanufacturing Capacity (GW)", fontsize=FS_AXIS)
        plt.ylabel("Manufacturing Capacity (GW)", fontsize=FS_AXIS)
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()

        # -----------------------------
        # 5. Conditional Legend
        # -----------------------------
        # Only show legend for Solar (or if forced) to keep other plots clean
        if "solar" in tech_name.lower():
            handles, labels = plt.gca().get_legend_handles_labels()
            # Remove duplicates
            by_label = dict(zip(labels, handles))
            # Sort by year
            sorted_keys = sorted(by_label.keys())

            plt.legend(
                [by_label[k] for k in sorted_keys],
                sorted_keys,
                loc="lower center",
                bbox_to_anchor=(0.5, 1.02),
                ncol=4,
                fontsize=FS_LEGEND,
                frameon=True,
                edgecolor="black",
                framealpha=1,
                fancybox=False,
                handlelength=0.7,
                handletextpad=0.3,
                columnspacing=1.0,
            )

        # -----------------------------
        # 6. Save
        # -----------------------------
        fig_path = output_dir / f"cumulative_scatter_tracer_{tech_name}.png"
        plt.savefig(fig_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✔ Plot saved: {fig_path}")


def plot_window_capacity_scatter(
    tech_list,
    nzia_scenarios_dict,
    windows=[(2024, 2025), (2026, 2030), (2031, 2035), (2036, 2040)],
    output_dir="plots/window_scatter",
    save_csv=True,
    perform_clustering=True,
    eps=0.7,
    min_samples=2,
):
    """
    Scatter plot of capacities aggregated by windows (Remanufacturing vs Manufacturing)
    for selected technologies, with optional DBSCAN clustering and integrated ternary grid output.

    Added:
      - after clustering, produce an interactive ternary grid (2x2 default) per tech using clustered dataframe.
      - handles df_with_clusters that uses either 'year' or 'window_id'.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # RGB color palette for windows (kept)
    window_colors = ["#F4E100", "#3A737D", "#05A5D2", "#D79327"]

    for tech_name in tech_list:
        all_data = []

        # Load and process NZIA files
        for (lr, scenario_name), file_path in nzia_scenarios_dict.items():
            if not Path(file_path).exists():
                continue
            try:
                df = pd.read_excel(file_path, sheet_name="extension_only_caps")
            except Exception as e:
                print(f"⚠ Could not read {file_path}: {e}")
                continue

            df.columns = df.columns.str.strip()
            df["tech"] = df["tech"].astype(str).str.strip()
            df["stf"] = df["stf"].ffill()
            if "location" in df.columns:
                df["location"] = df["location"].ffill()

            df_tech = df[df["tech"] == tech_name].copy()
            if df_tech.empty:
                continue

            # Aggregate over windows
            for i, (start_year, end_year) in enumerate(windows, start=1):
                df_window = df_tech[
                    (df_tech["stf"] >= start_year) & (df_tech["stf"] <= end_year)
                ]
                all_data.append(
                    {
                        "tech": tech_name,
                        "window_id": i,
                        "window_label": f"{start_year}-{end_year}",
                        "learning_rate": lr,
                        "scenario": scenario_name,
                        "Remanufacturing": df_window["capacity_ext_eusecondary"].sum()
                        / 1e3,  # GW
                        "Manufacturing": df_window["capacity_ext_euprimary"].sum()
                        / 1e3,  # GW
                        "Stockpile": df_window["capacity_ext_stockout"].sum() / 1e3,
                        "Totals (incl. Imports)": df_window[
                            "newly_added_capacity"
                        ].sum()
                        / 1e3,
                    }
                )

        if not all_data:
            print(f"No data for {tech_name}. Skipping.")
            continue

        df_all = pd.DataFrame(all_data)

        # Save CSV if requested
        if save_csv:
            csv_path = Path(output_dir) / f"window_data_{tech_name}.csv"
            df_all.to_csv(csv_path, index=False)
            print(f"✔ Data exported for {tech_name}: {csv_path}")

        # Simple scatter plot (points only)
        plt.figure(figsize=(8, 6))
        for i, (_, group) in enumerate(df_all.groupby("window_id")):
            plt.scatter(
                group["Remanufacturing"],
                group["Manufacturing"],
                color=window_colors[i % len(window_colors)],
                s=50,
                label=group["window_label"].iloc[0],
            )

        plt.xlabel("Remanufacturing Capacity (GW)")
        plt.ylabel("Manufacturing Capacity (GW)")
        plt.title(f"Capacity by Window for {tech_name}")
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.legend(title="Window", frameon=True, edgecolor="black")
        plt.tight_layout(rect=[0.02, 0.06, 0.98, 0.94])  # leave extra bottom space
        plt.subplots_adjust(bottom=0.25)  # increase bottom margin
        fig_path = Path(output_dir) / f"window_scatter_points_{tech_name}.png"
        plt.savefig(fig_path, dpi=300)
        plt.close()
        print(f"✔ Scatter plot saved for {tech_name}: {fig_path}")

        # Optional clustering (DBSCAN)
        if perform_clustering:
            # Keep all columns needed for plotting stacked bars and ternary
            df_for_clustering = df_all.copy()
            # For DBSCAN the upstream helper expects 'year' column; rename
            if "window_id" in df_for_clustering.columns:
                df_for_clustering = df_for_clustering.rename(
                    columns={"window_id": "year"}
                )

            # Call your clustering helper (assumed available in your environment)
            df_summary, df_with_clusters = identify_yearly_capacity_clusters(
                df_for_clustering,
                years_of_interest=df_for_clustering["year"].unique(),
                eps=eps,
                min_samples=min_samples,
            )

            cluster_dir = output_dir / "clusters_window"
            cluster_dir.mkdir(exist_ok=True)
            df_summary.to_csv(
                cluster_dir / f"cluster_summary_{tech_name}.csv", index=False
            )
            df_with_clusters.to_csv(
                cluster_dir / f"clustered_data_{tech_name}.csv", index=False
            )
            print(f"✅ Clustering done for {tech_name}. Results saved in {cluster_dir}")

            # Call your existing clustered bar plotting if you still want it
            plot_clustered_benchmark_from_window_df(
                df_with_clusters, output_dir=output_dir / "clustered_benchmark_window"
            )

    print("All done.")


def plot_window_scatter_relative_single(
    tech_list,
    nzia_scenarios_dict,
    windows=[(2024, 2025), (2026, 2030), (2031, 2035), (2036, 2040)],
    output_dir="plots/window_scatter_relative",
    save_csv=True,
    figsize=(7, 6),
    grid_mode=True,
    grid_figsize=(13, 10),  # Used if grid_mode=True
    target_lines=(0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.7, 0.75, 0.8, 0.85),
    project_with_stock=True,
    projection_color="#ff7f0e",
    barrier_color="#d62728",
    show_top_projections=0,
    scale_marker_by_totals=False,
    min_stock_frac_to_show=0.01,
    # tracer_step=0.05,                # draw tracer "L" lines every 5% by default
    # tracer_color="0.85",
    # tracer_lw=0.6,
    # tracer_alpha=0.28,
    global_tick_labelsize=13,  # increased tick label sizes
    global_xlabel_size=14,
    global_ylabel_size=14,
    global_title_size=16,
    legend_fontsize=10,
):
    """
    Single-window fractional scatter.

    Important behavior:
    - Maximum used to determine dynamic barrier (target) line lengths is
      computed from the overall fraction we calculate: Rem_frac + Man_frac + Stock_frac
      (stored in LocalSourcing_frac). That per-window maximum sets how high
      dashed target lines are drawn (effective_p = min(requested_p, max_local_sourcing)).
    - The baseline 0.40 target is always shown (solid/thick). It is drawn up to
      min(0.40, axis_max) so it is visible in every subplot (but clipped by axis limits).
    - Other target_lines (e.g., 0.45, 0.50...) are dashed and capped by the
      per-window maximum LocalSourcing_frac.
    - Tracer "L" guides are drawn every tracer_step up to the per-window maximum.
    """

    # Tech color palette (add more as needed)
    tech_colors = {
        "solarPV": (223 / 255, 221 / 255, 25 / 255),  # yellow
        "windon": (44 / 255, 80 / 255, 180 / 255),  # blue
        "windoff": (143 / 255, 60 / 255, 175 / 255),  # purple
    }
    default_tech_color = (0.13, 0.13, 0.13)

    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    saved_paths = []

    def _draw_barrier_connect_axes(
        ax,
        p,
        max_point,
        axis_min,
        axis_max,
        color=barrier_color,
        linewidth=1.6,
        linestyle="--",
        alpha=0.6,
        baseline_value=0.40,
    ):
        """
        Draw the barrier line y = p - x in a 'connect-axes' style but with the visible
        height determined as follows:
         - if p is the baseline (baseline_value, default 0.40), draw it up to
           min(baseline_value, axis_max) so it's always present (but clipped by axis limits).
         - otherwise (dynamic targets), compute effective_p = min(p, max_point)
           and draw the segment from (0,effective_p) to (effective_p,0).

        This matches the visual of a full connect-axes target line while ensuring
        dynamic lines reflect the per-window overall LocalSourcing_frac maximum.
        """
        if axis_max <= axis_min:
            return

        # baseline: always present (but clipped by axis_max)
        if abs(p - baseline_value) < 1e-9:
            effective_p = min(baseline_value, axis_max)
            if effective_p <= axis_min:
                return
        else:
            # dynamic targets: capped by per-window max of LocalSourcing_frac
            effective_p = min(p, max_point)
            if effective_p <= axis_min:
                return

        xs = np.linspace(0.0, effective_p, 300)
        ys = effective_p - xs
        ys = np.clip(ys, axis_min, axis_max)
        ax.plot(
            xs,
            ys,
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            alpha=alpha,
            zorder=1,
        )

    for tech_name in tech_list:
        all_data = []
        tech_rgb = tech_colors.get(tech_name, default_tech_color)

        # Aggregate inputs (reads extension_only_caps sheet)
        for (lr, scenario_name), file_path in nzia_scenarios_dict.items():
            p = Path(file_path)
            if not p.exists():
                continue
            try:
                df = pd.read_excel(p, sheet_name="extension_only_caps")
            except Exception as e:
                print(f"⚠ Could not read {p}: {e}")
                continue

            df.columns = df.columns.str.strip()
            df["tech"] = df["tech"].astype(str).str.strip()
            df["stf"] = df["stf"].ffill()
            if "location" in df.columns:
                df["location"] = df["location"].ffill()

            df_tech = df[df["tech"] == tech_name].copy()
            if df_tech.empty:
                continue

            for i, (start_year, end_year) in enumerate(windows, start=1):
                df_window = df_tech[
                    (df_tech["stf"] >= start_year) & (df_tech["stf"] <= end_year)
                ]
                all_data.append(
                    {
                        "tech": tech_name,
                        "window_id": i,
                        "window_label": f"{start_year}-{end_year}",
                        "window_end_year": end_year,
                        "learning_rate": lr,
                        "scenario": scenario_name,
                        "Remanufacturing": df_window["capacity_ext_eusecondary"].sum()
                        / 1e3,
                        "Manufacturing": df_window["capacity_ext_euprimary"].sum()
                        / 1e3,
                        "Stockpile": df_window["capacity_ext_stockout"].sum() / 1e3,
                        "Totals (incl. Imports)": df_window[
                            "newly_added_capacity"
                        ].sum()
                        / 1e3,
                    }
                )

        if not all_data:
            print(f"No data for {tech_name}. Skipping.")
            continue

        df_all = pd.DataFrame(all_data)

        if save_csv:
            csv_path = outdir / f"window_data_{tech_name}.csv"
            df_all.to_csv(csv_path, index=False)
            print(f"✔ Data exported for {tech_name}: {csv_path}")

        totals = df_all["Totals (incl. Imports)"].replace(0, np.nan)
        df_all["Rem_frac"] = df_all["Remanufacturing"].div(totals).fillna(0)
        df_all["Man_frac"] = df_all["Manufacturing"].div(totals).fillna(0)
        df_all["Stock_frac"] = df_all["Stockpile"].div(totals).fillna(0)
        # overall fraction user requested to use for maxing target lines
        df_all["LocalSourcing_frac"] = (
            df_all["Rem_frac"] + df_all["Man_frac"] + df_all["Stock_frac"]
        )

        unique_windows = sorted(df_all["window_id"].unique())
        window_labels = [
            df_all[df_all["window_id"] == win]["window_label"].iloc[0]
            for win in unique_windows
        ]

        if grid_mode:
            # --------- 2x2 grid mode (all windows for this tech) ----------
            fig, axes = plt.subplots(2, 2, figsize=grid_figsize, squeeze=True)
            axes = axes.flatten()

            # Compute global axis scaling
            all_local_max = float(df_all["LocalSourcing_frac"].max(skipna=True))
            all_proj_local_max = float(df_all["LocalSourcing_frac"].max(skipna=True))
            global_max = np.nanmax([all_local_max, all_proj_local_max, 0.6])
            axis_max = min(1.0, max(global_max * 1.05, 0.6))
            axis_min = 0.0

            # Tech internal name and greenish palette
            tech_name_map = {
                "Solar PV": "solarPV",
                "Onshore Wind": "windon",
                "Offshore Wind": "windoff",
            }

            tech_colors = {
                "solarPV": "#E69F00",  # bright orange/gold
                "windon": "#66C2A5",  # light vibrant green
                "windoff": "#00876C",  # dark green
            }
            default_tech_color = "#808080"

            internal_name = tech_name_map.get(tech_name, tech_name)
            edgecolor = tech_colors.get(internal_name, default_tech_color)
            facecolor = edgecolor

            for ax_idx, win in enumerate(unique_windows):
                sub = df_all[df_all["tech"] == internal_name].copy()
                sub = sub[sub["window_id"] == win]
                ax = axes[ax_idx]

                if sub.empty:
                    ax.set_visible(False)
                    continue  # Skip everything if no data

                plot_x = sub["Rem_frac"].to_numpy(copy=True)
                plot_y = sub["Man_frac"].to_numpy(copy=True)

                # Jitter for very small values
                seed = abs(hash(f"{internal_name}_{win}")) % (2**32)
                rng = np.random.default_rng(seed)
                jitter_scale = 0.002
                jitter_x = rng.normal(scale=jitter_scale, size=len(sub))
                jitter_y = rng.normal(scale=jitter_scale, size=len(sub))
                small_mask_x = plot_x <= 1e-6
                small_mask_y = plot_y <= 1e-6
                plot_x[small_mask_x] += jitter_x[small_mask_x]
                plot_y[small_mask_y] += jitter_y[small_mask_y]
                plot_x = np.clip(plot_x, axis_min, axis_max)
                plot_y = np.clip(plot_y, axis_min, axis_max)

                # Marker sizing
                if scale_marker_by_totals:
                    tot = sub["Totals (incl. Imports)"].fillna(0)
                    sizes = np.clip(
                        (tot / (tot.max() if tot.max() > 0 else 1)) * 120, 12, 120
                    )
                else:
                    sizes = np.full(len(sub), 48)

                # Projections under markers
                if project_with_stock:
                    for idx, r in sub.iterrows():
                        sf = r["Stock_frac"]
                        if sf >= min_stock_frac_to_show:
                            x = r["Rem_frac"]
                            y = r["Man_frac"]
                            proj_x = min(max(x + sf / 2.0, axis_min), axis_max)
                            proj_y = min(max(y + sf / 2.0, axis_min), axis_max)
                            ax.plot(
                                [x, proj_x],
                                [y, proj_y],
                                color=projection_color,
                                linewidth=0.7,
                                alpha=0.9,
                                zorder=2,
                            )
                            ax.plot(
                                proj_x,
                                proj_y,
                                marker="o",
                                color=projection_color,
                                markersize=4,
                                markeredgecolor="white",
                                zorder=2,
                            )

                # Filled markers
                ax.scatter(
                    plot_x,
                    plot_y,
                    s=sizes,
                    facecolors=facecolor,
                    edgecolors=edgecolor,
                    linewidths=0.7,
                    zorder=4,
                    marker="o",
                    alpha=0.9,
                )

                # Barrier lines (only if data exists)
                max_point = (
                    float(sub["LocalSourcing_frac"].max(skipna=True))
                    if len(sub)
                    else 0.0
                )
                for p in target_lines:
                    linestyle = "-" if abs(p - 0.40) < 1e-9 else "--"
                    linewidth = 2.4 if abs(p - 0.40) < 1e-9 else 1.6
                    alpha = 0.98 if abs(p - 0.40) < 1e-9 else 0.6
                    _draw_barrier_connect_axes(
                        ax,
                        p,
                        max_point,
                        axis_min,
                        axis_max,
                        color=barrier_color,
                        linewidth=linewidth,
                        linestyle=linestyle,
                        alpha=alpha,
                        baseline_value=0.40,
                    )

                # Axis labels, grid, and ticks
                ax.set_xlim(axis_min, axis_max)
                ax.set_ylim(axis_min, axis_max)
                ax.set_aspect("equal", adjustable="box")
                ax.set_xlabel("Remanufacturing (fraction of total)", fontsize=18)
                ax.set_ylabel("Manufacturing (fraction of total)", fontsize=18)
                ax.grid(True, linestyle="--", alpha=0.25)
                ax.tick_params(axis="x", labelsize=16, pad=6)
                ax.tick_params(axis="y", labelsize=16)
                ax.set_title(f"{window_labels[ax_idx]}", fontsize=16)

                # ---------------------------
                # Legend below 2x2 grid (outside plot area)
                # ---------------------------

                # --- FIX: Map internal names back to "Nice Names" for the legend ---
                display_name_map = {
                    "solarPV": "Solar PV",
                    "windon": "Onshore Wind",
                    "windoff": "Offshore Wind",
                }
                # Fallback to tech_name if the internal name isn't in the map
                nice_tech_name = display_name_map.get(internal_name, tech_name)
                # -------------------------------------------------------------------

                proxy_marker = Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="w",
                    markerfacecolor=facecolor,
                    markeredgecolor=edgecolor,
                    markeredgewidth=1.0,
                    markersize=10,
                )
                proxy_proj = Line2D([0], [0], color=projection_color, lw=1.2)
                proxy_benchmark = Line2D([0], [0], color=barrier_color, lw=2.4)

                fig.legend(
                    [proxy_marker, proxy_proj, proxy_benchmark],
                    [
                        f"{nice_tech_name} Scenario",
                        "stockpile additions",
                        "NZIA Benchmark (40%)",
                    ],
                    fontsize=18,
                    frameon=True,
                    ncol=3,
                    loc="lower center",
                    bbox_to_anchor=(0.5, -0.08),
                )

                fig.tight_layout(rect=[0, 0, 1, 0.95])
                fname = outdir / f"{internal_name}_window_ALL_relative_grid.png"
                fig.savefig(fname, dpi=1000, bbox_inches="tight")
                plt.close(fig)
                saved_paths.append(fname)
                print(f"✔ Saved 2x2 grid plot: {fname}")
        else:
            # --------- One plot per window (as before) ----------
            for win in unique_windows:
                sub = df_all[df_all["window_id"] == win].copy()
                if sub.empty:
                    continue

                try:
                    # local_max should be computed from LocalSourcing_frac (overall fraction)
                    local_max = float(sub["LocalSourcing_frac"].max(skipna=True))
                except Exception:
                    local_max = 0.6
                axis_max = min(1.0, max(local_max * 1.05, 0.6))
                axis_min = 0.0

                fig, ax = plt.subplots(figsize=figsize)

                # marker sizing: larger for trend visibility; can be scaled by totals if requested
                if scale_marker_by_totals:
                    tot = sub["Totals (incl. Imports)"].fillna(0)
                    sizes = np.clip(
                        (tot / (tot.max() if tot.max() > 0 else 1)) * 120, 24, 180
                    )
                else:
                    sizes = np.full(len(sub), 80)

                # deterministic jitter for axis-packed points
                seed = abs(hash(f"{tech_name}_{win}")) % (2**32)
                rng = np.random.default_rng(seed)
                jitter_scale = 0.002
                jitter_x = rng.normal(scale=jitter_scale, size=len(sub))
                jitter_y = rng.normal(scale=jitter_scale, size=len(sub))
                plot_x = sub["Rem_frac"].to_numpy(copy=True)
                plot_y = sub["Man_frac"].to_numpy(copy=True)
                small_mask_x = plot_x <= 1e-6
                small_mask_y = plot_y <= 1e-6
                plot_x[small_mask_x] += jitter_x[small_mask_x]
                plot_y[small_mask_y] += jitter_y[small_mask_y]
                plot_x = np.clip(plot_x, axis_min, axis_max)
                plot_y = np.clip(plot_y, axis_min, axis_max)

                # draw tracer levels up to this subplot's max point (based on LocalSourcing_frac)
                max_point = (
                    float(sub["LocalSourcing_frac"].max(skipna=True))
                    if len(sub)
                    else 0.0
                )
                _draw_tracer_levels(
                    ax,
                    max_point,
                    step=tracer_step,
                    color=tracer_color,
                    lw=tracer_lw,
                    alpha=tracer_alpha,
                )

                # draw barrier lines: baseline always present (solid, thicker) up to axis_max,
                # other target_lines dashed and capped by per-window LocalSourcing_frac (max_point)
                for p in target_lines:
                    linestyle = "-" if abs(p - 0.40) < 1e-9 else "--"
                    linewidth = 2.4 if abs(p - 0.40) < 1e-9 else 1.6
                    alpha = 0.98 if abs(p - 0.40) < 1e-9 else 0.6
                    _draw_barrier_connect_axes(
                        ax,
                        p,
                        max_point,
                        axis_min,
                        axis_max,
                        color=barrier_color,
                        linewidth=linewidth,
                        linestyle=linestyle,
                        alpha=alpha,
                        baseline_value=0.40,
                    )

                # projections
                proj_lw = 0.7
                for idx, r in sub.iterrows():
                    sf = r["Stock_frac"]
                    if sf >= min_stock_frac_to_show and project_with_stock:
                        x = r["Rem_frac"]
                        y = r["Man_frac"]
                        proj_x = min(max(x + sf / 2.0, axis_min), axis_max)
                        proj_y = min(max(y + sf / 2.0, axis_min), axis_max)
                        ax.plot(
                            [x, proj_x],
                            [y, proj_y],
                            color=projection_color,
                            linewidth=proj_lw,
                            alpha=0.9,
                            zorder=2,
                        )
                        ax.plot(
                            proj_x,
                            proj_y,
                            marker="o",
                            color=projection_color,
                            markersize=6,
                            markeredgecolor="white",
                            zorder=2,
                        )

                # filled markers
                edgecolor = tech_colors.get(tech_name, default_tech_color)
                facecolor = (edgecolor[0], edgecolor[1], edgecolor[2], 0.9)
                ax.scatter(
                    plot_x,
                    plot_y,
                    s=sizes,
                    facecolors=[facecolor],
                    edgecolors=[edgecolor],
                    linewidths=1.4,
                    zorder=4,
                    marker="o",
                )

                # annotate top projections if requested
                if show_top_projections and len(sub) > 0:
                    top = (
                        sub[sub["Stock_frac"] >= min_stock_frac_to_show]
                        .sort_values("Stock_frac", ascending=False)
                        .head(show_top_projections)
                    )
                    for _, trow in top.iterrows():
                        px = min(
                            max(trow["Rem_frac"] + trow["Stock_frac"] / 2.0, axis_min),
                            axis_max,
                        )
                        py = min(
                            max(trow["Man_frac"] + trow["Stock_frac"] / 2.0, axis_min),
                            axis_max,
                        )
                        label = f"+{trow['Stock_frac'] * 100:.1f}%\n{trow['Stockpile']:.1f} GW"
                        ax.text(
                            px + 0.01 * (axis_max - axis_min),
                            py + 0.01 * (axis_max - axis_min),
                            label,
                            fontsize=8,
                            bbox=dict(facecolor="white", alpha=0.85, edgecolor="none"),
                        )

                # aesthetics & equal axes
                ax.set_xlim(axis_min, axis_max)
                ax.set_ylim(axis_min, axis_max)
                ax.set_aspect("equal", adjustable="box")
                ax.set_xlabel(
                    "Remanufacturing (fraction of total)", fontsize=global_xlabel_size
                )
                ax.set_ylabel(
                    "Manufacturing (fraction of total)", fontsize=global_ylabel_size
                )
                window_label = sub["window_label"].iloc[0]
                ax.set_title(
                    f"{tech_name} — {window_label}", fontsize=global_title_size
                )
                ax.grid(True, linestyle="--", alpha=0.25)

                # tick sizing
                ax.tick_params(axis="x", labelsize=global_tick_labelsize, pad=6)
                ax.tick_params(axis="y", labelsize=global_tick_labelsize)

                # Compact legend: tech marker, projection, NZIA Benchmark
                proxy_marker = Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="w",
                    markerfacecolor=facecolor,
                    markeredgecolor=edgecolor,
                    markeredgewidth=1.4,
                    markersize=8,
                )
                proxy_proj = Line2D([0], [0], color=projection_color, lw=1.2)
                proxy_benchmark = Line2D([0], [0], color=barrier_color, lw=2.4)
                ax.legend(
                    [proxy_marker, proxy_proj, proxy_benchmark],
                    [
                        f"{tech_name} scenario",
                        "stockpile projection (equal split)",
                        "NZIA Benchmark (40%)",
                    ],
                    fontsize=legend_fontsize,
                    frameon=True,
                    loc="upper right",
                )

                # save the figure
                safe_label = window_label.replace(" ", "_").replace("/", "-")
                fname = outdir / f"{tech_name}_window_{safe_label}_relative.png"
                fig.tight_layout(rect=[0, 0, 1, 0.96])
                fig.savefig(fname, dpi=500)
                plt.close(fig)
                saved_paths.append(fname)
                print(f"✔ Saved relative fractional plot: {fname}")

    return saved_paths


def plot_clustered_benchmark_from_window_df(df_with_clusters, output_dir):
    """
    Plot clustered benchmark with PHYSICAL LABEL OFFSET.
    - Uses a 20-point physical offset (approx 7mm) for labels.
    - Guarantees visibility regardless of axis scale.
    """
    # ================================================================
    # GLOBAL SETTINGS
    # ================================================================
    FS_TICK = 20
    FS_AXIS = 22
    FS_LEGEND = 20
    FS_WINDOW_LABEL = 20

    # Layout
    FIXED_MARGINS = dict(top=0.82, bottom=0.12, left=0.15, right=0.95)
    Y_LABEL_COORDS = (-0.14, 0.5)
    LEGEND_Y_POS = 1.13

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    components = ["Remanufacturing", "Stockpile", "Manufacturing"]
    labels = ["Remanufacturing", "Stockpile", "Manufacturing"]
    colors = ["#FDC5B5", "#F99B7D", "#F76C5E"]
    hatches = ["..", "//", "xx"]

    # --- DEFINITIONS ---
    # Colors for the 4 windows
    window_colors_list = ["#F4E100", "#3A737D", "#05A5D2", "#D79327"]
    # Markers: Diamond, Circle, Triangle_Up, Square
    window_markers_list = ["D", "o", "^", "s"]

    base_patches = [
        mpatches.Patch(facecolor=fc, edgecolor="black", hatch=h, label=lab)
        for fc, h, lab in zip(colors, hatches, labels)
    ]
    imports_patch = mpatches.Patch(
        facecolor="#D3D3D3", edgecolor="black", label="Imports"
    )
    nzia_line = Line2D(
        [0], [0], color="red", linestyle="--", linewidth=2, label="NZIA Benchmark"
    )

    for tech in df_with_clusters["tech"].unique():
        df_tech = df_with_clusters[df_with_clusters["tech"] == tech].copy()

        # --- ROBUSTNESS: Enforce Integer Year ---
        df_tech["year"] = df_tech["year"].astype(int)
        windows = sorted(df_tech["year"].unique())

        # Map each window year to a specific color and marker index
        # This prevents mismatches if windows are missing or out of order
        win_to_idx = {win: i for i, win in enumerate(windows)}

        # Label Helpers
        winid_to_label = {
            row["year"]: row["window_label"]
            for _, row in df_tech.drop_duplicates(
                subset=["year", "window_label"]
            ).iterrows()
        }
        window_labels = [winid_to_label[w] for w in windows]
        x_base = np.arange(len(windows))

        # Bar Width
        max_clusters = max(df_tech.groupby("year")["cluster_id"].nunique())
        total_width = 0.8
        gap = 0.02
        width = (total_width - (max_clusters - 1) * gap) / max_clusters

        # ================================================================
        # 1. RELATIVE PLOT
        # ================================================================
        fig_rel, ax_rel = plt.subplots(figsize=(12, 7))
        fig_rel.subplots_adjust(**FIXED_MARGINS)

        for i, win in enumerate(windows):
            df_win = df_tech[df_tech["year"] == win]
            clusters_this_win = sorted(df_win["cluster_id"].unique())
            start_offset = (
                -(len(clusters_this_win) * width + (len(clusters_this_win) - 1) * gap)
                / 2
                + width / 2
            )

            for j, cluster in enumerate(clusters_this_win):
                df_cluster = df_win[df_win["cluster_id"] == cluster]
                row = df_cluster[
                    [
                        "Remanufacturing",
                        "Stockpile",
                        "Manufacturing",
                        "Totals (incl. Imports)",
                    ]
                ].mean()
                x_pos = x_base[i] + start_offset + j * (width + gap)

                total = row["Totals (incl. Imports)"]
                denom = total if total > 0 else 1

                # Background
                ax_rel.bar(
                    x_pos,
                    1,
                    width=width,
                    facecolor="#D3D3D3",
                    edgecolor="black",
                    linewidth=0.8,
                    zorder=0,
                )

                # Stack
                bottom = 0
                for comp, color, hatch in zip(components, colors, hatches):
                    frac = row[comp] / denom
                    ax_rel.bar(
                        x_pos,
                        frac,
                        width=width,
                        bottom=bottom,
                        facecolor=color,
                        edgecolor="black",
                        hatch=hatch,
                        linewidth=0.8,
                        zorder=1,
                    )
                    bottom += frac

                font_size = max(6, min(16, 80 / len(clusters_this_win)))
                ax_rel.text(
                    x_pos,
                    bottom + 0.02,
                    f"C{int(cluster)}",
                    ha="center",
                    va="bottom",
                    rotation=90,
                    fontsize=font_size,
                )

        ax_rel.axhline(0.4, color="red", linestyle="--", linewidth=2)
        ax_rel.set_xticks(x_base)
        ax_rel.set_xticklabels(window_labels, fontsize=FS_WINDOW_LABEL)
        ax_rel.tick_params(axis="y", labelsize=FS_TICK)
        ax_rel.set_ylim(0, 1.08)
        ax_rel.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda y, _: f"{int(y * 100)}%")
        )
        ax_rel.set_ylabel("% of Total Capacity Additions", fontsize=FS_AXIS)
        ax_rel.yaxis.set_label_coords(*Y_LABEL_COORDS)
        ax_rel.grid(axis="y", alpha=0.3)
        ax_rel.legend(
            handles=[nzia_line],
            fontsize=FS_LEGEND,
            frameon=True,
            loc="upper center",
            bbox_to_anchor=(0.5, LEGEND_Y_POS),
            ncol=1,
            borderaxespad=0,
        )
        fig_rel.savefig(output_dir / f"{tech}_clustered_relative_window.png", dpi=1000)
        plt.close(fig_rel)

        # ================================================================
        # 2. ABSOLUTE PLOT
        # ================================================================
        fig_abs, ax_abs = plt.subplots(figsize=(12, 7))
        fig_abs.subplots_adjust(**FIXED_MARGINS)

        # DEFINE PHYSICAL OFFSET TRANSFORM
        offset_trans = mtransforms.ScaledTranslation(
            0, 20 / 72, fig_abs.dpi_scale_trans
        )
        text_trans = ax_abs.transData + offset_trans

        global_max_h = df_tech["Totals (incl. Imports)"].max()
        if np.isnan(global_max_h) or global_max_h == 0:
            global_max_h = 1.0
        ax_abs.set_ylim(0, global_max_h * 1.2)

        for i, win in enumerate(windows):
            df_win = df_tech[df_tech["year"] == win]
            clusters_this_win = sorted(df_win["cluster_id"].unique())
            start_offset = (
                -(len(clusters_this_win) * width + (len(clusters_this_win) - 1) * gap)
                / 2
                + width / 2
            )

            for j, cluster in enumerate(clusters_this_win):
                df_cluster = df_win[df_win["cluster_id"] == cluster]
                row = df_cluster[
                    [
                        "Remanufacturing",
                        "Stockpile",
                        "Manufacturing",
                        "Totals (incl. Imports)",
                    ]
                ].mean()
                x_pos = x_base[i] + start_offset + j * (width + gap)

                total_height = row["Totals (incl. Imports)"]
                stack_height = (
                    row["Remanufacturing"] + row["Stockpile"] + row["Manufacturing"]
                )

                # Bars
                ax_abs.bar(
                    x_pos,
                    total_height,
                    width=width,
                    facecolor="#D3D3D3",
                    edgecolor="black",
                    linewidth=0.8,
                )
                bottom = 0
                for comp, color, hatch in zip(components, colors, hatches):
                    val = row[comp]
                    ax_abs.bar(
                        x_pos,
                        val,
                        width=width,
                        bottom=bottom,
                        facecolor=color,
                        edgecolor="black",
                        hatch=hatch,
                        linewidth=0.8,
                    )
                    bottom += val

                font_size = max(6, min(16, 80 / len(clusters_this_win)))
                is_wind = tech in ["windon", "windoff"]
                is_edge_window = (i == 0) or (i == 3)
                anchor_y = (
                    total_height if (is_wind and is_edge_window) else stack_height
                )

                ax_abs.text(
                    x_pos,
                    anchor_y,
                    f"C{int(cluster)}",
                    ha="center",
                    va="bottom",
                    rotation=90,
                    fontsize=font_size,
                    transform=text_trans,
                )

        ax_abs.set_xticks(x_base)
        ax_abs.set_xticklabels(window_labels, fontsize=FS_WINDOW_LABEL)
        ax_abs.tick_params(axis="y", labelsize=FS_TICK)
        ax_abs.set_ylabel("Capacity (GW)", fontsize=FS_AXIS)
        ax_abs.yaxis.set_label_coords(*Y_LABEL_COORDS)
        ax_abs.grid(axis="y", alpha=0.3)

        abs_handles = [imports_patch, base_patches[1], base_patches[2], base_patches[0]]
        ax_abs.legend(
            handles=abs_handles,
            fontsize=FS_LEGEND,
            frameon=True,
            loc="upper center",
            bbox_to_anchor=(0.5, LEGEND_Y_POS),
            ncol=len(abs_handles),
        )

        fig_abs.savefig(output_dir / f"{tech}_clustered_absolute_window.png", dpi=1000)
        plt.close(fig_abs)

        # =====================================================
        # 3. SCATTER OVERLAY WITH CLUSTER LABELS (RESTORED & IMPROVED)
        # =====================================================
        fig_scat, ax_scat = plt.subplots(figsize=(10, 8))

        # A. Plot Scatter Points using groupby (SAFE METHOD)
        # This matches your original logic exactly
        for win, subset in df_tech.groupby("year"):
            # Determine index for this window to get correct color/marker
            idx = win_to_idx.get(win, 0)

            # Cyclic selection
            marker_char = window_markers_list[idx % len(window_markers_list)]
            color_hex = window_colors_list[idx % len(window_colors_list)]

            ax_scat.scatter(
                subset["Remanufacturing"],
                subset["Manufacturing"],
                marker=marker_char,
                facecolors=color_hex,
                edgecolors="black",
                alpha=0.6,
                s=90,
                linewidths=0.6,
                label=None,  # We build legend manually below
                zorder=3,
            )

        # B. Compute Centroids and prepare for AdjustText
        centroids = (
            df_tech.groupby(["year", "cluster_id"])[
                ["Remanufacturing", "Manufacturing"]
            ]
            .mean()
            .reset_index()
        )

        x_range = df_tech["Remanufacturing"].max() - df_tech["Remanufacturing"].min()
        y_range = df_tech["Manufacturing"].max() - df_tech["Manufacturing"].min()
        radius = 0.05 * max(
            x_range if x_range > 0 else 1e-6, y_range if y_range > 0 else 1e-6
        )

        texts_to_adjust = []

        for _, row in centroids.iterrows():
            win_val = int(row["year"])
            idx = win_to_idx.get(win_val, 0)
            color = window_colors_list[idx % len(window_colors_list)]

            # Draw centroid circle
            circle = plt.Circle(
                (row["Remanufacturing"], row["Manufacturing"]),
                radius=radius,
                edgecolor=color,
                facecolor=color,
                lw=2.0,
                alpha=0.3,
                zorder=2,
            )
            ax_scat.add_patch(circle)

            t = ax_scat.text(
                row["Remanufacturing"],
                row["Manufacturing"],
                f"C{int(row['cluster_id'])}",
                fontsize=11,
                fontweight="bold",
                color="black",
                ha="center",
                va="center",
                zorder=10,
            )
            texts_to_adjust.append(t)

        # C. Apply AdjustText
        adjust_text(
            texts_to_adjust,
            ax=ax_scat,
            arrowprops=dict(arrowstyle="-", color="gray", lw=1.0, alpha=0.8),
            expand_points=(1.2, 1.2),
            expand_text=(1.2, 1.2),
            force_text=(0.5, 0.5),
        )

        ax_scat.set_xlabel("Remanufacturing Capacity (GW)", fontsize=20)
        ax_scat.set_ylabel("Manufacturing Capacity (GW)", fontsize=20)
        ax_scat.grid(True, linestyle="--", alpha=0.3)
        ax_scat.tick_params(axis="x", labelsize=20)
        ax_scat.tick_params(axis="y", labelsize=20)

        # Build legend
        legend_handles = []
        for i, lbl in enumerate(window_labels):
            mk = window_markers_list[i % len(window_markers_list)]
            col = window_colors_list[i % len(window_colors_list)]

            marker_handle = Line2D(
                [0],
                [0],
                marker=mk,
                color="w",  # invisible line
                markerfacecolor=col,
                markeredgecolor="black",
                markeredgewidth=0.8,
                markersize=10,
                linestyle="None",
                label=lbl,
            )
            legend_handles.append(marker_handle)

        ax_scat.legend(
            handles=legend_handles,
            title="Period",
            frameon=True,
            fontsize=16,  # Controls the labels
            title_fontsize=16,  # Controls the title "Window"
            loc="best",
        )

        fig_scat.tight_layout()
        fname = output_dir / f"{tech}_scatter_cluster_overlay_window.png"
        fig_scat.savefig(fname, dpi=1000)
        plt.close(fig_scat)
        print(f"✔ Scatter with SMART LABELS saved for {tech}")


def plot_cluster_flow(df_with_clusters, tech, output_dir="plots/cluster_flows"):
    """
    Create a Sankey-style cluster flow diagram across years.
    - Cluster nodes: white boxes with black outlines and names.
    - Flows: colored based on first-year cluster assignment.
    - Cluster names are dynamic per year based on Remanufacturing capacity.
    - Colors remain consistent across all years from original (first-year) clusters.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df_tech = df_with_clusters[df_with_clusters["tech"] == tech].copy()
    df_tech["combo"] = (
        df_tech["learning_rate"].astype(str) + "_" + df_tech["scenario"].astype(str)
    )
    years = sorted(df_tech["year"].unique())

    # --------------------------------------------------
    # Fixed color mapping from first-year clusters
    # --------------------------------------------------
    first_year = years[0]
    first_clusters = (
        df_tech[df_tech["year"] == first_year]
        .groupby("cluster_id")["Remanufacturing"]
        .mean()
        .sort_values(ascending=False)
    )
    cluster_order = list(first_clusters.index)
    base_colors = [
        "#636EFA",
        "#EF553B",
        "#00CC96",
        "#AB63FA",
        "#FFA15A",
        "#19D3F3",
        "#FF6692",
        "#B6E880",
    ]
    cluster_colors = {
        cid: base_colors[i % len(base_colors)] for i, cid in enumerate(cluster_order)
    }

    # --------------------------------------------------
    # Assign color based on *first-year* cluster of each combo
    # --------------------------------------------------
    combo_to_first_cluster = (
        df_tech[df_tech["year"] == first_year][["combo", "cluster_id"]]
        .set_index("combo")["cluster_id"]
        .to_dict()
    )

    df_tech["origin_cluster"] = df_tech["combo"].map(combo_to_first_cluster)
    df_tech["origin_color"] = df_tech["origin_cluster"].map(cluster_colors)

    # --------------------------------------------------
    # Dynamic cluster names per year based on Remanufacturing
    # --------------------------------------------------
    year_cluster_names = {}
    for year in years:
        clusters_sorted = (
            df_tech[df_tech["year"] == year]
            .groupby("cluster_id")["Remanufacturing"]
            .mean()
            .sort_values(ascending=False)
        )
        year_cluster_names[year] = {
            cid: f"Cluster {i + 1}" for i, cid in enumerate(clusters_sorted.index)
        }

    # --------------------------------------------------
    # Build flow data (color stays from origin)
    # --------------------------------------------------
    flows = []
    for i in range(len(years) - 1):
        year_from = years[i]
        year_to = years[i + 1]
        df_from = df_tech[df_tech["year"] == year_from][
            ["combo", "cluster_id", "origin_color"]
        ]
        df_to = df_tech[df_tech["year"] == year_to][["combo", "cluster_id"]]

        merged = df_from.merge(df_to, on="combo", suffixes=("_from", "_to"))
        grouped = (
            merged.groupby(["cluster_id_from", "cluster_id_to", "origin_color"])
            .size()
            .reset_index(name="count")
        )

        for _, row in grouped.iterrows():
            flows.append(
                {
                    "source": f"{year_cluster_names[year_from][row['cluster_id_from']]}_{year_from}",
                    "target": f"{year_cluster_names[year_to][row['cluster_id_to']]}_{year_to}",
                    "value": row["count"],
                    "color": row["origin_color"],
                }
            )

    # --------------------------------------------------
    # Build nodes (white boxes)
    # --------------------------------------------------
    nodes = []
    node_set = set()
    for f in flows:
        for n in [f["source"], f["target"]]:
            if n not in node_set:
                nodes.append(n)
                node_set.add(n)
    node_indices = {n: i for i, n in enumerate(nodes)}

    # --------------------------------------------------
    # Sankey Diagram
    # --------------------------------------------------
    fig = go.Figure(
        go.Sankey(
            node=dict(
                label=nodes,
                color="white",  # white boxes
                line=dict(color="black", width=1),  # black outlines
            ),
            link=dict(
                source=[node_indices[f["source"]] for f in flows],
                target=[node_indices[f["target"]] for f in flows],
                value=[f["value"] for f in flows],
                color=[f["color"] for f in flows],
            ),
        )
    )

    fig.update_layout(title_text=f"Cluster Flow for {tech}", font_size=10)
    fig.write_html(output_dir / f"{tech}_cluster_flow.html")


def plot_all_cluster_flows(df_with_clusters, output_dir="plots/cluster_flows"):
    """
    Plot Sankey diagrams for cluster transitions for all technologies in df_with_clusters.

    Parameters
    ----------
    df_with_clusters : pd.DataFrame
        Must contain columns: ['tech', 'year', 'learning_rate', 'scenario', 'cluster_id']
    output_dir : str
        Folder to save Sankey diagrams
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for tech in df_with_clusters["tech"].unique():
        print(f"📊 Generating cluster flow for {tech}...")
        plot_cluster_flow(df_with_clusters, tech=tech, output_dir=output_dir)


def calculate_and_plot_cost_bars(
    base_path,
    nzia_scenarios_dict,
    start_year=2024,
    end_year=2040,
    output_dir="plots/costs",
):
    """
    1. Calculates ANNUAL total costs (sum per year) for Base and all Scenarios.
    2. Computes annual % deviation vs Base for every year.
    3. Plots a Grouped Bar Chart over TIME (Min vs Max deviation per Year).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"--- Processing Costs Over Time ({start_year}-{end_year}) ---")

    years = range(start_year, end_year + 1)

    # --- Helper: Load Annual Costs ---
    def get_yearly_costs(file_path):
        if not file_path.exists():
            return None
        try:
            df = pd.read_excel(file_path, sheet_name="extension_cost")
            # Filter for relevant years first
            df = df[df["stf"].isin(years)]
            # Group by year ('stf') and sum 'Total_Cost'
            yearly_sums = df.groupby("stf")["Total_Cost"].sum()
            # Reindex to ensure all years in range are present (fill missing with 0)
            return yearly_sums.reindex(years, fill_value=0)
        except Exception as e:
            # print(f"Warning reading {file_path.name}: {e}")
            return None

    # 1. Load Base Cost Series
    base_cost_series = get_yearly_costs(base_path)
    if base_cost_series is None or base_cost_series.sum() == 0:
        print("❌ Critical: Base cost not found or zero.")
        return

    print("Base Scenario loaded.")

    # 2. Calculate Annual Deviations for all scenarios
    # Structure: {year: [dev_scen1, dev_scen2, ...]}
    yearly_deviations = {y: [] for y in years}

    for (lr, scen_name), path in nzia_scenarios_dict.items():
        scen_costs = get_yearly_costs(path)
        if scen_costs is not None:
            # Calculate % deviation for each year
            for y in years:
                base_val = base_cost_series.loc[y]
                scen_val = scen_costs.loc[y]

                # Avoid division by zero if base cost is 0 for a specific year
                if base_val != 0:
                    pct_diff = ((scen_val - base_val) / base_val) * 100
                    yearly_deviations[y].append(pct_diff)

    # 3. Aggregate Min/Max per Year across ALL scenarios
    min_vals = []
    max_vals = []
    valid_years = []

    for y in years:
        devs = yearly_deviations[y]
        if devs:
            min_vals.append(min(devs))
            max_vals.append(max(devs))
            valid_years.append(y)

    if not valid_years:
        print("No valid deviation data found.")
        return

    # -------------------------------
    # 3. PLOTTING (Tracer Style Sizes)
    # -------------------------------

    # Local Font Sizes matching the tracer plots
    FS_AXIS = 20
    FS_TICK = 20
    FS_LEGEND = 20
    FS_BAR_LABEL = 16  # Increased size for visibility (was 12)

    # Increased figsize to accommodate larger fonts
    fig, ax = plt.subplots(figsize=(14, 7))

    x = np.array(valid_years)
    width = 0.4

    # Plot grouped bars (Years on X-axis)
    # Min Deviation
    ax.bar(
        x - width / 2,
        min_vals,
        width=width,
        label="Minimum deviation",
        color="#67B2D8",
        zorder=2,
    )
    # Max Deviation
    ax.bar(
        x + width / 2,
        max_vals,
        width=width,
        label="Maximum deviation",
        color="#E67E22",
        zorder=2,
    )

    # Add labels on top of bars
    for rects in ax.containers:
        # padding=4 moves it up slightly to avoid overlap with bar edge
        ax.bar_label(
            rects, padding=4, fontsize=FS_BAR_LABEL, fmt="%.1f%%", weight="bold"
        )

    # Styling
    ax.grid(axis="y", linestyle=":", color="0.8", linewidth=0.8, zorder=-2)

    # Updated Tick Params
    ax.tick_params(axis="x", labelsize=FS_TICK)
    ax.tick_params(axis="y", labelsize=FS_TICK)

    # Updated Labels
    ax.set_ylabel("Total Cost Deviation from Base (%)", fontsize=FS_AXIS)
    ax.set_xlabel("Year", fontsize=FS_AXIS)

    # Set X-Ticks to Requested Years only
    major_ticks = [2025, 2030, 2035, 2040]
    # Filter to ensure we only set ticks for years that actually exist in the data
    actual_ticks = [y for y in major_ticks if y in valid_years]
    ax.set_xticks(actual_ticks)

    # Legend Styling
    leg = ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.0, 1.15),
        ncol=2,
        frameon=True,
        handlelength=1.25,
        handletextpad=0.5,
        fontsize=FS_LEGEND,
    )
    leg._legend_box.align = "left"
    leg.get_frame().set_edgecolor("black")

    # Add a horizontal line at 0 for clarity
    ax.axhline(0, color="black", linewidth=1, zorder=1)

    plt.tight_layout()

    save_path = output_dir / "Annual_Cost_Deviation_Range.png"
    fig.savefig(save_path, dpi=400, bbox_inches="tight")
    print(f"✔ Plot saved to: {save_path}")


def calculate_and_plot_cost_bars_range(
    base_path,
    nzia_scenarios_dict,
    start_year=2024,
    end_year=2040,
    output_dir="plots/costs",
):
    """
    1. Calculates ANNUAL total costs (sum per year) for Base and all Scenarios.
    2. Computes annual % deviation vs Base for every year.
    3. Plots a Range Plot (Line Chart with Shaded Area) over TIME.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"--- Processing Costs Over Time ({start_year}-{end_year}) ---")

    years = range(start_year, end_year + 1)

    # --- Helper: Load Annual Costs ---
    def get_yearly_costs(file_path):
        if not file_path.exists():
            return None
        try:
            df = pd.read_excel(file_path, sheet_name="extension_cost")
            # Filter for relevant years first
            df = df[df["stf"].isin(years)]
            # Group by year ('stf') and sum 'Total_Cost'
            yearly_sums = df.groupby("stf")["Total_Cost"].sum()
            # Reindex to ensure all years in range are present (fill missing with 0)
            return yearly_sums.reindex(years, fill_value=0)
        except Exception as e:
            # print(f"Warning reading {file_path.name}: {e}")
            return None

    # 1. Load Base Cost Series
    base_cost_series = get_yearly_costs(base_path)
    if base_cost_series is None or base_cost_series.sum() == 0:
        print("❌ Critical: Base cost not found or zero.")
        return

    print("Base Scenario loaded.")

    # 2. Calculate Annual Deviations for all scenarios
    # Structure: {year: [dev_scen1, dev_scen2, ...]}
    yearly_deviations = {y: [] for y in years}

    for (lr, scen_name), path in nzia_scenarios_dict.items():
        scen_costs = get_yearly_costs(path)
        if scen_costs is not None:
            # Calculate % deviation for each year
            for y in years:
                base_val = base_cost_series.loc[y]
                scen_val = scen_costs.loc[y]

                # Avoid division by zero if base cost is 0 for a specific year
                if base_val != 0:
                    pct_diff = ((scen_val - base_val) / base_val) * 100
                    yearly_deviations[y].append(pct_diff)

    # 3. Aggregate Min/Max per Year across ALL scenarios
    min_vals = []
    max_vals = []
    valid_years = []

    for y in years:
        devs = yearly_deviations[y]
        if devs:
            min_vals.append(min(devs))
            max_vals.append(max(devs))
            valid_years.append(y)

    if not valid_years:
        print("No valid deviation data found.")
        return

    # -------------------------------
    # 3. PLOTTING (Range/Line Plot)
    # -------------------------------

    FS_AXIS = 20
    FS_TICK = 20
    FS_LEGEND = 20
    FS_LABEL = 16  # Font size for annotations

    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.array(valid_years)

    # Fill Between (The Range)
    # This creates the shaded corridor between min and max
    ax.fill_between(
        x, min_vals, max_vals, color="#BDC3C7", alpha=0.3, label="Deviation Range"
    )

    # Plot Lines for Min and Max edges
    ax.plot(
        x,
        min_vals,
        color="#67B2D8",
        linewidth=3,
        marker="o",
        markersize=8,
        label="Minimum deviation",
    )
    ax.plot(
        x,
        max_vals,
        color="#E67E22",
        linewidth=3,
        marker="o",
        markersize=8,
        label="Maximum deviation",
    )

    # Add text labels for SPECIFIC major years only (to avoid clutter)
    label_years = [2025, 2030, 2035, 2040]

    for i, year in enumerate(valid_years):
        if year in label_years:
            # Min Label (Placed slightly below point)
            ax.annotate(
                f"{min_vals[i]:.1f}%",
                (year, min_vals[i]),
                xytext=(0, -20),
                textcoords="offset points",
                ha="center",
                va="top",
                fontsize=FS_LABEL,
                color="#2980B9",
                weight="bold",
            )

            # Max Label (Placed slightly above point)
            ax.annotate(
                f"{max_vals[i]:.1f}%",
                (year, max_vals[i]),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=FS_LABEL,
                color="#D35400",
                weight="bold",
            )

    # Styling
    ax.grid(axis="y", linestyle=":", color="0.8", linewidth=0.8, zorder=-2)

    # Tick Parameters
    ax.tick_params(axis="x", labelsize=FS_TICK)
    ax.tick_params(axis="y", labelsize=FS_TICK)

    # Labels
    ax.set_ylabel("Total Cost Deviation from Base (%)", fontsize=FS_AXIS)
    ax.set_xlabel("Year", fontsize=FS_AXIS)

    # Set X-Ticks to Requested Years only
    major_ticks = [2025, 2030, 2035, 2040]
    actual_ticks = [y for y in major_ticks if y in valid_years]
    ax.set_xticks(actual_ticks)

    # Ensure Y-Axis extends to at least -10% if requested
    bottom, top = ax.get_ylim()
    if bottom > -10:
        ax.set_ylim(bottom=-10.5)

    # Legend
    leg = ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.0, 1.15),
        ncol=3,
        frameon=True,
        handlelength=1.25,
        handletextpad=0.5,
        fontsize=FS_LEGEND,
    )
    leg._legend_box.align = "left"
    leg.get_frame().set_edgecolor("black")

    # Zero Line
    ax.axhline(0, color="black", linewidth=1, zorder=1)

    plt.tight_layout()

    save_path = output_dir / "Annual_Cost_Deviation_Range.png"
    fig.savefig(save_path, dpi=400, bbox_inches="tight")
    print(f"✔ Plot saved to: {save_path}")


# -------------------------------
# Main Execution
# -------------------------------

tech_list = ["solarPV", "windon", "windoff", "Batteries"]


def run_all_analyses():
    """Run all analyses automatically"""
    print("🚀 Starting automated analysis...")

    # Build scenario dictionaries
    nzia_scenarios = build_scenario_dict()
    base_file = get_base_scenario()

    print(f"📁 Base scenario: {base_file}")
    print(f"📁 NZIA scenarios: {len(nzia_scenarios)} files")

    # Run analyses
    # calculate_and_plot_cost_bars_range(base_file,nzia_scenarios)
    # plot_base_generation_mix(base_file) #JA Stand 2. Dez
    # plot_renewables_breakdown_100pct(base_file) #JA Stand 2. Dez
    # plot_renewables_installed_capacity_vertical(base_file) #JA Stand 2. Dez
    # plot_scrap_comparison(base_file, nzia_scenarios)
    # plot_lng_analysis(base_file, nzia_scenarios)
    # export_lng_data(base_file, nzia_scenarios)
    # plot_system_costs_boxplot(base_file, nzia_scenarios)
    # plot_nzia_boxplots(
    #    tech_list=tech_list,
    #    nzia_scenarios_dict=nzia_scenarios,
    #    target_years=[2025, 2030, 2035, 2040],
    #    output_dir="plots/nzia_plots",
    # )
    # plot_window_scatter_relative_single(tech_list=tech_list,
    #    nzia_scenarios_dict=nzia_scenarios)

    # plot_window_capacity_scatter( #JA
    #    tech_list=tech_list,
    #    nzia_scenarios_dict=nzia_scenarios,
    #    perform_clustering=True,  # enable clustering
    #    eps=0.25,  # tune sensitivity
    #    min_samples=10
    # )
    plot_cumulative_capacity_scatter(  # JA Stand 2. Dez für Tracers
        tech_list=tech_list,
        nzia_scenarios_dict=nzia_scenarios,
        perform_clustering=True,  # enable clustering
        eps=0.3,  # tune sensitivity
        min_samples=5,
    )
    # create_cumulative_capacity_csv_with_stats(
    #    nzia_scenarios_dict=nzia_scenarios,
    #    target_years=[2030, 2040],
    #    techs=["solarPV", "windon", "windoff"],
    #    output_csv="nzia_cumulative_totalcapacity.csv"
    # )
    # plot_capacity_violin_per_tech() #JA Stand 2. Dez

    print("✅ All analyses completed!")


if __name__ == "__main__":
    run_all_analyses()
