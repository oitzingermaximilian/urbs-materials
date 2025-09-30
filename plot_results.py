import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker as mticker
import numpy as np
from pathlib import Path

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

def plot_scrap_with_nzia_range(base_file: Path, nzia_files: list, sheet_name: str = "Total_Scrap"):
    """
    Plot scrap over time by technology:
    - Base scenario as a solid line
    - NZIA scenarios as a shaded min-max range per technology

    Args:
        base_file: Path to base scenario Excel
        nzia_files: List of Paths to NZIA scenario Excel files
        sheet_name: Name of sheet containing scrap data
    """
    # --- Load base scenario ---
    df_base = pd.read_excel(base_file, sheet_name=sheet_name)
    df_base["value"] = df_base["value"] / 1e6  # convert to Mt
    years = list(range(2024, 2041))
    techs = df_base["key_1"].unique()

    # --- Load NZIA scenarios ---
    nzia_data = {tech: [] for tech in techs}
    for f in nzia_files:
        df = pd.read_excel(f, sheet_name=sheet_name)
        df["value"] = df["value"] / 1e6  # Mt
        for tech in techs:
            tech_df = df[df["key_1"] == tech].set_index("year").sort_index()
            series = tech_df["value"].reindex(years).fillna(0)
            nzia_data[tech].append(series)

    # --- Plot per technology ---
    for tech in techs:
        base_series = df_base[df_base["key_1"] == tech].set_index("year").reindex(years)["value"].fillna(0)
        if base_series.sum() == 0:
            print(f"⚠ No data for technology '{tech}', skipping.")
            continue

        # Compute min/max range across NZIA scenarios
        nzia_df = pd.DataFrame(nzia_data[tech]).T  # index = years, columns = scenarios
        min_series = nzia_df.min(axis=1)
        max_series = nzia_df.max(axis=1)

        # Plot
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(years, base_series.values, color="darkred", linewidth=2, label="Base Scenario")
        ax.fill_between(years, min_series.values, max_series.values, color="seagreen", alpha=0.3, label="NZIA Range")

        ax.set_title(f"Scrap volume – {tech}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Scrap [Mt]")
        ax.set_xlim(2023, 2041)
        ax.set_xticks([2025, 2030, 2035, 2040])
        ax.set_ylim(0, max(max_series.max(), base_series.max()) * 1.1)
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.legend()

        plt.tight_layout()
        output_dir = Path("plots/scrap_range")
        output_dir.mkdir(exist_ok=True, parents=True)
        fig.savefig(output_dir / f"scrap_range_{tech}.png", dpi=300)
        plt.close(fig)

        print(f"✔ Plot saved for: {tech} → scrap_range_{tech}.png")

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



nzia_files = list(NZIA_SCENARIOS.values())

plot_base_scenario(base_file=BASE_SCENARIO)
plot_scrap_with_nzia_range(
    base_file=BASE_SCENARIO,
    nzia_files=nzia_files
)

plot_lng_spaghetti(
    base_file=BASE_FILE,
    nzia_files=list(NZIA_SCENARIOS.values()),
    years=range(2024, 2041),
    output_file="scenario_comparison/lng_spaghetti.png"
)
