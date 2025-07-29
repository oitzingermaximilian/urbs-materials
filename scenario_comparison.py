import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

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
RESULTS_BASE_PATH = r"C:\Users\maxoi\OneDrive\Desktop\results_crm_paper"

# Define learning rate scenarios - updated with all your LRs including LR6
LEARNING_RATES = {
    "LR1": "1% Learning Rate",
    "LR3_5": "3.5% Learning Rate",
    "LR4": "4% Learning Rate",
    "LR5": "5% Learning Rate",
    "LR6": "6% Learning Rate",
    "LR10": "10% Learning Rate",
    "LR25": "25% Learning Rate"
}

# Define price scenarios in order - updated to match CRM_Paper scenarios
PRICE_SCENARIOS = [
    "extremely_low",
    "very_low",
    "low",
    "moderately_low",
    "slightly_below_average",
    "average",
    "slightly_above_average",
    "moderately_high",
    "high",
    "very_high",
    "extremely_high"
]

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

def plot_eu_secondary_additions_by_years():
    """Plot EU secondary additions across different years and price scenarios for each technology using boxplots"""

    # Create output directory
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)
    print(f"Created/using output directory: {output_dir}")

    # First, let's identify what technologies are available
    sample_df = load_scenario_data("LR25", "moderate", "Total Cap Sec")
    if sample_df is None:
        print("Error: Could not load sample data to identify technologies")
        return

    # Get unique technologies from the data
    technologies = sample_df['key_1'].unique()
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

            for scenario in PRICE_SCENARIOS:
                scenario_data = []

                for lr_code, lr_name in LEARNING_RATES.items():
                    df = load_scenario_data(lr_code, scenario, "Total Cap Sec")

                    if df is not None:
                        # Filter for specific year and technology
                        df_year_tech = df[(df['year'] == year) & (df['key_1'] == technology)]
                        if not df_year_tech.empty:
                            # Take the value directly (no summing needed)
                            total_addition = df_year_tech['value'].iloc[0] / 1000  # Convert MW to GW
                            scenario_data.append(total_addition)
                        else:
                            print(f"Warning: No {year} data found for {lr_code} {scenario} {technology}")
                            scenario_data.append(0)
                    else:
                        scenario_data.append(0)

                data_for_boxplot.append(scenario_data)
                labels_for_boxplot.append(scenario.replace('_', ' ').title())

            # Create boxplot for this year
            box_plot = ax.boxplot(data_for_boxplot,
                                 labels=labels_for_boxplot,
                                 patch_artist=True,
                                 showmeans=True,
                                 meanprops={'marker': 'D', 'markerfacecolor': 'red', 'markeredgecolor': 'red', 'markersize': 8})

            # Color the boxes with a gradient
            colors_gradient = ['#E8F4FD', '#B8D4E8', '#88B5D3', '#5896BE', '#2877A9']
            for patch, color in zip(box_plot['boxes'], colors_gradient):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

            # Customize each subplot
            ax.set_xlabel('Price Scenarios')
            ax.set_ylabel('EU Secondary Additions (GW)')
            ax.set_title(f'{technology} - {year}')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(bottom=0)

            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # Add overall title for the technology
        fig.suptitle(f'{technology} - EU Secondary Capacity Additions Across Years', fontsize=16, y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # Save the plot for this technology
        safe_tech_name = technology.replace('/', '_').replace(' ', '_')
        output_path = output_dir / f"{safe_tech_name}_eu_secondary_by_years_boxplots.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot for {technology}: {output_path}")

        plt.show()

def plot_eu_secondary_additions_2040():
    """Plot total EU secondary additions in 2040 across price scenarios and learning rates for each technology using boxplots"""
    # Keep the original function for backward compatibility
    plot_eu_secondary_additions_by_years()

def plot_lng_demand_comparison():
    """Plot LNG demand comparison across learning rates and price scenarios"""

    # First, let's check what sheets are available to find LNG demand data
    sample_file = Path(RESULTS_BASE_PATH) / "LR25" / "result_scenario_moderate.xlsx"

    if sample_file.exists():
        try:
            xl = pd.ExcelFile(sample_file)
            print("Available sheets:", xl.sheet_names)

            # Look for sheets that might contain LNG demand data
            potential_sheets = [sheet for sheet in xl.sheet_names
                              if any(keyword in sheet.lower() for keyword in
                                   ['lng', 'demand', 'gas', 'import', 'balance'])]
            print("Potential LNG-related sheets:", potential_sheets)

        except Exception as e:
            print(f"Error reading sample file: {e}")

    # For now, let's create a placeholder plot structure
    # You can modify this once we identify the correct sheet name
    fig, ax = plt.subplots(figsize=(12, 8))

    # Placeholder data - replace with actual LNG demand data
    data_for_plot = {}

    for lr_code, lr_name in LEARNING_RATES.items():
        lng_demands = []

        for scenario in PRICE_SCENARIOS:
            # TODO: Replace 'LNG_SHEET_NAME' with the actual sheet name containing LNG data
            # df = load_scenario_data(lr_code, scenario, 'LNG_SHEET_NAME')
            # For now, using placeholder values
            lng_demands.append(np.random.uniform(50, 150))  # Placeholder

        data_for_plot[lr_name] = lng_demands

    # Create the plot
    x_positions = np.arange(len(PRICE_SCENARIOS))

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    for i, (lr_name, values) in enumerate(data_for_plot.items()):
        ax.plot(x_positions, values, marker='o', linewidth=2,
               markersize=8, label=lr_name, color=colors[i])

    ax.set_xlabel('Price Scenarios')
    ax.set_ylabel('LNG Demand (BCM)')  # Adjust unit as needed
    ax.set_title('LNG Demand Comparison Across Learning Rates and Price Scenarios')
    ax.set_xticks(x_positions)
    ax.set_xticklabels([scenario.replace('_', ' ').title() for scenario in PRICE_SCENARIOS])
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save the plot
    output_path = Path("scenario_comparison_lng_demand.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot: {output_path}")

    plt.show()

def main():
    """Main function to generate all comparison plots"""
    print("Starting scenario comparison plotting...")
    print(f"Results base path: {RESULTS_BASE_PATH}")

    # Check if base path exists
    if not Path(RESULTS_BASE_PATH).exists():
        print(f"Error: Results path does not exist: {RESULTS_BASE_PATH}")
        return

    # Generate plots
    print("\n1. Generating EU Secondary Additions 2040 comparison...")
    plot_eu_secondary_additions_2040()

    print("\n2. Generating LNG Demand comparison...")
    plot_lng_demand_comparison()

    print("\nScenario comparison plotting completed!")

if __name__ == "__main__":
    main()
