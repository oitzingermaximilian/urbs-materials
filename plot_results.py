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

# -------------------------------
# Configuration
# -------------------------------
BASE_PATH = Path("C:/Users/maxoi/OneDrive/Desktop/results_crm_paper/base")
NZIA_PATH = Path("C:/Users/maxoi/OneDrive/Desktop/results_crm_paper/NZIA")
LNG_LOWEST_PATH = Path("C:/Users/maxoi/OneDrive/Desktop/results_crm_paper/lng_lowest")

LR_FOLDERS = ["LR1", "LR3_5", "LR4", "LR5", "LR6", "LR7", "LR8", "LR9", "LR10"]

SCENARIO_NAMES = [
    "scenario_min_min_min", "scenario_min_min_avg", "scenario_min_min_high",
    "scenario_min_avg_min", "scenario_min_avg_avg", "scenario_min_avg_high",
    "scenario_min_high_min", "scenario_min_high_avg", "scenario_min_high_high",
    "scenario_avg_min_min", "scenario_avg_min_avg", "scenario_avg_min_high",
    "scenario_avg_avg_min", "scenario_avg_avg_avg", "scenario_avg_avg_high",
    "scenario_avg_high_min", "scenario_avg_high_avg", "scenario_avg_high_high",
    "scenario_high_min_min", "scenario_high_min_avg", "scenario_high_min_high",
    "scenario_high_avg_min", "scenario_high_avg_avg", "scenario_high_avg_high",
    "scenario_high_high_min", "scenario_high_high_avg", "scenario_high_high_high",
]

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


def load_generation_data(file_path, sheet_name="extension_balance", years=range(2025, 2041)):
    """Load generation data from Excel file"""
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df[df["Stf"].isin(years)]


def load_scrap_data(file_path, sheet_name="scrap", years=range(2024, 2041)):
    """Load scrap data from Excel file"""
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Handle column name variations
    year_col = next((col for col in ["stf", "Stf", "year", "Year"] if col in df.columns), None)
    tech_col = next((col for col in ["tech", "Tech", "key_1", "key1", "technology", "Process","pro"] if col in df.columns),
                    None)
    value_col = next((col for col in ["capacity_scrap_total", "value", "capacity_scrap", "capacity_scrap_tonnes"] if
                      col in df.columns), None)

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

def identify_capacity_clusters(df, eps=0.7, min_samples=4):
    """
    Identify DBSCAN clusters in a given DataFrame (single tech).
    Groups by year and clusters using Manufacturing + Remanufacturing.
    Returns summary and full DataFrame with cluster_id.
    """
    cluster_summary = []
    clustered_dfs = []

    for year, df_group in df.groupby("year"):
        if len(df_group) < min_samples:
            cluster_summary.append({
                "year": year,
                "num_clusters": 0,
                "num_points": len(df_group),
                "note": "too few points"
            })
            continue

        X = df_group[["Remanufacturing", "Manufacturing"]].values
        X_scaled = StandardScaler().fit_transform(X)

        db = DBSCAN(eps=eps, min_samples=min_samples)
        labels = db.fit_predict(X_scaled)

        df_group = df_group.copy()
        df_group["cluster_id"] = labels
        clustered_dfs.append(df_group)

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        cluster_summary.append({
            "year": year,
            "num_clusters": n_clusters,
            "num_points": len(df_group),
            "noise_points": np.sum(labels == -1)
        })

    df_summary = pd.DataFrame(cluster_summary)
    df_with_clusters = pd.concat(clustered_dfs, ignore_index=True) if clustered_dfs else pd.DataFrame()
    return df_summary, df_with_clusters
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
            value = year_df[year_df["Process"].isin(processes)]["Value"].sum() / 1_000_000  # Convert to TWh
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
            wedgeprops=dict(width=0.4, edgecolor="w")
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
        totals = {g: year_df[year_df["Process"].isin(GROUPS[g])]["Value"].sum() for g in group_order}
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
        ax.barh(y_pos, width, left=left, height=bar_height, color=GROUP_COLORS[g],
                edgecolor="white", linewidth=1.2, zorder=5)
        left += width

    ax.set_yticks(y_pos, [str(y) for y in years])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
    ax.xaxis.set_ticks_position("top")

    ax.vlines(np.arange(0, 101, 10), -0.5, n - 0.5, colors="white", linewidth=1.5, zorder=7)
    ax.set_facecolor("#E6E6E6")

    ax.set_title("Base Scenario Generation Share by Year (%)", loc="left",
                 fontsize=18, fontweight="bold", color="#1F4E79")

    handles = [plt.Rectangle((0, 0), 1, 1, color=GROUP_COLORS[g]) for g in group_order]
    ax.legend(handles, group_order, loc="upper center", bbox_to_anchor=(0.5, -0.06),
              ncol=len(group_order), frameon=False, fontsize=11)

    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.94])
    output_path = Path(output_dir) / "base_generation_share_100pct.png"
    plt.savefig(output_path, dpi=300)
    plt.show()
    print(f"✔ Base scenario stacked bar chart saved → {output_path}")


def plot_scrap_comparison(base_file=None, nzia_scenarios_dict=None, output_dir="plots/scrap_range"):
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

        grouped = df.groupby([year_col, tech_col], as_index=True)[value_col].sum().reset_index()
        pivot = grouped.pivot(index=year_col, columns=tech_col, values=value_col).fillna(0)
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
        base_series = base_pivot[tech].reindex(years).fillna(0) if tech in base_pivot.columns else pd.Series(0.0,
                                                                                                             index=years)

        # NZIA series
        nzia_series_list = []
        for p in nzia_pivots:
            s = p[tech].reindex(years).fillna(0) if tech in p.columns else pd.Series(0.0, index=years)
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
        ax.plot(years, base_series.values, color="darkred", linewidth=2.2, label="Base scenario")
        ax.fill_between(years, nz_min.values, nz_max.values, color="seagreen", alpha=0.25, label="NZIA min–max range")
        ax.plot(years, nz_mean.values, color="seagreen", linestyle="--", linewidth=1.5, label="NZIA mean")

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


def plot_lng_analysis(base_file=None, nzia_scenarios_dict=None, lng_file = None, output_dir="plots/lng_analysis"):
    """Comprehensive LNG analysis with multiple plot types"""
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

    # 1. Spaghetti plot
    plt.figure(figsize=(8, 5))
    for f in nzia_files:
        series = load_lng(f, years)
        plt.plot(series.index, series.values, color="grey", alpha=0.3, linewidth=1)

    base_series = load_lng(base_file, years)
    best_case_series = load_lng(lng_file, years)
    plt.plot(best_case_series.index, best_case_series.values, color="red",linewidth=2.5, label="Best Case scenario")
    plt.plot(base_series.index, base_series.values, color="lightsteelblue",
             linewidth=2.5, label="Base scenario")

    plt.xlabel("Year")
    plt.ylabel("LNG Demand [BCM]")
    plt.title("LNG Demand – NZIA scenarios")
    plt.xlim(min(years) - 1, max(years) + 1)
    plt.xticks([2025, 2030, 2035, 2040])
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()
    plt.savefig(out_path / "lng_spaghetti.png", dpi=300)
    plt.show()
    print("✔ LNG spaghetti plot saved")

    # 2. Cumulative percentage deviation boxplot
    base_cumulative = load_lng(base_file, years).cumsum()
    nzia_cumulative = [load_lng(f, years).cumsum() for f in nzia_files]

    data = pd.DataFrame({i: s for i, s in enumerate(nzia_cumulative)}).T
    pct_dev = pd.DataFrame({
        y: 100 * (data[y] - base_cumulative[y]) / base_cumulative[y] for y in target_years
    })

    plt.figure(figsize=(8, 5))

    # Use 0,1,2,... for positions and then relabel
    positions = np.arange(len(target_years))
    box_data = [pct_dev[y].dropna() for y in target_years]

    # Make narrower boxes
    bp = plt.boxplot(box_data, positions=positions, widths=0.2, patch_artist=True,
                     boxprops=dict(facecolor="lightsteelblue", alpha=0.6, linewidth=1.2),
                     medianprops=dict(color="darkblue", linewidth=2),
                     whiskerprops=dict(color="grey", linestyle="--", linewidth=1.2),
                     capprops=dict(color="grey", linewidth=1.2))

    # Optional scatter points for individual scenario deviations
    # for i, year in enumerate(target_years):
    #     y_vals = pct_dev[year].dropna().values
    #     x_vals = positions[i] + 0.08 * (np.random.rand() - 0.5)
    #     plt.scatter(x_vals, y_vals, color="grey", alpha=0.6, s=30, zorder=3)

    #plt.axhline(0, color="lightsteelblue", linewidth=2.5, linestyle="-", label="Base scenario")
    plt.title("Cumulative LNG Demand – Compared to current Policies", fontsize=14, weight="bold")
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Deviation from Base [%]", fontsize=12)
    plt.xticks(positions, target_years, fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.legend(frameon=False, fontsize=11)

    # Add margins to avoid touching edges
    plt.margins(x=0.1)  # 10% horizontal margin
    plt.tight_layout()
    plt.savefig(out_path / "lng_cumulative_pct_deviation.png", dpi=300)
    plt.show()
    print("✔ LNG cumulative deviation plot saved")


def plot_system_costs_boxplot(base_file=None, nzia_scenarios_dict=None, output_dir="plots/system_costs"):
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
    base_yearly = [base_costs.get(y, 0)/1e9 for y in years]  # Convert to bn€

    # Load NZIA costs
    nzia_data = []
    for scenario_name, file_path in nzia_scenarios_dict.items():
        if file_path.exists():
            costs = load_system_costs(file_path)
            yearly_bn = [costs.get(y, 0)/1e9 for y in years]  # Convert to bn€
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
        boxprops=dict(facecolor='lightblue', color='blue'),
        medianprops=dict(color='darkblue')
    )

    # Overlay Base scenario as a line
    plt.plot(range(1, len(years)+1), base_yearly, 'r-', linewidth=2.5, label='Base Scenario')

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
        output_dir="plots/nzia_boxplots"
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
    components = ["Manufacturing", "Remanufacturing", "Stockpile Out"]  # original column names
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
                    df_tech = pd.concat([df_tech, pd.DataFrame([{
                        "tech": tech_name,
                        "stf": year,
                        "location": df_tech["location"].iloc[-1] if "location" in df_tech.columns else None,
                        "capacity_ext_eusecondary": 0,
                        "capacity_ext_stockout": 0,
                        "capacity_ext_euprimary": 0
                    }])], ignore_index=True)

            df_tech = df_tech.sort_values("stf")
            df_tech["cum_eusecondary"] = df_tech["capacity_ext_eusecondary"].cumsum()
            df_tech["cum_stockout"] = df_tech["capacity_ext_stockout"].cumsum()
            df_tech["cum_euprimary"] = df_tech["capacity_ext_euprimary"].cumsum()

            for year in target_years:
                row = df_tech[df_tech["stf"] == year]
                all_data_yearly.append({
                    "year": year,
                    "scenario": scenario_name,
                    "Manufacturing": row["capacity_ext_euprimary"].sum() / 1e3,
                    "Remanufacturing": row["capacity_ext_eusecondary"].sum() / 1e3,
                    "Stockpile Out": row["capacity_ext_stockout"].sum() / 1e3
                })
                all_data_cumulative.append({
                    "year": year,
                    "scenario": scenario_name,
                    "Manufacturing": row["cum_euprimary"].sum() / 1e3,
                    "Remanufacturing": row["cum_eusecondary"].sum() / 1e3,
                    "Stockpile Out": row["cum_stockout"].sum() / 1e3
                })

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
                data = [df_plot[df_plot["year"] == year][comp].values for year in target_years]
                pos = positions + (i - 1) * box_width  # shift each component
                bp = plt.boxplot(data, positions=pos, widths=box_width, patch_artist=True,
                                 boxprops=dict(facecolor=colors[i], alpha=0.7, linewidth=1.2),
                                 medianprops=dict(color='black', linewidth=2),
                                 whiskerprops=dict(color='grey', linestyle='--', linewidth=1.2),
                                 capprops=dict(color='grey', linewidth=1.2))

            plt.xticks(positions, target_years)
            plt.xlabel("Year")
            plt.ylabel("Capacity Additions (GW)")
            plt.title(f"{title} for {tech_name}")
            plt.grid(axis="y", linestyle="--", alpha=0.3)

            # Legend with black outline and padding
            for i, comp_name in enumerate(components_legend):
                plt.plot([], color=colors[i], label=comp_name, linewidth=4)  # smaller width
            plt.legend(frameon=True, edgecolor='black', borderpad=0.5, labelspacing=0.5)

            plt.tight_layout()
            plt.savefig(output_dir / filename, dpi=300)
            plt.show()

        plot_grouped_boxplot(df_yearly, "Yearly Capacity Additions", f"{tech_name}_yearly_boxplot.png")
        plot_grouped_boxplot(df_cum, "Cumulative Capacity Additions", f"{tech_name}_cumulative_boxplot.png")



def plot_cumulative_capacity_scatter(
    tech_list,
    nzia_scenarios_dict,
    target_years=[2025, 2030, 2035, 2040],
    output_dir="plots/cumulative_scatter",
    save_csv=True,
    perform_clustering=True,
    eps=0.7,
    min_samples=4
):
    """
    Scatter plot of cumulative capacities:
    - X-axis: Remanufacturing
    - Y-axis: Manufacturing
    - Different colors for each target year
    - Optional tracer lines connecting the same scenario over time
    - Optional DBSCAN clustering (used only for benchmarking, not plotted)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # RGB color palette for years
    year_colors = {
        2025: (223 / 255, 221 / 255, 25 / 255),
        2030: (239 / 255, 119 / 255, 72 / 255),
        2035: (231 / 255, 35 / 255, 133 / 255),
        2040: (91 / 255, 47 / 255, 104 / 255),
    }

    for tech_name in tech_list:
        all_data = []

        # -----------------------------
        # Load and process NZIA files
        # -----------------------------
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

            df_tech = df_tech.sort_values("stf")
            df_tech["cum_eusecondary"] = df_tech["capacity_ext_eusecondary"].cumsum()
            df_tech["cum_stockout"] = df_tech["capacity_ext_stockout"].cumsum()
            df_tech["cum_euprimary"] = df_tech["capacity_ext_euprimary"].cumsum()
            df_tech["cum_newly_added_capacity"] = df_tech["newly_added_capacity"].cumsum()

            for year in target_years:
                row = df_tech[df_tech["stf"] == year]
                all_data.append({
                    "tech": tech_name,
                    "year": year,
                    "learning_rate": lr,
                    "scenario": scenario_name,
                    "Remanufacturing": row["cum_eusecondary"].sum() / 1e3,
                    "Manufacturing": row["cum_euprimary"].sum() / 1e3,
                    "Stockpile": row["cum_stockout"].sum() / 1e3,
                    "Totals (incl. Imports)": row["cum_newly_added_capacity"].sum() / 1e3
                })

        if not all_data:
            print(f"No data for {tech_name}. Skipping.")
            continue

        df_all = pd.DataFrame(all_data)

        # -----------------------------
        # Save CSV if requested
        # -----------------------------
        if save_csv:
            csv_path = Path(output_dir) / f"cumulative_data_{tech_name}.csv"
            df_all.to_csv(csv_path, index=False)
            print(f"✔ Data exported for {tech_name}: {csv_path}")

        # -----------------------------
        # Simple scatter (points only)
        # -----------------------------
        plt.figure(figsize=(8, 6))
        for year in target_years:
            subset = df_all[df_all["year"] == year]
            plt.scatter(
                subset["Remanufacturing"], subset["Manufacturing"],
                color=year_colors[year],
                s=50,
                label=str(year)
            )

        plt.xlabel("Remanufacturing Capacity (GW)")
        plt.ylabel("Manufacturing Capacity (GW)")
        plt.title(f"Cumulative Capacity for {tech_name}")
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.legend(title="Year", frameon=True, edgecolor='black')
        plt.tight_layout()
        fig_path = Path(output_dir) / f"cumulative_scatter_points_{tech_name}.png"
        plt.savefig(fig_path, dpi=300)
        plt.show()
        print(f"✔ Simple scatter plot saved for {tech_name}: {fig_path}")

        # -----------------------------
        # Scatter with tracers (lines connecting scenarios)
        # -----------------------------
        plt.figure(figsize=(8, 6))
        for (lr, scenario_name), group_df in df_all.groupby(['learning_rate', 'scenario']):
            group_df = group_df.sort_values('year')
            plt.plot(
                group_df['Remanufacturing'], group_df['Manufacturing'],
                color='gray', alpha=0.3, linestyle='--', zorder=1
            )
            for year in target_years:
                point = group_df[group_df['year'] == year]
                if not point.empty:
                    plt.scatter(
                        point['Remanufacturing'], point['Manufacturing'],
                        color=year_colors[year],
                        s=50,
                        label=str(year) if f"{year}" not in plt.gca().get_legend_handles_labels()[1] else None,
                        zorder=2
                    )

        plt.xlabel("Remanufacturing Capacity (GW)")
        plt.ylabel("Manufacturing Capacity (GW)")
        plt.title(f"Cumulative Capacity with Tracers for {tech_name}")
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.legend(title="Year", frameon=True, edgecolor='black')
        plt.tight_layout()
        fig_path = Path(output_dir) / f"cumulative_scatter_tracer_{tech_name}.png"
        plt.savefig(fig_path, dpi=300)
        plt.show()
        print(f"✔ Scatter + tracer plot saved for {tech_name}: {fig_path}")

        # -----------------------------
        # Run clustering if requested (used for benchmarking only)
        # -----------------------------
        if perform_clustering:
            df_summary, df_with_clusters = identify_capacity_clusters(
                df_all, eps=eps, min_samples=min_samples
            )
            cluster_dir = output_dir / "clusters"
            cluster_dir.mkdir(exist_ok=True)
            df_summary.to_csv(cluster_dir / f"cluster_summary_{tech_name}.csv", index=False)
            df_with_clusters.to_csv(cluster_dir / f"clustered_data_{tech_name}.csv", index=False)
            print(f"✅ Clustering done for {tech_name}. Results saved in {cluster_dir}")

            # Plot clustered benchmark & flows
            plot_clustered_benchmark_from_df(df_with_clusters, output_dir="plots/clustered_benchmark")
            #plot_all_cluster_flows(df_with_clusters)




def plot_clustered_benchmark_from_df(df_with_clusters, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    components = ["Remanufacturing", "Stockpile", "Manufacturing"]
    labels = ["Remanufacturing", "Stock", "Manufacturing"]
    colors = ["#FDC5B5", "#F99B7D", "#F76C5E"]
    hatches = ["..", "//", "xx"]

    for tech in df_with_clusters["tech"].unique():
        df_tech = df_with_clusters[df_with_clusters["tech"] == tech].copy()
        years = sorted(df_tech["year"].unique())
        x_base = np.arange(len(years))

        # --- Determine global max cluster count ---
        max_clusters = max(df_tech.groupby("year")["cluster_id"].nunique())

        total_width = 0.8     # width of the full "year group"
        gap = 0.02            # small visible gap between bars
        width = (total_width - (max_clusters - 1) * gap) / max_clusters

        # =====================================================
        # RELATIVE PLOT
        # =====================================================
        fig_rel, ax_rel = plt.subplots(figsize=(11, 6))

        for i, year in enumerate(years):
            df_year = df_tech[df_tech["year"] == year]
            clusters_this_year = sorted(df_year["cluster_id"].unique())
            n_clusters = len(clusters_this_year)

            # Compute leftmost offset so group is centered
            group_width = n_clusters * width + (n_clusters - 1) * gap
            start_offset = -group_width / 2 + width / 2

            for j, cluster in enumerate(clusters_this_year):
                df_cluster = df_year[df_year["cluster_id"] == cluster]
                row = df_cluster[
                    ["Remanufacturing", "Stockpile", "Manufacturing", "Totals (incl. Imports)"]
                ].mean()

                x_pos = x_base[i] + start_offset + j * (width + gap)
                bottom = 0
                total = row["Totals (incl. Imports)"] if row["Totals (incl. Imports)"] > 0 else 1

                for comp, color, hatch in zip(components, colors, hatches):
                    frac = row[comp] / total
                    ax_rel.bar(
                        x_pos,
                        frac,
                        width=width,
                        bottom=bottom,
                        facecolor=color,
                        edgecolor="black",
                        linewidth=0.8,
                        hatch=hatch,
                    )
                    bottom += frac

                ax_rel.text(x_pos, bottom + 0.02, f"C{int(cluster)}", ha="center", fontsize=8)

        # Benchmark line
        ax_rel.axhline(0.4, color="red", linestyle="--", alpha=0.7, linewidth=2)

        ax_rel.set_xticks(x_base)
        ax_rel.set_xticklabels(years)
        ax_rel.set_ylim(0, 1)
        ax_rel.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{int(y * 100)}%"))
        ax_rel.set_title(f"Clustered Local Sourcing % - {tech}", pad=15)
        ax_rel.set_xlabel("Year")
        ax_rel.set_ylabel("% of Total Capacity Additions")
        ax_rel.grid(axis="y", alpha=0.3)

        legend_patches = [
            mpatches.Patch(facecolor=fc, edgecolor="black", hatch=h, label=lab)
            for fc, h, lab in zip(colors, hatches, labels)
        ]
        nzia_line = plt.Line2D([0], [0], color="red", linestyle="--", linewidth=2, label="NZIA Benchmark")
        ax_rel.legend(handles=legend_patches + [nzia_line], frameon=True, loc="upper right")

        fig_rel.tight_layout()
        fig_rel.savefig(output_dir / f"{tech}_clustered_relative.png", dpi=300)
        plt.close(fig_rel)

        # =====================================================
        # ABSOLUTE PLOT
        # =====================================================
        fig_abs, ax_abs = plt.subplots(figsize=(11, 6))

        for i, year in enumerate(years):
            df_year = df_tech[df_tech["year"] == year]
            clusters_this_year = sorted(df_year["cluster_id"].unique())
            n_clusters = len(clusters_this_year)

            group_width = n_clusters * width + (n_clusters - 1) * gap
            start_offset = -group_width / 2 + width / 2

            for j, cluster in enumerate(clusters_this_year):
                df_cluster = df_year[df_year["cluster_id"] == cluster]
                row = df_cluster[
                    ["Remanufacturing", "Stockpile", "Manufacturing", "Totals (incl. Imports)"]
                ].mean()

                x_pos = x_base[i] + start_offset + j * (width + gap)
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
                        linewidth=0.8,
                        hatch=hatch,
                    )
                    bottom += val

                ax_abs.text(x_pos, bottom + 0.5, f"C{int(cluster)}", ha="center", fontsize=8)

        ax_abs.set_xticks(x_base)
        ax_abs.set_xticklabels(years)
        ax_abs.set_ylabel("Capacity (GW)")
        ax_abs.set_xlabel("Year")
        ax_abs.set_title(f"Clustered Absolute Capacity - {tech}", pad=15)
        ax_abs.grid(axis="y", alpha=0.3)

        legend_patches_abs = [
            mpatches.Patch(facecolor=fc, edgecolor="black", hatch=h, label=lab)
            for fc, h, lab in zip(colors, hatches, labels)
        ]
        ax_abs.legend(handles=legend_patches_abs, frameon=True, loc="upper right")

        fig_abs.tight_layout()
        fig_abs.savefig(output_dir / f"{tech}_clustered_absolute.png", dpi=300)
        plt.close(fig_abs)

        print(f"✔ Clustered bar plots saved for {tech}")

        # =====================================================
        # SCATTER OVERLAY WITH CLUSTER LABELS
        # =====================================================
        fig_scatter, ax_scat = plt.subplots(figsize=(8, 6))
        year_colors = {
            2025: (223 / 255, 221 / 255, 25 / 255),
            2030: (239 / 255, 119 / 255, 72 / 255),
            2035: (231 / 255, 35 / 255, 133 / 255),
            2040: (91 / 255, 47 / 255, 104 / 255),
        }

        for year, subset in df_tech.groupby("year"):
            ax_scat.scatter(
                subset["Remanufacturing"],
                subset["Manufacturing"],
                color=year_colors.get(year, "gray"),
                alpha=0.4,
                label=str(year),
            )

        centroids = (
            df_tech.groupby(["year", "cluster_id"])[["Remanufacturing", "Manufacturing"]]
            .mean()
            .reset_index()
        )

        # Adaptive circle radius based on data scale
        x_range = df_tech["Remanufacturing"].max() - df_tech["Remanufacturing"].min()
        y_range = df_tech["Manufacturing"].max() - df_tech["Manufacturing"].min()
        radius = 0.05 * max(x_range, y_range)  # 5% of max axis span

        for _, row in centroids.iterrows():
            circle = plt.Circle(
                (row["Remanufacturing"], row["Manufacturing"]),
                radius=radius,
                edgecolor="black",
                facecolor="none",
                lw=1.5,
                alpha=0.8,
            )
            ax_scat.add_patch(circle)
            ax_scat.text(
                row["Remanufacturing"],
                row["Manufacturing"],
                f"C{int(row['cluster_id'])}",
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold",
                color="black",
            )

        ax_scat.set_xlabel("Remanufacturing Capacity (GW)")
        ax_scat.set_ylabel("Manufacturing Capacity (GW)")
        ax_scat.set_title(f"Cluster Overview on Scatter - {tech}")
        ax_scat.grid(True, linestyle="--", alpha=0.3)
        ax_scat.legend(title="Year", frameon=True)
        fig_scatter.tight_layout()
        fig_scatter.savefig(output_dir / f"{tech}_scatter_cluster_overlay.png", dpi=300)
        plt.close(fig_scatter)

        print(f"✔ Scatter with cluster overlays saved for {tech}")


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
    df_tech["combo"] = df_tech["learning_rate"].astype(str) + "_" + df_tech["scenario"].astype(str)
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
    base_colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA",
                   "#FFA15A", "#19D3F3", "#FF6692", "#B6E880"]
    cluster_colors = {cid: base_colors[i % len(base_colors)] for i, cid in enumerate(cluster_order)}

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
        year_cluster_names[year] = {cid: f"Cluster {i+1}" for i, cid in enumerate(clusters_sorted.index)}

    # --------------------------------------------------
    # Build flow data (color stays from origin)
    # --------------------------------------------------
    flows = []
    for i in range(len(years) - 1):
        year_from = years[i]
        year_to = years[i + 1]
        df_from = df_tech[df_tech["year"] == year_from][["combo", "cluster_id", "origin_color"]]
        df_to = df_tech[df_tech["year"] == year_to][["combo", "cluster_id"]]

        merged = df_from.merge(df_to, on="combo", suffixes=("_from", "_to"))
        grouped = merged.groupby(["cluster_id_from", "cluster_id_to", "origin_color"]).size().reset_index(name="count")

        for _, row in grouped.iterrows():
            flows.append({
                "source": f"{year_cluster_names[year_from][row['cluster_id_from']]}_{year_from}",
                "target": f"{year_cluster_names[year_to][row['cluster_id_to']]}_{year_to}",
                "value": row["count"],
                "color": row["origin_color"]
            })

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
    fig = go.Figure(go.Sankey(
        node=dict(
            label=nodes,
            color="white",  # white boxes
            line=dict(color="black", width=1)  # black outlines
        ),
        link=dict(
            source=[node_indices[f["source"]] for f in flows],
            target=[node_indices[f["target"]] for f in flows],
            value=[f["value"] for f in flows],
            color=[f["color"] for f in flows]
        )
    ))

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

    for tech in df_with_clusters['tech'].unique():
        print(f"📊 Generating cluster flow for {tech}...")
        plot_cluster_flow(df_with_clusters, tech=tech, output_dir=output_dir)


# -------------------------------
# Main Execution
# -------------------------------

tech_list = ['solarPV', 'windon', 'windoff']

def run_all_analyses():
    """Run all analyses automatically"""
    print("🚀 Starting automated analysis...")

    # Build scenario dictionaries
    nzia_scenarios = build_scenario_dict()
    base_file = get_base_scenario()

    print(f"📁 Base scenario: {base_file}")
    print(f"📁 NZIA scenarios: {len(nzia_scenarios)} files")

    # Run analyses
    #plot_base_generation_mix(base_file)
    #plot_scrap_comparison(base_file, nzia_scenarios)
    #plot_lng_analysis(base_file, nzia_scenarios)
    #plot_system_costs_boxplot(base_file, nzia_scenarios)
    #plot_nzia_boxplots(
    #    tech_list=tech_list,
    #    nzia_scenarios_dict=nzia_scenarios,
    #    target_years=[2025, 2030, 2035, 2040],
    #    output_dir="plots/nzia_plots",
    #)

    plot_cumulative_capacity_scatter(
        tech_list=tech_list,
        nzia_scenarios_dict=nzia_scenarios,
        perform_clustering=True,  # enable clustering
        eps=0.3,  # tune sensitivity
        min_samples=3
    )


    print("✅ All analyses completed!")


if __name__ == "__main__":
    run_all_analyses()