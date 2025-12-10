import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import os

# Define file path — adjust for your system
desktop_path = r"C:/Users/maxoi/GitHub/urbs-extension/plots"
file_name = "LCOE_grouped_bar.png"
file_path = os.path.join(desktop_path, file_name)
plt.rcParams["font.family"] = "Arial"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# Optional: default font size for these plots
plt.rcParams["font.size"] = 8


# -----------------------------
# Function to calculate LCOE
# -----------------------------
def calculate_lcoe(
    capex, om_cost, capacity, capacity_factor, lifetime, discount_rate=0.07
):
    """
    Calculate LCOE with discounting for a given tech option.
    """
    capital_cost = capex * capacity
    discounted_om = 0
    discounted_energy = 0

    for year in range(1, lifetime + 1):
        discounted_om += om_cost * capacity / ((1 + discount_rate) ** year)
        discounted_energy += (
            capacity * capacity_factor * 8760 / ((1 + discount_rate) ** year)
        )

    total_cost = capital_cost + discounted_om
    lcoe = total_cost / discounted_energy
    return lcoe


# -----------------------------
# Define technologies & supply options
# -----------------------------
capex_option_names = [
    "Import",
    "Manufacturing",
    "Rem. - Low",
    "Rem. - Avg",
    "Rem.- High",
]

technologies = {
    "Solar PV": {
        "capacity": 1,
        "capacity_factor": 0.125,
        "om_cost": 4400,
        "lifetime": 25,
        "capex_options": [250240, 303600, 310423.02, 390052.48, 680050.35],
    },
    "Onshore Wind": {
        "capacity": 1,
        "capacity_factor": 0.3,
        "om_cost": 17386.63,
        "lifetime": 20,
        "capex_options": [1052044.84, 1673707.7, 1377124.68, 1730304.07, 3016719.09],
    },
    "Offshore Wind": {
        "capacity": 1,
        "capacity_factor": 0.481,
        "om_cost": 44000,
        "lifetime": 20,
        "capex_options": [1775265.64, 2337972.5216, 2405501.38, 3022419.75, 5269473.43],
    },
}

discount_rate = 0.03
results = []

# -----------------------------
# Calculate LCOEs
# -----------------------------
for tech, params in technologies.items():
    for name, capex in zip(capex_option_names, params["capex_options"]):
        lcoe = calculate_lcoe(
            capex=capex,
            om_cost=params["om_cost"],
            capacity=params["capacity"],
            capacity_factor=params["capacity_factor"],
            lifetime=params["lifetime"],  # use tech-specific lifetime
            discount_rate=discount_rate,
        )
        results.append(
            {
                "Technology": tech,
                "Supply Option": name,
                "CAPEX": capex,
                "Lifetime (years)": params["lifetime"],
                "LCOE (€/MWh)": lcoe,
            }
        )

df_results = pd.DataFrame(results)
print(df_results)

# -----------------------------
# Plot LCOE per technology & supply option
# -----------------------------
# --- RGB(A) colors you can easily modify ---
colors_255 = {
    "Solar PV": (244, 225, 0),  # yellow
    "Onshore Wind": (5, 165, 210),  # light blue
    "Offshore Wind": (58, 115, 125),  # dark blue
}

tech_colors = {
    "Solar PV": "#E69F00",  # Orange
    "Onshore Wind": "#66C2A5",  # Teal
    "Offshore Wind": "#00876C",  # Dark Green
}
# Convert 0-255 RGB to 0–1 using to_rgb
colors = {k: mcolors.to_rgb(tuple(np.array(v) / 255)) for k, v in colors_255.items()}

# Set position for grouped bar chart
supply_options = capex_option_names
x = np.arange(len(supply_options))  # positions for groups
width = 0.25  # bar width

plt.figure(figsize=(12, 7))

for i, tech in enumerate(df_results["Technology"].unique()):
    tech_data = df_results[df_results["Technology"] == tech]
    plt.bar(
        x + i * width,
        tech_data["LCOE (€/MWh)"],
        width=width,
        color=tech_colors[tech],  # RGB handled by matplotlib
        edgecolor="black",
        linewidth=1.2,
        label=tech,
    )

# Larger tick labels
plt.xticks(x + width, supply_options, rotation=45, ha="right", fontsize=20)
plt.yticks(fontsize=16)
# Add dotted horizontal grid lines
plt.grid(axis="y", linestyle=":", color="gray", alpha=0.7)
plt.ylabel("LCOE (€/MWh)", fontsize=20)
plt.legend(
    fontsize=20,
    frameon=True,
    edgecolor="black",
    facecolor="white",
    framealpha=1,
    shadow=False,
    loc="best",
    borderpad=1,
)
plt.tight_layout()
plt.savefig(file_path, dpi=1000)  # dpi=300 for publication quality
plt.show()

print(f"Plot saved to {file_path}")
