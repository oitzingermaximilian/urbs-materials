import itertools
import re

# Adjust as needed
price_levels = ["min", "avg", "high"]
price_values = {
    "solarPV":   {"min": 685,   "avg": 1720,   "high": 5490},
    "windon":    {"min": 1000, "avg": 2500,  "high": 5000},
    "windoff":   {"min": 1000,"avg": 2500,  "high": 5000},
    "Batteries": {"min": 1508, "avg": 6743,   "high": 20608}
}

def get_cost_combo(solar_lvl, wind_lvl, batt_lvl):
    return {
        "solarPV": price_values["solarPV"][solar_lvl],
        "windon": price_values["windon"][wind_lvl],
        "windoff": price_values["windoff"][wind_lvl],
        "Batteries": price_values["Batteries"][batt_lvl]
    }

def generate_scenario_function(solar_lvl, wind_lvl, batt_lvl):
    func_name = f"scenario_{solar_lvl}_{wind_lvl}_{batt_lvl}"
    costs = get_cost_combo(solar_lvl, wind_lvl, batt_lvl)
    cost_str = ",\n            ".join([f'"{k}": {v}' for k, v in costs.items()])
    func = f'''
def {func_name}(data, data_urbsextensionv1):
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 0
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 0
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 0
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 0
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0

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
                    print(f"Updated recycling cost for {{tech}} in {{stf}} to {{new_costs[tech]}} EUR/ton")
    return data, data_urbsextensionv1
'''
    return func

# Read existing scenario function names from scenarios.py
scenarios_file = "scenarios.py"
try:
    with open(scenarios_file, "r") as f:
        existing_code = f.read()
except FileNotFoundError:
    existing_code = ""

existing_scenarios = set(re.findall(r'def (scenario_[a-z]+_[a-z]+_[a-z]+)\(', existing_code))

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