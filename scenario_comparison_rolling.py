import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path
from matplotlib.colors import to_hex  # <-- Robust color conversion
from scipy.spatial import ConvexHull
import matplotlib.patches as mpatches
import seaborn as sns

# Set the font sizes to match plot_auto.py style
plt.rcParams.update(
    {
        "font.size": 12,  # General font size
        "axes.labelsize": 14,  # Axis labels
        "axes.titlesize": 14,  # Title size
        "xtick.labelsize": 12,  # X-axis tick labels
        "ytick.labelsize": 12,  # Y-axis tick labels
        "legend.fontsize": 12,  # Legend font size
        "figure.titlesize": 14,  # Figure title size
        "figure.figsize": (12, 8),  # Default figure size
    }
)

# Define the base results path
RESULTS_BASE_PATH = r"/home/users/moitzinger/projects/max_workspace/urbs-extension/result/"  # r"C:\Users\maxoi\OneDrive\Desktop\results_crm_paper" #Dektop: r"C:\Users\Gerald\Desktop\crm_paper_Results

# Define learning rate scenarios - updated with all your LRs including LR6
LEARNING_RATES = {
    "LR1": "1% Learning Rate",
    "LR3_5": "3.5% Learning Rate",
    "LR4": "4% Learning Rate",
    "LR4": "5% Learning Rate",
    "LR6": "6% Learning Rate",
    "LR7": "7% Learning Rate",
    "LR8": "8% Learning Rate",
    "LR9": "9% Learning Rate",
    "LR10": "10% Learning Rate",
}

# Define price scenarios in order - split by LNG type
SCENARIO_COMBOS_LNG_NZ = [
    "min_min_min_LNG_NZ",
    "min_min_avg_LNG_NZ",
    "min_min_high_LNG_NZ",
    "min_avg_min_LNG_NZ",
    "min_avg_avg_LNG_NZ",
    "min_avg_high_LNG_NZ",
    "min_high_min_LNG_NZ",
    "min_high_avg_LNG_NZ",
    "min_high_high_LNG_NZ",
    "avg_min_min_LNG_NZ",
    "avg_min_avg_LNG_NZ",
    "avg_min_high_LNG_NZ",
    "avg_avg_min_LNG_NZ",
    "avg_avg_avg_LNG_NZ",
    "avg_avg_high_LNG_NZ",
    "avg_high_min_LNG_NZ",
    "avg_high_avg_LNG_NZ",
    "avg_high_high_LNG_NZ",
    "high_min_min_LNG_NZ",
    "high_min_avg_LNG_NZ",
    "high_min_high_LNG_NZ",
    "high_avg_min_LNG_NZ",
    "high_avg_avg_LNG_NZ",
    "high_avg_high_LNG_NZ",
    "high_high_min_LNG_NZ",
    "high_high_avg_LNG_NZ",
    "high_high_high_LNG_NZ",
]

SCENARIO_COMBOS_LNG_PF = [
    "min_min_min_LNG_PF",
    "min_min_avg_LNG_PF",
    "min_min_high_LNG_PF",
    "min_avg_min_LNG_PF",
    "min_avg_avg_LNG_PF",
    "min_avg_high_LNG_PF",
    "min_high_min_LNG_PF",
    "min_high_avg_LNG_PF",
    "min_high_high_LNG_PF",
    "avg_min_min_LNG_PF",
    "avg_min_avg_LNG_PF",
    "avg_min_high_LNG_PF",
    "avg_avg_min_LNG_PF",
    "avg_avg_avg_LNG_PF",
    "avg_avg_high_LNG_PF",
    "avg_high_min_LNG_PF",
    "avg_high_avg_LNG_PF",
    "avg_high_high_LNG_PF",
    "high_min_min_LNG_PF",
    "high_min_avg_LNG_PF",
    "high_min_high_LNG_PF",
    "high_avg_min_LNG_PF",
    "high_avg_avg_LNG_PF",
    "high_avg_high_LNG_PF",
    "high_high_min_LNG_PF",
    "high_high_avg_LNG_PF",
    "high_high_high_LNG_PF",
]

# Combine both LNG scenario lists for comprehensive analysis
SCENARIO_COMBOS_LNG = SCENARIO_COMBOS_LNG_NZ  # + SCENARIO_COMBOS_LNG_PF  # Combined list for legacy functions

# Define rolling horizon results path
ROLLING_HORIZON_BASE_PATH = r"/home/users/moitzinger/projects/max_workspace/urbs-extension/result/"  # r"C:\Users\maxoi\OneDrive\Desktop\results_crm_paper"


def create_compact_scenario_label(scenario):
    """
    Create a compact label from the new 3x3x3 scenario naming structure.

    Args:
        scenario (str): Scenario name like "min_avg_high_LNG_NZ" or "avg_min_min_LNG_PF"

    Returns:
        str: Compact label like "mah_nz" or "amm_pf"
    """
    # Remove LNG prefix and split
    if "_LNG_" in scenario:
        params_part, lng_type = scenario.split("_LNG_")
        params = params_part.split("_")

        if len(params) == 3:
            param1, param2, param3 = params
            # Use first letter of each parameter
            p1 = param1[0].lower()
            p2 = param2[0].lower()
            p3 = param3[0].lower()

            # Create compact label without "LNG"
            label = f"{p1}{p2}{p3}_{lng_type.lower()}"
            return label

    # Fallback to original method if pattern doesn't match
    return scenario.replace("_", " ").title()


def load_scenario_data(lr_folder, scenario, sheet_name):
    """Load data from a specific learning rate folder and scenario"""
    file_path = Path(RESULTS_BASE_PATH) / lr_folder / f"result_scenario_{scenario}.xlsx"

    if not file_path.exists():
        print(f"Warning: File not found: {file_path}")
        return None

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except Exception as e:
        print(f"Error loading {file_path}, sheet {sheet_name}: {e}")
        return None


def load_rolling_horizon_data(lr_folder, rolling_horizon_folder, scenario, sheet_name):
    """Load data from a specific rolling horizon folder and scenario"""
    # Corrected path structure: results_crm_paper/LR_folder/rolling_horizon_folder/scenario_name.xlsx
    file_path = (
        Path(RESULTS_BASE_PATH)
        / lr_folder
        / rolling_horizon_folder
        / f"scenario_{scenario}.xlsx"
    )

    if not file_path.exists():
        print(f"Warning: File not found: {file_path}")
        return None

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except Exception as e:
        print(f"Error loading {file_path}, sheet {sheet_name}: {e}")
        return None


def plot_eu_secondary_additions_by_years():
    """Plot EU secondary additions across different years and price scenarios for each technology using boxplots"""

    # Create output directory
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)
    print(f"Created/using output directory: {output_dir}")

    # First, let's identify what technologies are available
    sample_df = load_scenario_data("LR25", "average", "Total Cap Sec")
    if sample_df is None:
        print("Error: Could not load sample data to identify technologies")
        return

    # Get unique technologies from the data
    technologies = sample_df["key_1"].unique()
    print(f"Available technologies: {technologies}")

    # Define the years to analyze
    years_to_analyze = [2025, 2030, 2035, 2040]

    # Create separate plots for each technology
    for technology in technologies[:4]:  # Limit to 4 main technologies
        # Create 4 subplots for the 4 years (2x2 grid)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()

        for year_idx, year in enumerate(years_to_analyze):
            ax = axes[year_idx]

            # Collect all data for this technology and year across all learning rates and price scenarios
            data_for_boxplot = []
            labels_for_boxplot = []

            for scenario in SCENARIO_COMBOS_LNG:
                scenario_data = []

                for lr_code, lr_name in LEARNING_RATES.items():
                    df = load_scenario_data(lr_code, scenario, "Total Cap Sec")

                    if df is not None:
                        # Filter for specific year and technology
                        df_year_tech = df[
                            (df["year"] == year) & (df["key_1"] == technology)
                        ]
                        if not df_year_tech.empty:
                            # Take the value directly (no summing needed)
                            total_addition = (
                                df_year_tech["value"].iloc[0] / 1000
                            )  # Convert MW to GW
                            scenario_data.append(total_addition)
                        else:
                            print(
                                f"Warning: No {year} data found for {lr_code} {scenario} {technology}"
                            )
                            scenario_data.append(0)
                    else:
                        scenario_data.append(0)

                data_for_boxplot.append(scenario_data)
                labels_for_boxplot.append(create_compact_scenario_label(scenario))

            # Use seaborn's color palette to always get enough colors
            colors_gradient = sns.color_palette(
                "Blues", n_colors=len(SCENARIO_COMBOS_LNG)
            )
            colors_gradient = [to_hex(c) for c in colors_gradient]

            # Create boxplot for this year
            box_plot = ax.boxplot(
                data_for_boxplot,
                labels=labels_for_boxplot,
                patch_artist=True,
                showmeans=True,
                meanprops={
                    "marker": "D",
                    "markerfacecolor": "red",
                    "markeredgecolor": "red",
                    "markersize": 8,
                },
            )

            # Color the boxes with the generated palette
            for patch, color in zip(box_plot["boxes"], colors_gradient):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

            # Customize each subplot
            ax.set_xlabel("Price Scenarios")
            ax.set_ylabel("EU Secondary Additions (GW)")
            ax.set_title(f"{technology} - {year}")
            ax.grid(True, alpha=0.3)
            ax.set_ylim(bottom=0)

            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # Add overall title for the technology
        fig.suptitle(
            f"{technology} - EU Secondary Capacity Additions Across Years",
            fontsize=16,
            y=0.98,
        )
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # Save the plot for this technology
        safe_tech_name = technology.replace("/", "_").replace(" ", "_")
        output_path = (
            output_dir / f"{safe_tech_name}_eu_secondary_by_years_boxplots.png"
        )
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Saved plot for {technology}: {output_path}")

        # plt.show()


def plot_eu_secondary_additions_2040():
    """Plot total EU secondary additions in 2040 across price scenarios and learning rates for each technology using boxplots"""
    # Keep the original function for backward compatibility
    plot_eu_secondary_additions_by_years()


def plot_lng_demand_comparison():
    """Plot LNG demand comparison across learning rates and price scenarios using a heatmap"""

    def mwh_to_bcm(mwh, energy_content_mj_per_m3=35.8):
        return mwh * 3.6 * 1000 / (energy_content_mj_per_m3 * 1e9)

    # Create output directory
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Prepare the data matrix
    lng_matrix = np.zeros((len(SCENARIO_COMBOS_LNG), len(LEARNING_RATES)))

    for i, scenario in enumerate(SCENARIO_COMBOS_LNG):
        for j, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
            df = load_scenario_data(lr_code, scenario, "Commodities_Demand")

            if df is not None:
                # Filter for LNG data and years 2024-2040
                lng_data = df[
                    (df["key_2"].str.strip() == "LNG")
                    & (df["year"] >= 2024)
                    & (df["year"] <= 2040)
                ]

                if not lng_data.empty:
                    # Sum total LNG demand from 2024-2040 (in MWh)
                    total_lng_mwh = lng_data["value"].sum()
                    # Convert to BCM
                    total_lng_bcm = mwh_to_bcm(total_lng_mwh)
                    lng_matrix[i, j] = total_lng_bcm
                else:
                    lng_matrix[i, j] = np.nan
            else:
                lng_matrix[i, j] = np.nan

    # Create the heatmap plot
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(
        lng_matrix,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",  # Yellow-Orange-Red gradient
        linewidths=0.5,
        linecolor="gray",
        cbar_kws={"label": "LNG Demand 2024-2040 (BCM)"},
        ax=ax,
    )

    # Set axis labels and ticks
    ax.set_xticks(np.arange(len(LEARNING_RATES)) + 0.5)
    ax.set_yticks(np.arange(len(SCENARIO_COMBOS_LNG)) + 0.5)
    ax.set_xticklabels([v for v in LEARNING_RATES.values()], rotation=45, ha="right")
    ax.set_yticklabels(
        [create_compact_scenario_label(s) for s in SCENARIO_COMBOS_LNG], rotation=0
    )
    ax.set_xlabel("Learning Rate Scenario")
    ax.set_ylabel("Price Scenario")
    ax.set_title("LNG Demand Matrix (2024-2040)")

    plt.tight_layout()
    output_path = output_dir / "lng_demand_matrix_2024_2040.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved LNG demand matrix plot: {output_path}")

    # plt.show()

    # Also create a line plot with better separation using alpha and markers
    fig, ax = plt.subplots(figsize=(14, 8))
    x_positions = np.arange(len(SCENARIO_COMBOS_LNG))

    # Use different markers and line styles for better distinction
    markers = ["o", "s", "^", "D", "v", "<", ">", "p", "*", "h"]
    linestyles = ["-", "--", "-.", ":"]

    colors = sns.color_palette("tab10", n_colors=len(LEARNING_RATES))
    colors = [to_hex(c) for c in colors]

    for i, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
        lng_demands = lng_matrix[:, i]  # Get the column for this learning rate

        ax.plot(
            x_positions,
            lng_demands,
            marker=markers[i % len(markers)],
            linestyle=linestyles[i % len(linestyles)],
            linewidth=2,
            markersize=8,
            label=lr_name,
            color=colors[i % len(colors)],
            alpha=0.8,
        )

    ax.set_xlabel("Price Scenarios")
    ax.set_ylabel("LNG Demand 2024-2040 (BCM)")
    ax.set_title(
        "LNG Demand Comparison Across Learning Rates and Price Scenarios (2024-2040)"
    )
    ax.set_xticks(x_positions)
    ax.set_xticklabels(
        [create_compact_scenario_label(s) for s in SCENARIO_COMBOS_LNG],
        rotation=45,
        ha="right",
    )
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", ncol=1)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path_lines = output_dir / "lng_demand_lines_improved_2024_2040.png"
    plt.savefig(output_path_lines, dpi=300, bbox_inches="tight")
    print(f"Saved improved line plot: {output_path_lines}")

    # ()


def plot_lng_demand_yearly_scatter():
    """Plot yearly LNG demand scatter plot - Option 1: Color by Learning Rate, markers for price scenarios"""

    def mwh_to_bcm(mwh, energy_content_mj_per_m3=35.8):
        return mwh * 3.6 * 1000 / (energy_content_mj_per_m3 * 1e9)

    # Create output directory
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Collect yearly data
    yearly_data = []

    for lr_code, lr_name in LEARNING_RATES.items():
        for scenario in SCENARIO_COMBOS_LNG:
            df = load_scenario_data(lr_code, scenario, "Commodities_Demand")

            if df is not None:
                # Filter for LNG data
                lng_data = df[df["key_2"].str.strip() == "LNG"]

                for _, row in lng_data.iterrows():
                    year = row["year"]
                    lng_bcm = mwh_to_bcm(row["value"])
                    yearly_data.append(
                        {
                            "Year": year,
                            "LNG_BCM": lng_bcm,
                            "Learning_Rate": lr_name,
                            "Price_Scenario": scenario.replace("_", " ").title(),
                            "LR_Code": lr_code,
                            "Scenario_Code": scenario,
                        }
                    )

    df_yearly = pd.DataFrame(yearly_data)

    # Option 1: Color by Learning Rate, different markers for price scenarios
    fig, ax = plt.subplots(figsize=(14, 8))

    # Create unique markers for price scenarios
    price_markers = ["o", "s", "^", "D", "v", "<", ">", "p", "*", "h", "+"]
    price_scenario_map = {
        scenario: price_markers[i % len(price_markers)]
        for i, scenario in enumerate(SCENARIO_COMBOS_LNG)
    }

    colors = sns.color_palette("tab10", n_colors=len(LEARNING_RATES))
    lr_color_map = {
        lr_name: colors[i] for i, lr_name in enumerate(LEARNING_RATES.values())
    }

    for lr_name in LEARNING_RATES.values():
        for scenario in SCENARIO_COMBOS_LNG:
            scenario_title = scenario.replace("_", " ").title()
            subset = df_yearly[
                (df_yearly["Learning_Rate"] == lr_name)
                & (df_yearly["Price_Scenario"] == scenario_title)
            ]

            if not subset.empty:
                ax.scatter(
                    subset["Year"],
                    subset["LNG_BCM"],
                    color=lr_color_map[lr_name],
                    marker=price_scenario_map[scenario],
                    s=60,
                    alpha=0.7,
                    label=f"{lr_name}" if scenario == SCENARIO_COMBOS_LNG[0] else "",
                )

    ax.set_xlabel("Year")
    ax.set_ylabel("LNG Demand (BCM)")
    ax.set_title("Yearly LNG Demand by Learning Rate and Price Scenario")
    ax.legend(title="Learning Rates", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    output_path = output_dir / "lng_yearly_scatter_by_lr.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved yearly scatter plot: {output_path}")
    # plt.show()


def plot_lng_demand_yearly_barplot():
    """Plot yearly LNG demand using grouped bar plots - separate bars for each price scenario, grouped by learning rate"""

    def mwh_to_bcm(mwh, energy_content_mj_per_m3=35.8):
        return mwh * 3.6 * 1000 / (energy_content_mj_per_m3 * 1e9)

    # Create output directory
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Collect yearly data
    yearly_data = []

    for lr_code, lr_name in LEARNING_RATES.items():
        for scenario in SCENARIO_COMBOS_LNG:
            df = load_scenario_data(lr_code, scenario, "Commodities_Demand")

            if df is not None:
                # Filter for LNG data
                lng_data = df[df["key_2"].str.strip() == "LNG"]

                for _, row in lng_data.iterrows():
                    year = row["year"]
                    lng_bcm = mwh_to_bcm(row["value"])
                    yearly_data.append(
                        {
                            "Year": year,
                            "LNG_BCM": lng_bcm,
                            "Learning_Rate": lr_name,
                            "Price_Scenario": scenario.replace("_", " ").title(),
                            "LR_Code": lr_code,
                            "Scenario_Code": scenario,
                        }
                    )

    df_yearly = pd.DataFrame(yearly_data)

    # Get unique years and sort them
    years = sorted(df_yearly["Year"].unique())

    # Create subplots for each learning rate
    n_lr = len(LEARNING_RATES)
    n_cols = 2  # 2 columns of subplots
    n_rows = (n_lr + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))
    if n_lr == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    # Colors for price scenarios (use a colorful palette)
    colors_price = sns.color_palette("Set3", n_colors=len(SCENARIO_COMBOS_LNG))

    # Bar width and positioning
    bar_width = 0.07  # Very slim bars as requested

    for i, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
        ax = axes[i]

        # For each year, create grouped bars
        for year_idx, year in enumerate(years):
            year_data = df_yearly[
                (df_yearly["LR_Code"] == lr_code) & (df_yearly["Year"] == year)
            ]

            for scenario_idx, scenario in enumerate(SCENARIO_COMBOS_LNG):
                scenario_title = scenario.replace("_", " ").title()
                scenario_data = year_data[year_data["Price_Scenario"] == scenario_title]

                if not scenario_data.empty:
                    lng_value = scenario_data["LNG_BCM"].iloc[0]

                    # Calculate bar position
                    x_pos = (
                        year + (scenario_idx - len(SCENARIO_COMBOS_LNG) / 2) * bar_width
                    )

                    ax.bar(
                        x_pos,
                        lng_value,
                        width=bar_width,
                        color=colors_price[scenario_idx],
                        alpha=0.8,
                        label=scenario_title if year_idx == 0 else "",
                    )

        ax.set_xlabel("Year")
        ax.set_ylabel("LNG Demand (BCM)")
        ax.set_title(f"{lr_name}")
        ax.grid(True, alpha=0.3, axis="y")
        ax.set_xticks(years)

        # Only show legend for the first subplot to avoid clutter
        if i == 0:
            ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

    # Hide unused subplots
    for i in range(n_lr, len(axes)):
        axes[i].set_visible(False)

    plt.suptitle(
        "Yearly LNG Demand by Price Scenario (Grouped by Learning Rate)", fontsize=16
    )
    plt.tight_layout()

    output_path = output_dir / "lng_yearly_barplot_grouped.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved yearly bar plot: {output_path}")


# plt.show()


def plot_total_system_cost_matrix():  # TODO Disabled reenable if needed
    """
    Create a matrix heatmap of total system cost for the year 2040.
    Rows: price scenarios
    Columns: learning rate scenarios
    Cell value: sum of 'value' column for year 2040 in the 'Total_Cost' sheet
    """
    # Prepare the data matrix
    cost_matrix = np.zeros((len(SCENARIO_COMBOS_LNG), len(LEARNING_RATES)))

    for i, scenario in enumerate(SCENARIO_COMBOS_LNG):
        for j, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
            df = load_scenario_data(lr_code, scenario, "Total_Cost")
            if df is not None:
                df_2040 = df[df["year"] == 2040]
                total_cost = (
                    df_2040["value"].sum() / 1e9
                )  # Convert to bEUR (assuming value in EUR)
                cost_matrix[i, j] = total_cost
            else:
                cost_matrix[i, j] = np.nan  # Use NaN for missing data

    # Create the heatmap plot
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(
        cost_matrix,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",  # Yellow-Orange-Red gradient for cost
        linewidths=0.5,
        linecolor="gray",
        cbar_kws={"label": "Total System Cost (bEUR)"},
        ax=ax,
    )

    # Set axis labels and ticks
    ax.set_xticks(np.arange(len(LEARNING_RATES)) + 0.5)
    ax.set_yticks(np.arange(len(SCENARIO_COMBOS_LNG)) + 0.5)
    ax.set_xticklabels([v for v in LEARNING_RATES.values()], rotation=45, ha="right")
    ax.set_yticklabels(
        [create_compact_scenario_label(s) for s in SCENARIO_COMBOS_LNG], rotation=0
    )
    ax.set_xlabel("Learning Rate Scenario")
    ax.set_ylabel("Price Scenario")
    ax.set_title("Total System Cost Matrix (2040)")

    plt.tight_layout()
    output_path = Path("scenario_comparison") / "total_system_cost_matrix_2040.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved total system cost matrix plot: {output_path}")


# plt.show()


def plot_total_system_cost_matrix_2024_2040():
    """
    Create sophisticated heatmaps of total system cost (2024–2040) for both Net Zero and Persistent Fossil scenario types,
    showing with_NZIA (top) and without_NZIA (bottom). One PNG per scenario type.
    """

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Scenario configurations
    scenario_types = [
        {"name": "NZ", "scenarios": SCENARIO_COMBOS_LNG_NZ, "title": "Net Zero"},
        {
            "name": "PF",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "title": "Persistent Fossil",
        },
    ]

    # NZIA variants (top: with NZIA, bottom: without NZIA)
    nzia_variants = [
        {"variant": "results_with_nzia", "label": "with_NZIA", "title": "with NZIA"},
        {
            "variant": "results_without_nzia",
            "label": "without_NZIA",
            "title": "without NZIA",
        },
    ]

    for scenario_type in scenario_types:
        print(
            f"Processing total system cost matrix for scenario type: {scenario_type['title']}"
        )
        matrices = []
        for nzia in nzia_variants:
            cost_matrix = np.full(
                (len(scenario_type["scenarios"]), len(LEARNING_RATES)), np.nan
            )
            for i, scenario in enumerate(scenario_type["scenarios"]):
                for j, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
                    file_path = (
                        Path(RESULTS_BASE_PATH)
                        / nzia["variant"]
                        / lr_code
                        / "rolling_2024_to_2050"
                        / f"scenario_{scenario}.xlsx"
                    )
                    if not file_path.exists():
                        continue
                    try:
                        df = pd.read_excel(file_path, sheet_name="extension_cost")
                    except Exception:
                        continue
                    if "stf" not in df or "Total_Cost" not in df:
                        continue
                    df_period = df[(df["stf"] >= 2024) & (df["stf"] <= 2040)]
                    total_cost = (
                        df_period["Total_Cost"].sum() / 1e9
                    )  # Convert to bEUR if value in EUR
                    cost_matrix[i, j] = total_cost
            matrices.append(cost_matrix)

        # Plot: with_NZIA on top, without_NZIA below
        fig, axes = plt.subplots(2, 1, figsize=(14, 11), sharex=True)
        vmin = min(np.nanmin(mat) for mat in matrices)
        vmax = max(np.nanmax(mat) for mat in matrices)
        for ax, cost_matrix, nzia in zip(axes, matrices, nzia_variants):
            sns.heatmap(
                cost_matrix,
                annot=True,
                fmt=".1f",
                cmap="YlOrRd",
                linewidths=0.5,
                linecolor="gray",
                cbar=ax == axes[0],
                vmin=vmin,
                vmax=vmax,
                cbar_kws={"label": "Total System Cost (2024–2040, bEUR)"}
                if ax == axes[0]
                else None,
                ax=ax,
            )
            ax.set_xticks(np.arange(len(LEARNING_RATES)) + 0.5)
            ax.set_yticks(np.arange(len(scenario_type["scenarios"])) + 0.5)
            ax.set_xticklabels(
                [v for v in LEARNING_RATES.values()], rotation=45, ha="right"
            )
            ax.set_yticklabels(
                [create_compact_scenario_label(s) for s in scenario_type["scenarios"]],
                rotation=0,
            )
            ax.set_ylabel(f"{nzia['title']} – Price Scenario")
            if ax == axes[0]:
                ax.set_title(
                    f"Total System Cost Matrix (2024–2040)\n{scenario_type['title']}"
                )
            else:
                ax.set_xlabel("Learning Rate Scenario")
        plt.tight_layout()
        output_path = (
            output_dir
            / f"total_system_cost_matrix_2024_2040_{scenario_type['name']}.png"
        )
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(
            f"Saved total system cost matrix plot (2024–2040) for {scenario_type['title']}: {output_path}"
        )


def plot_3d_cost_matrix_grid_style_fixed():
    """
    Create a 3D plot with corrected price scenario labels using the new compact labeling.
    """

    # Create output directory
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Prepare the data matrix
    cost_matrix = np.zeros((len(SCENARIO_COMBOS_LNG), len(LEARNING_RATES)))

    for i, scenario in enumerate(SCENARIO_COMBOS_LNG):
        for j, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
            df = load_scenario_data(lr_code, scenario, "Total_Cost")
            if df is not None:
                df_period = df[(df["year"] >= 2024) & (df["year"] <= 2040)]
                total_cost = df_period["value"].sum() / 1e9  # Convert to bEUR
                cost_matrix[i, j] = total_cost
            else:
                cost_matrix[i, j] = np.nan

    # DEBUG: Print the actual SCENARIO_COMBOS_LNG to see what we're working with
    print("SCENARIO_COMBOS_LNG:")
    for i, scenario in enumerate(SCENARIO_COMBOS_LNG):
        print(f"{i}: {scenario}")

    # Create 3D plot
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection="3d")

    # Create meshgrid for 3D surface
    X = np.arange(len(LEARNING_RATES))
    Y = np.arange(len(SCENARIO_COMBOS_LNG))
    X, Y = np.meshgrid(X, Y)
    Z = cost_matrix

    # Rotate so lowest values face towards us
    ax.view_init(elev=25, azim=225)

    # Create the 3D surface plot
    surf = ax.plot_surface(
        X,
        Y,
        Z,
        cmap="YlOrRd",
        alpha=0.9,
        linewidth=0.8,
        edgecolor="darkred",
        antialiased=True,
    )

    # Clean axis labels
    ax.set_xlabel("Learning Rate [%]")
    ax.set_ylabel("Price Scenario")
    ax.set_zlabel("Cost [bEUR]")

    # Set ticks
    ax.set_xticks(range(len(LEARNING_RATES)))
    ax.set_yticks(range(len(SCENARIO_COMBOS_LNG)))

    # Simple learning rate labels
    lr_labels = [v.split("%")[0] for v in LEARNING_RATES.values()]

    # Use the new compact scenario labeling function
    price_labels_compact = [
        create_compact_scenario_label(scenario) for scenario in SCENARIO_COMBOS_LNG
    ]

    # DEBUG: Print the compact labels
    print("\nCompact price labels:")
    for i, label in enumerate(price_labels_compact):
        print(f"{i}: {SCENARIO_COMBOS_LNG[i]} -> {label}")

    ax.set_xticklabels(lr_labels, fontsize=10)
    ax.set_yticklabels(price_labels_compact, fontsize=9)

    plt.tight_layout()

    # Save the plot
    output_path = output_dir / "3d_cost_matrix_grid_style_fixed.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved fixed grid style 3D plot: {output_path}")


# plt.show()


def plot_3d_cost_matrix_with_mapping():
    """
    Create plot using explicit mapping to avoid label conflicts
    """

    # Get the mapping
    price_mapping = create_price_scenario_mapping()

    # Create output directory
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Prepare the data matrix
    cost_matrix = np.zeros((len(SCENARIO_COMBOS_LNG), len(LEARNING_RATES)))

    for i, scenario in enumerate(SCENARIO_COMBOS_LNG):
        for j, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
            df = load_scenario_data(lr_code, scenario, "Total_Cost")
            if df is not None:
                df_period = df[(df["year"] >= 2024) & (df["year"] <= 2040)]
                total_cost = df_period["value"].sum() / 1e9
                cost_matrix[i, j] = total_cost
            else:
                cost_matrix[i, j] = np.nan

    # Create 3D plot
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection="3d")

    X = np.arange(len(LEARNING_RATES))
    Y = np.arange(len(SCENARIO_COMBOS_LNG))
    X, Y = np.meshgrid(X, Y)
    Z = cost_matrix

    ax.view_init(elev=25, azim=225)

    surf = ax.plot_surface(
        X,
        Y,
        Z,
        cmap="YlOrRd",
        alpha=0.9,
        linewidth=0.8,
        edgecolor="darkred",
        antialiased=True,
    )

    ax.set_xlabel("Learning Rate [%]")
    ax.set_ylabel("Price Scenario")
    ax.set_zlabel("Cost [bEUR]")

    ax.set_xticks(range(len(LEARNING_RATES)))
    ax.set_yticks(range(len(SCENARIO_COMBOS_LNG)))

    lr_labels = [v.split("%")[0] for v in LEARNING_RATES.values()]

    # Use the explicit mapping
    price_labels_mapped = []
    for scenario in SCENARIO_COMBOS_LNG:
        scenario_clean = scenario.lower().replace("_", " ").strip()
        if scenario_clean in price_mapping:
            price_labels_mapped.append(price_mapping[scenario_clean])
        else:
            # Fallback for any scenario not in mapping
            price_labels_mapped.append(scenario.replace("_", " ").title()[:8])

    ax.set_xticklabels(lr_labels, fontsize=10)
    ax.set_yticklabels(price_labels_mapped, fontsize=9)

    plt.tight_layout()

    output_path = output_dir / "3d_cost_matrix_mapped_labels.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved mapped labels 3D plot: {output_path}")


# plt.show()


def mwh_to_bcm(mwh, energy_content_mj_per_m3=35.8):
    """Convert MWh to bcm for LNG"""
    return mwh * 3.6 * 1000 / (energy_content_mj_per_m3 * 1e9)


def find_pareto_front(costs, objectives, minimize_both=True):
    """Find Pareto front points"""
    points = np.column_stack((costs, objectives))

    if minimize_both:
        # For minimization problems
        pareto_mask = np.ones(len(points), dtype=bool)
        for i, point in enumerate(points):
            if pareto_mask[i]:
                # Check if any other point dominates this point
                dominated = np.all(points <= point, axis=1) & np.any(
                    points < point, axis=1
                )
                if np.any(dominated):
                    pareto_mask[i] = False
    else:
        # For cost minimization vs objective maximization
        pareto_mask = np.ones(len(points), dtype=bool)
        for i, point in enumerate(points):
            if pareto_mask[i]:
                # A point dominates if it has lower cost AND higher objective
                dominated = (
                    (points[:, 0] <= point[0])
                    & (points[:, 1] >= point[1])
                    & ((points[:, 0] < point[0]) | (points[:, 1] > point[1]))
                )
                if np.any(dominated):
                    pareto_mask[i] = False

    return pareto_mask


def plot_pareto_cost_vs_lng():
    """Pareto plot: Total system cost (2024-2030) vs LNG demand in 2030"""

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    results = []

    for lr_code, lr_name in LEARNING_RATES.items():
        for scenario in SCENARIO_COMBOS_LNG:
            # Load cost data
            df_cost = load_scenario_data(lr_code, scenario, "Total_Cost")
            # Load LNG data
            df_lng = load_scenario_data(lr_code, scenario, "Commodities_Demand")

            if df_cost is None or df_lng is None:
                continue

            # Total system cost 2024-2030 (including 2030)
            cost_data = df_cost[(df_cost["year"] >= 2024) & (df_cost["year"] <= 2030)]
            total_cost = cost_data["value"].sum() / 1e9  # Convert to billion EUR

            # LNG demand in 2030 only (as it's import demand in that specific year)
            lng_2030 = df_lng[
                (df_lng["year"] == 2030) & (df_lng["key_2"].str.strip() == "LNG")
            ]
            if not lng_2030.empty:
                lng_mwh = lng_2030["value"].sum()
                lng_bcm = mwh_to_bcm(lng_mwh)
            else:
                lng_bcm = 0

            results.append(
                {
                    "Learning_Rate": lr_name,
                    "Price_Scenario": scenario.replace("_", " ").title(),
                    "Total_Cost_bEUR": total_cost,
                    "LNG_Import_2030_BCM": lng_bcm,
                    "LR_Code": lr_code,
                    "Scenario_Code": scenario,
                }
            )

    df_results = pd.DataFrame(results)

    # Find Pareto front (minimize cost, minimize LNG imports)
    costs = df_results["Total_Cost_bEUR"].values
    lng_imports = df_results["LNG_Import_2030_BCM"].values

    pareto_mask = find_pareto_front(costs, lng_imports, minimize_both=True)
    pareto_points = df_results[pareto_mask].copy()
    pareto_points = pareto_points.sort_values("Total_Cost_bEUR")

    # Create the plot
    plt.figure(figsize=(12, 8))

    # Plot all points
    colors = sns.color_palette("tab10", n_colors=len(LEARNING_RATES))
    lr_color_map = {
        lr_name: colors[i] for i, lr_name in enumerate(LEARNING_RATES.values())
    }

    for lr_name in LEARNING_RATES.values():
        subset = df_results[df_results["Learning_Rate"] == lr_name]
        plt.scatter(
            subset["Total_Cost_bEUR"],
            subset["LNG_Import_2030_BCM"],
            color=lr_color_map[lr_name],
            label=lr_name,
            alpha=0.7,
            s=60,
        )

    # Plot Pareto front
    plt.plot(
        pareto_points["Total_Cost_bEUR"],
        pareto_points["LNG_Import_2030_BCM"],
        "r--",
        linewidth=2,
        label="Pareto Front",
    )
    plt.scatter(
        pareto_points["Total_Cost_bEUR"],
        pareto_points["LNG_Import_2030_BCM"],
        color="red",
        s=100,
        marker="*",
        label="Pareto Optimal",
        zorder=5,
    )

    plt.xlabel("Total System Cost until 2030 (billion EUR)")
    plt.ylabel("LNG Import Demand 2030 (BCM)")
    plt.title("Pareto Front: Cost vs. LNG Import Demand")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output_path = output_dir / "pareto_cost_vs_lng_2030.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved Pareto plot (Cost vs LNG): {output_path}")

    # Print Pareto optimal points
    print("\nPareto Optimal Points (Cost vs LNG):")
    for _, row in pareto_points.iterrows():
        print(
            f"  {row['Learning_Rate']} - {row['Price_Scenario']}: "
            f"Cost={row['Total_Cost_bEUR']:.1f}b€, LNG={row['LNG_Import_2030_BCM']:.1f}BCM"
        )


# plt.show()


def plot_pareto_cost_vs_remanufacturing():
    """Pareto plot: Total system cost (2024-2030) vs Remanufacturing share in 2030"""

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    results = []

    for lr_code, lr_name in LEARNING_RATES.items():
        for scenario in SCENARIO_COMBOS_LNG:
            # Load cost data
            df_cost = load_scenario_data(lr_code, scenario, "Total_Cost")
            # Load remanufacturing data
            df_reman = load_scenario_data(lr_code, scenario, "Total Cap Sec")

            if df_cost is None or df_reman is None:
                continue

            # Total system cost 2024-2030
            cost_data = df_cost[(df_cost["year"] >= 2024) & (df_cost["year"] <= 2030)]
            total_cost = cost_data["value"].sum() / 1e9  # Convert to billion EUR

            # Remanufacturing additions in 2030 (sum across all technologies)
            reman_2030 = df_reman[df_reman["year"] == 2030]
            total_reman = reman_2030["value"].sum() / 1000  # Convert MW to GW

            results.append(
                {
                    "Learning_Rate": lr_name,
                    "Price_Scenario": scenario.replace("_", " ").title(),
                    "Total_Cost_bEUR": total_cost,
                    "Remanufacturing_2030_GW": total_reman,
                    "LR_Code": lr_code,
                    "Scenario_Code": scenario,
                }
            )

    df_results = pd.DataFrame(results)

    # Find Pareto front (minimize cost, maximize remanufacturing)
    costs = df_results["Total_Cost_bEUR"].values
    remanufacturing = df_results["Remanufacturing_2030_GW"].values

    pareto_mask = find_pareto_front(costs, remanufacturing, minimize_both=False)
    pareto_points = df_results[pareto_mask].copy()
    pareto_points = pareto_points.sort_values("Total_Cost_bEUR")

    # Create the plot
    plt.figure(figsize=(12, 8))

    # Plot all points
    colors = sns.color_palette("tab10", n_colors=len(LEARNING_RATES))
    lr_color_map = {
        lr_name: colors[i] for i, lr_name in enumerate(LEARNING_RATES.values())
    }

    for lr_name in LEARNING_RATES.values():
        subset = df_results[df_results["Learning_Rate"] == lr_name]
        plt.scatter(
            subset["Total_Cost_bEUR"],
            subset["Remanufacturing_2030_GW"],
            color=lr_color_map[lr_name],
            label=lr_name,
            alpha=0.7,
            s=60,
        )

    # Plot Pareto front
    plt.plot(
        pareto_points["Total_Cost_bEUR"],
        pareto_points["Remanufacturing_2030_GW"],
        "r--",
        linewidth=2,
        label="Pareto Front",
    )
    plt.scatter(
        pareto_points["Total_Cost_bEUR"],
        pareto_points["Remanufacturing_2030_GW"],
        color="red",
        s=100,
        marker="*",
        label="Pareto Optimal",
        zorder=5,
    )

    plt.xlabel("Total System Cost until 2030 (billion EUR)")
    plt.ylabel("Remanufacturing Additions 2030 (GW)")
    plt.title("Pareto Front: Cost vs. Remanufacturing Additions")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output_path = output_dir / "pareto_cost_vs_remanufacturing_2030.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved Pareto plot (Cost vs Remanufacturing): {output_path}")

    # Print Pareto optimal points
    print("\nPareto Optimal Points (Cost vs Remanufacturing):")
    for _, row in pareto_points.iterrows():
        print(
            f"  {row['Learning_Rate']} - {row['Price_Scenario']}: "
            f"Cost={row['Total_Cost_bEUR']:.1f}b€, Reman={row['Remanufacturing_2030_GW']:.1f}GW"
        )


# plt.show()


def plot_3d_scrap_bars_cumulative():
    """
    Create 3D bar charts showing cumulative scrap 2024-2040 for 4 key technologies
    """

    # Create output directory
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Key technologies to analyze
    technologies = ["solarPV", "windon", "windoff", "Batteries"]

    # Get fixed price labels
    price_labels_fixed = get_fixed_price_labels()

    # Create figure with 2x2 subplots
    fig = plt.figure(figsize=(20, 16))

    for tech_idx, technology in enumerate(technologies):
        ax = fig.add_subplot(2, 2, tech_idx + 1, projection="3d")

        # Prepare data matrix
        scrap_matrix = np.zeros((len(SCENARIO_COMBOS_LNG), len(LEARNING_RATES)))

        for i, scenario in enumerate(SCENARIO_COMBOS_LNG):
            for j, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
                # Load from "Total_Scrap" sheet, then filter by technology
                df = load_scenario_data(lr_code, scenario, "Total_Scrap")
                if df is not None and not df.empty:
                    # Filter for specific technology
                    tech_data = df[df["key_1"] == technology]
                    if not tech_data.empty:
                        df_period = tech_data[
                            (tech_data["year"] >= 2024) & (tech_data["year"] <= 2040)
                        ]
                        cumulative_scrap = (
                            df_period["value"].sum() / 1e6
                        )  # Convert to megatons
                        scrap_matrix[i, j] = cumulative_scrap
                    else:
                        scrap_matrix[i, j] = 0
                else:
                    scrap_matrix[i, j] = 0

        # Create 3D bar plot
        X = np.arange(len(LEARNING_RATES))
        Y = np.arange(len(SCENARIO_COMBOS_LNG))
        X, Y = np.meshgrid(X, Y)

        # Flatten for bar plot
        x_flat = X.flatten()
        y_flat = Y.flatten()
        z_flat = np.zeros_like(x_flat)
        dx = dy = 0.8
        dz = scrap_matrix.flatten()

        # Create bars with color mapping
        max_val = np.max(dz) if np.max(dz) > 0 else 1
        colors = plt.cm.YlOrRd(dz / max_val)

        ax.bar3d(x_flat, y_flat, z_flat, dx, dy, dz, color=colors, alpha=0.8)

        # Customize plot
        ax.set_title(f"{technology} - Cumulative Scrap 2024-2040", fontsize=14, pad=20)
        ax.set_xlabel("Learning Rate [%]")
        ax.set_ylabel("Price Scenario")
        ax.set_zlabel("Scrap [Mt]")

        # Set ticks
        ax.set_xticks(range(len(LEARNING_RATES)))
        ax.set_yticks(range(len(SCENARIO_COMBOS_LNG)))

        # Use fixed labels
        lr_labels = [v.split("%")[0] for v in LEARNING_RATES.values()]

        ax.set_xticklabels(lr_labels, fontsize=8)
        ax.set_yticklabels(price_labels_fixed, fontsize=8)

        # Set viewing angle
        ax.view_init(elev=25, azim=45)

    plt.suptitle("Cumulative Scrap Generation by Technology (2024-2040)", fontsize=16)
    plt.tight_layout()

    output_path = output_dir / "3d_scrap_bars_cumulative.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved cumulative scrap 3D bars: {output_path}")


# plt.show()


def plot_3d_scrap_bars_2040():
    """
    Create 3D bar charts showing 2040 annual scrap for 4 key technologies
    """

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    technologies = ["solarPV", "windon", "windoff", "Batteries"]

    # Get fixed price labels
    price_labels_fixed = get_fixed_price_labels()

    fig = plt.figure(figsize=(20, 16))

    for tech_idx, technology in enumerate(technologies):
        ax = fig.add_subplot(2, 2, tech_idx + 1, projection="3d")

        # Prepare data matrix for 2040
        scrap_matrix = np.zeros((len(SCENARIO_COMBOS_LNG), len(LEARNING_RATES)))

        for i, scenario in enumerate(SCENARIO_COMBOS_LNG):
            for j, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
                # Load from "Total_Scrap" sheet, then filter by technology
                df = load_scenario_data(lr_code, scenario, "Total_Scrap")
                if df is not None and not df.empty:
                    # Filter for specific technology
                    tech_data = df[df["key_1"] == technology]
                    if not tech_data.empty:
                        scrap_2040 = tech_data[tech_data["year"] == 2040]["value"]
                        if not scrap_2040.empty:
                            scrap_matrix[i, j] = (
                                scrap_2040.iloc[0] / 1e6
                            )  # Convert to megatons
                        else:
                            scrap_matrix[i, j] = 0
                    else:
                        scrap_matrix[i, j] = 0
                else:
                    scrap_matrix[i, j] = 0

        # Create 3D bar plot
        X = np.arange(len(LEARNING_RATES))
        Y = np.arange(len(SCENARIO_COMBOS_LNG))
        X, Y = np.meshgrid(X, Y)

        x_flat = X.flatten()
        y_flat = Y.flatten()
        z_flat = np.zeros_like(x_flat)
        dx = dy = 0.8
        dz = scrap_matrix.flatten()

        # Create bars with color mapping
        max_val = np.max(dz) if np.max(dz) > 0 else 1
        colors = plt.cm.YlOrRd(dz / max_val)

        ax.bar3d(x_flat, y_flat, z_flat, dx, dy, dz, color=colors, alpha=0.8)

        # Customize plot
        ax.set_title(f"{technology} - Annual Scrap in 2040", fontsize=14, pad=20)
        ax.set_xlabel("Learning Rate [%]")
        ax.set_ylabel("Price Scenario")
        ax.set_zlabel("Scrap [Mt/year]")

        # Set ticks and labels
        ax.set_xticks(range(len(LEARNING_RATES)))
        ax.set_yticks(range(len(SCENARIO_COMBOS_LNG)))

        lr_labels = [v.split("%")[0] for v in LEARNING_RATES.values()]

        ax.set_xticklabels(lr_labels, fontsize=8)
        ax.set_yticklabels(price_labels_fixed, fontsize=8)

        ax.view_init(elev=25, azim=45)

    plt.suptitle("Annual Scrap Generation by Technology in 2040", fontsize=16)
    plt.tight_layout()

    output_path = output_dir / "3d_scrap_bars_2040.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved 2040 scrap 3D bars: {output_path}")


# plt.show()


def plot_scrap_time_evolution_3d():
    """
    Create 3D surfaces showing scrap evolution over time for solarPV
    """

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Focus on one technology for clarity
    technology = "solarPV"

    # Key years to show
    key_years = [2025, 2030, 2035, 2040]

    # Get fixed price labels
    price_labels_fixed = get_fixed_price_labels()

    fig = plt.figure(figsize=(20, 16))

    for year_idx, year in enumerate(key_years):
        ax = fig.add_subplot(2, 2, year_idx + 1, projection="3d")

        # Prepare data matrix for this year
        scrap_matrix = np.zeros((len(SCENARIO_COMBOS_LNG), len(LEARNING_RATES)))

        for i, scenario in enumerate(SCENARIO_COMBOS_LNG):
            for j, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
                # Load from "Total_Scrap" sheet, then filter by technology
                df = load_scenario_data(lr_code, scenario, "Total_Scrap")
                if df is not None and not df.empty:
                    # Filter for specific technology
                    tech_data = df[df["key_1"] == technology]
                    if not tech_data.empty:
                        year_data = tech_data[tech_data["year"] == year]["value"]
                        if not year_data.empty:
                            scrap_matrix[i, j] = (
                                year_data.iloc[0] / 1e6
                            )  # Convert to megatons
                        else:
                            scrap_matrix[i, j] = 0
                    else:
                        scrap_matrix[i, j] = 0
                else:
                    scrap_matrix[i, j] = 0

        # Create 3D surface
        X = np.arange(len(LEARNING_RATES))
        Y = np.arange(len(SCENARIO_COMBOS_LNG))
        X, Y = np.meshgrid(X, Y)
        Z = scrap_matrix

        surf = ax.plot_surface(
            X, Y, Z, cmap="YlOrRd", alpha=0.8, linewidth=0.5, edgecolor="darkred"
        )

        ax.set_title(f"{technology} Scrap - {year}", fontsize=14)
        ax.set_xlabel("Learning Rate [%]")
        ax.set_ylabel("Price Scenario")
        ax.set_zlabel("Scrap [Mt/year]")

        # Set ticks
        ax.set_xticks(range(len(LEARNING_RATES)))
        ax.set_yticks(range(len(SCENARIO_COMBOS_LNG)))

        lr_labels = [v.split("%")[0] for v in LEARNING_RATES.values()]
        # Use shorter labels for better fit in time evolution plots
        price_labels_short = [label[:6] for label in price_labels_fixed]

        ax.set_xticklabels(lr_labels, fontsize=8)
        ax.set_yticklabels(price_labels_short, fontsize=7)

        ax.view_init(elev=25, azim=225)

    plt.suptitle(f"{technology} Scrap Evolution Over Time", fontsize=16)
    plt.tight_layout()

    output_path = output_dir / f"3d_scrap_time_evolution_{technology}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved time evolution plot: {output_path}")


# plt.show()


def generate_all_scrap_visualizations():
    """
    Generate all recommended scrap visualizations with fixed labeling
    """
    print("Generating cumulative scrap 3D bar charts...")
    plot_3d_scrap_bars_cumulative()

    print("Generating 2040 annual scrap 3D bar charts...")
    plot_3d_scrap_bars_2040()

    print("Generating time evolution 3D surfaces...")
    plot_scrap_time_evolution_3d()

    print("All scrap visualizations completed!")


def plot_lng_lines_by_learning_rate():
    """
    Plot LNG demand over time - separate subplot for each learning rate,
    with different colored lines for each price scenario
    """

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Collect all LNG data
    lng_data = []

    for lr_code, lr_name in LEARNING_RATES.items():
        for scenario in SCENARIO_COMBOS_LNG:
            df = load_scenario_data(lr_code, scenario, "Commodities_Demand")

            if df is not None:
                # Filter for LNG data
                lng_subset = df[df["key_2"].str.strip() == "LNG"]

                for _, row in lng_subset.iterrows():
                    lng_data.append(
                        {
                            "year": row["year"],
                            "lng_bcm": mwh_to_bcm(row["value"]),
                            "lr_code": lr_code,
                            "lr_name": lr_name,
                            "scenario": scenario,
                        }
                    )

    df_lng = pd.DataFrame(lng_data)

    if df_lng.empty:
        print("No LNG data found!")
        return

    # Get fixed price labels
    price_labels_fixed = get_fixed_price_labels()
    price_label_map = dict(zip(SCENARIO_COMBOS_LNG, price_labels_fixed))

    # Split learning rates into groups of 4 for multiple PNGs
    lr_items = list(LEARNING_RATES.items())
    lr_groups = [lr_items[i : i + 4] for i in range(0, len(lr_items), 4)]

    # Colors for price scenarios
    colors = sns.color_palette("tab10", len(SCENARIO_COMBOS_LNG))
    color_map = dict(zip(SCENARIO_COMBOS_LNG, colors))

    for group_idx, lr_group in enumerate(lr_groups):
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()

        for i, (lr_code, lr_name) in enumerate(lr_group):
            ax = axes[i]

            # Plot each price scenario as a separate line
            for scenario in SCENARIO_COMBOS_LNG:
                scenario_data = df_lng[
                    (df_lng["lr_code"] == lr_code) & (df_lng["scenario"] == scenario)
                ]

                if not scenario_data.empty:
                    scenario_data_sorted = scenario_data.sort_values("year")
                    ax.plot(
                        scenario_data_sorted["year"],
                        scenario_data_sorted["lng_bcm"],
                        color=color_map[scenario],
                        linewidth=2,
                        marker="o",
                        markersize=4,
                        label=price_label_map[scenario],
                        alpha=0.8,
                    )

            ax.set_xlabel("Year")
            ax.set_ylabel("LNG Demand (BCM)")
            ax.set_title(f"{lr_name}")
            ax.grid(True, alpha=0.3)

            # Add legend to first subplot only
            if i == 0:
                ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

        # Hide unused subplots if we have fewer than 4 in this group
        for i in range(len(lr_group), 4):
            axes[i].set_visible(False)

        plt.suptitle(
            f"LNG Demand by Price Scenario - Group {group_idx + 1}", fontsize=16
        )
        plt.tight_layout()

        output_path = output_dir / f"lng_lines_by_lr_group_{group_idx + 1}.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Saved LNG lines by LR6 group {group_idx + 1}: {output_path}")
    #  plt.show()


def plot_lng_lines_by_price_scenario():
    """
    Plot LNG demand over time - separate subplot for each price scenario,
    with different colored lines for each learning rate
    """

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Collect all LNG data
    lng_data = []

    for lr_code, lr_name in LEARNING_RATES.items():
        for scenario in SCENARIO_COMBOS_LNG:
            df = load_scenario_data(lr_code, scenario, "Commodities_Demand")

            if df is not None:
                # Filter for LNG data
                lng_subset = df[df["key_2"].str.strip() == "LNG"]

                for _, row in lng_subset.iterrows():
                    lng_data.append(
                        {
                            "year": row["year"],
                            "lng_bcm": mwh_to_bcm(row["value"]),
                            "lr_code": lr_code,
                            "lr_name": lr_name,
                            "scenario": scenario,
                        }
                    )

    df_lng = pd.DataFrame(lng_data)

    if df_lng.empty:
        print("No LNG data found!")
        return

    # Get fixed price labels
    price_labels_fixed = get_fixed_price_labels()
    price_label_map = dict(zip(SCENARIO_COMBOS_LNG, price_labels_fixed))

    # Split price scenarios into groups of 4 for multiple PNGs
    scenario_groups = [
        SCENARIO_COMBOS_LNG[i : i + 4] for i in range(0, len(SCENARIO_COMBOS_LNG), 4)
    ]

    # Colors for learning rates
    colors = sns.color_palette("viridis", len(LEARNING_RATES))
    lr_color_map = dict(zip(LEARNING_RATES.keys(), colors))

    for group_idx, scenario_group in enumerate(scenario_groups):
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()

        for i, scenario in enumerate(scenario_group):
            ax = axes[i]

            # Plot each learning rate as a separate line
            for lr_code, lr_name in LEARNING_RATES.items():
                lr_data = df_lng[
                    (df_lng["scenario"] == scenario) & (df_lng["lr_code"] == lr_code)
                ]

                if not lr_data.empty:
                    lr_data_sorted = lr_data.sort_values("year")
                    ax.plot(
                        lr_data_sorted["year"],
                        lr_data_sorted["lng_bcm"],
                        color=lr_color_map[lr_code],
                        linewidth=2,
                        marker="s",
                        markersize=4,
                        label=lr_name,
                        alpha=0.8,
                    )

            ax.set_xlabel("Year")
            ax.set_ylabel("LNG Demand (BCM)")
            ax.set_title(f"{price_label_map[scenario]}")
            ax.grid(True, alpha=0.3)

            # Add legend to first subplot only
            if i == 0:
                ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

        # Hide unused subplots if we have fewer than 4 in this group
        for i in range(len(scenario_group), 4):
            axes[i].set_visible(False)

        plt.suptitle(
            f"LNG Demand by Learning Rate - Group {group_idx + 1}", fontsize=16
        )
        plt.tight_layout()

        output_path = output_dir / f"lng_lines_by_scenario_group_{group_idx + 1}.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Saved LNG lines by scenario group {group_idx + 1}: {output_path}")
    # plt.show()


def lng_lineplot_horizons(lr_code="LR25", price_scenario="extremely_low"):
    """
    Plot LNG demand over time for a specific LR6 and price scenario combination
    across all rolling horizons. Shows 4 lines (one for each rolling horizon).

    Args:
        lr_code (str): Learning rate code (e.g., "LR1", "LR25")
        price_scenario (str): Price scenario name (e.g., "extremely_low", "average")
    """

    # Create output directory
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)
    print(f"Creating LNG rolling horizon comparison for all LRs and price scenarios...")

    rolling_horizons = [
        "rolling_2024_to_2050",
        "rolling_2029_to_2050",
        "rolling_2034_to_2050",
        "rolling_2039_to_2050",
    ]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    markers = ["o", "s", "^", "D"]

    all_price_scenarios = SCENARIO_COMBOS_LNG_NZ  # + SCENARIO_COMBOS_LNG_PF

    for lr_code, lr_name in LEARNING_RATES.items():
        for price_scenario in all_price_scenarios:
            plt.figure(figsize=(14, 8))
            print(f"LR6: {lr_code}, Price scenario: {price_scenario}")
            for horizon_idx, rolling_horizon in enumerate(rolling_horizons):
                df = load_rolling_horizon_data(
                    lr_code, rolling_horizon, price_scenario, "e_pro_in"
                )
                if df is not None:
                    df["com"] = df["com"].str.strip()
                    lng_data = df[(df["com"] == "LNG") & (df["stf"] <= 2040)]
                    if not lng_data.empty:
                        yearly_lng = (
                            lng_data.groupby("stf")["e_pro_in"].sum().reset_index()
                        )
                        yearly_lng["lng_bcm"] = yearly_lng["e_pro_in"].apply(mwh_to_bcm)
                        yearly_lng = yearly_lng.sort_values("stf")
                        plt.plot(
                            yearly_lng["stf"],
                            yearly_lng["lng_bcm"],
                            color=colors[horizon_idx],
                            marker=markers[horizon_idx],
                            linewidth=2,
                            markersize=6,
                            label=f"{rolling_horizon.replace('_', ' ').title()}",
                            alpha=0.8,
                        )
            plt.xlabel("Year")
            plt.ylabel("LNG Demand (BCM)")
            plt.title(
                f"LNG Demand Over Time: {lr_code} - {price_scenario.replace('_', ' ').title()}"
            )
            plt.legend(
                title="Rolling Horizons", bbox_to_anchor=(1.05, 1), loc="upper left"
            )
            plt.grid(True, linestyle="--", alpha=0.7)
            plt.xlim(None, 2041)
            plt.tight_layout()
            output_path = (
                output_dir / f"lng_lineplot_horizons_{lr_code}_{price_scenario}.png"
            )
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()


def plot_lng_demand_rolling_horizon_boxplots():
    """
    Plot LNG demand boxplots from rolling horizon results
    - For 2030: 2 side-by-side plots for rolling_2024_to_2050 vs rolling_2029_to_2050
    - For 2040: 4 plots (2x2) for rolling_2024_to_2050, rolling_2029_to_2050, rolling_2034_to_2050, rolling_2039_to_2050
    X-axis: Price Scenarios, Boxplots contain values from all learning rates for each price scenario
    Y-axis: Centered around median (median = 0), showing deviations from median
    """

    # Create output directory
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)
    print(f"Creating LNG demand rolling horizon boxplots...")

    # Define rolling horizon folders for each target year
    rolling_horizons_2030 = ["rolling_2024_to_2050", "rolling_2029_to_2050"]
    rolling_horizons_2040 = [
        "rolling_2024_to_2050",
        "rolling_2029_to_2050",
        "rolling_2034_to_2050",
        "rolling_2039_to_2050",
    ]

    # ===== PLOT FOR 2030 (2 side-by-side subplots) =====
    print("Generating 2030 LNG demand rolling horizon boxplots...")
    fig_2030, axes_2030 = plt.subplots(1, 2, figsize=(20, 8))

    for horizon_idx, rolling_horizon in enumerate(rolling_horizons_2030):
        ax = axes_2030[horizon_idx]
        print(f"  Processing {rolling_horizon}")

        # Collect data for this rolling horizon - organized by PRICE SCENARIOS (x-axis)
        data_for_boxplot = []
        labels_for_boxplot = []
        all_values = []  # Collect all values to calculate median

        # For each price scenario, collect data from all learning rates
        for scenario in SCENARIO_COMBOS_LNG:
            scenario_data = []

            for lr_code, lr_name in LEARNING_RATES.items():
                df = load_rolling_horizon_data(
                    lr_code, rolling_horizon, scenario, "e_pro_in"
                )

                if df is not None:
                    # Strip whitespace from commodity names
                    df["com"] = df["com"].str.strip()

                    # Filter for LNG data in 2030
                    lng_data = df[(df["com"] == "LNG") & (df["stf"] == 2030)]
                    if not lng_data.empty:
                        lng_demand_mwh = lng_data["e_pro_in"].sum()
                        lng_demand_bcm = mwh_to_bcm(lng_demand_mwh)
                        scenario_data.append(lng_demand_bcm)
                        all_values.append(lng_demand_bcm)
                    else:
                        scenario_data.append(0)
                else:
                    scenario_data.append(0)

            data_for_boxplot.append(scenario_data)
            labels_for_boxplot.append(scenario.replace("_", " ").title())

        # Check if we have any non-zero data
        non_zero_values = [val for val in all_values if val > 0]
        has_data = len(non_zero_values) > 0
        print(f"    Has data: {has_data}")

        if not has_data:
            ax.text(
                0.5,
                0.5,
                f"No LNG data available\nfor {rolling_horizon}",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=14,
            )
            ax.set_title(f"{rolling_horizon.replace('_', ' ').title()} - No Data")
            continue

        # Calculate median of all non-zero values for centering
        median_value = np.median(non_zero_values)
        print(f"    Median value: {median_value:.2f} BCM")

        # Center all data around median (subtract median from each value)
        data_for_boxplot_centered = []
        for scenario_data in data_for_boxplot:
            centered_data = [
                (val - median_value) if val > 0 else 0 for val in scenario_data
            ]
            data_for_boxplot_centered.append(centered_data)

        # Create boxplot colors
        colors_gradient = sns.color_palette("Blues", n_colors=len(SCENARIO_COMBOS_LNG))
        colors_gradient = [to_hex(c) for c in colors_gradient]

        # Create boxplot
        box_plot = ax.boxplot(
            data_for_boxplot_centered,
            labels=labels_for_boxplot,
            patch_artist=True,
            showmeans=True,
            meanprops={
                "marker": "D",
                "markerfacecolor": "red",
                "markeredgecolor": "red",
                "markersize": 8,
            },
        )

        # Color the boxes
        for patch, color in zip(box_plot["boxes"], colors_gradient):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        # Add horizontal line at y=0 (median)
        ax.axhline(
            y=0, color="black", linestyle="-", linewidth=1, alpha=0.8, label="Median"
        )

        # Customize subplot
        ax.set_xlabel("Price Scenarios")
        ax.set_ylabel("LNG Demand Deviation from Median (BCM)")
        ax.set_title(
            f"{rolling_horizon.replace('_', ' ').title()}\n(Median: {median_value:.2f} BCM)"
        )
        ax.grid(True, alpha=0.3)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # Set y-axis limits based on centered data range
        all_centered = [
            val for sublist in data_for_boxplot_centered for val in sublist if val != 0
        ]
        if all_centered:
            y_range = max(abs(min(all_centered)), abs(max(all_centered)))
            ax.set_ylim(-y_range * 1.1, y_range * 1.1)

    # Add overall title and save for 2030
    fig_2030.suptitle(
        "LNG Demand in 2030 - Rolling Horizon Comparison (Centered on Median)",
        fontsize=16,
        y=0.98,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    output_path_2030 = (
        output_dir / "lng_demand_2030_rolling_horizons_boxplots_centered.png"
    )
    plt.savefig(output_path_2030, dpi=300, bbox_inches="tight")
    print(f"✓ Saved LNG demand 2030 plot: {output_path_2030}")

    # ===== PLOT FOR 2040 (4 subplots in 2x2 grid) =====
    print("Generating 2040 LNG demand rolling horizon boxplots...")
    fig_2040, axes_2040 = plt.subplots(2, 2, figsize=(20, 16))
    axes_2040 = axes_2040.flatten()

    for horizon_idx, rolling_horizon in enumerate(rolling_horizons_2040):
        ax = axes_2040[horizon_idx]
        print(f"  Processing {rolling_horizon}")

        # Collect data for this rolling horizon - organized by PRICE SCENARIOS (x-axis)
        data_for_boxplot = []
        labels_for_boxplot = []
        all_values = []  # Collect all values to calculate median

        # For each price scenario, collect data from all learning rates
        for scenario in SCENARIO_COMBOS_LNG:
            scenario_data = []

            for lr_code, lr_name in LEARNING_RATES.items():
                df = load_rolling_horizon_data(
                    lr_code, rolling_horizon, scenario, "e_pro_in"
                )

                if df is not None:
                    # Strip whitespace from commodity names
                    df["com"] = df["com"].str.strip()

                    # Filter for LNG data in 2040
                    lng_data = df[(df["com"] == "LNG") & (df["stf"] == 2040)]
                    if not lng_data.empty:
                        lng_demand_mwh = lng_data["e_pro_in"].sum()
                        lng_demand_bcm = mwh_to_bcm(lng_demand_mwh)
                        scenario_data.append(lng_demand_bcm)
                        all_values.append(lng_demand_bcm)
                    else:
                        scenario_data.append(0)
                else:
                    scenario_data.append(0)

            data_for_boxplot.append(scenario_data)
            labels_for_boxplot.append(scenario.replace("_", " ").title())

        # Check if we have any non-zero data
        non_zero_values = [val for val in all_values if val > 0]
        has_data = len(non_zero_values) > 0
        print(f"    Has data: {has_data}")

        if not has_data:
            ax.text(
                0.5,
                0.5,
                f"No LNG data available\nfor {rolling_horizon}",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=14,
            )
            ax.set_title(f"{rolling_horizon.replace('_', ' ').title()} - No Data")
            continue

        # Calculate median of all non-zero values for centering
        median_value = np.median(non_zero_values)
        print(f"    Median value: {median_value:.2f} BCM")

        # Center all data around median (subtract median from each value)
        data_for_boxplot_centered = []
        for scenario_data in data_for_boxplot:
            centered_data = [
                (val - median_value) if val > 0 else 0 for val in scenario_data
            ]
            data_for_boxplot_centered.append(centered_data)

        # Create boxplot colors
        colors_gradient = sns.color_palette("Blues", n_colors=len(SCENARIO_COMBOS_LNG))
        colors_gradient = [to_hex(c) for c in colors_gradient]

        # Create boxplot
        box_plot = ax.boxplot(
            data_for_boxplot_centered,
            labels=labels_for_boxplot,
            patch_artist=True,
            showmeans=True,
            meanprops={
                "marker": "D",
                "markerfacecolor": "red",
                "markeredgecolor": "red",
                "markersize": 8,
            },
        )

        # Color the boxes
        for patch, color in zip(box_plot["boxes"], colors_gradient):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        # Add horizontal line at y=0 (median)
        ax.axhline(y=0, color="black", linestyle="-", linewidth=1, alpha=0.8)

        # Customize subplot
        ax.set_xlabel("Price Scenarios")
        ax.set_ylabel("LNG Demand Deviation from Median (BCM)")
        ax.set_title(
            f"{rolling_horizon.replace('_', ' ').title()}\n(Median: {median_value:.2f} BCM)"
        )
        ax.grid(True, alpha=0.3)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # Set y-axis limits based on centered data range
        all_centered = [
            val for sublist in data_for_boxplot_centered for val in sublist if val != 0
        ]
        if all_centered:
            y_range = max(abs(min(all_centered)), abs(max(all_centered)))
            ax.set_ylim(-y_range * 1.1, y_range * 1.1)

    # Add overall title and save for 2040
    fig_2040.suptitle(
        "LNG Demand in 2040 - Rolling Horizon Comparison (Centered on Median)",
        fontsize=16,
        y=0.98,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    output_path_2040 = (
        output_dir / "lng_demand_2040_rolling_horizons_boxplots_centered.png"
    )
    plt.savefig(output_path_2040, dpi=300, bbox_inches="tight")
    print(f"✓ Saved LNG demand 2040 plot: {output_path_2040}")

    print("✓ Rolling horizon boxplot generation completed successfully!")

    # Close figures to free memory
    plt.close(fig_2030)
    plt.close(fig_2040)


def plot_capacity_mix_stacked_bars():
    """Plot capacity mix as true stacked bar plots with all technologies stacked vertically,
    using pastel Set3 palette for tech colors and hatches for supply options. Legend is separated:
    one for tech (color), one for supply (hatch). 'Imported' is filled with process color, no hatch."""

    tech_stack_order = [
        "solarPV",
        "windon",
        "windoff",
        "Gas Plant (CCGT)",
        "Gas Plant (CCGT) LNG",
    ]
    renewable_technologies = ["solarPV", "windon", "windoff"]
    other_technologies = ["Gas Plant (CCGT)", "Gas Plant (CCGT) LNG"]
    years_to_plot = [2030, 2040]

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Pastel color palette via seaborn
    n_techs = len(tech_stack_order)
    colors = sns.color_palette("Set3", n_colors=n_techs)
    tech_colors = {tech: colors[i] for i, tech in enumerate(tech_stack_order)}

    supply_sources = {
        "capacity_ext_eusecondary": {
            "label": "Remanufacturing",
            "hatch": "..",
            "alpha_adjust": 0.0,
        },
        "capacity_ext_stockout": {
            "label": "Stock",
            "hatch": "//",
            "alpha_adjust": -0.1,
        },
        "capacity_ext_euprimary": {
            "label": "Manufacturing",
            "hatch": "xx",
            "alpha_adjust": -0.2,
        },
        "capacity_ext_imported": {
            "label": "Imported",
            "hatch": None,
            "alpha_adjust": -0.3,
        },
    }
    supply_order = [
        "capacity_ext_eusecondary",
        "capacity_ext_stockout",
        "capacity_ext_euprimary",
        "capacity_ext_imported",
    ]

    for lr_key, lr_name in LEARNING_RATES.items():
        for target_year in years_to_plot:
            fig, ax = plt.subplots(1, 1, figsize=(14, 8))

            capacity_data = {tech: [] for tech in tech_stack_order}
            supply_composition = {
                tech: {source: [] for source in supply_order}
                for tech in renewable_technologies
            }
            scenario_labels = []

            for price_scenario in SCENARIO_COMBOS_LNG:
                try:
                    file_path = (
                        Path(RESULTS_BASE_PATH)
                        / f"{lr_key}"
                        / "rolling_2024_to_2050"
                        / f"scenario_{price_scenario}.xlsx"
                    )
                    if not file_path.exists():
                        for tech in tech_stack_order:
                            capacity_data[tech].append(0)
                        for tech in renewable_technologies:
                            for source in supply_order:
                                supply_composition[tech][source].append(0)
                        continue

                    try:
                        extension_df = pd.read_excel(
                            file_path, sheet_name="extension_only_caps"
                        )
                        extension_df["stf"] = extension_df["stf"].fillna(method="ffill")
                        extension_df["stf"] = pd.to_numeric(
                            extension_df["stf"], errors="coerce"
                        )
                        extension_df = extension_df.dropna(subset=["stf"])
                    except:
                        for tech in renewable_technologies:
                            capacity_data[tech].append(0)
                            for source in supply_order:
                                supply_composition[tech][source].append(0)
                        try:
                            total_caps_df = pd.read_excel(
                                file_path, sheet_name="extension_total_caps"
                            )
                            total_caps_df["stf"] = total_caps_df["stf"].fillna(
                                method="ffill"
                            )
                            target_year_caps = total_caps_df[
                                total_caps_df["stf"] == target_year
                            ]
                            for tech in other_technologies:
                                tech_data = target_year_caps[
                                    target_year_caps["pro"] == tech
                                ]
                                if not tech_data.empty:
                                    capacity = tech_data["cap_pro"].iloc[0] / 1000
                                    capacity_data[tech].append(capacity)
                                else:
                                    capacity_data[tech].append(0)
                        except:
                            for tech in other_technologies:
                                capacity_data[tech].append(0)
                        continue

                    total_caps_df = pd.read_excel(
                        file_path, sheet_name="extension_total_caps"
                    )
                    total_caps_df["stf"] = total_caps_df["stf"].fillna(method="ffill")
                    target_year_caps = total_caps_df[
                        total_caps_df["stf"] == target_year
                    ]
                    scenario_labels.append(price_scenario.replace("_", " ").title())

                    for tech in renewable_technologies:
                        if tech in extension_df["tech"].unique():
                            tech_data = extension_df[extension_df["tech"] == tech]
                            cumulative_data = tech_data[tech_data["stf"] <= target_year]
                            total_capacity = 0
                            for source in supply_order:
                                if source in cumulative_data.columns:
                                    cumulative_value = (
                                        cumulative_data[source].sum() / 1000
                                    )
                                    supply_composition[tech][source].append(
                                        cumulative_value
                                    )
                                    total_capacity += cumulative_value
                                else:
                                    supply_composition[tech][source].append(0)
                            capacity_data[tech].append(total_capacity)
                        else:
                            capacity_data[tech].append(0)
                            for source in supply_order:
                                supply_composition[tech][source].append(0)

                    for tech in other_technologies:
                        tech_data = target_year_caps[target_year_caps["pro"] == tech]
                        if not tech_data.empty:
                            capacity = tech_data["cap_pro"].iloc[0] / 1000
                            capacity_data[tech].append(capacity)
                        else:
                            capacity_data[tech].append(0)

                except Exception as e:
                    for tech in tech_stack_order:
                        capacity_data[tech].append(0)
                    for tech in renewable_technologies:
                        for source in supply_order:
                            supply_composition[tech][source].append(0)

            x_positions = np.arange(len(scenario_labels))
            bar_width = 0.6
            current_bottom = np.zeros(len(scenario_labels))

            # Plot stacked bars (no labels, to keep legend clean)
            for tech in tech_stack_order:
                if tech in renewable_technologies:
                    tech_bottom = current_bottom.copy()
                    base_color = tech_colors[tech]
                    for source in supply_order:
                        values = np.array(supply_composition[tech][source])
                        if np.any(values > 0):
                            source_info = supply_sources[source]
                            alpha = max(0.4, 0.9 + source_info["alpha_adjust"])
                            if source == "capacity_ext_imported":
                                # Fill with tech color, no hatch, as requested
                                bars = ax.bar(
                                    x_positions,
                                    values,
                                    bar_width,
                                    bottom=tech_bottom,
                                    color=base_color,
                                    alpha=alpha,
                                    hatch=None,
                                    edgecolor="black",
                                    linewidth=0.5,
                                    label=None,
                                )
                            else:
                                bars = ax.bar(
                                    x_positions,
                                    values,
                                    bar_width,
                                    bottom=tech_bottom,
                                    color=base_color,
                                    alpha=alpha,
                                    hatch=source_info["hatch"],
                                    edgecolor="black",
                                    linewidth=0.5,
                                    label=None,
                                )
                            tech_bottom += values
                    current_bottom = tech_bottom
                else:
                    values = np.array(capacity_data[tech])
                    if np.any(values > 0):
                        bars = ax.bar(
                            x_positions,
                            values,
                            bar_width,
                            bottom=current_bottom,
                            color=tech_colors[tech],
                            alpha=0.8,
                            edgecolor="black",
                            linewidth=0.5,
                            label=None,
                        )
                        current_bottom += values

            # Add value labels
            for i, x_pos in enumerate(x_positions):
                total_value = current_bottom[i]
                if total_value > 0:
                    ax.text(
                        x_pos,
                        total_value + total_value * 0.02,
                        f"{total_value:.0f} GW",
                        ha="center",
                        va="bottom",
                        fontsize=10,
                        fontweight="bold",
                    )

            ax.set_xlabel("Price Scenarios", fontsize=14)
            ax.set_ylabel(f"Cumulative Capacity 2024-{target_year} (GW)", fontsize=14)
            ax.set_title(
                f"{lr_name} - Base Case Technology Mix until {target_year}", fontsize=16
            )
            ax.grid(True, alpha=0.3, axis="y")
            ax.set_xticks(x_positions)
            ax.set_xticklabels(scenario_labels, rotation=45, ha="right")

            # ---- LEGEND PATCHES ----
            tech_patches = [
                mpatches.Patch(
                    facecolor=tech_colors[tech], label=tech, edgecolor="black"
                )
                for tech in tech_stack_order
            ]
            supply_patches = [
                mpatches.Patch(
                    facecolor="lightgray",
                    edgecolor="black",
                    hatch=supply_sources[src]["hatch"],
                    label=supply_sources[src]["label"],
                )
                for src in supply_order
                if supply_sources[src]["hatch"]
            ]
            first_legend = ax.legend(
                handles=tech_patches,
                title="Technologie (Farbe)",
                loc="upper left",
                bbox_to_anchor=(1.01, 1.0),
                fontsize=11,
                title_fontsize=12,
            )
            ax.add_artist(first_legend)
            second_legend = ax.legend(
                handles=supply_patches,
                title="Supply Option (Muster)",
                loc="upper left",
                bbox_to_anchor=(1.01, 0.52),
                fontsize=11,
                title_fontsize=12,
            )

            plt.tight_layout()
            safe_lr_name = lr_key
            output_path = (
                output_dir / f"{safe_lr_name}_stacked_capacity_mix_{target_year}.png"
            )
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            # plt.show()
            plt.close()

        print(f"✓ Completed stacked analysis for {lr_name}")

    print("✓ All stacked capacity plots completed!")


def plot_stock_level_facet_per_technology():
    """
    Creates one PNG with 4 subplots (facets), one for each technology (solarPV, windon, windoff, Batteries).
    Each subplot shows the yearly stock level (capacity_ext_stock) from 2024 to 2040.
    Each scenario is a separate line in the subplot.
    """
    tech_stack_order = ["solarPV", "windon", "windoff", "Batteries"]
    years = list(range(2024, 2041))
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Pastel color palette for techs (for subplot titles, etc)
    n_techs = len(tech_stack_order)
    colors = sns.color_palette("Set3", n_colors=n_techs)
    tech_colors = {tech: colors[i] for i, tech in enumerate(tech_stack_order)}

    # Use Set1 for scenarios (distinct lines)
    scenario_colors = sns.color_palette("Set1", n_colors=len(SCENARIO_COMBOS_LNG))
    scenario_color_map = {
        sc: scenario_colors[i] for i, sc in enumerate(SCENARIO_COMBOS_LNG)
    }

    print(f"Processing stock levels for technologies: {tech_stack_order}")
    print(f"Price scenarios: {SCENARIO_COMBOS_LNG}")
    print(f"Results base path: {RESULTS_BASE_PATH}")

    for lr_key, lr_name in LEARNING_RATES.items():
        print(f"\nProcessing learning rate: {lr_name}")

        fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharex=True, sharey=False)
        axes = axes.flatten()

        for idx, tech in enumerate(tech_stack_order):
            ax = axes[idx]
            print(f"  Processing technology: {tech}")

            lines_plotted = 0

            for sc in SCENARIO_COMBOS_LNG:
                file_path = (
                    Path(RESULTS_BASE_PATH)
                    / f"{lr_key}"
                    / "rolling_2024_to_2050"
                    / f"scenario_{sc}.xlsx"
                )
                if not file_path.exists():
                    print(f"    File not found: {file_path}")
                    continue

                try:
                    # Load data
                    df = pd.read_excel(file_path, sheet_name="extension_only_caps")

                    # Forward fill stf column
                    df["stf"] = df["stf"].fillna(method="ffill")

                    # Filter for technology
                    tech_df = df[df["tech"] == tech].copy()

                    if tech_df.empty:
                        print(f"    No data for {tech} in {sc}")
                        continue

                    # Filter for years 2024-2040
                    year_df = tech_df[tech_df["stf"].between(2024, 2040)]

                    if year_df.empty:
                        print(f"    No year data for {tech} in {sc}")
                        continue

                    # Check if capacity_ext_stock column exists
                    if "capacity_ext_stock" not in year_df.columns:
                        print(
                            f"    'capacity_ext_stock' column not found for {tech} in {sc}"
                        )
                        continue

                    # DIREKTE WERTE pro Jahr verwenden - NICHT summieren!
                    # Stock Level sind bereits aktuelle Bestände pro Jahr
                    yearly_stock = year_df.set_index("stf")["capacity_ext_stock"]

                    # Convert MW to GW
                    yearly_stock = yearly_stock / 1000

                    # Reindex to ensure all years are present
                    stock_per_year = yearly_stock.reindex(years, fill_value=0)

                    # Check if we have any non-zero data
                    if stock_per_year.sum() > 0:
                        # Plot the line
                        ax.plot(
                            stock_per_year.index,
                            stock_per_year.values,
                            marker="o",
                            markersize=4,
                            linewidth=2,
                            label=sc.replace("_", " ").title(),
                            color=scenario_color_map[sc],
                            alpha=0.8,
                        )
                        lines_plotted += 1
                        print(
                            f"    Plotted {tech} - {sc}: max={stock_per_year.max():.1f} GW"
                        )
                    else:
                        print(f"    No non-zero data for {tech} in {sc}")

                except Exception as e:
                    print(f"    Error for {sc} - {tech}: {e}")
                    continue

            # Customize subplot
            ax.set_title(
                f"{tech}", fontsize=14, fontweight="bold", color=tech_colors[tech]
            )
            ax.grid(True, alpha=0.3)

            if idx % 2 == 0:  # Left column
                ax.set_ylabel("Stock Level (GW)", fontsize=12)
            if idx >= 2:  # Bottom row
                ax.set_xlabel("Year", fontsize=12)

            ax.set_xticks(years[::2])  # Every 2 years
            ax.set_xlim([2024, 2040])
            ax.set_ylim(bottom=0)

            print(f"    Plotted {lines_plotted} lines for {tech}")

        # Add legend to the first subplot with better positioning
        if len(SCENARIO_COMBOS_LNG) > 0:
            axes[0].legend(
                title="Price Scenario",
                fontsize=9,
                title_fontsize=10,
                bbox_to_anchor=(1.05, 1),
                loc="upper left",
            )

        plt.suptitle(
            f"Stock Level Evolution 2024-2040\n{lr_name}",
            fontsize=16,
            fontweight="bold",
        )
        plt.tight_layout(rect=[0, 0, 1, 0.94])

        output_path = output_dir / f"{lr_key}_stock_level_facets.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"✓ Saved: {output_path}")

        # plt.show()
        plt.close()

    print("✓ Stock level facet plots completed!")


def lng_lineplot_range():
    """
    Plot LNG demand range over time showing min/max envelope across all price scenarios.
    Creates separate plots for each learning rate and rolling horizon combination.
    Creates two separate plots: one for LNG_NZ scenarios and one for LNG_PF scenarios.
    """

    # Create output directory
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)
    print(f"Creating LNG range plots for all LRs and rolling horizons...")

    rolling_horizons = [
        "rolling_2024_to_2050",
        "rolling_2029_to_2050",
        "rolling_2034_to_2050",
        "rolling_2039_to_2050",
    ]

    # Different colors for each rolling horizon
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    # Separate NZ and PF scenarios
    nz_scenarios = SCENARIO_COMBOS_LNG_NZ
    pf_scenarios = SCENARIO_COMBOS_LNG_PF

    for lr_code, lr_name in LEARNING_RATES.items():
        print(f"Processing LR6: {lr_code}")

        # ===== PLOT 1: LNG_NZ SCENARIOS =====
        plt.figure(figsize=(14, 8))

        for horizon_idx, rolling_horizon in enumerate(rolling_horizons):
            print(f"  Processing NZ horizon: {rolling_horizon}")

            # Process NZ scenarios only
            nz_scenario_data = {}  # year -> [values across NZ scenarios]
            for price_scenario in nz_scenarios:
                df = load_rolling_horizon_data(
                    lr_code, rolling_horizon, price_scenario, "e_pro_in"
                )
                if df is not None:
                    df["com"] = df["com"].str.strip()
                    lng_data = df[(df["com"] == "LNG") & (df["stf"] <= 2040)]
                    if not lng_data.empty:
                        yearly_lng = (
                            lng_data.groupby("stf")["e_pro_in"].sum().reset_index()
                        )
                        yearly_lng["lng_bcm"] = yearly_lng["e_pro_in"].apply(mwh_to_bcm)

                        for _, row in yearly_lng.iterrows():
                            year = row["stf"]
                            bcm = row["lng_bcm"]
                            if year not in nz_scenario_data:
                                nz_scenario_data[year] = []
                            nz_scenario_data[year].append(bcm)

            # Plot NZ range
            if nz_scenario_data:
                years_nz = sorted(nz_scenario_data.keys())
                min_values_nz = []
                max_values_nz = []

                for year in years_nz:
                    values = nz_scenario_data[year]
                    if values:
                        min_v = min(values)
                        max_v = max(values)
                        if max_v > 0:
                            any_nonzero = True
                    else:
                        min_v = 0
                        max_v = 0
                    min_values_nz.append(min_v)
                    max_values_nz.append(max_v)

                if years_nz and any(max_values_nz):
                    # Plot NZ range
                    plt.fill_between(
                        years_nz,
                        min_values_nz,
                        max_values_nz,
                        color=colors[horizon_idx],
                        alpha=0.3,
                        label=f"{rolling_horizon.replace('_', ' ').title()} (Range)",
                    )

                    # Plot NZ min and max lines
                    plt.plot(
                        years_nz,
                        min_values_nz,
                        color=colors[horizon_idx],
                        linestyle="--",
                        linewidth=1.5,
                        label=f"{rolling_horizon.replace('_', ' ').title()} (Min)",
                    )

                    plt.plot(
                        years_nz,
                        max_values_nz,
                        color=colors[horizon_idx],
                        linestyle="-",
                        linewidth=2,
                        label=f"{rolling_horizon.replace('_', ' ').title()} (Max)",
                    )

                    print(
                        f"    Plotted NZ range: {min(min_values_nz):.1f} - {max(max_values_nz):.1f} BCM"
                    )

        # Finalize NZ plot
        plt.xlabel("Year")
        plt.ylabel("LNG Demand (BCM)")
        plt.title(f"LNG Demand Range: Net Zero Scenarios\n{lr_name}")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=9)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.xlim(None, 2041)
        plt.tight_layout()

        output_path_nz = output_dir / f"lng_range_plot_NZ_{lr_code}.png"
        plt.savefig(output_path_nz, dpi=300, bbox_inches="tight")
        print(f"✓ Saved NZ plot: {output_path_nz}")
        # plt.show()
        plt.close()

        # ===== PLOT 2: LNG_PF SCENARIOS =====
        plt.figure(figsize=(14, 8))

        for horizon_idx, rolling_horizon in enumerate(rolling_horizons):
            print(f"  Processing PF horizon: {rolling_horizon}")

            # Process PF scenarios only
            pf_scenario_data = {}  # year -> [values across PF scenarios]
            for price_scenario in pf_scenarios:
                df = load_rolling_horizon_data(
                    lr_code, rolling_horizon, price_scenario, "e_pro_in"
                )
                if df is not None:
                    df["com"] = df["com"].str.strip()
                    lng_data = df[(df["com"] == "LNG") & (df["stf"] <= 2040)]
                    if not lng_data.empty:
                        yearly_lng = (
                            lng_data.groupby("stf")["e_pro_in"].sum().reset_index()
                        )
                        yearly_lng["lng_bcm"] = yearly_lng["e_pro_in"].apply(mwh_to_bcm)

                        for _, row in yearly_lng.iterrows():
                            year = row["stf"]
                            bcm = row["lng_bcm"]
                            if year not in pf_scenario_data:
                                pf_scenario_data[year] = []
                            pf_scenario_data[year].append(bcm)

            # Plot PF range
            if pf_scenario_data:
                years_pf = sorted(pf_scenario_data.keys())
                min_values_pf = []
                max_values_pf = []

                for year in years_pf:
                    values = pf_scenario_data[year]
                    if values:
                        min_values_pf.append(min(values))
                        max_values_pf.append(max(values))
                    else:
                        min_values_pf.append(0)
                        max_values_pf.append(0)

                if years_pf and any(max_values_pf):
                    # Plot PF range with different styling
                    plt.fill_between(
                        years_pf,
                        min_values_pf,
                        max_values_pf,
                        color=colors[horizon_idx],
                        alpha=0.4,
                        hatch="///",
                        label=f"{rolling_horizon.replace('_', ' ').title()} (Range)",
                    )

                    # Plot PF min and max lines
                    plt.plot(
                        years_pf,
                        min_values_pf,
                        color=colors[horizon_idx],
                        linestyle="--",
                        linewidth=1.5,
                        label=f"{rolling_horizon.replace('_', ' ').title()} (Min)",
                    )

                    plt.plot(
                        years_pf,
                        max_values_pf,
                        color=colors[horizon_idx],
                        linestyle="-",
                        linewidth=2,
                        label=f"{rolling_horizon.replace('_', ' ').title()} (Max)",
                    )

                    print(
                        f"    Plotted PF range: {min(min_values_pf):.1f} - {max(max_values_pf):.1f} BCM"
                    )

        # Finalize PF plot
        plt.xlabel("Year")
        plt.ylabel("LNG Demand (BCM)")
        plt.title(f"LNG Demand Range: Persisting Fossil Scenarios\n{lr_name}")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=9)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.xlim(None, 2041)
        plt.tight_layout()

        output_path_pf = output_dir / f"lng_range_plot_PF_{lr_code}.png"
        plt.savefig(output_path_pf, dpi=300, bbox_inches="tight")
        print(f"✓ Saved PF plot: {output_path_pf}")
        # plt.show()
        plt.close()

    print("✓ LNG range plot generation completed!")


def lng_lineplot_range_comp_basecase():
    """Plot LNG demand range (min/max envelope) for 2024-2050 horizon only, displaying
    four ranges in one plot per learning rate:
      1. NZ with NZIA
      2. NZ without NZIA
      3. PF with NZIA
      4. PF without NZIA
    Data directory structure:
      result/results_with_nzia/<LR6>/<rolling_2024_to_2050>/scenario_<price_scenario>.xlsx
      result/results_without_nzia/<LR6>/<rolling_2024_to_2050>/scenario_<price_scenario>.xlsx
    """
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)
    rolling_horizon = "rolling_2024_to_2050"
    years_full = list(range(2024, 2051))

    # Styling for the four groups
    group_definitions = [
        {
            "label": "NZ with NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_NZ,
            "color": "#1f77b4",
            "alpha": 0.30,
            "hatch": None,
        },
        {
            "label": "NZ without NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_NZ,
            "color": "#6baed6",
            "alpha": 0.30,
            "hatch": "..",
        },
        {
            "label": "PF with NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "color": "#d62728",
            "alpha": 0.30,
            "hatch": None,
        },
        {
            "label": "PF without NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "color": "#ff9896",
            "alpha": 0.30,
            "hatch": "//",
        },
    ]

    def load_group_data(base_variant, lr_code, scenarios):
        """Load LNG yearly BCM values for all scenarios in a group for a given LR6.
        Returns dict: year -> list of bcm values across scenarios"""
        data_by_year = {y: [] for y in years_full}
        for scenario in scenarios:
            file_path = (
                Path(RESULTS_BASE_PATH)
                / base_variant
                / lr_code
                / rolling_horizon
                / f"scenario_{scenario}.xlsx"
            )
            if not file_path.exists():
                print(f"  Missing file: {file_path}")
                continue
            try:
                df = pd.read_excel(file_path, sheet_name="e_pro_in")
            except Exception as e:
                print(f"  Error reading {file_path}: {e}")
                continue
            df["com"] = df["com"].astype(str).str.strip()
            lng_df = df[
                (df["com"] == "LNG") & (df["stf"] >= 2024) & (df["stf"] <= 2050)
            ]
            if lng_df.empty:
                continue
            yearly = lng_df.groupby("stf")["e_pro_in"].sum().reset_index()
            yearly["lng_bcm"] = yearly["e_pro_in"].apply(mwh_to_bcm)
            for _, row in yearly.iterrows():
                year = int(row["stf"])
                if year in data_by_year:
                    data_by_year[year].append(row["lng_bcm"])
        return data_by_year

    print("Creating 2024-2050 NZIA comparison LNG range plots...")
    for lr_code, lr_name in LEARNING_RATES.items():
        print(f"Processing LR6 {lr_code} ...")
        plt.figure(figsize=(14, 8))
        for group in group_definitions:
            print(f"  Group: {group['label']}")
            group_data = load_group_data(group["variant"], lr_code, group["scenarios"])
            min_vals = []
            max_vals = []
            any_nonzero = False

            for y in years_full:
                vals = group_data.get(y, [])
                if vals:
                    min_v = min(vals)
                    max_v = max(vals)
                    if max_v > 0:
                        any_nonzero = True
                else:
                    min_v = 0
                    max_v = 0
                min_vals.append(min_v)
                max_vals.append(max_v)

            if any_nonzero:
                # Filled range
                plt.fill_between(
                    years_full,
                    min_vals,
                    max_vals,
                    color=group["color"],
                    alpha=group["alpha"],
                    hatch=group["hatch"],
                    edgecolor=group["color"],
                    label=f"{group['label']} (Range)",
                )
                # Min / Max lines
                plt.plot(
                    years_full,
                    min_vals,
                    color=group["color"],
                    linestyle="--",
                    linewidth=1.2,
                    label=f"{group['label']} (Min)",
                )
                plt.plot(
                    years_full,
                    max_vals,
                    color=group["color"],
                    linestyle="-",
                    linewidth=2,
                    label=f"{group['label']} (Max)",
                )

                print(
                    f"    {group['label']}: {min([v for v in min_vals if v > 0] or [0]):.2f} - {max(max_vals):.2f} BCM"
                )
            else:
                print(f"    Skipped (no non-zero data): {group['label']}")

        plt.xlabel("Year")
        plt.ylabel("LNG Demand (BCM)")
        plt.title(
            f"LNG Demand Ranges 2024-2050 with/without NZIA\n{lr_name} (Non-Scenario Driven)"
        )
        plt.xlim(2024, 2050)
        plt.grid(True, linestyle="--", alpha=0.6)

        # Deduplicate legend entries
        handles, labels = plt.gca().get_legend_handles_labels()
        seen = set()
        dedup_handles = []
        dedup_labels = []
        for h, l in zip(handles, labels):
            if l not in seen:
                seen.add(l)
                dedup_handles.append(h)
                dedup_labels.append(l)

        plt.legend(
            dedup_handles,
            dedup_labels,
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
            fontsize=9,
        )
        plt.tight_layout()

        out_path = output_dir / f"lng_range_plot_nzia_comparison_{lr_code}.png"
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✓ Saved: {out_path}")

    print("✓ Completed 2024-2050 NZIA comparison LNG range plots!")


def lng_lineplot_range_comp_basecase_3x3():
    """Plot LNG demand range (min/max envelope) for 2024-2050 horizon only, displaying
    four ranges in one plot per learning rate in a 3x3 grid layout:
      1. NZ with NZIA
      2. NZ without NZIA
      3. PF with NZIA
      4. PF without NZIA
    Data directory structure:
      result/results_with_nzia/<LR6>/<rolling_2024_to_2050>/scenario_<price_scenario>.xlsx
      result/results_without_nzia/<LR6>/<rolling_2024_to_2050>/scenario_<price_scenario>.xlsx
    """
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)
    rolling_horizon = "rolling_2024_to_2050"
    years_full = list(range(2024, 2051))

    # Styling for the four groups
    group_definitions = [
        {
            "label": "NZ with NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_NZ,
            "color": "#1f77b4",
            "alpha": 0.30,
            "hatch": None,
        },
        {
            "label": "NZ without NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_NZ,
            "color": "#6baed6",
            "alpha": 0.30,
            "hatch": "..",
        },
        {
            "label": "PF with NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "color": "#d62728",
            "alpha": 0.30,
            "hatch": None,
        },
        {
            "label": "PF without NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "color": "#ff9896",
            "alpha": 0.30,
            "hatch": "//",
        },
    ]

    def load_group_data(base_variant, lr_code, scenarios):
        """Load LNG yearly BCM values for all scenarios in a group for a given LR6.
        Returns dict: year -> list of bcm values across scenarios"""
        data_by_year = {y: [] for y in years_full}
        for scenario in scenarios:
            file_path = (
                Path(RESULTS_BASE_PATH)
                / base_variant
                / lr_code
                / rolling_horizon
                / f"scenario_{scenario}.xlsx"
            )
            if not file_path.exists():
                print(f"  Missing file: {file_path}")
                continue
            try:
                df = pd.read_excel(file_path, sheet_name="e_pro_in")
            except Exception as e:
                print(f"  Error reading {file_path}: {e}")
                continue
            df["com"] = df["com"].astype(str).str.strip()
            lng_df = df[
                (df["com"] == "LNG") & (df["stf"] >= 2024) & (df["stf"] <= 2040)
            ]
            if lng_df.empty:
                continue
            yearly = lng_df.groupby("stf")["e_pro_in"].sum().reset_index()
            yearly["lng_bcm"] = yearly["e_pro_in"].apply(mwh_to_bcm)
            for _, row in yearly.iterrows():
                year = int(row["stf"])
                if year in data_by_year:
                    data_by_year[year].append(row["lng_bcm"])
        return data_by_year

    print("Creating 2024-2050 NZIA comparison LNG range plots in 3x3 grid...")

    # Create 3x3 subplot grid
    fig, axes = plt.subplots(3, 3, figsize=(24, 18))
    axes = axes.flatten()

    # Process each learning rate in a subplot
    for idx, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
        if idx >= 9:  # Safety check for 3x3 grid
            break

        ax = axes[idx]
        print(f"Processing LR6 {lr_code} in subplot {idx + 1}...")

        for group in group_definitions:
            print(f"  Group: {group['label']}")
            group_data = load_group_data(group["variant"], lr_code, group["scenarios"])
            min_vals = []
            max_vals = []
            any_nonzero = False

            for y in years_full:
                vals = group_data.get(y, [])
                if vals:
                    min_v = min(vals)
                    max_v = max(vals)
                    if max_v > 0:
                        any_nonzero = True
                else:
                    min_v = 0
                    max_v = 0
                min_vals.append(min_v)
                max_vals.append(max_v)

            if any_nonzero:
                # Filled range
                ax.fill_between(
                    years_full,
                    min_vals,
                    max_vals,
                    color=group["color"],
                    alpha=group["alpha"],
                    hatch=group["hatch"],
                    edgecolor=group["color"],
                    label=f"{group['label']} (Range)",
                )
                # Min / Max lines
                ax.plot(
                    years_full,
                    min_vals,
                    color=group["color"],
                    linestyle="--",
                    linewidth=1.2,
                    label=f"{group['label']} (Min)",
                )
                ax.plot(
                    years_full,
                    max_vals,
                    color=group["color"],
                    linestyle="-",
                    linewidth=2,
                    label=f"{group['label']} (Max)",
                )

                print(
                    f"    {group['label']}: {min([v for v in min_vals if v > 0] or [0]):.2f} - {max(max_vals):.2f} BCM"
                )
            else:
                print(f"    Skipped (no non-zero data): {group['label']}")

        # Customize each subplot
        ax.set_xlabel("Year", fontsize=10)
        ax.set_ylabel("LNG Demand (BCM)", fontsize=10)
        ax.set_title(f"{lr_name}", fontsize=12, fontweight="bold")
        ax.set_xlim(2024, 2040)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.tick_params(axis="both", which="major", labelsize=9)

        # Add legend only to the first subplot to avoid clutter
        if idx == 0:
            # Deduplicate legend entries
            handles, labels = ax.get_legend_handles_labels()
            seen = set()
            dedup_handles = []
            dedup_labels = []
            for h, l in zip(handles, labels):
                if l not in seen:
                    seen.add(l)
                    dedup_handles.append(h)
                    dedup_labels.append(l)

            ax.legend(
                dedup_handles,
                dedup_labels,
                bbox_to_anchor=(1.05, 1),
                loc="upper left",
                fontsize=8,
            )

    # Hide empty subplots if there are fewer than 9 learning rates
    for idx in range(len(LEARNING_RATES), 9):
        axes[idx].set_visible(False)

    # Add overall title
    fig.suptitle(
        "LNG Demand Ranges 2024-2040 with/without NZIA by Learning Rate (non-Scenario Driven)",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    out_path = output_dir / "lng_range_plot_nzia_comparison_all_lr.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved: {out_path}")

    print("✓ Completed 2024-2040 NZIA comparison LNG range plots in 3x3 grid!")


def co2_lineplot_range_comp_basecase():
    """Plot CO2 emissions range (min/max envelope) for 2024-2050 horizon in a 3x3 grid.
    Each subplot shows one learning rate with four ranges:
      1. NZ with NZIA
      2. NZ without NZIA
      3. PF with NZIA
      4. PF without NZIA
    Data from "us_co2" sheet: stf (year), pro (process), value (tons CO2).
    Sums yearly CO2 values across all processes per year.
    """
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)
    rolling_horizon = "rolling_2024_to_2050"
    years_full = list(range(2024, 2051))

    # Styling for the four groups
    group_definitions = [
        {
            "label": "NZ with NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_NZ,
            "color": "#1f77b4",
            "alpha": 0.30,
            "hatch": None,
        },
        {
            "label": "NZ without NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_NZ,
            "color": "#6baed6",
            "alpha": 0.30,
            "hatch": "..",
        },
        {
            "label": "PF with NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "color": "#d62728",
            "alpha": 0.30,
            "hatch": None,
        },
        {
            "label": "PF without NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "color": "#ff9896",
            "alpha": 0.30,
            "hatch": "//",
        },
    ]

    def load_co2_group_data(base_variant, lr_code, scenarios):
        """Load CO2 yearly emissions for all scenarios in a group for a given LR6.
        Returns dict: year -> list of CO2 values (in Mt) across scenarios"""
        data_by_year = {y: [] for y in years_full}
        for scenario in scenarios:
            file_path = (
                Path(RESULTS_BASE_PATH)
                / base_variant
                / lr_code
                / rolling_horizon
                / f"scenario_{scenario}.xlsx"
            )
            if not file_path.exists():
                continue
            try:
                df = pd.read_excel(file_path, sheet_name="us_co2")
            except Exception as e:
                continue
            if "stf" not in df.columns or "value" not in df.columns:
                continue

            # Filter for years 2024-2050 and sum CO2 emissions per year
            co2_df = df[(df["stf"] >= 2024) & (df["stf"] <= 2040)]
            if co2_df.empty:
                continue

            # Sum all CO2 emissions per year across all processes
            yearly_co2 = co2_df.groupby("stf")["value"].sum().reset_index()

            for _, row in yearly_co2.iterrows():
                year = int(row["stf"])
                if year in data_by_year:
                    # Convert tons to megatons (Mt)
                    co2_mt = row["value"] / 1e6
                    data_by_year[year].append(co2_mt)
        return data_by_year

    print("Creating 3×3 CO2 emissions range plots with NZIA comparison...")

    # Create 3×3 subplot grid
    fig, axes = plt.subplots(3, 3, figsize=(20, 16), sharex=True, sharey=True)
    axes = axes.flatten()

    # Process each learning rate as a subplot
    for lr_idx, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
        if lr_idx >= 9:  # Maximum 9 subplots in 3×3 grid
            break

        ax = axes[lr_idx]
        print(f"Processing LR6 {lr_code} (subplot {lr_idx + 1}/9)...")

        subplot_has_data = False

        for group in group_definitions:
            group_data = load_co2_group_data(
                group["variant"], lr_code, group["scenarios"]
            )
            min_vals = []
            max_vals = []
            any_nonzero = False

            for y in years_full:
                vals = group_data.get(y, [])
                if vals:
                    min_v = min(vals)
                    max_v = max(vals)
                    if max_v > 0:
                        any_nonzero = True
                else:
                    min_v = 0
                    max_v = 0
                min_vals.append(min_v)
                max_vals.append(max_v)

            if any_nonzero:
                subplot_has_data = True
                # Filled range
                ax.fill_between(
                    years_full,
                    min_vals,
                    max_vals,
                    color=group["color"],
                    alpha=group["alpha"],
                    hatch=group["hatch"],
                    edgecolor=group["color"],
                    label=f"{group['label']} (Range)",
                )
                # Min / Max lines
                ax.plot(
                    years_full,
                    min_vals,
                    color=group["color"],
                    linestyle="--",
                    linewidth=1.2,
                    label=f"{group['label']} (Min)",
                )
                ax.plot(
                    years_full,
                    max_vals,
                    color=group["color"],
                    linestyle="-",
                    linewidth=2,
                    label=f"{group['label']} (Max)",
                )

        # Customize subplot
        lr_short = lr_name.split("%")[0].replace("Learning Rate", "").strip() + "%"
        ax.set_title(f"{lr_short}", fontsize=12, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.set_xlim(2024, 2040)

        # Only show x-axis labels on bottom row
        if lr_idx >= 6:  # Bottom row (indices 6, 7, 8)
            ax.set_xlabel("Year", fontsize=11)
            ax.tick_params(axis="x", rotation=45)

        # Only show y-axis labels on left column
        if lr_idx % 3 == 0:  # Left column (indices 0, 3, 6)
            ax.set_ylabel("CO2 Emissions (Mt)", fontsize=11)

        # Show "No Data" if no data was plotted
        if not subplot_has_data:
            ax.text(
                0.5,
                0.5,
                "No Data",
                transform=ax.transAxes,
                ha="center",
                va="center",
                fontsize=12,
                alpha=0.6,
                color="gray",
            )

    # Hide empty subplots if there are fewer than 9 learning rates
    for empty_idx in range(len(LEARNING_RATES), 9):
        axes[empty_idx].set_visible(False)

    # Add overall title
    fig.suptitle(
        "CO2 Emissions Ranges 2024-2050: NZIA Policy Comparison Across Learning Rates",
        fontsize=18,
        fontweight="bold",
        y=0.98,
    )

    # Create legend using the first subplot that has data
    legend_ax = None
    for ax in axes:
        handles, labels = ax.get_legend_handles_labels()
        if handles:  # If this subplot has legend data
            legend_ax = ax
            break

    if legend_ax is not None:
        # Deduplicate legend entries
        handles, labels = legend_ax.get_legend_handles_labels()
        seen = set()
        dedup_handles = []
        dedup_labels = []
        for h, l in zip(handles, labels):
            if l not in seen:
                seen.add(l)
                dedup_handles.append(h)
                dedup_labels.append(l)

        # Place legend outside the plot area
        fig.legend(
            dedup_handles,
            dedup_labels,
            bbox_to_anchor=(1.02, 0.5),
            loc="center left",
            fontsize=10,
        )

    # Adjust layout to accommodate legend
    plt.tight_layout(rect=[0, 0, 0.85, 0.96])

    # Save the combined plot
    output_path = output_dir / "co2_range_plot_nzia_comparison_3x3_grid.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved: {output_path}")

    print("✓ Completed 3×3 CO2 emissions range plots with NZIA comparison!")


def plot_capacity_additions_by_technology_and_lr():
    """
    Plot cumulative capacity additions by technology across learning rates.
    Creates plots with 4 subplots (one per technology: solarPV, windon, windoff, Batteries).
    X-axis: Learning Rates (1% to 10%)
    Y-axis: Cumulative capacity additions in GW (from 2024 to target year)
    Separate plots for:
    - Remanufacturing additions (capacity_ext_eusecondary) cumulative 2024-2030 and 2024-2040
    - Manufacturing additions (capacity_ext_euprimary) cumulative 2024-2030 and 2024-2040
    """

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Technologies to analyze
    technologies = ["solarPV", "windon", "windoff", "Batteries"]

    # Supply sources to analyze
    supply_sources = {
        "capacity_ext_eusecondary": "Remanufacturing",
        "capacity_ext_euprimary": "Manufacturing",
    }
    years = [2030, 2040]

    print(
        "Creating cumulative capacity additions plots by technology and learning rate..."
    )

    for supply_source, supply_label in supply_sources.items():
        for target_year in years:
            print(f"Processing {supply_label} cumulative 2024-{target_year}...")

            # Create figure with 2x2 subplots for the 4 technologies
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            axes = axes.flatten()

            for tech_idx, technology in enumerate(technologies):
                ax = axes[tech_idx]
                print(f"  Processing technology: {technology}")

                # Collect data for this technology across all LRs and price scenarios
                lr_data = {}  # lr_code -> [values across all price scenarios]

                for lr_code, lr_name in LEARNING_RATES.items():
                    capacity_values = []

                    for price_scenario in SCENARIO_COMBOS_LNG:
                        try:
                            file_path = (
                                Path(RESULTS_BASE_PATH)
                                / lr_code
                                / "rolling_2024_to_2050"
                                / f"scenario_{price_scenario}.xlsx"
                            )

                            if not file_path.exists():
                                capacity_values.append(0)
                                continue

                            # Load extension data
                            try:
                                extension_df = pd.read_excel(
                                    file_path, sheet_name="extension_only_caps"
                                )
                                extension_df["stf"] = extension_df["stf"].fillna(
                                    method="ffill"
                                )
                                extension_df["stf"] = pd.to_numeric(
                                    extension_df["stf"], errors="coerce"
                                )
                                extension_df = extension_df.dropna(subset=["stf"])
                            except:
                                capacity_values.append(0)
                                continue

                            # Filter for specific technology
                            tech_data = extension_df[extension_df["tech"] == technology]

                            if tech_data.empty:
                                capacity_values.append(0)
                                continue

                            # Filter for years from 2024 to target year (inclusive)
                            cumulative_data = tech_data[
                                (tech_data["stf"] >= 2024)
                                & (tech_data["stf"] <= target_year)
                            ]

                            if (
                                cumulative_data.empty
                                or supply_source not in cumulative_data.columns
                            ):
                                capacity_values.append(0)
                                continue

                            # Calculate cumulative capacity additions from 2024 to target year
                            cumulative_capacity = (
                                cumulative_data[supply_source].sum() / 1000
                            )  # Convert MW to GW
                            capacity_values.append(cumulative_capacity)

                        except Exception as e:
                            print(
                                f"    Error processing {lr_code} - {price_scenario}: {e}"
                            )
                            capacity_values.append(0)

                    lr_data[lr_code] = capacity_values

                # Prepare data for boxplot
                data_for_boxplot = []
                labels_for_boxplot = []

                for lr_code, lr_name in LEARNING_RATES.items():
                    data_for_boxplot.append(lr_data[lr_code])
                    # Extract just the percentage number for cleaner labels
                    lr_percent = (
                        lr_name.split("%")[0].replace("Learning Rate", "").strip()
                    )
                    labels_for_boxplot.append(f"{lr_percent}%")

                # Create boxplot
                colors_gradient = sns.color_palette(
                    "viridis", n_colors=len(LEARNING_RATES)
                )
                colors_gradient = [to_hex(c) for c in colors_gradient]
                box_plot = ax.boxplot(
                    data_for_boxplot,
                    labels=labels_for_boxplot,
                    patch_artist=True,
                    showmeans=True,
                    meanprops={
                        "marker": "D",
                        "markerfacecolor": "red",
                        "markeredgecolor": "red",
                        "markersize": 6,
                    },
                )

                # Color the boxes
                for patch, color in zip(box_plot["boxes"], colors_gradient):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)

                # Customize subplot
                ax.set_xlabel("Learning Rate", fontsize=12)
                ax.set_ylabel(f"Cumulative {supply_label} Additions (GW)", fontsize=12)
                ax.set_title(f"{technology}", fontsize=14, fontweight="bold")
                ax.grid(True, alpha=0.3)
                ax.set_ylim(bottom=0)

                # Calculate and display some statistics
                all_values = [
                    val for sublist in data_for_boxplot for val in sublist if val > 0
                ]
                if all_values:
                    max_val = max(all_values)
                    mean_val = np.mean(all_values)
                    print(
                        f"    {technology}: max={max_val:.1f} GW, mean={mean_val:.1f} GW"
                    )
                else:
                    print(f"    {technology}: No non-zero data")

            # Add overall title
            fig.suptitle(
                f"Cumulative {supply_label} Capacity Additions 2024-{target_year} by Learning Rate (Non-Scenario Driven)",
                fontsize=16,
                fontweight="bold",
                y=0.98,
            )
            plt.tight_layout(rect=[0, 0, 1, 0.96])

            # Save the plot
            safe_supply_name = supply_source.replace("capacity_ext_", "")
            output_path = (
                output_dir
                / f"cumulative_capacity_additions_{safe_supply_name}_2024_{target_year}_by_lr.png"
            )
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            print(f"✓ Saved: {output_path}")

            plt.close()

    print(
        "✓ Completed cumulative capacity additions plots by technology and learning rate!"
    )


def plot_capacity_additions_by_technology_and_lr_nzia_split():
    """
    For each technology, create 2 PNGs (2030, 2040). Each PNG has 4 subplots:
    - NZ with NZIA
    - NZ without NZIA
    - PF with NZIA
    - PF without NZIA
    Each subplot: x-axis = learning rates, 3 grouped boxplots per LR6 = Manufacturing, Remanufacturing, Stockpile
    """
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    technologies = ["solarPV", "windon", "windoff", "Batteries"]

    # All 3 supply sources with better labels
    supply_sources = {
        "capacity_ext_euprimary": "Manufacturing",
        "capacity_ext_eusecondary": "Remanufacturing",
        "capacity_ext_stockout": "Stockpile Withdrawals",
    }

    # Colors for the 3 supply sources (light blues and complementary colors)
    supply_colors = {
        "Manufacturing": "#87CEEB",  # Sky blue
        "Remanufacturing": "#4682B4",  # Steel blue
        "Stockpile Withdrawals": "#B0C4DE",  # Light steel blue
    }

    years = [2030, 2040]

    scenario_groups = [
        {
            "label": "NZ with NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_NZ,
        },
        {
            "label": "NZ without NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_NZ,
        },
        {
            "label": "PF with NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
        },
        {
            "label": "PF without NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
        },
    ]

    print("Creating cumulative capacity additions plots with grouped supply sources...")

    for target_year in years:
        for technology in technologies:
            print(f"Processing {technology} cumulative 2024-{target_year}...")
            fig, axes = plt.subplots(
                2, 2, figsize=(18, 14)
            )  # Slightly wider for grouped boxes
            axes = axes.flatten()

            for group_idx, group in enumerate(scenario_groups):
                ax = axes[group_idx]
                print(f"  Subplot: {group['label']}")

                # Collect data for all supply sources and learning rates
                all_data_for_plot = []
                all_positions = []
                all_colors = []
                all_labels = []

                # Position parameters for grouped boxplots
                box_width = 0.25
                lr_positions = list(range(len(LEARNING_RATES)))

                for supply_idx, (supply_source, supply_label) in enumerate(
                    supply_sources.items()
                ):
                    data_for_this_supply = []
                    positions_for_this_supply = []

                    for lr_idx, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
                        scenario_values = []

                        for scenario in group["scenarios"]:
                            file_path = (
                                Path(RESULTS_BASE_PATH)
                                / group["variant"]
                                / lr_code
                                / "rolling_2024_to_2050"
                                / f"scenario_{scenario}.xlsx"
                            )

                            if not file_path.exists():
                                scenario_values.append(0)
                                continue

                            try:
                                extension_df = pd.read_excel(
                                    file_path, sheet_name="extension_only_caps"
                                )
                                extension_df["stf"] = extension_df["stf"].fillna(
                                    method="ffill"
                                )
                                extension_df["stf"] = pd.to_numeric(
                                    extension_df["stf"], errors="coerce"
                                )
                                extension_df = extension_df.dropna(subset=["stf"])
                            except Exception as e:
                                scenario_values.append(0)
                                continue

                            tech_data = extension_df[extension_df["tech"] == technology]
                            if tech_data.empty:
                                scenario_values.append(0)
                                continue

                            cumulative_data = tech_data[
                                (tech_data["stf"] >= 2024)
                                & (tech_data["stf"] <= target_year)
                            ]
                            if (
                                cumulative_data.empty
                                or supply_source not in cumulative_data.columns
                            ):
                                scenario_values.append(0)
                                continue

                            cumulative_capacity = (
                                cumulative_data[supply_source].sum() / 1000
                            )  # Convert to GW
                            scenario_values.append(cumulative_capacity)

                        data_for_this_supply.append(scenario_values)
                        # Position offset: -0.25, 0, +0.25 for the 3 supply sources
                        position = lr_idx + (supply_idx - 1) * box_width
                        positions_for_this_supply.append(position)

                    all_data_for_plot.extend(data_for_this_supply)
                    all_positions.extend(positions_for_this_supply)
                    all_colors.extend(
                        [supply_colors[supply_label]] * len(data_for_this_supply)
                    )

                    # Add label only once per supply source (for legend)
                    if supply_idx == 0:
                        all_labels.extend(
                            [supply_label] + [""] * (len(data_for_this_supply) - 1)
                        )
                    else:
                        all_labels.extend(
                            [supply_label] + [""] * (len(data_for_this_supply) - 1)
                        )

                # Create the grouped boxplot
                box_plot = ax.boxplot(
                    all_data_for_plot,
                    positions=all_positions,
                    patch_artist=True,
                    showmeans=True,
                    meanprops={
                        "marker": "D",
                        "markerfacecolor": "red",
                        "markeredgecolor": "red",
                        "markersize": 4,
                    },
                    widths=[box_width * 0.8] * len(all_data_for_plot),
                )

                # Color the boxes according to supply source
                for patch, color in zip(box_plot["boxes"], all_colors):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.8)
                    patch.set_edgecolor("darkblue")
                    patch.set_linewidth(1)

                # Customize x-axis
                lr_labels = [
                    lr_name.split("%")[0].replace("Learning Rate", "").strip() + "%"
                    for lr_name in LEARNING_RATES.values()
                ]
                ax.set_xticks(lr_positions)
                ax.set_xticklabels(lr_labels)
                ax.set_xlabel("Learning Rate", fontsize=12)
                ax.set_ylabel("Cumulative Capacity Additions (GW)", fontsize=12)
                ax.set_title(group["label"], fontsize=14, fontweight="bold")
                ax.grid(True, alpha=0.3)
                ax.set_ylim(bottom=0)

                # Add legend only to first subplot
                if group_idx == 0:
                    from matplotlib.patches import Patch

                    legend_elements = [
                        Patch(facecolor=color, label=label, alpha=0.8)
                        for label, color in supply_colors.items()
                    ]
                    ax.legend(
                        handles=legend_elements,
                        title="Supply Source",
                        loc="upper left",
                        bbox_to_anchor=(1.02, 1),
                    )

            # Add overall title
            fig.suptitle(
                f"{technology} - Cumulative Capacity Additions 2024-{target_year}\n(Manufacturing, Remanufacturing, Stockpile Withdrawals - non Scenario Driven)",
                fontsize=16,
                fontweight="bold",
                y=0.98,
            )

            plt.tight_layout(rect=[0, 0, 1, 0.96])

            output_path = (
                output_dir
                / f"{technology}_cumulative_capacity_additions_all_sources_2024_{target_year}_by_lr_nzia_split.png"
            )
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            print(f"✓ Saved: {output_path}")
            plt.close()

    print(
        "✓ Completed all cumulative capacity additions plots with grouped supply sources!"
    )


def plot_pareto_cost_vs_total_domestic_additions():
    """Pareto plot: Total technology costs vs Total Domestic Additions
    2x2 grid: NZ/PF × With/Without NZIA
    Creates plots for both 2030 and 2040
    Both costs and domestic additions are cumulative from 2024 to target year"""

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Scenario groups definition - 2x2 grid
    scenario_groups = [
        {
            "label": "NZ with NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_NZ,
            "color": "#1f77b4",
        },
        {
            "label": "NZ without NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_NZ,
            "color": "#6baed6",
        },
        {
            "label": "PF with NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "color": "#d62728",
        },
        {
            "label": "PF without NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "color": "#ff9896",
        },
    ]

    # Technologies to analyze for domestic additions
    technologies = ["solarPV", "windon", "windoff", "Batteries"]

    # Cost types for each technology
    cost_types = [
        "_costs_EU_primary",
        "_costs_EU_secondary",
        "_costs_ext_import",
        "_costs_ext_storage",
    ]

    # Domestic supply sources (excluding imported)
    domestic_sources = [
        "capacity_ext_eusecondary",
        "capacity_ext_euprimary",
        "capacity_ext_stockout",
    ]

    # Target years
    target_years = [2030, 2040]

    # Colors for learning rates
    colors = sns.color_palette("tab10", n_colors=len(LEARNING_RATES))
    lr_color_map = {
        lr_name: colors[i] for i, lr_name in enumerate(LEARNING_RATES.values())
    }

    for target_year in target_years:
        print(
            f"\nProcessing total domestic additions plots for target year: {target_year}"
        )

        # Create figure with 2x2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()

        for group_idx, group in enumerate(scenario_groups):
            ax = axes[group_idx]
            print(f"Processing group: {group['label']}")

            results = []

            for lr_code, lr_name in LEARNING_RATES.items():
                for scenario in group["scenarios"]:
                    # Load data from the Excel file
                    cost_file_path = (
                        Path(RESULTS_BASE_PATH)
                        / group["variant"]
                        / lr_code
                        / "rolling_2024_to_2050"
                        / f"scenario_{scenario}.xlsx"
                    )

                    if not cost_file_path.exists():
                        continue

                    try:
                        # Load cost data from extension_cost sheet
                        df_cost = pd.read_excel(
                            cost_file_path, sheet_name="extension_cost"
                        )

                        # Calculate TOTAL technology costs across ALL technologies (2024 to target_year)
                        total_tech_cost = 0

                        for technology in technologies:
                            # Filter for technology-specific costs in the 'pro' column
                            technology_cost_patterns = [
                                f"{technology}{cost_type}" for cost_type in cost_types
                            ]

                            # Filter for this technology's costs
                            tech_cost_data = df_cost[
                                df_cost["pro"].str.contains(
                                    "|".join(technology_cost_patterns),
                                    case=False,
                                    na=False,
                                )
                            ]

                            # Filter for years 2024 to target_year and sum technology costs
                            tech_cost_filtered = tech_cost_data[
                                (tech_cost_data["stf"] >= 2024)
                                & (tech_cost_data["stf"] <= target_year)
                            ]
                            total_tech_cost += tech_cost_filtered["Total_Cost"].sum()

                        total_tech_cost = (
                            total_tech_cost / 1e9
                        )  # Convert to billion EUR

                        # Load domestic capacity additions data
                        extension_df = pd.read_excel(
                            cost_file_path, sheet_name="extension_only_caps"
                        )
                        extension_df["stf"] = extension_df["stf"].fillna(method="ffill")
                        extension_df["stf"] = pd.to_numeric(
                            extension_df["stf"], errors="coerce"
                        )
                        extension_df = extension_df.dropna(subset=["stf"])

                        # Calculate CUMULATIVE domestic additions across ALL technologies from 2024 to target_year
                        total_domestic_cumulative = 0

                        for technology in technologies:
                            tech_data = extension_df[extension_df["tech"] == technology]
                            if not tech_data.empty:
                                # Filter for years 2024 to target_year (CUMULATIVE)
                                tech_period = tech_data[
                                    (tech_data["stf"] >= 2024)
                                    & (tech_data["stf"] <= target_year)
                                ]
                                if not tech_period.empty:
                                    # Sum domestic sources for this technology across all years 2024-target_year
                                    for source in domestic_sources:
                                        if source in tech_period.columns:
                                            tech_domestic = (
                                                tech_period[source].sum() / 1000
                                            )  # Convert MW to GW
                                            total_domestic_cumulative += tech_domestic

                        results.append(
                            {
                                "Learning_Rate": lr_name,
                                "Price_Scenario": scenario.replace("_", " ").title(),
                                "Total_Technology_Cost_bEUR": total_tech_cost,
                                f"Total_Domestic_Cumulative_2024_{target_year}_GW": total_domestic_cumulative,
                                "LR_Code": lr_code,
                                "Scenario_Code": scenario,
                            }
                        )

                    except Exception as e:
                        print(f"    Error processing {lr_code} - {scenario}: {e}")
                        continue

            if not results:
                ax.text(
                    0.5,
                    0.5,
                    f"No data available\nfor {group['label']}",
                    horizontalalignment="center",
                    verticalalignment="center",
                    transform=ax.transAxes,
                    fontsize=14,
                )
                ax.set_title(f"{group['label']} - No Data")
                continue

            df_results = pd.DataFrame(results)

            # Skip if no valid data points
            if (
                df_results["Total_Technology_Cost_bEUR"].sum() == 0
                or df_results[f"Total_Domestic_Cumulative_2024_{target_year}_GW"].sum()
                == 0
            ):
                ax.text(
                    0.5,
                    0.5,
                    f"No valid data\nfor {group['label']}",
                    horizontalalignment="center",
                    verticalalignment="center",
                    transform=ax.transAxes,
                    fontsize=14,
                )
                ax.set_title(f"{group['label']} - No Data")
                continue

            # Find Pareto front (minimize cost, maximize domestic additions)
            costs = df_results["Total_Technology_Cost_bEUR"].values
            domestic_additions = df_results[
                f"Total_Domestic_Cumulative_2024_{target_year}_GW"
            ].values

            pareto_mask = find_pareto_front(
                costs, domestic_additions, minimize_both=False
            )
            pareto_points = df_results[pareto_mask].copy()
            pareto_points = pareto_points.sort_values("Total_Technology_Cost_bEUR")

            # Plot all points colored by learning rate
            for lr_name in LEARNING_RATES.values():
                subset = df_results[df_results["Learning_Rate"] == lr_name]
                if not subset.empty:
                    ax.scatter(
                        subset["Total_Technology_Cost_bEUR"],
                        subset[f"Total_Domestic_Cumulative_2024_{target_year}_GW"],
                        color=lr_color_map[lr_name],
                        label=lr_name if group_idx == 0 else "",
                        alpha=0.7,
                        s=60,
                    )

            # Plot Pareto front
            if len(pareto_points) > 1:
                ax.plot(
                    pareto_points["Total_Technology_Cost_bEUR"],
                    pareto_points[f"Total_Domestic_Cumulative_2024_{target_year}_GW"],
                    "r--",
                    linewidth=2,
                    alpha=0.8,
                )

            if len(pareto_points) > 0:
                ax.scatter(
                    pareto_points["Total_Technology_Cost_bEUR"],
                    pareto_points[f"Total_Domestic_Cumulative_2024_{target_year}_GW"],
                    color="red",
                    s=100,
                    marker="*",
                    zorder=5,
                    alpha=0.9,
                )

            # Customize subplot
            ax.set_xlabel(f"Total RES Technology Costs (bEUR)", fontsize=12)
            ax.set_ylabel(f"Total RES Capacity added (GW)", fontsize=12)
            ax.set_title(f"{group['label']}", fontsize=14, fontweight="bold")
            ax.grid(True, alpha=0.3)

            # Print Pareto optimal points for this group
            if len(pareto_points) > 0:
                print(
                    f"\nPareto Optimal Points for {group['label']} (Cumulative Cost vs Cumulative Domestic 2024-{target_year}):"
                )
                for _, row in pareto_points.iterrows():
                    print(
                        f"  {row['Learning_Rate']} - {row['Price_Scenario']}: "
                        f"Cost={row['Total_Technology_Cost_bEUR']:.1f}b€, Domestic={row[f'Total_Domestic_Cumulative_2024_{target_year}_GW']:.1f}GW"
                    )

        # Add legend to the first subplot only
        if len(LEARNING_RATES) > 0:
            axes[0].legend(
                title="Learning Rates",
                bbox_to_anchor=(1.05, 1),
                loc="upper left",
                fontsize=10,
            )

        # Add overall title
        fig.suptitle(
            f"Pareto Front: Cumulative RES Technology Costs vs. Cumulative domestic RES Capacity 2024-{target_year}",
            fontsize=16,
            fontweight="bold",
            y=0.98,
        )
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # Save the plot
        output_path = (
            output_dir
            / f"pareto_cumulative_cost_vs_cumulative_domestic_{target_year}.png"
        )
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"✓ Saved Cumulative Pareto plot ({target_year}): {output_path}")

        plt.close()

    print(
        f"\n✓ Completed cumulative domestic additions Pareto analysis for both {target_years[0]} and {target_years[1]}"
    )


def plot_domestic_percentage_heatmap():
    """Create sophisticated heatmap showing domestic additions percentage over time

    Creates 8 figures total:
    - 4 technologies × 2 scenario types (NZ/PF)
    - Each figure has ~54 subplots in 6×9 grid
    - Top 3 rows: with NZIA scenarios, Bottom 3 rows: without NZIA scenarios
    - Uses squares for yearly additions in 2-year steps
    - White to red color scheme for better 40% benchmark visibility
    """

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Technologies to analyze
    technologies = ["solarPV", "windon", "windoff", "Batteries"]

    # Years to analyze (2-year steps)
    years = list(
        range(2024, 2041, 2)
    )  # [2024, 2026, 2028, 2030, 2032, 2034, 2036, 2038, 2040]

    # Domestic vs all sources
    domestic_sources = [
        "capacity_ext_eusecondary",
        "capacity_ext_euprimary",
        "capacity_ext_stockout",
    ]
    all_sources = [
        "capacity_ext_eusecondary",
        "capacity_ext_euprimary",
        "capacity_ext_stockout",
        "capacity_ext_imported",
    ]

    # Scenario configurations
    scenario_types = [
        {"name": "NZ", "scenarios": SCENARIO_COMBOS_LNG_NZ, "title": "Net Zero"},
        {
            "name": "PF",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "title": "Persistent Fossil",
        },
    ]

    # NZIA variants (now combined in same plot)
    nzia_variants = [
        {"variant": "results_with_nzia", "label": "with_NZIA", "title": "with NZIA"},
        {
            "variant": "results_without_nzia",
            "label": "without_NZIA",
            "title": "without NZIA",
        },
    ]

    # White to red color scheme for better 40% benchmark visibility
    from matplotlib.colors import LinearSegmentedColormap, Normalize

    # White (0%) to very dark red (100%) - much better contrast around 40%
    white_to_red_colors = [
        "#f7fbff",  # White/neutral (0%)
        "#fee5d9",  # Very light red
        "#fcae91",  # Light red
        "#fb6a4a",  # Medium red
        "#de2d26",  # Dark red
        "#a50f15",  # Very dark red (100%)
    ]

    cmap = LinearSegmentedColormap.from_list("white_to_red", white_to_red_colors, N=256)
    norm = Normalize(vmin=0, vmax=100)

    for technology in technologies:
        for scenario_type in scenario_types:
            print(
                f"\nProcessing {technology} - {scenario_type['title']} - NZIA Comparison..."
            )

            # Get all price scenarios for this scenario type
            price_scenarios = scenario_type["scenarios"]
            n_scenarios = len(price_scenarios)

            # Use 6×9 grid layout (6 rows, 9 columns)
            # Top 3 rows: with NZIA, Bottom 3 rows: without NZIA
            n_rows = 6
            n_cols = 9

            # Create figure with extra space for horizontal legend below
            fig, axes = plt.subplots(
                n_rows, n_cols, figsize=(24, 14)
            )  # Taller figure for 6 rows

            # Flatten axes array for easy indexing
            axes = axes.flatten()

            # Process each NZIA variant (with/without)
            for nzia_idx, nzia_config in enumerate(nzia_variants):
                print(f"  Processing {nzia_config['title']}...")

                # Calculate row offset: 0-26 for with NZIA (top 3 rows), 27-53 for without NZIA (bottom 3 rows)
                row_offset = nzia_idx * (
                    3 * n_cols
                )  # 0 for with NZIA, 27 for without NZIA

                # Process each price scenario as a subplot
                for scenario_idx, price_scenario in enumerate(price_scenarios):
                    if scenario_idx >= 3 * n_cols:  # Only 27 scenarios per NZIA variant
                        break

                    # Calculate actual subplot index
                    subplot_idx = row_offset + scenario_idx
                    if subplot_idx >= len(axes):
                        break

                    ax = axes[subplot_idx]
                    print(f"    Processing price scenario: {price_scenario}")

                    # Track if any data was plotted
                    data_plotted = False

                    for lr_idx, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
                        # Load data file
                        file_path = (
                            Path(RESULTS_BASE_PATH)
                            / nzia_config["variant"]
                            / lr_code
                            / "rolling_2024_to_2050"
                            / f"scenario_{price_scenario}.xlsx"
                        )

                        if not file_path.exists():
                            continue

                        try:
                            # Load capacity data from extension_only_caps sheet
                            extension_df = pd.read_excel(
                                file_path, sheet_name="extension_only_caps"
                            )
                            extension_df["stf"] = extension_df["stf"].fillna(
                                method="ffill"
                            )
                            extension_df["stf"] = pd.to_numeric(
                                extension_df["stf"], errors="coerce"
                            )
                            extension_df = extension_df.dropna(subset=["stf"])

                            # Filter for this specific technology
                            tech_data = extension_df[extension_df["tech"] == technology]

                            if tech_data.empty:
                                continue

                            # Calculate domestic percentage for each year (YEARLY ADDITIONS, not cumulative)
                            for year in years:
                                tech_year_data = tech_data[tech_data["stf"] == year]

                                if tech_year_data.empty:
                                    continue

                                # Calculate yearly domestic additions
                                domestic_yearly = 0
                                total_yearly = 0

                                # Sum domestic sources for THIS YEAR ONLY
                                for source in domestic_sources:
                                    if source in tech_year_data.columns:
                                        domestic_yearly += tech_year_data[source].sum()

                                # Sum all sources for THIS YEAR ONLY (domestic + imported)
                                for source in all_sources:
                                    if source in tech_year_data.columns:
                                        total_yearly += tech_year_data[source].sum()

                                # Calculate percentage for this year's additions
                                if total_yearly > 0:
                                    domestic_percentage = (
                                        domestic_yearly / total_yearly
                                    ) * 100

                                    # Create square position
                                    y_position = lr_idx
                                    x_position = years.index(year)

                                    # Plot colored square (looks like bars)
                                    color = cmap(norm(domestic_percentage))
                                    ax.scatter(
                                        x_position,
                                        y_position,
                                        c=[color],
                                        s=150,
                                        marker="s",  # Smaller squares for 6x9
                                        alpha=0.9,
                                        edgecolors="black",
                                        linewidth=0.3,
                                    )
                                    data_plotted = True

                        except Exception as e:
                            print(
                                f"      Error processing {lr_code} - {price_scenario}: {e}"
                            )
                            continue

                    # Customize subplot
                    ax.set_xlim(-0.5, len(years) - 0.5)
                    ax.set_ylim(-0.5, len(LEARNING_RATES) - 0.5)

                    # Set ticks
                    ax.set_xticks(range(len(years)))
                    ax.set_yticks(range(len(LEARNING_RATES)))
                    ax.set_yticklabels(list(LEARNING_RATES.values()), fontsize=6)

                    # Only show x-axis labels on bottom row
                    if subplot_idx >= (n_rows - 1) * n_cols:  # Bottom row
                        ax.set_xticklabels(
                            [str(year) for year in years], rotation=45, fontsize=7
                        )
                        ax.set_xlabel("Year", fontsize=8)
                    else:
                        ax.set_xticklabels([])

                    # Only show y-axis label on left column
                    if subplot_idx % n_cols == 0:  # Left column
                        ax.set_ylabel("Learning Rate", fontsize=8)
                    else:
                        ax.set_yticklabels([])

                    # Clean title: remove LNG_NZ/LNG_PF, just show price combination
                    price_clean = (
                        price_scenario.replace("_LNG_NZ", "")
                        .replace("_LNG_PF", "")
                        .replace("_", " ")
                        .title()
                    )
                    ax.set_title(price_clean, fontsize=7, fontweight="bold", pad=4)

                    # Add subtle grid for better readability
                    ax.grid(True, alpha=0.2, linestyle="-", linewidth=0.3, color="gray")

                    # Show "No Data" message if no data was plotted
                    if not data_plotted:
                        ax.text(
                            0.5,
                            0.5,
                            "No Data",
                            transform=ax.transAxes,
                            ha="center",
                            va="center",
                            fontsize=8,
                            alpha=0.5,
                            color="gray",
                        )

            # Hide empty subplots
            for empty_idx in range(2 * n_scenarios, len(axes)):
                axes[empty_idx].set_visible(False)

            # Add section labels for NZIA variants
            # Add text labels to distinguish the two sections
            fig.text(
                0.02,
                0.75,
                "WITH NZIA",
                rotation=90,
                fontsize=14,
                fontweight="bold",
                ha="center",
                va="center",
                color="darkgreen",
            )
            fig.text(
                0.02,
                0.25,
                "WITHOUT NZIA",
                rotation=90,
                fontsize=14,
                fontweight="bold",
                ha="center",
                va="center",
                color="darkred",
            )

            # Add horizontal colorbar below the plots
            if n_scenarios > 0:
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])

                # Create horizontal colorbar at the bottom
                cbar_ax = fig.add_axes(
                    [0.15, 0.02, 0.7, 0.02]
                )  # [left, bottom, width, height]
                cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
                cbar.set_label(
                    "Domestic Additions (% of yearly total)", fontsize=12, labelpad=8
                )
                cbar.ax.tick_params(labelsize=10)

                # Add percentage markers on colorbar, highlighting 40% benchmark
                cbar.set_ticks([0, 20, 40, 60, 80, 100])
                cbar.set_ticklabels(
                    ["0%", "20%", "40%\n(Benchmark)", "60%", "80%", "100%"]
                )

            # Main title
            fig.suptitle(
                f"Domestic Yearly Additions: {technology} - {scenario_type['title']} - NZIA Policy Comparison",
                fontsize=18,
                fontweight="bold",
                y=0.97,
            )

            # Adjust layout with space for horizontal colorbar and section labels
            plt.tight_layout(
                rect=[0.04, 0.06, 1, 0.95]
            )  # Leave space for labels and colorbar

            # Save plot
            output_path = (
                output_dir
                / f"domestic_yearly_nzia_comparison_{technology}_{scenario_type['name']}.png"
            )
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"✓ Saved: {output_path}")

    print("\n✓ Completed all NZIA comparison domestic yearly percentage square plots!")
    print(f"Created 8 figures total: 4 technologies × 2 scenario types")


def plot_domestic_percentage_heatmap_scenario_driven():
    """Create scenario-driven heatmap showing domestic additions percentage over time

    Creates 16 figures total:
    - 4 technologies × 2 scenario types × 2 NZIA variants
    - Each figure has ~27 subplots (one per price scenario) in 3×9 grid
    - Uses squares for yearly additions in 2-year steps
    - Better color contrast and horizontal legend below plots

    Data structure: Uses result_scenario_ files with separate sheets for each supply option
    """

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Technologies to analyze
    technologies = ["solarPV", "windon", "windoff", "Batteries"]

    # Years to analyze (2-year steps)
    years = list(
        range(2024, 2041, 2)
    )  # [2024, 2026, 2028, 2030, 2032, 2034, 2036, 2038, 2040]

    # Domestic vs all sources (now separate sheets)
    domestic_sources = [
        "capacity_ext_eusecondary",
        "capacity_ext_euprimary",
        "capacity_ext_stockout",
    ]
    all_sources = [
        "capacity_ext_eusecondary",
        "capacity_ext_euprimary",
        "capacity_ext_stockout",
        "capacity_ext_imported",
    ]

    # Scenario configurations
    scenario_types = [
        {"name": "NZ", "scenarios": SCENARIO_COMBOS_LNG_NZ, "title": "Net Zero"},
        {
            "name": "PF",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "title": "Persistent Fossil",
        },
    ]

    # NZIA variants (now separate)
    nzia_variants = [
        {"variant": "results_with_nzia", "label": "with_NZIA", "title": "with NZIA"},
        {
            "variant": "results_without_nzia",
            "label": "without_NZIA",
            "title": "without NZIA",
        },
    ]

    # Better color scheme: Blue to Red gradient for better contrast
    from matplotlib.colors import LinearSegmentedColormap, Normalize

    # Blue (low %) to Red (high %) - much easier to distinguish
    contrast_colors = [
        "#08519c",  # Dark blue (0%)
        "#3182bd",  # Medium blue
        "#6baed6",  # Light blue
        "#bdd7e7",  # Very light blue
        "#f7fbff",  # White/neutral (50%)
        "#fee5d9",  # Very light red
        "#fcae91",  # Light red
        "#fb6a4a",  # Medium red
        "#de2d26",  # Dark red
        "#a50f15",  # Very dark red (100%)
    ]

    cmap = LinearSegmentedColormap.from_list("blue_to_red", contrast_colors, N=256)
    norm = Normalize(vmin=0, vmax=100)

    for technology in technologies:
        for scenario_type in scenario_types:
            for nzia_config in nzia_variants:
                print(
                    f"\nProcessing {technology} - {scenario_type['title']} - {nzia_config['title']}..."
                )

                # Get all price scenarios for this scenario type
                price_scenarios = scenario_type["scenarios"]
                n_scenarios = len(price_scenarios)

                # Use 3×9 grid layout (3 rows, 9 columns)
                n_rows = 3
                n_cols = 9

                # Create figure with extra space for horizontal legend below
                fig, axes = plt.subplots(
                    n_rows, n_cols, figsize=(20, 10)
                )  # Wider figure

                # Flatten axes array for easy indexing
                axes = axes.flatten()

                # Process each price scenario as a subplot
                for scenario_idx, price_scenario in enumerate(price_scenarios):
                    if scenario_idx >= len(axes):
                        break

                    ax = axes[scenario_idx]
                    print(f"  Processing price scenario: {price_scenario}")

                    # Track if any data was plotted
                    data_plotted = False

                    for lr_idx, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
                        # Load data file (scenario-driven structure)
                        file_path = (
                            Path(RESULTS_BASE_PATH)
                            / nzia_config["variant"]
                            / lr_code
                            / f"result_scenario_{price_scenario}.xlsx"
                        )

                        if not file_path.exists():
                            print(f"    Missing file: {file_path}")
                            continue

                        try:
                            # Load data from separate sheets for each supply option
                            supply_data = {}

                            # Read each supply option sheet
                            for source in all_sources:
                                try:
                                    sheet_df = pd.read_excel(
                                        file_path, sheet_name=source
                                    )
                                    # Structure: window_index | year | key_0 | key_1 | value
                                    # Filter for this technology (assuming key_0 or key_1 contains technology info)
                                    tech_df = sheet_df[
                                        (sheet_df["key_0"] == technology)
                                        | (sheet_df["key_1"] == technology)
                                    ]
                                    supply_data[source] = tech_df
                                except Exception as e:
                                    print(f"    Could not read sheet {source}: {e}")
                                    supply_data[source] = pd.DataFrame()

                            # Calculate domestic percentage for each year (YEARLY VALUES, already yearly)
                            for year in years:
                                domestic_yearly = 0
                                total_yearly = 0

                                # Sum domestic sources for THIS YEAR
                                for source in domestic_sources:
                                    if (
                                        source in supply_data
                                        and not supply_data[source].empty
                                    ):
                                        year_data = supply_data[source][
                                            supply_data[source]["year"] == year
                                        ]
                                        if not year_data.empty:
                                            domestic_yearly += year_data["value"].sum()

                                # Sum all sources for THIS YEAR (domestic + imported)
                                for source in all_sources:
                                    if (
                                        source in supply_data
                                        and not supply_data[source].empty
                                    ):
                                        year_data = supply_data[source][
                                            supply_data[source]["year"] == year
                                        ]
                                        if not year_data.empty:
                                            total_yearly += year_data["value"].sum()

                                # Calculate percentage for this year's additions
                                if total_yearly > 0:
                                    domestic_percentage = (
                                        domestic_yearly / total_yearly
                                    ) * 100

                                    # Create square position
                                    y_position = lr_idx
                                    x_position = years.index(year)

                                    # Plot colored square (looks like bars)
                                    color = cmap(norm(domestic_percentage))
                                    ax.scatter(
                                        x_position,
                                        y_position,
                                        c=[color],
                                        s=200,
                                        marker="s",  # 's' = square
                                        alpha=0.9,
                                        edgecolors="black",
                                        linewidth=0.5,
                                    )
                                    data_plotted = True

                        except Exception as e:
                            print(
                                f"    Error processing {lr_code} - {price_scenario}: {e}"
                            )
                            continue

                    # Customize subplot
                    ax.set_xlim(-0.5, len(years) - 0.5)
                    ax.set_ylim(-0.5, len(LEARNING_RATES) - 0.5)

                    # Set ticks
                    ax.set_xticks(range(len(years)))
                    ax.set_yticks(range(len(LEARNING_RATES)))
                    ax.set_yticklabels(list(LEARNING_RATES.values()), fontsize=8)

                    # Only show x-axis labels on bottom row
                    if scenario_idx >= (n_rows - 1) * n_cols:  # Bottom row
                        ax.set_xticklabels(
                            [str(year) for year in years], rotation=45, fontsize=9
                        )
                        ax.set_xlabel("Year", fontsize=10)
                    else:
                        ax.set_xticklabels([])

                    # Only show y-axis label on left column
                    if scenario_idx % n_cols == 0:  # Left column
                        ax.set_ylabel("Learning Rate", fontsize=10)
                    else:
                        ax.set_yticklabels([])

                    # Clean title: remove LNG_NZ/LNG_PF, just show price combination
                    price_clean = (
                        price_scenario.replace("LNG_NZ_", "")
                        .replace("LNG_PF_", "")
                        .replace("_", " ")
                        .title()
                    )
                    ax.set_title(price_clean, fontsize=9, fontweight="bold", pad=8)

                    # Add subtle grid for better readability
                    ax.grid(True, alpha=0.2, linestyle="-", linewidth=0.5, color="gray")

                    # Show "No Data" message if no data was plotted
                    if not data_plotted:
                        ax.text(
                            0.5,
                            0.5,
                            "No Data",
                            transform=ax.transAxes,
                            ha="center",
                            va="center",
                            fontsize=10,
                            alpha=0.5,
                            color="gray",
                        )

                # Hide empty subplots
                for empty_idx in range(n_scenarios, len(axes)):
                    axes[empty_idx].set_visible(False)

                # Add horizontal colorbar below the plots
                if n_scenarios > 0:
                    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                    sm.set_array([])

                    # Create horizontal colorbar at the bottom
                    cbar_ax = fig.add_axes(
                        [0.15, 0.02, 0.7, 0.03]
                    )  # [left, bottom, width, height]
                    cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
                    cbar.set_label(
                        "Domestic Additions (% of yearly total)",
                        fontsize=12,
                        labelpad=10,
                    )
                    cbar.ax.tick_params(labelsize=10)

                    # Add percentage markers on colorbar
                    cbar.set_ticks([0, 25, 50, 75, 100])
                    cbar.set_ticklabels(["0%", "25%", "50%", "75%", "100%"])

                # Main title
                fig.suptitle(
                    f"Domestic Yearly Additions: {technology} - {scenario_type['title']} - {nzia_config['title']} (Scenario Driven)",
                    fontsize=16,
                    fontweight="bold",
                    y=0.95,
                )

                # Adjust layout with space for horizontal colorbar
                plt.tight_layout(
                    rect=[0, 0.08, 1, 0.93]
                )  # Leave space at bottom for colorbar

                # Save plot
                output_path = (
                    output_dir
                    / f"domestic_yearly_squares_scenario_{technology}_{scenario_type['name']}_{nzia_config['label']}.png"
                )
                plt.savefig(output_path, dpi=300, bbox_inches="tight")
                plt.close()
                print(f"✓ Saved: {output_path}")

    print("\n✓ Completed all scenario-driven domestic yearly percentage square plots!")
    print(
        f"Created 16 figures total: 4 technologies × 2 scenario types × 2 NZIA variants"
    )


def plot_combined_domestic_percentage_heatmap():
    """Create sophisticated heatmap showing TOTAL domestic additions percentage over time

    Creates 4 figures total:
    - 2 scenario types × 2 NZIA variants
    - Each figure has ~27 subplots (one per price scenario) in 3×9 grid
    - Uses squares for yearly additions in 2-year steps
    - White to dark red color scheme for better 40% benchmark visibility
    """

    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)

    # Technologies to analyze (ALL COMBINED)
    technologies = ["solarPV", "windon", "windoff", "Batteries"]

    # Years to analyze (2-year steps)
    years = list(
        range(2024, 2041, 2)
    )  # [2024, 2026, 2028, 2030, 2032, 2034, 2036, 2038, 2040]

    # Domestic vs all sources
    domestic_sources = [
        "capacity_ext_eusecondary",
        "capacity_ext_euprimary",
        "capacity_ext_stockout",
    ]
    all_sources = [
        "capacity_ext_eusecondary",
        "capacity_ext_euprimary",
        "capacity_ext_stockout",
        "capacity_ext_imported",
    ]

    # Scenario configurations
    scenario_types = [
        {"name": "NZ", "scenarios": SCENARIO_COMBOS_LNG_NZ, "title": "Net Zero"},
        {
            "name": "PF",
            "scenarios": SCENARIO_COMBOS_LNG_PF,
            "title": "Persistent Fossil",
        },
    ]

    # NZIA variants (now separate)
    nzia_variants = [
        {"variant": "results_with_nzia", "label": "with_NZIA", "title": "with NZIA"},
        {
            "variant": "results_without_nzia",
            "label": "without_NZIA",
            "title": "without NZIA",
        },
    ]

    # White to dark red color scheme (upper part only)
    from matplotlib.colors import LinearSegmentedColormap, Normalize

    # White (0%) to very dark red (100%) - much better contrast around 40%
    white_to_red_colors = [
        "#f7fbff",  # White/neutral (0%)
        "#fee5d9",  # Very light red
        "#fcae91",  # Light red
        "#fb6a4a",  # Medium red
        "#de2d26",  # Dark red
        "#a50f15",  # Very dark red (100%)
    ]

    cmap = LinearSegmentedColormap.from_list("white_to_red", white_to_red_colors, N=256)
    norm = Normalize(vmin=0, vmax=100)

    for scenario_type in scenario_types:
        for nzia_config in nzia_variants:
            print(
                f"\nProcessing COMBINED TECHNOLOGIES - {scenario_type['title']} - {nzia_config['title']}..."
            )

            # Get all price scenarios for this scenario type
            price_scenarios = scenario_type["scenarios"]
            n_scenarios = len(price_scenarios)

            # Use 3×9 grid layout (3 rows, 9 columns)
            n_rows = 3
            n_cols = 9

            # Create figure with extra space for horizontal legend below
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 10))  # Wider figure

            # Flatten axes array for easy indexing
            axes = axes.flatten()

            # Process each price scenario as a subplot
            for scenario_idx, price_scenario in enumerate(price_scenarios):
                if scenario_idx >= len(axes):
                    break

                ax = axes[scenario_idx]
                print(f"  Processing price scenario: {price_scenario}")

                # Track if any data was plotted
                data_plotted = False

                for lr_idx, (lr_code, lr_name) in enumerate(LEARNING_RATES.items()):
                    # Load data file
                    file_path = (
                        Path(RESULTS_BASE_PATH)
                        / nzia_config["variant"]
                        / lr_code
                        / "rolling_2024_to_2050"
                        / f"scenario_{price_scenario}.xlsx"
                    )

                    if not file_path.exists():
                        continue

                    try:
                        # Load capacity data from extension_only_caps sheet
                        extension_df = pd.read_excel(
                            file_path, sheet_name="extension_only_caps"
                        )
                        extension_df["stf"] = extension_df["stf"].fillna(method="ffill")
                        extension_df["stf"] = pd.to_numeric(
                            extension_df["stf"], errors="coerce"
                        )
                        extension_df = extension_df.dropna(subset=["stf"])

                        # Filter for ALL technologies (COMBINED)
                        tech_data = extension_df[
                            extension_df["tech"].isin(technologies)
                        ]

                        if tech_data.empty:
                            continue

                        # Calculate COMBINED domestic percentage for each year
                        for year in years:
                            tech_year_data = tech_data[tech_data["stf"] == year]

                            if tech_year_data.empty:
                                continue

                            # Calculate yearly domestic additions (SUMMED ACROSS ALL TECHNOLOGIES)
                            domestic_yearly = 0
                            total_yearly = 0

                            # Sum domestic sources for THIS YEAR across ALL TECHNOLOGIES
                            for source in domestic_sources:
                                if source in tech_year_data.columns:
                                    domestic_yearly += tech_year_data[source].sum()

                            # Sum all sources for THIS YEAR across ALL TECHNOLOGIES
                            for source in all_sources:
                                if source in tech_year_data.columns:
                                    total_yearly += tech_year_data[source].sum()

                            # Calculate percentage for this year's TOTAL additions
                            if total_yearly > 0:
                                domestic_percentage = (
                                    domestic_yearly / total_yearly
                                ) * 100

                                # Create square position
                                y_position = lr_idx
                                x_position = years.index(year)

                                # Plot colored square (looks like bars)
                                color = cmap(norm(domestic_percentage))
                                ax.scatter(
                                    x_position,
                                    y_position,
                                    c=[color],
                                    s=200,
                                    marker="s",  # 's' = square
                                    alpha=0.9,
                                    edgecolors="black",
                                    linewidth=0.5,
                                )
                                data_plotted = True

                    except Exception as e:
                        print(f"    Error processing {lr_code} - {price_scenario}: {e}")
                        continue

                # Customize subplot
                ax.set_xlim(-0.5, len(years) - 0.5)
                ax.set_ylim(-0.5, len(LEARNING_RATES) - 0.5)

                # Set ticks
                ax.set_xticks(range(len(years)))
                ax.set_yticks(range(len(LEARNING_RATES)))
                ax.set_yticklabels(list(LEARNING_RATES.values()), fontsize=8)

                # Only show x-axis labels on bottom row
                if scenario_idx >= (n_rows - 1) * n_cols:  # Bottom row
                    ax.set_xticklabels(
                        [str(year) for year in years], rotation=45, fontsize=9
                    )
                    ax.set_xlabel("Year", fontsize=10)
                else:
                    ax.set_xticklabels([])

                # Only show y-axis label on left column
                if scenario_idx % n_cols == 0:  # Left column
                    ax.set_ylabel("Learning Rate", fontsize=10)
                else:
                    ax.set_yticklabels([])

                # Clean title: remove LNG_NZ/LNG_PF, just show price combination
                price_clean = (
                    price_scenario.replace("_LNG_NZ", "")
                    .replace("_LNG_PF", "")
                    .replace("_", " ")
                    .title()
                )
                ax.set_title(price_clean, fontsize=9, fontweight="bold", pad=8)

                # Add subtle grid for better readability
                ax.grid(True, alpha=0.2, linestyle="-", linewidth=0.5, color="gray")

                # Show "No Data" message if no data was plotted
                if not data_plotted:
                    ax.text(
                        0.5,
                        0.5,
                        "No Data",
                        transform=ax.transAxes,
                        ha="center",
                        va="center",
                        fontsize=10,
                        alpha=0.5,
                        color="gray",
                    )

            # Hide empty subplots
            for empty_idx in range(n_scenarios, len(axes)):
                axes[empty_idx].set_visible(False)

            # Add horizontal colorbar below the plots
            if n_scenarios > 0:
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])

                # Create horizontal colorbar at the bottom
                cbar_ax = fig.add_axes(
                    [0.15, 0.02, 0.7, 0.03]
                )  # [left, bottom, width, height]
                cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
                cbar.set_label(
                    "Total Domestic Additions (% of yearly total)",
                    fontsize=12,
                    labelpad=10,
                )
                cbar.ax.tick_params(labelsize=10)

                # Add percentage markers on colorbar, highlighting 40% benchmark
                cbar.set_ticks([0, 20, 40, 60, 80, 100])
                cbar.set_ticklabels(
                    ["0%", "20%", "40%\n(Benchmark)", "60%", "80%", "100%"]
                )

            # Main title
            fig.suptitle(
                f"Total Domestic Yearly Additions: All Technologies - {scenario_type['title']} - {nzia_config['title']}",
                fontsize=16,
                fontweight="bold",
                y=0.95,
            )

            # Adjust layout with space for horizontal colorbar
            plt.tight_layout(
                rect=[0, 0.08, 1, 0.93]
            )  # Leave space at bottom for colorbar

            # Save plot
            output_path = (
                output_dir
                / f"total_domestic_yearly_squares_{scenario_type['name']}_{nzia_config['label']}.png"
            )
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"✓ Saved: {output_path}")

    print("\n✓ Completed all TOTAL domestic yearly percentage square plots!")
    print(f"Created 4 figures total: 2 scenario types × 2 NZIA variants")


def plot_capacity_and_stock_separately():
    """
    For each scenario (LR6, NZIA, scenario):
    - Plots stacked bar for total installed capacities (excluding Batteries, positive y)
    - Plots a separate stacked bar for stock levels of solarPV, windon, windoff (positive y)
    - Data from extension_total_caps and extension_only_caps, up to 2040
    """
    years_of_interest = [2024, 2030, 2035, 2040]
    max_year = 2040

    colors = {
        "Biomass Plant": "#FFB347",
        "Wind (onshore)": "#77DD77",
        "Wind (offshore)": "#006400",
        "Nuclear Plant": "#FFB6C1",
        "Hydro (run-of-river)": "#A0C4E1",
        "Hydro (reservoir)": "#74B3D6",
        "Solar PV": "#FDFD96",
        "Gas Plant (CCGT)": "#FF6961",
        "Gas Plant (CCGT) LNG": "brown",
        "Coal Plant": "#B0B0B0",
        "Coal Lignite": "#808080",
        "Gas Plant (CCGT) CCUS": "black",
        "Coal CCUS": "black",
        "Coal Lignite CCUS": "black",
    }
    techs_exclude = ["Batteries"]

    TECH_NAME_MAP = {
        "Biomass Plant": "Biomass Plant",
        "Coal CCUS": "Coal CCUS",
        "Coal Lignite": "Coal Lignite",
        "Coal Lignite CCUS": "Coal Lignite CCUS",
        "Coal Plant": "Coal Plant",
        "Gas Plant (CCGT)": "Gas Plant (CCGT)",
        "Gas Plant (CCGT) CCUS": "Gas Plant (CCGT) CCUS",
        "Gas Plant (CCGT) LNG": "Gas Plant (CCGT) LNG",
        "Hydro (reservoir)": "Hydro (reservoir)",
        "Hydro (run-of-river)": "Hydro (run-of-river)",
        "Nuclear Plant": "Nuclear Plant",
        "solarPV": "Solar PV",
        "windoff": "Wind (offshore)",
        "windon": "Wind (onshore)",
    }
    STOCK_TECHS = ["solarPV", "windon", "windoff"]
    STOCK_PLOT_NAMES = [TECH_NAME_MAP[t] for t in STOCK_TECHS]

    nzia_variants = [
        {
            "label": "with_NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG,
        },
        {
            "label": "without_NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG,
        },
    ]

    for nzia in nzia_variants:
        for lr_code, lr_name in LEARNING_RATES.items():
            for scenario in nzia["scenarios"]:
                print(f"Processing: {nzia['label']} | {lr_code} | {scenario}")
                file_path = (
                    Path(RESULTS_BASE_PATH)
                    / nzia["variant"]
                    / lr_code
                    / "rolling_2024_to_2050"
                    / f"scenario_{scenario}.xlsx"
                )

                if not file_path.exists():
                    print(f"File not found: {file_path}")
                    continue

                output_dir = Path("scenario_comparison") / nzia["label"] / lr_code
                output_dir.mkdir(parents=True, exist_ok=True)

                # --- CAPACITY DATA ---
                try:
                    df_caps = pd.read_excel(
                        file_path, sheet_name="extension_total_caps"
                    )
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
                    continue

                df_caps["stf"] = df_caps["stf"].fillna(method="ffill")
                df_caps["stf"] = pd.to_numeric(df_caps["stf"], errors="coerce").astype(
                    int
                )
                df_caps = df_caps[df_caps["stf"] <= max_year]
                df_caps = df_caps[~df_caps["pro"].isin(techs_exclude)]
                df_caps["PlotTech"] = df_caps["pro"].map(TECH_NAME_MAP)
                df_caps = df_caps[~df_caps["PlotTech"].isna()]
                df_grouped = (
                    df_caps.groupby(["stf", "PlotTech"])["cap_pro"].sum().reset_index()
                )
                df_pivot = df_grouped.pivot_table(
                    index="stf",
                    columns="PlotTech",
                    values="cap_pro",
                    aggfunc="sum",
                    fill_value=0,
                )
                df_pivot_gw = df_pivot / 1e3  # MW to GW
                cols_to_plot = [col for col in df_pivot_gw.columns if col in colors]
                df_plot = df_pivot_gw[cols_to_plot]

                # --- STOCK DATA ---
                try:
                    df_stock = pd.read_excel(
                        file_path, sheet_name="extension_only_caps"
                    )
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
                    continue

                df_stock["stf"] = df_stock["stf"].fillna(method="ffill")
                df_stock["stf"] = pd.to_numeric(
                    df_stock["stf"], errors="coerce"
                ).astype(int)
                df_stock = df_stock[df_stock["stf"] <= max_year]
                df_stock = df_stock[df_stock["tech"].isin(STOCK_TECHS)]
                df_stock_grouped = (
                    df_stock.groupby(["stf", "tech"])["capacity_ext_stock"]
                    .sum()
                    .reset_index()
                )
                df_stock_grouped["PlotTech"] = df_stock_grouped["tech"].map(
                    TECH_NAME_MAP
                )
                df_stock_pivot = df_stock_grouped.pivot_table(
                    index="stf",
                    columns="PlotTech",
                    values="capacity_ext_stock",
                    aggfunc="sum",
                    fill_value=0,
                )
                df_stock_gw = df_stock_pivot / 1e3  # MW to GW

                # --- Align years for both plots ---
                all_years = sorted(set(df_plot.index) | set(df_stock_gw.index))
                df_plot = df_plot.reindex(all_years, fill_value=0)
                df_stock_gw = df_stock_gw.reindex(all_years, fill_value=0)

                # 1. --- CAPACITY MIX STACKED BAR ---
                fig, ax = plt.subplots(figsize=(12, 8))
                bar_width = 0.8
                x = range(len(df_plot.index))
                bottoms = [0] * len(df_plot.index)
                for col in df_plot.columns:
                    ax.bar(
                        x,
                        df_plot[col],
                        bar_width,
                        bottom=bottoms,
                        label=col,
                        color=colors[col],
                    )
                    bottoms = [b + v for b, v in zip(bottoms, df_plot[col].values)]

                ax.set_xticks(list(x))
                ax.set_xticklabels(
                    [
                        int(year) if year in years_of_interest else ""
                        for year in df_plot.index
                    ],
                    rotation=0,
                    fontsize=13,
                )
                ax.set_xlim(-0.5, len(df_plot.index) - 0.5)
                ax.grid(axis="y", color="#758D99", alpha=0.4, zorder=1)
                ax.set_ylabel("Total Capacity (GW)", fontsize=15)
                ax.set_xlabel("")
                ax.set_yticklabels(ax.get_yticks(), fontsize=14)
                ax.tick_params(axis="x", which="major", length=5)
                from matplotlib.patches import Patch

                legend_patches = [
                    Patch(facecolor=colors[col], label=col) for col in cols_to_plot
                ]
                ax.legend(
                    handles=legend_patches,
                    loc="lower center",
                    ncol=3,
                    fontsize=12,
                    bbox_to_anchor=(0.5, 1.06),
                    framealpha=0.9,
                    borderpad=0.8,
                    edgecolor="black",
                )
                plt.tight_layout()
                plt.xlim(-0.5, len(df_plot.index) - 0.5)
                plt.ylim(bottom=0, top=max(bottoms) * 1.1 if bottoms else 1)
                output_file = output_dir / f"capacity_mix_{scenario}.png"
                plt.savefig(output_file)
                plt.close(fig)
                print(f"Saved capacity mix bar plot as: {output_file}")

                # 2. --- STOCK LEVELS STACKED BAR ---
                fig2, ax2 = plt.subplots(figsize=(12, 8))
                bottoms = [0] * len(df_stock_gw.index)
                for col in STOCK_PLOT_NAMES:
                    values = df_stock_gw[col].values
                    ax2.bar(
                        x,
                        values,
                        bar_width,
                        bottom=bottoms,
                        label=col,
                        color=colors[col],
                        alpha=0.8,
                    )
                    bottoms = [b + v for b, v in zip(bottoms, values)]
                ax2.set_xticks(list(x))
                ax2.set_xticklabels(
                    [
                        int(year) if year in years_of_interest else ""
                        for year in df_stock_gw.index
                    ],
                    rotation=0,
                    fontsize=13,
                )
                ax2.set_xlim(-0.5, len(df_stock_gw.index) - 0.5)
                ax2.grid(axis="y", color="#758D99", alpha=0.4, zorder=1)
                ax2.set_ylabel("Stock Level (GW)", fontsize=15)
                ax2.set_xlabel("")
                ax2.set_yticklabels(ax2.get_yticks(), fontsize=14)
                ax2.tick_params(axis="x", which="major", length=5)
                legend_stock = [
                    Patch(facecolor=colors[col], label=col) for col in STOCK_PLOT_NAMES
                ]
                ax2.legend(
                    handles=legend_stock,
                    loc="lower center",
                    ncol=3,
                    fontsize=12,
                    bbox_to_anchor=(0.5, 1.06),
                    framealpha=0.9,
                    borderpad=0.8,
                    edgecolor="black",
                )
                plt.tight_layout()
                plt.xlim(-0.5, len(df_stock_gw.index) - 0.5)
                plt.ylim(bottom=0, top=max(bottoms) * 1.1 if bottoms else 1)
                output_file2 = output_dir / f"stock_levels_{scenario}.png"
                plt.savefig(output_file2)
                plt.close(fig2)
                print(f"Saved stock level stacked bar plot as: {output_file2}")

    print("✓ All US capacity and stock stacked bar plots completed!")


def summarize_capacity_and_stock_all_LRs():
    # Define mappings and constants
    years_of_interest = [2024, 2030, 2035, 2040]
    max_year = 2040

    techs_exclude = ["Batteries"]

    TECH_NAME_MAP = {
        "Biomass Plant": "Biomass Plant",
        "Coal CCUS": "Coal CCUS",
        "Coal Lignite": "Coal Lignite",
        "Coal Lignite CCUS": "Coal Lignite CCUS",
        "Coal Plant": "Coal Plant",
        "Gas Plant (CCGT)": "Gas Plant (CCGT)",
        "Gas Plant (CCGT) CCUS": "Gas Plant (CCGT) CCUS",
        "Gas Plant (CCGT) LNG": "Gas Plant (CCGT) LNG",
        "Hydro (reservoir)": "Hydro (reservoir)",
        "Hydro (run-of-river)": "Hydro (run-of-river)",
        "Nuclear Plant": "Nuclear Plant",
        "solarPV": "Solar PV",
        "windoff": "Wind (offshore)",
        "windon": "Wind (onshore)",
    }
    STOCK_TECHS = ["solarPV", "windon", "windoff"]
    STOCK_PLOT_NAMES = [TECH_NAME_MAP[t] for t in STOCK_TECHS]

    # Define variants as in your plotting function
    nzia_variants = [
        {
            "label": "with_NZIA",
            "variant": "results_with_nzia",
            "scenarios": SCENARIO_COMBOS_LNG,
        },
        {
            "label": "without_NZIA",
            "variant": "results_without_nzia",
            "scenarios": SCENARIO_COMBOS_LNG,
        },
    ]

    cap_records = []
    stock_records = []

    for lr_code, lr_name in LEARNING_RATES.items():
        for nzia in nzia_variants:
            for scenario in nzia["scenarios"]:
                file_path = (
                    Path(RESULTS_BASE_PATH)
                    / nzia["variant"]
                    / lr_code
                    / "rolling_2024_to_2050"
                    / f"scenario_{scenario}.xlsx"
                )
                if not file_path.exists():
                    continue

                # --- CAPACITY ---
                try:
                    df_caps = pd.read_excel(
                        file_path, sheet_name="extension_total_caps"
                    )
                except Exception:
                    continue
                df_caps["stf"] = df_caps["stf"].fillna(method="ffill")
                df_caps["stf"] = pd.to_numeric(df_caps["stf"], errors="coerce").astype(
                    int
                )
                df_caps = df_caps[df_caps["stf"] <= max_year]
                df_caps = df_caps[~df_caps["pro"].isin(techs_exclude)]
                df_caps["PlotTech"] = df_caps["pro"].map(TECH_NAME_MAP)
                df_caps = df_caps[~df_caps["PlotTech"].isna()]
                grouped = (
                    df_caps.groupby(["stf", "PlotTech"])["cap_pro"].sum().reset_index()
                )
                grouped["cap_pro_GW"] = grouped["cap_pro"] / 1e3
                grouped["LearningRate"] = lr_code
                cap_records.append(
                    grouped[["stf", "PlotTech", "LearningRate", "cap_pro_GW"]]
                )

                # --- STOCK ---
                try:
                    df_stock = pd.read_excel(
                        file_path, sheet_name="extension_only_caps"
                    )
                except Exception:
                    continue
                df_stock["stf"] = df_stock["stf"].fillna(method="ffill")
                df_stock["stf"] = pd.to_numeric(
                    df_stock["stf"], errors="coerce"
                ).astype(int)
                df_stock = df_stock[df_stock["stf"] <= max_year]
                df_stock = df_stock[df_stock["tech"].isin(STOCK_TECHS)]
                stock_grouped = (
                    df_stock.groupby(["stf", "tech"])["capacity_ext_stock"]
                    .sum()
                    .reset_index()
                )
                stock_grouped["PlotTech"] = stock_grouped["tech"].map(TECH_NAME_MAP)
                stock_grouped = stock_grouped[~stock_grouped["PlotTech"].isna()]
                stock_grouped["LearningRate"] = lr_code
                stock_grouped["stock_GW"] = stock_grouped["capacity_ext_stock"] / 1e3
                stock_records.append(
                    stock_grouped[["stf", "PlotTech", "LearningRate", "stock_GW"]]
                )

    # ---- Capacity summary ----
    if cap_records:
        cap_df = pd.concat(cap_records, ignore_index=True)
        cap_summary = (
            cap_df.groupby(["stf", "PlotTech", "LearningRate"])
            .agg(
                min_capacity_GW=("cap_pro_GW", "min"),
                max_capacity_GW=("cap_pro_GW", "max"),
                mean_capacity_GW=("cap_pro_GW", "mean"),
            )
            .reset_index()
        )
        cap_summary.to_csv("capacity_summary_all_LRs.csv", index=False)
        print("Saved: capacity_summary_all_LRs.csv")

    # ---- Stock summary ----
    if stock_records:
        stock_df = pd.concat(stock_records, ignore_index=True)
        stock_summary = (
            stock_df.groupby(["stf", "PlotTech", "LearningRate"])
            .agg(
                min_stock_GW=("stock_GW", "min"),
                max_stock_GW=("stock_GW", "max"),
                mean_stock_GW=("stock_GW", "mean"),
            )
            .reset_index()
        )
        stock_summary.to_csv("stocklevel_summary_all_LRs.csv", index=False)
        print("Saved: stocklevel_summary_all_LRs.csv")


def main():
    """
    Main entry point for scenario_comparison_rolling.py.
    Uncomment the desired plot functions to generate the corresponding plots.
    """
    # Example: Uncomment the plots you want to generate
    # plot_capacity_additions_by_technology_and_lr_nzia_split()
    # lng_lineplot_range_comp_basecase_3x3()
    # plot_pareto_cost_vs_total_domestic_additions()
    # plot_domestic_percentage_heatmap()
    # plot_domestic_percentage_heatmap_scenario_driven()
    # plot_combined_domestic_percentage_heatmap()
    # co2_lineplot_range_comp_basecase()
    # plot_total_system_cost_matrix_2024_2040()
    # plot_capacity_and_stock_separately()
    # summarize_capacity_and_stock_all_LRs()
    pass


if __name__ == "__main__":
    main()
