import os
import shutil
import argparse
import urbs
from datetime import date
import pandas as pd
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
    choices=["LR1", "LR3_5", "LR4", "LR4", "LR6", "LR7", "LR8", "LR9", "LR10", "LR25"],
    default="LR4",
    help="Learning rate scenario (default: LR4)",
)
args = parser.parse_args()

# Set environment variable for learning rate BEFORE importing urbs
os.environ["URBS_LR"] = args.lr

# Original setup (unchanged)
input_files = "urbs_intertemporal_2050"
input_dir = "Input"
input_path = os.path.join(input_dir, input_files)

learning_rate = args.lr  # Use the selected learning rate
result_name = f"urbs-{learning_rate}"
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
scenarios = [
    ("scenario_solar_recycling_low", urbs.scenario_solar_recycling_low),
    ("scenario_solar_recycling_medium", urbs.scenario_solar_recycling_medium),
    ("scenario_solar_recycling_high", urbs.scenario_solar_recycling_high),
]


def run_perfect_foresight():
    """Original perfect foresight execution"""
    for scenario_name, scenario in scenarios:
        prob = urbs.run_scenario(
            input_path,
            solver,
            timesteps,
            scenario,
            result_dir,
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
