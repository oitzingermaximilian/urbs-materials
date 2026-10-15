import os
import shutil
import argparse
import urbs
from datetime import date
import pandas as pd
from copy import deepcopy
from collections import defaultdict
import warnings  # <--- 1. Import warnings here

# <--- 2. Paste this block right here, before other imports like pandas or pyomo
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# Add command-line argument parsing
parser = argparse.ArgumentParser(
    description="Run URBS model in different optimization modes."
)
parser.add_argument(
    "--mode",
    choices=["perfect", "rolling"],
    default="perfect",
    help='Optimization mode: "perfect" (default) or "rolling" horizon',
)
parser.add_argument(
    "--window",
    type=int,
    default=5,
    help="Rolling horizon window length in years (default: 5)",
)
parser.add_argument(
    "--lr",
    choices=["all", "LR1", "LR4", "LR7", "LR10"],
    default="all",
    help="Learning rate scenario, or all four matrix levels (default: all)",
)
parser.add_argument(
    "--audit-matrix",
    action="store_true",
    help="Write the exact smallest/largest matrix coefficients for each run",
)
args = parser.parse_args()

# Set environment variable for learning rate BEFORE importing urbs
os.environ["URBS_LR"] = "LR4"
if args.audit_matrix:
    os.environ["URBS_AUDIT_MATRIX"] = "1"

# Original setup (unchanged)
# Use the new master Excel file instead of the directory
input_files = "urbs_intertemporal_master_vintages.xlsx"
input_dir = "Input"
input_path = os.path.join(input_dir, input_files)

result_name = "scenario-matrix" if args.lr == "all" else f"urbs-{args.lr}"
result_dir = urbs.prepare_result_directory(result_name)
year = date.today().year

# Copy input/run files to result directory
try:
    shutil.copytree(input_path, os.path.join(result_dir, input_dir))
except NotADirectoryError:
    shutil.copyfile(input_path, os.path.join(result_dir, input_files))
shutil.copy(__file__, result_dir)

# Configuration (unchanged)
objective = "cost"
solver = "gurobi"
(offset, length) = (0, 12)
timesteps = range(offset, offset + length + 1)
dt = 730

# Reporting/plotting setup (unchanged)
report_tuples = []
report_sites_name = {("EU27"): "All"}
plot_tuples = []
plot_sites_name = {("EU27"): "All"}
plot_periods = {"all": timesteps[1:]}
my_colors = {"EU27": (200, 230, 200)}
for country, color in my_colors.items():
    urbs.COLORS[country] = color
# Generate the full learning-rate x industry-independence x material-price matrix.
scenarios = []
learning_rates = ["LR1", "LR4", "LR7", "LR10"]
industry_levels = [
    ("nzia_0_crma_0", 0.00, 0.00),
    ("nzia_15_crma_10", 0.15, 0.10),
    ("nzia_30_crma_20", 0.30, 0.20),
    ("nzia_40_crma_25", 0.40, 0.25),
    ("nzia_50_crma_35", 0.50, 0.35),
]
material_levels = [
    ("materials_base", 1.00, 1.00, 1.00),
    ("materials_price_150", 1.50, 1.00, 1.00),
    ("materials_tier1_50_tier2_75_price_150", 1.50, 0.50, 0.75),
    ("materials_tier1_25_tier2_50_price_200", 2.00, 0.25, 0.50),
]


def make_matrix_scenario(
    learning_rate,
    industry_name,
    nzia_quota,
    crma_quota,
    material_name,
    price_multiplier,
    tier1_limit_multiplier,
    tier2_limit_multiplier,
):
    scenario_name = f"{learning_rate}_{industry_name}_{material_name}"

    def matrix_scenario(data, data_urbsextensionv1):
        extension_data = deepcopy(data_urbsextensionv1)
        extension_data["learning_rate"] = learning_rate
        extension_data["nzia_quota"] = nzia_quota
        extension_data["crma_quota"] = crma_quota
        extension_data["mat_prices"] = {
            key: value * price_multiplier
            for key, value in extension_data["mat_prices"].items()
        }
        limit_multipliers = {
            "Tier1": tier1_limit_multiplier,
            "Tier2": tier2_limit_multiplier,
        }
        extension_data["mat_limits"] = {
            key: value * limit_multipliers.get(key[2], 1.0)
            for key, value in extension_data["mat_limits"].items()
        }
        return data, extension_data

    matrix_scenario.__name__ = scenario_name
    return matrix_scenario


for learning_rate in learning_rates:
    if args.lr != "all" and args.lr != learning_rate:
        continue
    for industry_name, nzia_quota, crma_quota in industry_levels:
        for material_name, price_multiplier, tier1_multiplier, tier2_multiplier in material_levels:
            scenario_name = (
                f"{learning_rate}_{industry_name}_{material_name}"
            )
            scenarios.append(
                (
                    scenario_name,
                    make_matrix_scenario(
                        learning_rate,
                        industry_name,
                        nzia_quota,
                        crma_quota,
                        material_name,
                        price_multiplier,
                        tier1_multiplier,
                        tier2_multiplier,
                    ),
                )
            )


def run_perfect_foresight():
    """Original perfect foresight execution"""
    for scenario_name, scenario in scenarios:
        print(f"\n🚀 RUNNING: {scenario_name}")

        # Create a dynamic subfolder so quota runs do not overwrite each other.
        dynamic_result_dir = os.path.join(result_dir, scenario_name)
        os.makedirs(dynamic_result_dir, exist_ok=True)

        prob = urbs.run_scenario(
            input_path,
            solver,
            timesteps,
            scenario,
            dynamic_result_dir,  # <-- Save to the specific dynamic folder
            dt,
            objective,
            plot_tuples=plot_tuples,
            plot_sites_name=plot_sites_name,
            plot_periods=plot_periods,
            report_tuples=report_tuples,
            report_sites_name=report_sites_name,
        )


# Execute selected mode
if args.mode == "perfect":
    print("Running in perfect foresight mode")
    run_perfect_foresight()

print("\nSimulation completed successfully!")
