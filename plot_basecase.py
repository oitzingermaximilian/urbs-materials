import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib import ticker as mticker
import numpy as np

# -------------------------------
# Configuration
# -------------------------------
RESULTS_BASE_PATH = Path("result")
SCENARIOS = {"With NZIA": "NZIA_newest", "Without NZIA": "withoutNZIA_newest"}
ROLLING_HORIZON = "rolling_2024_to_2050"
YEARS = list(range(2024, 2041))
SCENARIO_FILE = "costsnew.xlsx"
LINE_COLORS = {"With NZIA": "seagreen", "Without NZIA": "darkred"}

GROUPS = {
    "Fossil fuels generation": [
        "Coal Plant",
        "Coal Plant CCUS",
        "Gas Plant (CCGT)",
        "Gas Plant (CCGT) CCUS",
        "Lignite Plant",
        "Lignite Plant CCUS",
        "Oil Plant",
        "Other non-res",
    ],
    "Renewable generation": [
        "Hydro (reservoir)",
        "Hydro (run-of-river)",
        "solarPV",
        "windoff",
        "windon",
    ],
    "Thermal nuclear generation": ["Nuclear Plant"],
}

GROUP_COLORS = {
    "Fossil fuels generation": "#F4C20D",  # yellow
    "Renewable generation": "#009688",  # teal
    "Thermal nuclear generation": "#F57C00",  # orange
}


# -------------------------------
# Conversion
# -------------------------------
def mwh_to_bcm(mwh):
    mmbtu = mwh * 3.412
    bcm = mmbtu / 35_315_000
    return bcm


# -------------------------------
# Load LNG data
# -------------------------------
def load_lng_data(scenario_dir):
    total_by_year = {y: 0 for y in YEARS}
    file_path = RESULTS_BASE_PATH / scenario_dir / ROLLING_HORIZON / SCENARIO_FILE

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return total_by_year

    try:
        df = pd.read_excel(file_path, sheet_name="gas demand per block")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return total_by_year

    df["blocks"] = df["blocks"].astype(str).str.strip()
    df["stf"] = df["stf"].ffill()  # forward-fill missing years
    lng_df = df[~df["blocks"].str.lower().str.contains("pipegas")]
    lng_df = lng_df[lng_df["stf"].between(2024, 2040)]

    if lng_df.empty:
        return total_by_year

    yearly = lng_df.groupby("stf")["gas_usage_block"].sum().reset_index()
    yearly["lng_bcm"] = yearly["gas_usage_block"].apply(mwh_to_bcm)

    for _, row in yearly.iterrows():
        year = int(row["stf"])
        total_by_year[year] += row["lng_bcm"]

    return total_by_year


# -------------------------------
# Plotting
# -------------------------------
def plot_lng_totals():
    plt.figure(figsize=(6, 4))

    max_value = 0
    for label, folder in SCENARIOS.items():
        totals = load_lng_data(folder)
        series = pd.Series([totals[y] for y in YEARS], index=YEARS)
        plt.plot(
            series.index,
            series.values,  # plot BCM values directly
            label=label,
            color=LINE_COLORS[label],
            linewidth=2,
        )
        max_value = max(max_value, series.max())

    plt.xlabel("Year")
    plt.ylabel("Total LNG Demand [BCM]")  # show units
    plt.title("Total LNG Demand 2024-2040 (Base Case)")
    plt.xlim(2023, 2041)
    plt.xticks([2025, 2030, 2035, 2040])
    plt.ylim(0, max_value * 1.1)  # dynamic y-axis based on actual BCM values
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.legend()

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)
    out_file = output_dir / "lng_total_high_high_high.png"
    plt.savefig(out_file, dpi=300)
    plt.show()
    print(f"✔ LNG plot saved → {out_file}")


# -------------------------------
# CSV output
# -------------------------------
def save_lng_table():
    table = pd.DataFrame({"Year": YEARS})
    for label, folder in SCENARIOS.items():
        totals = load_lng_data(folder)
        table[label] = [totals[y] for y in YEARS]

    output_csv = Path("scenario_comparison") / "lng_totals_2024_2040.csv"
    table.to_csv(output_csv, index=False)
    print(f"✔ LNG totals CSV saved → {output_csv}")


# -------------------------------
# Step Plotting
# -------------------------------
def plot_lng_totals_step():
    plt.figure(figsize=(6, 4))

    max_value = 0
    for label, folder in SCENARIOS.items():
        totals = load_lng_data(folder)
        series = pd.Series([totals[y] for y in YEARS], index=YEARS)
        plt.step(
            series.index,
            series.values,  # plot BCM values directly
            where="mid",  # 'pre', 'post', or 'mid' for step position
            label=label,
            color=LINE_COLORS[label],
            linewidth=2,
        )
        max_value = max(max_value, series.max())

    plt.xlabel("Year")
    plt.ylabel("Total LNG Demand [BCM]")  # show units
    plt.title("Total LNG Demand 2024-2040 (Base Case) - Step Plot")
    plt.xlim(2023, 2041)
    plt.xticks([2025, 2030, 2035, 2040])
    plt.ylim(0, max_value * 1.1)
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.legend()

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)
    out_file = output_dir / "lng_total_high_high_high_step.png"
    plt.savefig(out_file, dpi=300)
    plt.show()
    print(f"✔ LNG step plot saved → {out_file}")


# -------------------------------
# Function to plot donut charts
# -------------------------------
def plot_generation_mix(
    file_path,
    sheet_name="extension_balance",
    years=range(2025, 2041),
    output_file="generation_mix.png",
    convert_to_twh=True,
):
    """
    Plots 4x4 donut charts of generation mix per year.

    Args:
        file_path (str or Path): Path to the Excel file.
        sheet_name (str): Sheet containing generation data.
        years (list): List of years to plot.
        output_file (str or Path): Where to save the figure.
        convert_to_twh (bool): Convert values to TWh (dividing by 1e3 if values in GWh).
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Prepare yearly data
    yearly_data = {}
    for year in years:
        year_df = df[df["Stf"] == year]
        summary = {}
        for group, processes in GROUPS.items():
            value = year_df[year_df["Process"].isin(processes)]["Value"].sum()
            if convert_to_twh:
                value /= 1_000_000  # assuming original in MWh
            summary[group] = value
        yearly_data[year] = summary

    # Plot 4x4 donut charts
    fig, axes = plt.subplots(4, 4, figsize=(16, 16))
    axes = axes.flatten()

    for i, year in enumerate(years):
        data = yearly_data[year]
        total = sum(data.values())
        sizes = [v / total for v in data.values()]

        wedges, texts = axes[i].pie(
            sizes,
            labels=list(data.keys()),
            colors=[GROUP_COLORS[k] for k in data.keys()],
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor="w"),
        )
        axes[i].set_title(f"{year} (TWh)" if convert_to_twh else str(year), fontsize=12)

    # Remove empty subplots
    for j in range(i + 1, 16):
        fig.delaxes(axes[j])

    plt.suptitle(
        "Generation Mix (TWh)" if convert_to_twh else "Generation Mix", fontsize=16
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Save figure
    output_file = Path(output_file)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(output_file, dpi=300)
    plt.show()
    print(f"✔ Donut plots saved → {output_file}")


def plot_generation_share_by_year_100pct(
    file_path,
    sheet_name="extension_balance",
    years=range(2024, 2041),  # inclusive end year via range stop=2041
    output_file="generation_share_by_year.png",
    group_order=None,  # e.g., ["Renewable", "Thermal nuclear", "Fossil fuels"]
    title="Share of energy generated per year in %",
):
    """
    Create a 100% stacked horizontal bar chart (like the example),
    with years (2024–2040) on the Y-axis and your 3 groups stacked across 0–100%.

    Data assumptions:
    - Excel has columns: 'Stf' (year), 'Process', 'Value' (in MWh or similar).
    - GROUPS: dict mapping group -> list of Process names
    - GROUP_COLORS: dict mapping group -> hex color
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Order of groups (left-to-right in the bar)
    if group_order is None:
        group_order = list(GROUPS.keys())

    # Prepare shares per year
    records = []
    for y in years:
        year_df = df[df["Stf"] == y]
        totals = {}
        for group, procs in GROUPS.items():
            totals[group] = year_df[year_df["Process"].isin(procs)]["Value"].sum()

        total_all = sum(totals.values())
        if total_all <= 0:
            shares = {g: 0.0 for g in group_order}
        else:
            shares = {g: totals.get(g, 0.0) / total_all for g in group_order}

        records.append({"year": y, **shares})

    data = pd.DataFrame(records)

    # Figure size: scale with number of years (roughly like your reference)
    n = len(years)
    fig_h = max(10, 0.52 * n + 3.5)  # tuneable height
    fig, ax = plt.subplots(figsize=(10, fig_h))

    # Axes background and spines to mimic the reference style
    ax.set_facecolor("#E6E6E6")  # light grey panel
    for spine in ax.spines.values():
        spine.set_color("#9E9E9E")
        spine.set_linewidth(1)

    # Draw the 100% stacked bars
    y_pos = np.arange(n)
    left = np.zeros(n)
    bar_height = 0.6

    for g in group_order:
        width = data[g].values * 100.0
        ax.barh(
            y_pos,
            width,
            left=left,
            height=bar_height,
            color=GROUP_COLORS[g],
            edgecolor="white",  # white separator between segments
            linewidth=1.2,
            zorder=5,
        )
        left += width

    # Y-axis setup (years from 2024 at top down to 2040)
    ax.set_yticks(y_pos, [str(y) for y in years])
    ax.invert_yaxis()  # so earliest year is at the top
    ax.tick_params(axis="y", labelsize=11, colors="#3C3C3C")

    # X-axis setup: 0–100% with ticks every 10%, shown on top
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
    ax.xaxis.set_ticks_position("top")
    ax.tick_params(axis="x", labelsize=11, colors="#3C3C3C")

    # Vertical separators every 10% on top of bars (to match the style)
    ax.vlines(
        np.arange(0, 101, 10),
        -0.5,
        n - 0.5,
        colors="white",
        linewidth=1.5,
        zorder=7,
    )

    # Clean grid (we're using custom vlines instead)
    ax.grid(False)

    # Title (left-aligned, bold)
    ax.set_title(
        title, loc="left", fontsize=18, fontweight="bold", color="#1F4E79", pad=14
    )

    # Legend at the bottom, horizontal
    handles = [plt.Rectangle((0, 0), 1, 1, color=GROUP_COLORS[g]) for g in group_order]
    labels = list(group_order)
    legend = ax.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.06),
        ncol=len(group_order),
        frameon=False,
        fontsize=11,
    )

    # Tight layout with space for the top ticks and bottom legend
    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.94])

    # Save and show
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300)
    plt.show()
    print(f"✔ Stacked share chart saved → {output_file}")


# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    plot_lng_totals()
    # save_lng_table()
    plot_lng_totals_step()
    plot_generation_mix(
        file_path="result/withoutNZIA_newest/rolling_2024_to_2050/scenario_high_high_high.xlsx"
    )
    plot_generation_share_by_year_100pct(
        file_path="result/withoutNZIA_newest/rolling_2024_to_2050/scenario_high_high_high.xlsx"
    )
