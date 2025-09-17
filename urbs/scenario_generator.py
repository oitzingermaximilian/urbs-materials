import itertools
import re

# Adjust as needed
price_levels = ["min", "avg", "high"]

price_values = {
    "solarPV": {"min": 838.7, "avg": 1258.05, "high": 1677.4},
    "windon": {"min": 4673.4, "avg": 7010.1, "high": 9346.8},
    "windoff": {"min": 5563.4, "avg": 8345.15, "high": 11126.8},
    "Batteries": {"min": 1344.3, "avg": 2016.45, "high": 2688.6},
}


def get_cost_combo(solar_lvl, wind_lvl, batt_lvl):
    return {
        "solarPV": price_values["solarPV"][solar_lvl],
        "windon": price_values["windon"][wind_lvl],
        "windoff": price_values["windoff"][wind_lvl],
        "Batteries": price_values["Batteries"][batt_lvl],
    }


def generate_scenario_function(solar_lvl, wind_lvl, batt_lvl):
    func_name = f"scenario_{solar_lvl}_{wind_lvl}_{batt_lvl}"
    costs = get_cost_combo(solar_lvl, wind_lvl, batt_lvl)
    cost_str = ",\n            ".join([f'"{k}": {v}' for k, v in costs.items()])

    func = f"""
def {func_name}(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {{
            {cost_str}
        }}
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1
"""
    return func


# Read existing scenario function names from scenarios.py
scenarios_file = "scenarios.py"
try:
    with open(scenarios_file, "r") as f:
        existing_code = f.read()
except FileNotFoundError:
    existing_code = ""

existing_scenarios = set(
    re.findall(r"def (scenario_[a-z]+_[a-z]+_[a-z]+)\(", existing_code)
)

# Generate all scenario function names and code
all_combos = list(itertools.product(price_levels, repeat=3))
to_add = []
scenario_list_entries = []

for combo in all_combos:
    name = f"scenario_{combo[0]}_{combo[1]}_{combo[2]}"
    scenario_list_entries.append(f'    ("{name}", urbs.{name})')
    if name not in existing_scenarios:
        to_add.append(generate_scenario_function(*combo))

# Append missing scenario functions to the file
if to_add:
    with open(scenarios_file, "a") as f:
        for func in to_add:
            f.write(func)

print("\nAdd this to your scenario list:")
print("scenarios = [")
for entry in scenario_list_entries:
    print(entry + ",")
print("]")
