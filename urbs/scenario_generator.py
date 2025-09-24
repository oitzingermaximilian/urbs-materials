import itertools
import re

# Adjust as needed
price_levels = ["min", "avg", "high"]

price_values = {
    "solarPV": {"min": 838.7, "avg": 1258.05, "high": 1677.4},
    "windon": {"min": 4673.4, "avg": 7010.1, "high": 9346.8},
    "windoff": {"min": 5563.4, "avg": 8345.15, "high": 11126.8},
    "Batteries": {
        "min": 1344.3,
        "avg": 2016.45,
        "high": 2688.6,
    },  # can be fixed if you want
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

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {{}}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {{
            2031: 115.9, 2032: 118.4, 2033: 120.9, 2034: 123.4, 2035: 125.9,
            2036: 128.4, 2037: 130.9, 2038: 133.4, 2039: 135.9, 2040: 147.0,
            2041: 149.1, 2042: 151.2, 2043: 153.3, 2044: 155.4, 2045: 157.5,
            2046: 159.6, 2047: 161.7, 2048: 163.8, 2049: 165.9, 2050: 168.0
        }}
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 218766666.7, 229875000, 240983333.3, 252091666.7, 263208333.3,
            255236445.9, 262008333.3, 268783333.3, 275558333.3, 282333333.3, 289108333.3,
            295891666.7, 302666666.7, 309441666.7, 316216666.7, 294534045.3, 304233333.3,
            313933333.3, 323633333.3, 333333333.3, 343033333.3, 352733333.3, 362433333.3,
            372133333.3, 381858333.3, 338580792.8
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        # Copy all process logic from high_high_high scenario here

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)
        for stf in data["global_prop"].index.levels[0].tolist():
            mask = proco.index.get_level_values("support_timeframe") == stf
            proco.loc[mask, ["ratio-min"]] = proco_2024["ratio"].values

    # ---------------- RECYCLING COST ----------------
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
    return func_name, func


# ---------------- WRITE ALL SCENARIOS ----------------
scenarios_file = "scenarios.py"

try:
    with open(scenarios_file, "r") as f:
        existing_code = f.read()
except FileNotFoundError:
    existing_code = ""

all_combos = list(
    itertools.product(price_levels, repeat=3)
)  # 3 techs: solarPV, windon, windoff
to_write = []
scenario_list_entries = []

for combo in all_combos:
    func_name, func_code = generate_scenario_function(*combo)
    scenario_list_entries.append(f'    ("{func_name}", urbs.{func_name})')
    if func_name not in existing_code:
        to_write.append(func_code)

if to_write:
    with open(scenarios_file, "a") as f:
        for func in to_write:
            f.write(func)

# Print scenario list
print("scenarios = [")
for entry in scenario_list_entries:
    print(entry + ",")
print("]")
