import itertools
import re

# Adjust as needed
price_levels = ["min", "avg", "high"]
lng_scenarios = ["LNG_NZ", "LNG_PF"]  # Net Zero and Persisting Fossil
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

def generate_scenario_function(solar_lvl, wind_lvl, batt_lvl, lng_scenario):
    func_name = f"scenario_{solar_lvl}_{wind_lvl}_{batt_lvl}_{lng_scenario}"
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
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # ...existing piped gas logic...
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                if "{lng_scenario}" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Set LNG commodity price
                try:
                    co.loc[(stf, "EU27", "LNG", "Buy"), "price"] = lng_price
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

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

existing_scenarios = set(re.findall(r'def (scenario_[a-z]+_[a-z]+_[a-z]+_[a-z]+)\(', existing_code))

# Generate all scenario function names and code
all_combos = list(itertools.product(price_levels, repeat=3))
to_add = []
scenario_list_entries = []

for combo in all_combos:
    for lng_scenario in lng_scenarios:
        name = f"scenario_{combo[0]}_{combo[1]}_{combo[2]}_{lng_scenario}"
        scenario_list_entries.append(f'    ("{name}", urbs.{name})')
        if name not in existing_scenarios:
            to_add.append(generate_scenario_function(*combo, lng_scenario))

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
