import itertools
import re

# Adjust as needed
price_levels = ["min", "avg", "high"]

price_values = {
    "solarPV": {"min": 685.4, "avg": 1720.584, "high": 5490.56},
    "windon": {"min": 1982.15, "avg": 4975.2, "high": 15877},
    "windoff": {"min": 3462.33, "avg": 8690.45, "high":27733.28 },
    "Batteries": {
        "min": 5309.74,
        "avg": 13327.455,
        "high": 42531.04,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
